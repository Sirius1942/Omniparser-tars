# LangChain ChatPromptTemplate 详细说明

## 概述

`ChatPromptTemplate` 是 LangChain 中用于构建聊天提示的核心类，支持多种消息类型、模板变量和复杂的提示模式。它特别适用于与聊天模型（如GPT、Claude等）进行交互。

## 基本导入

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
```

## 1. 基本模板类型

### 1.1 from_template() - 简单模板

```python
# 最简单的单一消息模板
prompt = ChatPromptTemplate.from_template(
    "作为{role}，请为以下任务制定计划：\n任务：{task}\n\n计划："
)

# 使用模板
formatted = prompt.format(role="项目管理专家", task="设计用户反馈页面")
```

### 1.2 from_messages() - 多消息模板

```python
# 多条消息的对话模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{expert_type}助手。"),
    ("human", "请帮我分析以下问题：{problem}"),
    ("ai", "我理解你的问题，让我来分析..."),
    ("human", "具体的解决方案是什么？")
])
```

## 2. 消息类型

### 2.1 系统消息 (System Message)

```python
# 方式1：使用元组
("system", "你是一个有用的AI助手，专门处理{domain}相关的问题。")

# 方式2：使用SystemMessage对象
SystemMessage(content="你是一个有用的AI助手。")

# 方式3：使用简化形式
("system", """你是一个专业的项目管理AI助手。
请遵循以下原则：
1. 提供具体可行的建议
2. 考虑实际约束条件
3. 给出时间估计""")
```

### 2.2 人类消息 (Human Message)

```python
# 基本人类消息
("human", "请帮我{action}关于{topic}的内容")

# 复杂的人类消息
("user", """任务描述：{task_description}
要求：
- {requirement_1}
- {requirement_2}
- {requirement_3}

请提供详细的执行方案。""")
```

### 2.3 AI消息 (AI Message)

```python
# AI回复消息（通常用于few-shot示例）
("ai", "我理解你的需求，以下是我的分析：{analysis}")

# 或者使用assistant
("assistant", "根据你提供的信息，我建议：{suggestion}")
```

## 3. 高级模板模式

### 3.1 结构化输出模板

```python
structured_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个任务分析专家。请按照JSON格式返回分析结果：

请按照以下JSON格式回复：
{
    "goals": ["目标1", "目标2"],
    "steps": [
        {"step": 1, "action": "具体行动", "timeline": "时间估计"}
    ],
    "resources_needed": ["资源1", "资源2"],
    "risks": ["风险1", "风险2"]
}"""),
    ("user", "任务：{task_description}\n补充信息：{additional_info}")
])
```

### 3.2 多轮对话模板

```python
conversation_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，需要与用户进行多轮对话来理解需求。"),
    ("human", "我想要{initial_request}"),
    ("ai", "我理解你想要{initial_request}。为了更好地帮助你，我需要了解：{clarifying_questions}"),
    ("human", "{user_responses}"),
    ("ai", "基于你的回答，我的建议是：{final_recommendation}")
])
```

### 3.3 条件模板

```python
# 根据条件选择不同的系统消息
def create_conditional_prompt(user_type: str):
    if user_type == "beginner":
        system_msg = "你是一个耐心的导师，用简单易懂的语言解释概念。"
    elif user_type == "expert":
        system_msg = "你是一个技术专家，可以使用专业术语进行深入讨论。"
    else:
        system_msg = "你是一个通用助手。"
    
    return ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "{question}")
    ])
```

## 4. 变量和占位符

### 4.1 基本变量替换

```python
prompt = ChatPromptTemplate.from_template(
    "你好，{name}！今天是{date}，天气{weather}。"
)

# 使用字典传递变量
formatted = prompt.format(
    name="张三",
    date="2024年1月15日", 
    weather="晴朗"
)
```

### 4.2 复杂变量结构

```python
complex_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{agent_config.role}，专门处理{agent_config.domain}领域的问题。"),
    ("human", """项目信息：
名称：{project.name}
描述：{project.description}
预算：{project.budget}
时间：{project.timeline}

请制定详细计划。""")
])

# 使用嵌套字典
data = {
    "agent_config": {
        "role": "项目经理",
        "domain": "软件开发"
    },
    "project": {
        "name": "用户反馈系统",
        "description": "收集和分析用户反馈",
        "budget": "10万元",
        "timeline": "3个月"
    }
}
```

### 4.3 列表和循环

```python
list_prompt = ChatPromptTemplate.from_template("""
任务列表：
{tasks}

优先级排序：{priorities}

请分析每个任务的重要性。
""")

# 格式化列表数据
formatted = list_prompt.format(
    tasks="\n".join([f"- {task}" for task in ["任务1", "任务2", "任务3"]]),
    priorities=", ".join(["高", "中", "低"])
)
```

## 5. 特殊模板功能

### 5.1 部分变量绑定

```python
# 创建带有预设变量的模板
base_prompt = ChatPromptTemplate.from_template(
    "作为{role}，在{context}环境下，请处理：{task}"
)

# 部分绑定角色和环境
specialized_prompt = base_prompt.partial(
    role="数据分析师",
    context="电商平台"
)

# 后续只需要提供task
final_prompt = specialized_prompt.format(task="分析用户购买行为")
```

### 5.2 模板组合

```python
# 基础系统提示
system_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个{specialty}专家。")
])

# 任务模板
task_template = ChatPromptTemplate.from_messages([
    ("human", "请帮我{action}：{details}")
])

# 组合模板
combined_prompt = system_template + task_template
```

### 5.3 动态模板构建

```python
def build_dynamic_prompt(stages: list, include_examples: bool = False):
    messages = [
        ("system", "你是一个工作流程助手，需要按阶段执行任务。")
    ]
    
    # 动态添加阶段说明
    stage_descriptions = []
    for i, stage in enumerate(stages, 1):
        stage_descriptions.append(f"{i}. {stage['name']}: {stage['description']}")
    
    messages.append(("human", f"""工作流程：
{chr(10).join(stage_descriptions)}

当前阶段：{{current_stage}}
任务：{{task}}
"""))
    
    # 可选的示例
    if include_examples:
        messages.append(("ai", "我理解工作流程，让我开始执行..."))
    
    return ChatPromptTemplate.from_messages(messages)
```

## 6. 实际应用示例

### 6.1 PDCA循环模板（基于项目中的实际使用）

```python
# Plan阶段模板
plan_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的项目管理AI助手。请为给定的工作任务制定详细的执行计划。

请按照以下JSON格式回复：
{
    "goals": ["目标1", "目标2"],
    "steps": [
        {"step": 1, "action": "具体行动", "expected_outcome": "预期结果", "timeline": "时间估计"}
    ],
    "resources_needed": ["资源1", "资源2"],
    "success_criteria": ["成功标准1", "成功标准2"],
    "potential_risks": ["风险1", "风险2"]
}"""),
    ("user", "任务描述：{task_description}\n\n之前的改进行动：{improvement_actions}")
])

# Do阶段模板
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
    ("user", "请执行以下计划：\n{plan}")
])
```

### 6.2 代码分析模板

```python
code_analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个代码审查专家。请分析提供的代码并给出专业建议。

分析维度：
1. 代码质量和可读性
2. 性能优化建议  
3. 安全性问题
4. 最佳实践遵循情况
5. 改进建议"""),
    ("human", """编程语言：{language}
代码类型：{code_type}
代码内容：
```{language}
{code_content}
```

请提供详细的分析报告。""")
])
```

### 6.3 多语言支持模板

```python
multilingual_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个多语言助手，能够用{target_language}流利交流。"),
    ("human", "请用{target_language}回答：{question}"),
    ("ai", "我会用{target_language}为您详细解答..."),
    ("human", "如果需要，请提供{source_language}的对照说明。")
])
```

## 7. 最佳实践

### 7.1 模板设计原则

```python
# ✅ 好的模板设计
good_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个{role}。
遵循以下原则：
- 提供准确信息
- 保持专业态度
- 考虑用户需求"""),
    ("human", "{user_input}")
])

# ❌ 避免的模板设计
bad_prompt = ChatPromptTemplate.from_template(
    "帮我{action}{thing}然后{another_action}"  # 过于模糊
)
```

### 7.2 错误处理

```python
def safe_format_prompt(prompt_template, **kwargs):
    """安全的提示格式化，包含错误处理"""
    try:
        return prompt_template.format(**kwargs)
    except KeyError as e:
        print(f"缺少必需的变量: {e}")
        return None
    except Exception as e:
        print(f"格式化提示时出错: {e}")
        return None
```

### 7.3 模板验证

```python
def validate_prompt_template(template: ChatPromptTemplate, test_data: dict):
    """验证提示模板是否正确"""
    try:
        # 尝试格式化模板
        formatted = template.format(**test_data)
        
        # 检查是否还有未替换的变量
        if '{' in str(formatted) and '}' in str(formatted):
            print("⚠️ 警告：模板中可能有未替换的变量")
        
        print("✅ 模板验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 模板验证失败: {e}")
        return False
```

## 8. 高级用法

### 8.1 自定义消息类型

```python
from langchain_core.messages import BaseMessage

class CustomMessage(BaseMessage):
    """自定义消息类型"""
    type: str = "custom"

# 使用自定义消息
custom_prompt = ChatPromptTemplate.from_messages([
    ("system", "系统消息"),
    CustomMessage(content="自定义消息内容：{custom_data}")
])
```

### 8.2 模板继承和扩展

```python
class BasePromptTemplate:
    """基础提示模板类"""
    
    def __init__(self, role: str, domain: str):
        self.base_template = ChatPromptTemplate.from_messages([
            ("system", f"你是一个{role}，专门处理{domain}相关问题。")
        ])
    
    def extend(self, additional_messages: list):
        """扩展模板"""
        return self.base_template + ChatPromptTemplate.from_messages(additional_messages)

# 使用示例
base = BasePromptTemplate("分析师", "数据科学")
extended = base.extend([
    ("human", "请分析：{data}"),
    ("ai", "我将从以下角度分析...")
])
```

### 8.3 模板缓存和优化

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_prompt(template_key: str, role: str, domain: str):
    """缓存常用的提示模板"""
    templates = {
        "analysis": ChatPromptTemplate.from_messages([
            ("system", f"你是{role}，专注于{domain}分析。"),
            ("human", "请分析：{content}")
        ]),
        "planning": ChatPromptTemplate.from_messages([
            ("system", f"你是{role}，制定{domain}计划。"),
            ("human", "任务：{task}")
        ])
    }
    return templates.get(template_key)
```

## 9. 调试和测试

### 9.1 模板调试

```python
def debug_prompt_template(template: ChatPromptTemplate, variables: dict):
    """调试提示模板"""
    print("🔍 模板调试信息：")
    print(f"模板类型: {type(template)}")
    print(f"消息数量: {len(template.messages)}")
    
    for i, message in enumerate(template.messages):
        print(f"消息 {i+1}: {message}")
    
    print(f"变量: {variables}")
    
    try:
        formatted = template.format(**variables)
        print("✅ 格式化成功")
        print(f"结果: {formatted}")
    except Exception as e:
        print(f"❌ 格式化失败: {e}")
```

### 9.2 单元测试

```python
import unittest

class TestChatPromptTemplate(unittest.TestCase):
    def test_basic_template(self):
        """测试基本模板功能"""
        prompt = ChatPromptTemplate.from_template("Hello, {name}!")
        result = prompt.format(name="World")
        self.assertIn("Hello, World!", str(result))
    
    def test_multi_message_template(self):
        """测试多消息模板"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are {role}"),
            ("human", "{question}")
        ])
        result = prompt.format(role="assistant", question="Help me")
        self.assertEqual(len(result.messages), 2)
```

## 10. 总结

ChatPromptTemplate 提供了强大而灵活的提示构建能力：

- **多样化消息类型**：支持 system、human、ai 等不同角色
- **灵活变量系统**：支持简单变量、嵌套对象、列表处理
- **模板组合**：可以组合多个模板，支持继承和扩展
- **结构化输出**：特别适合需要JSON等结构化响应的场景
- **调试友好**：提供良好的错误信息和调试能力

在实际项目中，合理使用 ChatPromptTemplate 可以大大提高 AI 应用的可维护性和效果。 