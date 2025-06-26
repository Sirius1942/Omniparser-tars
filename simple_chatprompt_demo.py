#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ChatPromptTemplate 简化演示
展示LangChain中ChatPromptTemplate的主要功能
"""

import json
import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def demo_basic_usage():
    """基本用法演示"""
    print("=" * 60)
    print("📝 1. 基本模板用法")
    print("=" * 60)
    
    # 1.1 简单模板
    print("🔹 from_template() - 单一消息模板")
    simple_prompt = ChatPromptTemplate.from_template(
        "你是{role}，请为{task}制定计划"
    )
    
    formatted = simple_prompt.format(role="项目经理", task="团队建设")
    print(f"   输入: role=项目经理, task=团队建设")
    print(f"   输出: {formatted}")
    
    # 1.2 多消息模板
    print("\n🔹 from_messages() - 多消息模板")
    multi_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是{role}专家"),
        ("human", "请分析{topic}"),
        ("ai", "我将从{role}角度分析{topic}...")
    ])
    
    formatted = multi_prompt.format(role="数据", topic="用户行为")
    print(f"   输入: role=数据, topic=用户行为")
    if hasattr(formatted, 'messages'):
        print(f"   输出消息数量: {len(formatted.messages)}")
        for i, msg in enumerate(formatted.messages):
            print(f"   消息{i+1}: {msg.content}")
    else:
        print(f"   输出类型: {type(formatted)}")
        print(f"   输出内容: {formatted}")

def demo_message_types():
    """消息类型演示"""
    print("\n" + "=" * 60)
    print("💬 2. 消息类型")
    print("=" * 60)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "系统消息：定义AI角色和行为规则"),
        ("human", "人类消息：用户的输入或问题"),
        ("ai", "AI消息：模型的回复（用于few-shot示例）"),
        ("user", "用户消息：等同于human消息"),
        ("assistant", "助手消息：等同于ai消息")
    ])
    
    print("🔹 支持的消息类型：")
    print("   • system: 系统消息，定义AI角色")
    print("   • human/user: 人类用户消息") 
    print("   • ai/assistant: AI助手回复")
    print("   • 可以混合使用构建复杂对话")
    
    formatted = prompt.format()
    print(f"\n🔹 示例模板包含 {len(formatted.messages)} 条消息")

def demo_structured_output():
    """结构化输出演示"""
    print("\n" + "=" * 60)
    print("📊 3. 结构化输出模板")
    print("=" * 60)
    
    json_prompt = ChatPromptTemplate.from_messages([
        ("system", """请返回JSON格式的分析结果：
{
    "summary": "简要总结",
    "priority": "高/中/低",
    "steps": ["步骤1", "步骤2"],
    "risks": ["风险1", "风险2"]
}"""),
        ("human", "分析任务：{task}")
    ])
    
    print("🔹 JSON格式输出模板特点：")
    print("   • 在system消息中定义输出格式")
    print("   • 使用具体的JSON结构示例")
    print("   • 便于后续解析和处理")
    
    formatted = json_prompt.format(task="开发新功能")
    print(f"\n🔹 格式化后的系统消息（前100字符）：")
    print(f"   {formatted.messages[0].content[:100]}...")

def demo_template_composition():
    """模板组合演示"""
    print("\n" + "=" * 60)
    print("🔗 4. 模板组合")
    print("=" * 60)
    
    # 基础模板
    base_template = ChatPromptTemplate.from_messages([
        ("system", "你是{role}专家")
    ])
    
    # 任务模板
    task_template = ChatPromptTemplate.from_messages([
        ("human", "任务：{task}"),
        ("ai", "我理解任务，开始分析..."),
        ("human", "请提供{output}")
    ])
    
    # 组合模板
    combined = base_template + task_template
    
    print("🔹 模板组合过程：")
    print("   基础模板 (1条消息) + 任务模板 (3条消息) = 完整模板 (4条消息)")
    
    formatted = combined.format(
        role="业务分析师",
        task="分析市场趋势",
        output="详细报告"
    )
    
    print(f"\n🔹 组合后的完整对话流程：")
    for i, msg in enumerate(formatted.messages):
        print(f"   {i+1}. {msg.content}")

def demo_partial_binding():
    """部分绑定演示"""
    print("\n" + "=" * 60)
    print("🔧 5. 部分变量绑定")
    print("=" * 60)
    
    # 通用模板
    general_template = ChatPromptTemplate.from_template(
        "作为{role}，在{domain}领域，分析{topic}的{aspect}"
    )
    
    print("🔹 原始模板变量: role, domain, topic, aspect")
    
    # 部分绑定
    data_analyst_template = general_template.partial(
        role="数据分析师",
        domain="电商"
    )
    
    print("🔹 部分绑定后剩余变量: topic, aspect")
    
    # 最终使用
    final_result = data_analyst_template.format(
        topic="用户行为",
        aspect="购买转化率"
    )
    
    print(f"\n🔹 最终结果：")
    print(f"   {final_result}")

def demo_best_practices():
    """最佳实践演示"""
    print("\n" + "=" * 60)
    print("✨ 6. 最佳实践")
    print("=" * 60)
    
    print("🔹 模板设计原则：")
    print("   ✅ 清晰的变量命名")
    print("   ✅ 合理的消息类型选择") 
    print("   ✅ 适当的上下文信息")
    print("   ✅ 考虑错误处理")
    
    # 好的模板示例
    good_template = ChatPromptTemplate.from_messages([
        ("system", """你是{expert_type}专家，有{years}年经验。
请遵循以下原则：
- 提供准确信息
- 考虑实际约束
- 给出可行建议"""),
        ("human", "背景：{context}\n问题：{question}")
    ])
    
    print("\n🔹 良好模板特点：")
    print("   • 明确的角色定义")
    print("   • 清晰的行为准则") 
    print("   • 结构化的输入格式")
    
    # 模板验证函数
    def validate_template(template, test_vars):
        try:
            result = template.format(**test_vars)
            # 检查未替换变量
            content = str(result)
            if '{' in content and '}' in content:
                print("   ⚠️ 警告：可能有未替换的变量")
            else:
                print("   ✅ 模板验证通过")
            return True
        except KeyError as e:
            print(f"   ❌ 缺少变量: {e}")
            return False
    
    print("\n🔹 模板验证：")
    test_data = {
        "expert_type": "技术架构",
        "years": "10",
        "context": "微服务系统",
        "question": "如何优化性能"
    }
    validate_template(good_template, test_data)

async def demo_real_api():
    """实际API调用演示"""
    print("\n" + "=" * 60)
    print("🚀 7. 实际API调用")
    print("=" * 60)
    
    try:
        # 加载配置
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        openai_config = config.get("openai", {})
        
        # 初始化LLM
        llm = ChatOpenAI(
            api_key=openai_config["api_key"],
            base_url=openai_config["base_url"],
            model=openai_config["model"],
            temperature=0.3,
            max_tokens=200
        )
        
        # 创建分析模板
        analysis_template = ChatPromptTemplate.from_messages([
            ("system", "你是商业分析专家，简洁分析商业问题，50字以内。"),
            ("human", "问题：{problem}")
        ])
        
        problem = "线上商店转化率低"
        
        print(f"🔹 输入问题: {problem}")
        
        # 格式化并调用
        formatted = analysis_template.format(problem=problem)
        print(f"🔹 发送消息数: {len(formatted.messages)}")
        
        response = await llm.ainvoke(formatted)
        print(f"🔹 AI回复: {response.content}")
        
    except Exception as e:
        print(f"❌ API调用演示失败: {e}")
        print("   这是正常的，实际使用时需要正确的API配置")

def main():
    """主函数"""
    print("🎯 ChatPromptTemplate 功能演示")
    print("LangChain中最重要的提示模板工具")
    
    # 运行各个演示
    demo_basic_usage()
    demo_message_types()
    demo_structured_output()
    demo_template_composition()
    demo_partial_binding()
    demo_best_practices()
    
    # 异步演示
    asyncio.run(demo_real_api())
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("=" * 60)
    print("""
📋 ChatPromptTemplate 核心功能总结：

1️⃣ 基本模板类型
   • from_template(): 简单单消息模板
   • from_messages(): 复杂多消息模板

2️⃣ 消息类型支持
   • system: 系统角色定义
   • human/user: 用户输入
   • ai/assistant: AI回复

3️⃣ 高级功能
   • 结构化输出：JSON等格式化回复
   • 模板组合：拼接多个模板
   • 部分绑定：预设部分变量

4️⃣ 最佳实践
   • 清晰的变量命名
   • 合理的上下文设计
   • 完善的错误处理
   • 充分的模板验证

5️⃣ 实际应用
   • 与AI模型无缝集成
   • 支持异步调用
   • 灵活的提示工程

ChatPromptTemplate是LangChain中构建AI应用的核心组件！
    """)

if __name__ == "__main__":
    main() 