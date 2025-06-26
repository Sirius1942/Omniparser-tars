# LangGraph PDCA循环Agent Demo

## 概述

这是一个基于[LangGraph](https://www.langchain.com/langgraph)框架构建的PDCA（Plan-Do-Check-Act）循环工作任务处理Agent，使用配置中的语言模型（当前为Qwen3-32B）实现智能任务管理。

## PDCA循环介绍

PDCA是一个持续改进的管理方法，包含四个阶段：

- **Plan（计划）**: 分析现状，制定改进计划
- **Do（执行）**: 按计划执行，收集数据
- **Check（检查）**: 检查执行结果，评估效果
- **Act（行动）**: 根据检查结果，制定改进措施

## 特性

### 🔄 智能循环处理
- 自动执行PDCA四个阶段
- 支持多轮循环优化
- 智能判断是否需要继续改进

### 🎯 状态管理
- 使用LangGraph的状态图管理整个流程
- 持久化任务状态和执行历史
- 支持条件分支和循环控制

### 🤖 AI驱动决策
- 每个阶段都由AI智能分析和决策
- 自动评估质量并给出改进建议
- 支持自然语言交互

### 📊 过程可视化
- 实时显示当前执行阶段
- 详细记录每个步骤的输出
- 提供完整的执行摘要

## 文件结构

```
├── langgraph_pdca_demo.py          # 完整版PDCA Agent
├── langgraph_pdca_simple_demo.py   # 简化版PDCA Agent
├── config.json                     # 模型配置文件
└── README_LangGraph_PDCA.md        # 本说明文档
```

## 安装依赖

```bash
pip install langgraph langchain-openai
```

## 配置说明

编辑`config.json`文件：

```json
{
    "openai": {
        "api_key": "your-api-key",
        "base_url": "your-base-url",
        "model": "your-model-name",
        "temperature": 0.3,
        "max_tokens": 2000
    }
}
```

## 快速开始

### 运行简化版Demo

```bash
python langgraph_pdca_simple_demo.py
```

### 运行完整版Demo

```bash
python langgraph_pdca_demo.py
```

## 代码结构

### 状态定义

```python
class SimpleState(TypedDict):
    task: str                    # 任务描述
    phase: str                   # 当前阶段
    plan_content: str            # 计划内容
    execution_content: str       # 执行内容
    check_result: str           # 检查结果
    improvement: str            # 改进建议
    cycle: int                  # 循环次数
    complete: bool              # 是否完成
```

### 状态图构建

```python
def _build_graph(self):
    workflow = StateGraph(SimpleState)
    
    # 添加PDCA四个阶段的节点
    workflow.add_node("plan_phase", self._plan)
    workflow.add_node("do_phase", self._do)
    workflow.add_node("check_phase", self._check)
    workflow.add_node("act_phase", self._act)
    workflow.add_node("complete_phase", self._complete)
    
    # 设置节点间的连接关系
    workflow.add_edge(START, "plan_phase")
    workflow.add_edge("plan_phase", "do_phase")
    workflow.add_edge("do_phase", "check_phase")
    workflow.add_edge("check_phase", "act_phase")
    
    # 条件边：决定是否继续循环
    workflow.add_conditional_edges(
        "act_phase",
        self._should_continue,
        {
            "continue": "plan_phase",  # 开始新的PDCA循环
            "end": "complete_phase"    # 结束流程
        }
    )
    
    return workflow.compile()
```

## 使用示例

### 基本用法

```python
from langgraph_pdca_simple_demo import SimplePDCAAgent

# 创建Agent实例
agent = SimplePDCAAgent()

# 处理任务
result = await agent.process_task("设计一个用户反馈收集页面")
```

### 输出示例

```
🎯 开始PDCA处理: 设计一个简单的用户反馈收集页面
--------------------------------------------------
📋 PLAN阶段 - 循环 1
   计划：确定核心需求并完成UI/UX原型设计，开发前端表单与后端数据存储接口

🚀 DO阶段 - 执行计划  
   执行：页面在3周内完成开发并上线，收集到1200+有效反馈，用户提交转化率85%

🔍 CHECK阶段 - 检查结果
   检查：质量评分4.5/5（高效完成核心功能且用户转化率达标，但未提及测试覆盖率详情）

⚡ ACT阶段 - 制定改进
   改进：补充测试覆盖率报告和数据加密方案说明，以增强质量可追溯性

✅ COMPLETE阶段 - 任务完成
   📊 完成摘要：
      • 任务：设计一个简单的用户反馈收集页面
      • 循环次数：1
      • 最终改进：补充测试覆盖率报告和数据加密方案说明
```

## 扩展功能

### 1. 添加人工干预

```python
# 在检查阶段添加人工确认
def _check_phase(self, state):
    # ... AI检查逻辑 ...
    
    # 可选：添加人工确认节点
    if state["check_results"]["quality_score"] < 80:
        # 触发人工干预
        pass
    
    return state
```

### 2. 集成外部工具

```python
from langchain.tools import Tool

# 定义外部工具
def search_best_practices(query: str) -> str:
    # 搜索最佳实践
    return "best practices data"

# 在计划阶段使用工具
tools = [
    Tool(
        name="search_best_practices",
        description="搜索行业最佳实践",
        func=search_best_practices
    )
]
```

### 3. 添加记忆功能

```python
from langgraph.checkpoint.memory import MemorySaver

# 添加持久化存储
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
```

## 最佳实践

### 1. 任务描述
- 使用清晰、具体的任务描述
- 包含关键需求和约束条件
- 避免过于模糊的表述

### 2. 循环控制
- 设置合理的最大循环次数
- 定义明确的完成条件
- 避免无限循环

### 3. 质量评估
- 建立量化的评估标准
- 设置合理的质量阈值
- 记录评估依据

## 故障排除

### 常见问题

1. **API连接失败**
   - 检查配置文件中的API密钥和基础URL
   - 确认网络连接正常

2. **JSON解析错误**
   - 模型输出格式可能不稳定
   - 已添加异常处理和默认值

3. **循环不收敛**
   - 检查完成条件逻辑
   - 调整质量评分阈值

## 技术架构

### LangGraph核心概念

1. **StateGraph**: 状态图，定义节点和边的关系
2. **节点（Node）**: 执行具体业务逻辑的单元
3. **边（Edge）**: 连接节点，控制执行流程
4. **条件边**: 根据状态动态选择下一个节点
5. **检查点**: 保存和恢复执行状态

### 设计模式

- **状态机模式**: 使用状态图管理复杂流程
- **策略模式**: 不同阶段使用不同的AI策略
- **观察者模式**: 监控执行过程和状态变化

## 参考资料

- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [LangGraph为什么选择](https://langchain-ai.github.io/langgraph/concepts/why-langgraph/)
- [PDCA循环管理方法](https://en.wikipedia.org/wiki/PDCA)

## 贡献

欢迎提交Issue和Pull Request来改进这个Demo！

## 许可证

MIT License 