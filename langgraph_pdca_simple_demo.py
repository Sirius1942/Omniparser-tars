#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版LangGraph PDCA循环Agent Demo
快速测试版本
"""

import json
import asyncio
from typing import TypedDict, List, Dict, Any
from datetime import datetime

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate

# 简化状态类型
class SimpleState(TypedDict):
    task: str
    phase: str  # plan_phase, do_phase, check_phase, act_phase, complete_phase
    plan_content: str
    execution_content: str
    check_result: str
    improvement: str
    cycle: int
    complete: bool

class SimplePDCAAgent:
    """简化版PDCA Agent"""
    
    def __init__(self):
        # 加载配置
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        openai_config = config.get("openai", {})
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            api_key=openai_config["api_key"],
            base_url=openai_config["base_url"],
            model=openai_config["model"],
            temperature=0.3,
            max_tokens=500
        )
        
        # 构建图
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """构建状态图"""
        workflow = StateGraph(SimpleState)
        
        # 添加节点
        workflow.add_node("plan_phase", self._plan)
        workflow.add_node("do_phase", self._do)
        workflow.add_node("check_phase", self._check)
        workflow.add_node("act_phase", self._act)
        workflow.add_node("complete_phase", self._complete)
        
        # 设置边
        workflow.add_edge(START, "plan_phase")
        workflow.add_edge("plan_phase", "do_phase")
        workflow.add_edge("do_phase", "check_phase")
        workflow.add_edge("check_phase", "act_phase")
        
        # 条件边：是否继续循环
        workflow.add_conditional_edges(
            "act_phase",
            self._should_continue,
            {
                "continue": "plan_phase",
                "end": "complete_phase"
            }
        )
        
        workflow.add_edge("complete_phase", END)
        
        return workflow.compile()
    
    async def _plan(self, state: SimpleState) -> SimpleState:
        """Plan阶段"""
        print(f"📋 PLAN阶段 - 循环 {state['cycle'] + 1}")
        
        prompt = ChatPromptTemplate.from_template(
            "作为项目管理专家，为以下任务制定简洁的执行计划（1-2句话）：\n任务：{task}\n\n计划："
        )
        
        response = await self.llm.ainvoke(prompt.format(task=state["task"]))
        
        state["phase"] = "plan"
        state["plan_content"] = response.content.strip()
        print(f"   计划：{state['plan_content']}")
        
        return state
    
    async def _do(self, state: SimpleState) -> SimpleState:
        """Do阶段"""
        print(f"🚀 DO阶段 - 执行计划")
        
        prompt = ChatPromptTemplate.from_template(
            "作为执行专家，模拟执行以下计划并简述结果（1-2句话）：\n计划：{plan}\n\n执行结果："
        )
        
        response = await self.llm.ainvoke(prompt.format(plan=state["plan_content"]))
        
        state["phase"] = "do"
        state["execution_content"] = response.content.strip()
        print(f"   执行：{state['execution_content']}")
        
        return state
    
    async def _check(self, state: SimpleState) -> SimpleState:
        """Check阶段"""
        print(f"🔍 CHECK阶段 - 检查结果")
        
        prompt = ChatPromptTemplate.from_template(
            "作为质量专家，评估执行结果并给出质量评分（1-2句话）：\n计划：{plan}\n执行：{execution}\n\n检查结果："
        )
        
        response = await self.llm.ainvoke(prompt.format(
            plan=state["plan_content"], 
            execution=state["execution_content"]
        ))
        
        state["phase"] = "check"
        state["check_result"] = response.content.strip()
        print(f"   检查：{state['check_result']}")
        
        return state
    
    async def _act(self, state: SimpleState) -> SimpleState:
        """Act阶段"""
        print(f"⚡ ACT阶段 - 制定改进")
        
        prompt = ChatPromptTemplate.from_template(
            "作为改进专家，基于检查结果提出改进建议（1-2句话）：\n检查结果：{check_result}\n\n改进建议："
        )
        
        response = await self.llm.ainvoke(prompt.format(check_result=state["check_result"]))
        
        state["phase"] = "act"
        state["improvement"] = response.content.strip()
        state["cycle"] += 1
        print(f"   改进：{state['improvement']}")
        
        return state
    
    def _should_continue(self, state: SimpleState) -> str:
        """判断是否继续循环"""
        # 最多2个循环，或者如果检查结果包含"良好"、"完成"等关键词就停止
        if state["cycle"] >= 2:
            return "end"
        
        check_result = state["check_result"].lower()
        if any(word in check_result for word in ["优秀", "良好", "完成", "满意", "成功"]):
            return "end"
        
        return "continue"
    
    async def _complete(self, state: SimpleState) -> SimpleState:
        """Complete阶段"""
        print(f"✅ COMPLETE阶段 - 任务完成")
        
        state["phase"] = "complete"
        state["complete"] = True
        
        print(f"   📊 完成摘要：")
        print(f"      • 任务：{state['task']}")
        print(f"      • 循环次数：{state['cycle']}")
        print(f"      • 最终改进：{state['improvement']}")
        
        return state
    
    async def process_task(self, task: str) -> Dict[str, Any]:
        """处理任务"""
        print(f"🎯 开始PDCA处理: {task}")
        print("-" * 50)
        
        # 初始状态
        initial_state = SimpleState(
            task=task,
            phase="",
            plan_content="",
            execution_content="",
            check_result="",
            improvement="",
            cycle=0,
            complete=False
        )
        
        # 运行图
        result = await self.graph.ainvoke(initial_state)
        
        print("-" * 50)
        return result

async def quick_demo():
    """快速演示"""
    print("🤖 LangGraph PDCA循环 - 快速演示")
    print("=" * 50)
    
    agent = SimplePDCAAgent()
    
    # 测试任务
    test_task = "设计一个简单的用户反馈收集页面"
    
    try:
        result = await agent.process_task(test_task)
        print(f"\n🎉 演示完成！最终状态：{result['phase']}")
        
    except Exception as e:
        print(f"❌ 演示出错: {e}")

if __name__ == "__main__":
    asyncio.run(quick_demo()) 