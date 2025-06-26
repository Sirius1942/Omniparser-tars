#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于LangGraph的PDCA循环工作任务处理Agent Demo
PDCA: Plan-Do-Check-Act 循环
"""

import json
import asyncio
from typing import TypedDict, List, Dict, Any, Annotated
from datetime import datetime

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 定义状态类型
class PDCAState(TypedDict):
    """PDCA循环状态"""
    task_description: str  # 任务描述
    current_phase: str     # 当前阶段：plan, do, check, act
    plan: Dict[str, Any]   # 计划详情
    execution_log: List[str]  # 执行日志
    check_results: Dict[str, Any]  # 检查结果
    improvement_actions: List[str]  # 改进行动
    cycle_count: int       # 循环次数
    is_complete: bool      # 是否完成
    messages: List[Any]    # 对话历史

class PDCAAgent:
    """PDCA循环工作任务处理Agent"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化Agent"""
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        openai_config = config.get("openai", {})
        
        # 初始化LLM (注意：这里使用配置中的模型)
        self.llm = ChatOpenAI(
            api_key=openai_config["api_key"],
            base_url=openai_config["base_url"],
            model=openai_config["model"],  # 使用配置中的Qwen3-32B
            temperature=0.3,
            max_tokens=2000
        )
        
        # 创建检查点保存器
        self.memory = MemorySaver()
        
        # 构建状态图
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建PDCA循环状态图"""
        workflow = StateGraph(PDCAState)
        
        # 添加节点
        workflow.add_node("plan", self._plan_phase)
        workflow.add_node("do", self._do_phase)
        workflow.add_node("check", self._check_phase)
        workflow.add_node("act", self._act_phase)
        workflow.add_node("complete", self._complete_phase)
        
        # 设置入口点
        workflow.add_edge(START, "plan")
        
        # 定义条件边
        workflow.add_conditional_edges(
            "plan",
            self._should_continue_from_plan,
            {
                "do": "do",
                "complete": "complete"
            }
        )
        
        workflow.add_conditional_edges(
            "do",
            self._should_continue_from_do,
            {
                "check": "check",
                "complete": "complete"
            }
        )
        
        workflow.add_conditional_edges(
            "check",
            self._should_continue_from_check,
            {
                "act": "act",
                "complete": "complete"
            }
        )
        
        workflow.add_conditional_edges(
            "act",
            self._should_continue_from_act,
            {
                "plan": "plan",
                "complete": "complete"
            }
        )
        
        workflow.add_edge("complete", END)
        
        # 编译图
        return workflow.compile(checkpointer=self.memory)
    
    async def _plan_phase(self, state: PDCAState) -> PDCAState:
        """计划阶段"""
        print(f"📋 PLAN阶段 - 循环 {state['cycle_count'] + 1}")
        
        plan_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的项目管理AI助手。请为给定的工作任务制定详细的执行计划。

请按照以下JSON格式回复：
{
    "goals": ["目标1", "目标2"],
    "steps": [
        {"step": 1, "action": "具体行动", "expected_outcome": "预期结果", "timeline": "时间估计"},
        {"step": 2, "action": "具体行动", "expected_outcome": "预期结果", "timeline": "时间估计"}
    ],
    "resources_needed": ["资源1", "资源2"],
    "success_criteria": ["成功标准1", "成功标准2"],
    "potential_risks": ["风险1", "风险2"]
}"""),
            ("user", f"任务描述：{state['task_description']}\n\n之前的改进行动：{state.get('improvement_actions', [])}")
        ])
        
        response = await self.llm.ainvoke(plan_prompt.format_messages())
        
        try:
            # 解析JSON响应
            plan_content = response.content.strip()
            if plan_content.startswith("```json"):
                plan_content = plan_content.replace("```json", "").replace("```", "").strip()
            
            plan = json.loads(plan_content)
        except json.JSONDecodeError:
            # 如果JSON解析失败，创建基本计划
            plan = {
                "goals": ["完成指定任务"],
                "steps": [{"step": 1, "action": "开始执行任务", "expected_outcome": "任务进展", "timeline": "1小时"}],
                "resources_needed": ["时间", "注意力"],
                "success_criteria": ["任务完成"],
                "potential_risks": ["时间不足"]
            }
        
        state["current_phase"] = "plan"
        state["plan"] = plan
        state["messages"].append(AIMessage(content=f"制定了新的执行计划：\n{json.dumps(plan, ensure_ascii=False, indent=2)}"))
        
        return state
    
    async def _do_phase(self, state: PDCAState) -> PDCAState:
        """执行阶段"""
        print(f"🚀 DO阶段 - 执行计划")
        
        do_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个任务执行AI助手。请根据制定的计划模拟执行任务，并记录执行过程。

请按照以下JSON格式回复：
{
    "executed_steps": [
        {"step": 1, "action_taken": "实际执行的行动", "result": "执行结果", "issues": "遇到的问题"}
    ],
    "overall_progress": "整体进度百分比(0-100)",
    "challenges_encountered": ["挑战1", "挑战2"],
    "unexpected_outcomes": ["意外结果1", "意外结果2"]
}"""),
            ("user", f"请执行以下计划：\n{json.dumps(state['plan'], ensure_ascii=False, indent=2)}")
        ])
        
        response = await self.llm.ainvoke(do_prompt.format_messages())
        
        try:
            execution_content = response.content.strip()
            if execution_content.startswith("```json"):
                execution_content = execution_content.replace("```json", "").replace("```", "").strip()
            
            execution_result = json.loads(execution_content)
        except json.JSONDecodeError:
            execution_result = {
                "executed_steps": [{"step": 1, "action_taken": "执行了基本任务", "result": "取得进展", "issues": "无"}],
                "overall_progress": "50",
                "challenges_encountered": [],
                "unexpected_outcomes": []
            }
        
        # 记录执行日志
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] 执行进度: {execution_result['overall_progress']}%"
        state["execution_log"].append(log_entry)
        
        state["current_phase"] = "do"
        state["messages"].append(AIMessage(content=f"执行结果：\n{json.dumps(execution_result, ensure_ascii=False, indent=2)}"))
        
        return state
    
    async def _check_phase(self, state: PDCAState) -> PDCAState:
        """检查阶段"""
        print(f"🔍 CHECK阶段 - 检查结果")
        
        check_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个质量检查AI助手。请评估任务执行结果，与原计划进行对比。

请按照以下JSON格式回复：
{
    "goals_achieved": ["已实现的目标"],
    "goals_missed": ["未实现的目标"],
    "plan_vs_actual": {
        "planned_timeline": "计划时间",
        "actual_timeline": "实际时间",
        "planned_resources": "计划资源",
        "actual_resources": "实际资源"
    },
    "quality_score": 85,
    "areas_for_improvement": ["改进点1", "改进点2"],
    "lessons_learned": ["经验1", "经验2"],
    "next_cycle_recommendations": ["建议1", "建议2"]
}"""),
            ("user", f"原计划：\n{json.dumps(state['plan'], ensure_ascii=False, indent=2)}\n\n执行日志：\n{chr(10).join(state['execution_log'])}")
        ])
        
        response = await self.llm.ainvoke(check_prompt.format_messages())
        
        try:
            check_content = response.content.strip()
            if check_content.startswith("```json"):
                check_content = check_content.replace("```json", "").replace("```", "").strip()
            
            check_results = json.loads(check_content)
        except json.JSONDecodeError:
            check_results = {
                "goals_achieved": ["部分目标完成"],
                "goals_missed": [],
                "quality_score": 70,
                "areas_for_improvement": ["效率提升"],
                "lessons_learned": ["需要更好的计划"],
                "next_cycle_recommendations": ["优化流程"]
            }
        
        state["current_phase"] = "check"
        state["check_results"] = check_results
        state["messages"].append(AIMessage(content=f"检查结果：\n{json.dumps(check_results, ensure_ascii=False, indent=2)}"))
        
        return state
    
    async def _act_phase(self, state: PDCAState) -> PDCAState:
        """行动阶段"""
        print(f"⚡ ACT阶段 - 制定改进行动")
        
        act_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个持续改进AI助手。基于检查结果，制定具体的改进行动。

请按照以下JSON格式回复：
{
    "improvement_actions": ["具体改进行动1", "具体改进行动2"],
    "process_changes": ["流程改变1", "流程改变2"],
    "resource_adjustments": ["资源调整1", "资源调整2"],
    "should_continue_cycle": true,
    "reason_to_continue": "继续的原因",
    "expected_improvements": ["预期改进1", "预期改进2"]
}"""),
            ("user", f"检查结果：\n{json.dumps(state['check_results'], ensure_ascii=False, indent=2)}")
        ])
        
        response = await self.llm.ainvoke(act_prompt.format_messages())
        
        try:
            act_content = response.content.strip()
            if act_content.startswith("```json"):
                act_content = act_content.replace("```json", "").replace("```", "").strip()
            
            act_results = json.loads(act_content)
        except json.JSONDecodeError:
            act_results = {
                "improvement_actions": ["优化执行流程"],
                "process_changes": ["调整时间安排"],
                "resource_adjustments": ["增加注意力投入"],
                "should_continue_cycle": False,
                "reason_to_continue": "任务基本完成",
                "expected_improvements": ["效率提升"]
            }
        
        state["current_phase"] = "act"
        state["improvement_actions"] = act_results.get("improvement_actions", [])
        state["cycle_count"] += 1
        
        # 判断是否需要继续循环
        if (act_results.get("should_continue_cycle", False) and 
            state["cycle_count"] < 3 and  # 最多3个循环
            state["check_results"].get("quality_score", 0) < 90):
            state["is_complete"] = False
        else:
            state["is_complete"] = True
        
        state["messages"].append(AIMessage(content=f"改进行动：\n{json.dumps(act_results, ensure_ascii=False, indent=2)}"))
        
        return state
    
    async def _complete_phase(self, state: PDCAState) -> PDCAState:
        """完成阶段"""
        print(f"✅ COMPLETE阶段 - 任务完成")
        
        summary = {
            "task": state["task_description"],
            "total_cycles": state["cycle_count"],
            "final_quality_score": state["check_results"].get("quality_score", 0),
            "lessons_learned": state["check_results"].get("lessons_learned", []),
            "improvements_made": state["improvement_actions"]
        }
        
        state["current_phase"] = "complete"
        state["messages"].append(AIMessage(content=f"🎉 任务完成总结：\n{json.dumps(summary, ensure_ascii=False, indent=2)}"))
        
        return state
    
    def _should_continue_from_plan(self, state: PDCAState) -> str:
        """从计划阶段的条件判断"""
        return "do" if state.get("plan") else "complete"
    
    def _should_continue_from_do(self, state: PDCAState) -> str:
        """从执行阶段的条件判断"""
        return "check" if state.get("execution_log") else "complete"
    
    def _should_continue_from_check(self, state: PDCAState) -> str:
        """从检查阶段的条件判断"""
        return "act" if state.get("check_results") else "complete"
    
    def _should_continue_from_act(self, state: PDCAState) -> str:
        """从行动阶段的条件判断"""
        if state.get("is_complete", True):
            return "complete"
        else:
            return "plan"  # 开始新的PDCA循环
    
    async def process_task(self, task_description: str) -> Dict[str, Any]:
        """处理工作任务"""
        print(f"🎯 开始处理任务: {task_description}")
        print("=" * 50)
        
        # 初始化状态
        initial_state = PDCAState(
            task_description=task_description,
            current_phase="",
            plan={},
            execution_log=[],
            check_results={},
            improvement_actions=[],
            cycle_count=0,
            is_complete=False,
            messages=[HumanMessage(content=task_description)]
        )
        
        # 创建线程配置
        config = {"configurable": {"thread_id": f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}}
        
        # 运行图
        result = await self.graph.ainvoke(initial_state, config)
        
        print("=" * 50)
        print("🏁 任务处理完成!")
        
        return result

async def main():
    """主函数演示"""
    print("🤖 LangGraph PDCA循环Agent Demo")
    print("基于GPT-4o的工作任务处理系统")
    print("=" * 60)
    
    # 创建agent
    agent = PDCAAgent()
    
    # 示例任务
    tasks = [
        "开发一个用户登录功能的Web应用",
        "准备下周的项目汇报演示",
        "优化数据库查询性能"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n🚀 示例任务 {i}: {task}")
        print("-" * 40)
        
        try:
            result = await agent.process_task(task)
            
            # 打印最终结果摘要
            print(f"\n📊 任务完成摘要:")
            print(f"   • 任务: {result['task_description']}")
            print(f"   • PDCA循环次数: {result['cycle_count']}")
            print(f"   • 最终阶段: {result['current_phase']}")
            print(f"   • 质量评分: {result['check_results'].get('quality_score', 'N/A')}")
            print(f"   • 改进行动数量: {len(result.get('improvement_actions', []))}")
            
        except Exception as e:
            print(f"❌ 处理任务时出错: {e}")
        
        print("\n" + "="*60)
        
        # 暂停一下，避免API调用过快
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main()) 