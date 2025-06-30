#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ChatPromptTemplate 演示脚本
展示LangChain中ChatPromptTemplate的各种用法
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import json
import asyncio
from typing import Dict, List, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

class ChatPromptTemplateDemo:
    """ChatPromptTemplate演示类"""
    
    def __init__(self):
        # 加载配置
        with open(os.path.join(project_root, "config.json"), 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        openai_config = config.get("openai", {})
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            api_key=openai_config["api_key"],
            base_url=openai_config["base_url"],
            model=openai_config["model"],
            temperature=0.3,
            max_tokens=300
        )
    
    def demo_1_basic_template(self):
        """演示1：基本模板用法"""
        print("=" * 60)
        print("📝 演示1：基本模板 - from_template()")
        print("=" * 60)
        
        # 基本单一消息模板
        prompt = ChatPromptTemplate.from_template(
            "作为{role}，请为以下任务制定简洁计划：\n任务：{task}\n\n计划："
        )
        
        # 格式化模板
        formatted = prompt.format(
            role="项目经理",
            task="组织团队建设活动"
        )
        
        print("🔹 模板定义：")
        print(f"   作为{{role}}，请为以下任务制定简洁计划：\\n任务：{{task}}\\n\\n计划：")
        print("\n🔹 变量输入：")
        print(f"   role: 项目经理")
        print(f"   task: 组织团队建设活动")
        print("\n🔹 格式化结果：")
        if hasattr(formatted, 'messages'):
            print(f"   {formatted.messages[0].content}")
        else:
            print(f"   {formatted}")
    
    def demo_2_multi_message_template(self):
        """演示2：多消息模板"""
        print("\n" + "=" * 60)
        print("💬 演示2：多消息模板 - from_messages()")
        print("=" * 60)
        
        # 多消息对话模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的{expert_type}助手，具有{years}年经验。"),
            ("human", "请帮我分析以下问题：{problem}"),
            ("ai", "我理解你的问题，让我从{expert_type}的角度来分析..."),
            ("human", "请给出具体的解决方案")
        ])
        
        # 格式化模板
        formatted = prompt.format(
            expert_type="数据分析",
            years="5",
            problem="用户留存率下降"
        )
        
        print("🔹 模板结构：")
        for i, msg in enumerate(prompt.messages, 1):
            print(f"   消息{i}: {msg.type} - {msg.content[:50]}...")
        
        print("\n🔹 变量输入：")
        print(f"   expert_type: 数据分析")
        print(f"   years: 5")
        print(f"   problem: 用户留存率下降")
        
        print("\n🔹 格式化结果：")
        for i, msg in enumerate(formatted.messages, 1):
            print(f"   消息{i}({msg.type}): {msg.content}")
    
    def demo_3_structured_output_template(self):
        """演示3：结构化输出模板"""
        print("\n" + "=" * 60)
        print("📊 演示3：结构化输出模板")
        print("=" * 60)
        
        # 结构化JSON输出模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个任务分析专家。请按照JSON格式返回分析结果。

请严格按照以下JSON格式回复：
{
    "priority": "高/中/低",
    "estimated_time": "时间估计",
    "required_skills": ["技能1", "技能2"],
    "steps": [
        {"order": 1, "action": "具体行动", "duration": "时间"}
    ],
    "risks": ["风险1", "风险2"],
    "success_criteria": "成功标准"
}"""),
            ("user", "任务：{task_description}\n领域：{domain}")
        ])
        
        print("🔹 模板特点：")
        print("   - 系统消息定义了严格的JSON输出格式")
        print("   - 包含多种数据类型：字符串、数组、对象")
        print("   - 用户消息提供任务和领域信息")
        
        # 格式化示例
        formatted = prompt.format(
            task_description="开发移动端用户界面",
            domain="前端开发"
        )
        
        print("\n🔹 输入变量：")
        print(f"   task_description: 开发移动端用户界面")
        print(f"   domain: 前端开发")
        
        print("\n🔹 期望的AI响应格式：JSON结构化输出")
    
    def demo_4_conditional_template(self):
        """演示4：条件模板"""
        print("\n" + "=" * 60)
        print("🔀 演示4：条件模板")
        print("=" * 60)
        
        def create_user_level_prompt(user_level: str):
            """根据用户级别创建不同的提示模板"""
            if user_level == "beginner":
                system_msg = "你是一个耐心的导师，用简单易懂的语言解释技术概念，避免使用专业术语。"
                style = "详细解释每个步骤，提供实际例子"
            elif user_level == "intermediate":
                system_msg = "你是一个技术顾问，提供平衡的技术深度，适当使用专业术语。"
                style = "提供核心要点，给出最佳实践建议"
            elif user_level == "expert":
                system_msg = "你是一个技术专家，可以进行深入的技术讨论，使用专业术语。"
                style = "直接给出高级解决方案，讨论技术细节"
            else:
                system_msg = "你是一个通用技术助手。"
                style = "根据问题复杂度调整回答深度"
            
            return ChatPromptTemplate.from_messages([
                ("system", f"{system_msg}\n\n回答风格：{style}"),
                ("human", "问题：{question}\n背景：{context}")
            ])
        
        # 演示不同级别的模板
        levels = ["beginner", "intermediate", "expert"]
        
        for level in levels:
            print(f"\n🔹 {level.upper()} 级别模板：")
            prompt = create_user_level_prompt(level)
            
            formatted = prompt.format(
                question="如何优化数据库查询性能？",
                context="电商网站，用户量较大"
            )
            
            # 显示系统消息的差异
            system_content = formatted.messages[0].content
            print(f"   系统消息: {system_content[:80]}...")
    
    def demo_5_template_composition(self):
        """演示5：模板组合"""
        print("\n" + "=" * 60)
        print("🔗 演示5：模板组合")
        print("=" * 60)
        
        # 基础角色模板
        role_template = ChatPromptTemplate.from_messages([
            ("system", "你是一个{specialty}专家，擅长{domain}领域。")
        ])
        
        # 任务模板
        task_template = ChatPromptTemplate.from_messages([
            ("human", "当前任务：{task}"),
            ("ai", "我理解你的任务，让我来分析..."),
            ("human", "请提供详细的{output_type}。")
        ])
        
        # 组合模板
        combined_prompt = role_template + task_template
        
        print("🔹 模板组合过程：")
        print("   角色模板 + 任务模板 = 完整对话模板")
        
        print("\n🔹 角色模板内容：")
        for msg in role_template.messages:
            print(f"   {msg.type}: {msg.content}")
        
        print("\n🔹 任务模板内容：")
        for msg in task_template.messages:
            print(f"   {msg.type}: {msg.content}")
        
        print("\n🔹 组合后模板：")
        formatted = combined_prompt.format(
            specialty="UI/UX设计",
            domain="移动应用",
            task="设计登录界面",
            output_type="设计方案"
        )
        
        for i, msg in enumerate(formatted.messages, 1):
            print(f"   消息{i}({msg.type}): {msg.content}")
    
    def demo_6_partial_binding(self):
        """演示6：部分变量绑定"""
        print("\n" + "=" * 60)
        print("🔧 演示6：部分变量绑定 - partial()")
        print("=" * 60)
        
        # 创建通用分析模板
        analysis_template = ChatPromptTemplate.from_template(
            """作为{role}，请在{industry}行业背景下分析以下{analysis_type}：

内容：{content}
重点关注：{focus_areas}

请提供专业的{output_format}。"""
        )
        
        print("🔹 原始模板变量：")
        print("   role, industry, analysis_type, content, focus_areas, output_format")
        
        # 部分绑定：预设角色和行业
        ecommerce_analyst_template = analysis_template.partial(
            role="数据分析师",
            industry="电商",
            output_format="分析报告"
        )
        
        print("\n🔹 部分绑定后剩余变量：")
        print("   analysis_type, content, focus_areas")
        
        # 进一步专化：绑定分析类型
        user_behavior_template = ecommerce_analyst_template.partial(
            analysis_type="用户行为数据"
        )
        
        print("\n🔹 二次绑定后剩余变量：")
        print("   content, focus_areas")
        
        # 最终使用时只需要提供剩余变量
        final_prompt = user_behavior_template.format(
            content="用户在购物车页面的停留时间数据",
            focus_areas="转化率、跳出率、用户路径"
        )
        
        print("\n🔹 最终格式化结果：")
        print(f"   {final_prompt.messages[0].content}")
    
    async def demo_7_real_api_call(self):
        """演示7：实际API调用"""
        print("\n" + "=" * 60)
        print("🚀 演示7：与AI模型的实际交互")
        print("=" * 60)
        
        # 创建一个实用的分析模板
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个商业分析专家。请简洁分析给定的商业场景，
包括：关键问题、机会点、建议方案。控制在100字以内。"""),
            ("human", "场景：{scenario}")
        ])
        
        # 测试场景
        scenario = "一家咖啡店发现下午时段客流量明显下降，但成本固定，影响盈利"
        
        print("🔹 输入场景：")
        print(f"   {scenario}")
        
        try:
            # 格式化提示
            formatted_prompt = analysis_prompt.format(scenario=scenario)
            
            print("\n🔹 发送给AI的提示：")
            for msg in formatted_prompt.messages:
                print(f"   {msg.type}: {msg.content}")
            
            print("\n🔹 AI分析结果：")
            # 调用AI模型
            response = await self.llm.ainvoke(formatted_prompt)
            print(f"   {response.content}")
            
        except Exception as e:
            print(f"❌ API调用失败: {e}")
    
    def demo_8_template_validation(self):
        """演示8：模板验证和调试"""
        print("\n" + "=" * 60)
        print("🔍 演示8：模板验证和调试")
        print("=" * 60)
        
        def validate_template(template: ChatPromptTemplate, test_vars: dict):
            """验证模板是否能正确格式化"""
            try:
                # 尝试格式化
                formatted = template.format(**test_vars)
                
                # 检查是否还有未替换的变量
                all_content = " ".join([msg.content for msg in formatted.messages])
                if '{' in all_content and '}' in all_content:
                    print("   ⚠️ 警告：模板中可能有未替换的变量")
                    # 找出未替换的变量
                    import re
                    unresolved = re.findall(r'\{([^}]+)\}', all_content)
                    print(f"   未解析变量: {unresolved}")
                else:
                    print("   ✅ 模板验证通过")
                
                return True
                
            except KeyError as e:
                print(f"   ❌ 缺少必需变量: {e}")
                return False
            except Exception as e:
                print(f"   ❌ 格式化错误: {e}")
                return False
        
        # 测试正确的模板
        good_template = ChatPromptTemplate.from_template(
            "分析{topic}的{aspect}，重点关注{focus}"
        )
        
        print("🔹 测试正确模板：")
        test_data = {"topic": "市场趋势", "aspect": "发展方向", "focus": "技术创新"}
        validate_template(good_template, test_data)
        
        # 测试有问题的模板
        bad_template = ChatPromptTemplate.from_template(
            "分析{topic}的{aspect}，重点关注{focus}和{missing_var}"
        )
        
        print("\n🔹 测试缺少变量的模板：")
        validate_template(bad_template, test_data)
    
    async def run_all_demos(self):
        """运行所有演示"""
        print("🎯 ChatPromptTemplate 完整演示")
        print("展示LangChain中ChatPromptTemplate的各种功能和用法")
        
        # 运行各个演示
        self.demo_1_basic_template()
        self.demo_2_multi_message_template()
        self.demo_3_structured_output_template()
        self.demo_4_conditional_template()
        self.demo_5_template_composition()
        self.demo_6_partial_binding()
        await self.demo_7_real_api_call()
        self.demo_8_template_validation()
        
        print("\n" + "=" * 60)
        print("🎉 所有演示完成！")
        print("=" * 60)
        print("""
ChatPromptTemplate 主要功能总结：

1️⃣ 基本模板 - from_template()
   • 单一消息的简单模板
   • 支持变量替换

2️⃣ 多消息模板 - from_messages()
   • 支持system、human、ai等多种消息类型
   • 构建复杂对话流程

3️⃣ 结构化输出
   • 定义JSON等结构化响应格式
   • 适合需要格式化数据的场景

4️⃣ 条件模板
   • 根据条件动态选择模板内容
   • 支持个性化定制

5️⃣ 模板组合
   • 可以组合多个模板
   • 提高模板复用性

6️⃣ 部分绑定 - partial()
   • 预设部分变量值
   • 创建专门化的模板

7️⃣ 实际应用
   • 与AI模型无缝集成
   • 支持异步调用

8️⃣ 调试和验证
   • 提供模板验证功能
   • 帮助发现配置问题
        """)

async def main():
    """主函数"""
    demo = ChatPromptTemplateDemo()
    await demo.run_all_demos()

if __name__ == "__main__":
    asyncio.run(main()) 