#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于LangGraph的ACT Agent Demo (集成MCP工具)
ACT: Action-Criticism-Tool-use Agent
- Action: 执行具体的动作
- Criticism: 对执行结果进行批评和评估
- Tool-use: 使用MCP工具来辅助完成任务（包括ADB移动设备控制）
"""

import json
import asyncio
import os
import time
from typing import TypedDict, List, Dict, Any, Annotated
from datetime import datetime

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 导入MCP工具驱动
from util.adb_mcp_driver import (
    execute_mcp_tool, 
    get_mcp_tools_list, 
    test_mcp_connection,
    load_client_config
)

# 定义状态类型
class ACTState(TypedDict):
    """ACT Agent状态"""
    task_description: str      # 任务描述
    current_phase: str         # 当前阶段：action, criticism, tool_use
    action_plan: Dict[str, Any]    # 行动计划
    execution_result: Dict[str, Any]   # 执行结果
    criticism: Dict[str, Any]      # 批评评估
    tool_usage: List[Dict[str, Any]]   # 工具使用记录
    iteration_count: int       # 迭代次数
    is_complete: bool         # 是否完成
    confidence_score: float   # 置信度分数
    messages: List[Any]       # 对话历史

# MCP工具箱类
class MCPToolBox:
    """ACT Agent MCP工具箱"""
    
    def __init__(self, config: dict):
        self.config = config
        self.mcp_server_url = config.get('client', {}).get('mcp_server_url')
        self.available_tools = []
        
    async def initialize(self):
        """初始化MCP连接并获取可用工具"""
        try:
            # 测试MCP连接
            connection_ok = await test_mcp_connection(
                server_url=self.mcp_server_url, 
                verbose=False
            )
            
            if connection_ok:
                # 获取可用工具列表
                self.available_tools = await get_mcp_tools_list(
                    server_url=self.mcp_server_url,
                    verbose=False
                )
                print(f"✅ MCP工具箱初始化完成，可用工具: {self.available_tools}")
            else:
                print("⚠️ MCP服务器连接失败，将使用模拟工具")
                self.available_tools = ["take_screenshot", "click_screen", "input_text", "wake_screen", "go_home"]
            
        except Exception as e:
            print(f"⚠️ MCP工具箱初始化失败: {e}")
            self.available_tools = []
    
    async def execute_tool(self, tool_name: str, tool_args: dict = None) -> Dict[str, Any]:
        """执行MCP工具"""
        if tool_args is None:
            tool_args = {}
            
        try:
            result = await execute_mcp_tool(
                tool_name=tool_name,
                tool_args=tool_args,
                server_url=self.mcp_server_url,
                save_screenshots=True,
                verbose=True
            )
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"工具执行失败: {e}",
                "tool_name": tool_name,
                "timestamp": datetime.now().isoformat()
            }
    
    async def take_screenshot(self) -> Dict[str, Any]:
        """截图工具"""
        return await self.execute_tool("take_screenshot", {"compress": True})
    
    async def click_screen(self, x: int, y: int) -> Dict[str, Any]:
        """点击屏幕"""
        return await self.execute_tool("click_screen", {"x": x, "y": y})
    
    async def input_text(self, text: str) -> Dict[str, Any]:
        """输入文本"""
        return await self.execute_tool("input_text", {"text": text})
    
    async def wake_screen(self) -> Dict[str, Any]:
        """唤醒屏幕"""
        return await self.execute_tool("wake_screen", {})
    
    async def go_home(self) -> Dict[str, Any]:
        """回到主屏幕"""
        return await self.execute_tool("go_home", {})
    
    @staticmethod
    def calculator(expression: str) -> Dict[str, Any]:
        """本地计算器（辅助工具）"""
        try:
            # 简单的安全计算
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
            else:
                result = "表达式包含不安全字符"
        except Exception as e:
            result = f"计算错误: {str(e)}"
        
        return {
            "tool": "calculator",
            "expression": expression,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        local_tools = ["calculator"]
        return self.available_tools + local_tools

class ACTAgent:
    """ACT Agent - Action-Criticism-Tool-use Agent"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化Agent"""
        # 加载配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # 使用默认配置
            self.config = {
                "openai": {
                    "api_key": "sk-test",
                    "base_url": "http://116.63.86.12:3000/v1/",
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                "client": {
                    "mcp_server_url": "http://127.0.0.1:8568/sse",
                    "screenshot_dir": "screenshots"
                }
            }
        
        openai_config = self.config.get("openai", {})
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            api_key=openai_config["api_key"],
            base_url=openai_config["base_url"],
            model=openai_config["model"],
            temperature=openai_config.get("temperature", 0.3),
            max_tokens=openai_config.get("max_tokens", 2000)
        )
        
        # 初始化MCP工具箱
        self.toolbox = MCPToolBox(self.config)
        
        # 创建检查点保存器
        self.memory = MemorySaver()
        
        # 构建状态图
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建ACT循环状态图"""
        workflow = StateGraph(ACTState)
        
        # 添加节点
        workflow.add_node("action", self._action_phase)
        workflow.add_node("criticism", self._criticism_phase)
        workflow.add_node("tool_use", self._tool_use_phase)
        workflow.add_node("complete", self._complete_phase)
        
        # 设置入口点
        workflow.add_edge(START, "action")
        
        # 定义条件边
        workflow.add_conditional_edges(
            "action",
            self._should_continue_from_action,
            {
                "tool_use": "tool_use",
                "criticism": "criticism",
                "complete": "complete"
            }
        )
        
        workflow.add_conditional_edges(
            "tool_use",
            self._should_continue_from_tool_use,
            {
                "criticism": "criticism",
                "complete": "complete"
            }
        )
        
        workflow.add_conditional_edges(
            "criticism",
            self._should_continue_from_criticism,
            {
                "action": "action",
                "complete": "complete"
            }
        )
        
        workflow.add_edge("complete", END)
        
        # 编译图
        return workflow.compile(checkpointer=self.memory)
    
    async def _action_phase(self, state: ACTState) -> ACTState:
        """行动阶段 - 制定和执行具体行动"""
        print(f"🎯 ACTION阶段 - 迭代 {state['iteration_count'] + 1}")
        
        action_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的任务执行AI助手。请为给定的任务制定具体的行动计划并模拟执行。

请按照以下JSON格式回复：
{
    "action_type": "信息收集/问题解决/创建内容/分析数据",
    "specific_actions": [
        {"step": 1, "action": "具体行动", "reasoning": "执行原因"},
        {"step": 2, "action": "具体行动", "reasoning": "执行原因"}
    ],
    "execution_result": {
        "success": true/false,
        "output": "执行输出结果",
        "challenges": ["遇到的挑战"],
        "next_steps": ["建议的后续步骤"]
    },
    "tools_needed": ["需要的工具名称"],
    "confidence": 0.8
}

可用MCP工具: take_screenshot(截图), click_screen(点击屏幕), input_text(输入文本), wake_screen(唤醒屏幕), go_home(回主屏幕)
本地工具: calculator(计算器)"""),
            ("user", f"任务：{state['task_description']}\n\n前一次批评意见：{state.get('criticism', {}).get('feedback', '无')}")
        ])
        
        response = await self.llm.ainvoke(action_prompt.format_messages())
        
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            action_result = json.loads(content)
        except json.JSONDecodeError:
            action_result = {
                "action_type": "基础执行",
                "specific_actions": [{"step": 1, "action": "开始处理任务", "reasoning": "按照标准流程"}],
                "execution_result": {
                    "success": True,
                    "output": "基本任务执行",
                    "challenges": [],
                    "next_steps": ["继续优化"]
                },
                "tools_needed": [],
                "confidence": 0.7
            }
        
        state["current_phase"] = "action"
        state["action_plan"] = action_result
        state["execution_result"] = action_result.get("execution_result", {})
        state["confidence_score"] = action_result.get("confidence", 0.7)
        state["messages"].append(AIMessage(content=f"制定行动计划：{action_result['action_type']}"))
        
        return state
    
    async def _criticism_phase(self, state: ACTState) -> ACTState:
        """批评阶段 - 评估行动结果并提供改进建议"""
        print(f"🔍 CRITICISM阶段 - 评估结果")
        
        criticism_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个严格的质量评估AI助手。请对执行的行动进行客观、建设性的批评和评估。

请按照以下JSON格式回复：
{
    "overall_assessment": "整体评估 - 优秀/良好/一般/需改进",
    "quality_score": 8.5,
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["问题1", "问题2"],
    "specific_feedback": {
        "execution_quality": "执行质量评价",
        "result_accuracy": "结果准确性评价",
        "efficiency": "效率评价"
    },
    "improvement_suggestions": [
        {"area": "改进领域", "suggestion": "具体建议", "priority": "高/中/低"}
    ],
    "should_continue": true/false,
    "next_focus": "下一步重点关注的方向"
}"""),
            ("user", f"请评估以下执行结果：\n行动计划：{json.dumps(state['action_plan'], ensure_ascii=False, indent=2)}\n\n工具使用记录：{json.dumps(state['tool_usage'][-3:] if state['tool_usage'] else [], ensure_ascii=False, indent=2)}")
        ])
        
        response = await self.llm.ainvoke(criticism_prompt.format_messages())
        
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            criticism_result = json.loads(content)
        except json.JSONDecodeError:
            criticism_result = {
                "overall_assessment": "一般",
                "quality_score": 7.0,
                "strengths": ["基本完成任务"],
                "weaknesses": ["可以进一步优化"],
                "specific_feedback": {
                    "execution_quality": "标准执行",
                    "result_accuracy": "基本准确",
                    "efficiency": "效率一般"
                },
                "improvement_suggestions": [
                    {"area": "整体优化", "suggestion": "提升执行效率", "priority": "中"}
                ],
                "should_continue": False,
                "next_focus": "总结完成"
            }
        
        state["current_phase"] = "criticism"
        state["criticism"] = criticism_result
        state["messages"].append(AIMessage(content=f"质量评估：{criticism_result['overall_assessment']} (评分: {criticism_result['quality_score']})"))
        
        return state
    
    async def _tool_use_phase(self, state: ACTState) -> ACTState:
        """工具使用阶段 - 根据需要使用工具辅助完成任务"""
        print(f"🔧 TOOL_USE阶段 - 使用工具")
        
        tools_needed = state['action_plan'].get('tools_needed', [])
        
        if not tools_needed:
            # 如果没有明确的工具需求，智能判断需要什么工具
            tool_prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个智能工具选择助手。根据任务和当前状态，判断需要使用什么工具。

可用MCP工具：
- take_screenshot: 设备截图
- click_screen: 点击屏幕坐标
- input_text: 输入文本
- wake_screen: 唤醒设备屏幕
- go_home: 回到主屏幕
本地工具：
- calculator: 数学计算

请按照以下JSON格式回复：
{
    "recommended_tools": [
        {"tool": "工具名", "purpose": "使用目的", "parameters": {"param1": "value1"}}
    ],
    "reasoning": "选择这些工具的原因"
}"""),
                ("user", f"任务：{state['task_description']}\n当前执行状态：{state['execution_result']}")
            ])
            
            response = await self.llm.ainvoke(tool_prompt.format_messages())
            
            try:
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                
                tool_recommendation = json.loads(content)
                tools_to_use = tool_recommendation.get("recommended_tools", [])
            except:
                tools_to_use = []
        else:
            # 使用明确指定的工具
            tools_to_use = [{"tool": tool, "purpose": "任务需要", "parameters": {}} for tool in tools_needed]
        
        # 执行工具
        tool_results = []
        for tool_spec in tools_to_use[:3]:  # 限制最多使用3个工具
            tool_name = tool_spec["tool"]
            
            # 执行MCP工具
            if tool_name in self.toolbox.available_tools:
                if tool_name == "take_screenshot":
                    result = await self.toolbox.take_screenshot()
                elif tool_name == "click_screen":
                    # 从任务描述中智能推断点击坐标，或使用默认值
                    x, y = 400, 500  # 默认屏幕中心位置
                    result = await self.toolbox.click_screen(x, y)
                elif tool_name == "input_text":
                    # 根据任务推断要输入的文本
                    text = f"测试文本 - {state['task_description'][:20]}"
                    result = await self.toolbox.input_text(text)
                elif tool_name == "wake_screen":
                    result = await self.toolbox.wake_screen()
                elif tool_name == "go_home":
                    result = await self.toolbox.go_home()
                else:
                    result = await self.toolbox.execute_tool(tool_name, tool_spec.get("parameters", {}))
            
            # 执行本地工具
            elif tool_name == "calculator":
                result = self.toolbox.calculator("2+2")  # 示例计算
            
            else:
                result = {"tool": tool_name, "success": False, "error": "工具不可用"}
            
            tool_results.append(result)
            status = result.get('status', result.get('success', '完成'))
            print(f"   使用工具: {tool_name} - {status}")
        
        if not tool_results:
            tool_results.append({
                "tool": "none",
                "status": "无需使用额外工具",
                "timestamp": datetime.now().isoformat()
            })
        
        state["current_phase"] = "tool_use"
        state["tool_usage"].extend(tool_results)
        state["messages"].append(AIMessage(content=f"使用了 {len(tool_results)} 个工具"))
        
        return state
    
    async def _complete_phase(self, state: ACTState) -> ACTState:
        """完成阶段 - 总结整个ACT循环的结果"""
        print(f"✅ COMPLETE阶段 - 任务完成")
        
        summary = {
            "task": state["task_description"],
            "iterations": state["iteration_count"],
            "final_confidence": state["confidence_score"],
            "tools_used": len(state["tool_usage"]),
            "final_assessment": state.get("criticism", {}).get("overall_assessment", "未评估"),
            "quality_score": state.get("criticism", {}).get("quality_score", 0.0)
        }
        
        print(f"   📊 任务总结：")
        print(f"      - 迭代次数: {summary['iterations']}")
        print(f"      - 最终置信度: {summary['final_confidence']:.2f}")
        print(f"      - 工具使用: {summary['tools_used']} 次")
        print(f"      - 质量评估: {summary['final_assessment']} ({summary['quality_score']}/10)")
        
        state["current_phase"] = "complete"
        state["is_complete"] = True
        state["messages"].append(AIMessage(content=f"任务完成 - 质量评分: {summary['quality_score']}"))
        
        return state
    
    def _should_continue_from_action(self, state: ACTState) -> str:
        """判断行动阶段后的流向"""
        tools_needed = state['action_plan'].get('tools_needed', [])
        if tools_needed:
            return "tool_use"
        else:
            return "criticism"
    
    def _should_continue_from_tool_use(self, state: ACTState) -> str:
        """判断工具使用阶段后的流向"""
        return "criticism"
    
    def _should_continue_from_criticism(self, state: ACTState) -> str:
        """判断批评阶段后的流向"""
        criticism = state.get("criticism", {})
        
        # 检查是否应该继续
        should_continue = criticism.get("should_continue", False)
        quality_score = criticism.get("quality_score", 0)
        iteration_count = state["iteration_count"]
        
        # 停止条件：质量分数高、不建议继续、或迭代次数过多
        if quality_score >= 8.0 or not should_continue or iteration_count >= 3:
            return "complete"
        else:
            state["iteration_count"] += 1
            return "action"
    
    async def process_task(self, task_description: str) -> Dict[str, Any]:
        """处理任务的主要入口函数"""
        print(f"🤖 ACT Agent (MCP版) 开始处理任务")
        print(f"🎯 任务: {task_description}")
        print("=" * 60)
        
        # 初始化MCP工具箱
        print("🔧 初始化MCP工具箱...")
        await self.toolbox.initialize()
        
        # 初始化状态
        initial_state = {
            "task_description": task_description,
            "current_phase": "action",
            "action_plan": {},
            "execution_result": {},
            "criticism": {},
            "tool_usage": [],
            "iteration_count": 0,
            "is_complete": False,
            "confidence_score": 0.0,
            "messages": [HumanMessage(content=task_description)]
        }
        
        # 执行ACT循环
        config = {"configurable": {"thread_id": f"act_task_{int(time.time())}"}}
        
        final_state = None
        async for state in self.graph.astream(initial_state, config):
            final_state = state
        
        return final_state

# 简化版ACT Agent用于快速演示
class SimpleACTAgent:
    """简化版ACT Agent"""
    
    def __init__(self):
        self.iteration = 0
        self.tools_used = 0
    
    async def run_demo(self, task: str):
        """运行简化demo"""
        print(f"🤖 简化版ACT Agent演示")
        print(f"🎯 任务: {task}")
        print("=" * 50)
        
        # Action阶段
        print(f"🎯 ACTION阶段")
        print(f"   制定计划: 分析任务需求，制定3步执行方案")
        print(f"   开始执行: 按计划逐步实施，收集中间结果")
        
        # Tool-use阶段
        print(f"🔧 TOOL-USE阶段")
        print(f"   使用工具: take_screenshot - 设备截图")
        print(f"   使用工具: click_screen - 点击屏幕")
        print(f"   使用工具: calculator - 进行数据计算")
        self.tools_used = 3
        
        # Criticism阶段
        print(f"🔍 CRITICISM阶段")
        print(f"   质量评估: 8.5/10 (良好)")
        print(f"   改进建议: 可以优化数据处理效率")
        print(f"   决定: 质量达标，完成任务")
        
        print(f"✅ 任务完成!")
        print(f"   📊 使用工具: {self.tools_used} 个")
        print(f"   📊 最终评分: 8.5/10")
        print(f"   📱 MCP设备控制: 成功连接并执行操作")

async def main():
    """主函数 - 演示ACT Agent"""
    print("🚀 LangGraph ACT Agent Demo (MCP版)")
    print("=" * 60)
    
    # 测试任务
    test_tasks = [
        "控制移动设备截图并点击屏幕进行测试操作",
        "唤醒设备屏幕，输入测试文本，然后回到主屏幕", 
        "获取设备截图，分析界面元素，执行自动化测试流程"
    ]
    
    # 选择演示模式
    mode = input("选择演示模式 (1: 完整版-MCP工具, 2: 简化版): ").strip()
    
    if mode == "1":
        # 完整版演示
        try:
            print("🔧 初始化ACT Agent (MCP版)...")
            agent = ACTAgent()
            print(f"🎯 执行任务: {test_tasks[0]}")
            
            result = await agent.process_task(test_tasks[0])
            
            print("\n" + "=" * 60)
            print("🎉 ACT循环完成!")
            
            if result:
                final_state = result.get(list(result.keys())[-1], {})
                quality_score = final_state.get("criticism", {}).get("quality_score", 0.0)
                tools_used = len(final_state.get("tool_usage", []))
                print(f"📊 最终质量评分: {quality_score}/10")
                print(f"🔧 工具使用次数: {tools_used}")
            
        except Exception as e:
            print(f"❌ 运行出错: {e}")
            print("💡 提示:")
            print("   1. 请检查config.json配置文件")
            print("   2. 确保MCP服务器正在运行")
            print("   3. 检查ADB设备连接状态")
    
    else:
        # 简化版演示
        agent = SimpleACTAgent()
        await agent.run_demo(test_tasks[0])

if __name__ == "__main__":
    asyncio.run(main()) 