#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM Google搜索页面操作测试脚本
基于OmniParser解析的页面元素测试LLM的按钮选择能力
"""

import os
import json
import csv
from typing import Dict, List, Any

class GoogleSearchTestSuite:
    """Google搜索页面LLM操作测试套件"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化测试套件"""
        self.config_path = config_path
        self.results = []
        
    def load_page_elements(self, csv_path: str) -> List[Dict[str, Any]]:
        """加载页面元素数据"""
        try:
            elements = []
            with open(csv_path, 'r', encoding='utf-8-sig') as f:  # 使用utf-8-sig处理BOM
                reader = csv.DictReader(f)
                for row in reader:
                    elements.append(row)
            print(f"✅ 成功加载 {len(elements)} 个页面元素")
            return elements
        except Exception as e:
            print(f"❌ 加载CSV文件失败: {e}")
            return []
    
    def create_screen_context(self, elements: List[Dict[str, Any]]) -> str:
        """创建屏幕上下文信息"""
        context = "当前屏幕元素信息:\n"
        
        # 分类显示元素
        text_elements = [e for e in elements if e['type'] == 'text']
        icon_elements = [e for e in elements if e['type'] == 'icon']
        
        context += f"\n📝 文本元素 ({len(text_elements)} 个):\n"
        for elem in text_elements:
            bbox_str = elem['bbox'].strip('[]').replace(' ', '')
            context += f"ID {elem['ID']}: '{elem['content']}' (位置: {bbox_str})\n"
        
        context += f"\n🎯 图标元素 ({len(icon_elements)} 个):\n"
        for elem in icon_elements:
            bbox_str = elem['bbox'].strip('[]').replace(' ', '')
            interactable = "✓" if elem['interactivity'] == 'True' else "✗"
            context += f"ID {elem['ID']}: {elem['content']} [{interactable}可交互] (位置: {bbox_str})\n"
        
        return context
    
    def generate_test_tasks(self) -> List[Dict[str, Any]]:
        """生成测试任务"""
        return [
            {
                "id": 1,
                "task": "在Google搜索框中搜索'Python编程'",
                "description": "用户想要搜索Python编程相关内容",
                "expected_elements": ["Google Search", "搜索功能"],
                "keywords": ["search", "搜索", "google search"]
            },
            {
                "id": 2,
                "task": "点击'I'm Feeling Lucky'按钮",
                "description": "用户想要使用Google的'手气不错'功能",
                "expected_elements": ["I'm Feeling Luckye"],
                "keywords": ["feeling lucky", "手气不错"]
            },
            {
                "id": 3,
                "task": "登录Google账户",
                "description": "用户想要登录到Google账户",
                "expected_elements": ["Sign in"],
                "keywords": ["sign in", "登录", "login"]
            },
            {
                "id": 4,
                "task": "打开Gmail邮箱",
                "description": "用户想要访问Gmail邮箱",
                "expected_elements": ["Gmail", "打开Gmail邮箱"],
                "keywords": ["gmail", "邮箱", "email"]
            },
            {
                "id": 5,
                "task": "使用语音搜索功能",
                "description": "用户想要通过语音进行搜索",
                "expected_elements": ["语音搜索"],
                "keywords": ["语音", "voice", "麦克风"]
            }
        ]
    
    def create_test_prompt(self, task: Dict[str, Any], screen_context: str) -> str:
        """创建测试提示词"""
        prompt = f"""你是一个网页自动化助手，需要在Google搜索页面执行用户指定的任务。

任务: {task['task']}
描述: {task['description']}

{screen_context}

请分析当前页面，并回答以下问题：

1. 为了完成任务"{task['task']}"，你需要与哪个页面元素交互？
2. 请提供该元素的ID号
3. 简要说明你的选择理由

请按以下JSON格式回复：
```json
{{
    "selected_element_id": 元素ID号(数字),
    "element_content": "选中元素的描述",
    "reasoning": "选择理由",
    "confidence": 评分(1-10),
    "alternative_elements": [其他可能的元素ID]
}}
```
"""
        return prompt
    
    def evaluate_response(self, task: Dict[str, Any], selected_id: int, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估响应的正确性"""
        evaluation = {
            "task_id": task["id"],
            "task_name": task["task"],
            "success": False,
            "score": 0,
            "details": {}
        }
        
        # 查找选中的元素
        selected_element = None
        for elem in elements:
            if int(elem['ID']) == selected_id:
                selected_element = elem
                break
        
        if not selected_element:
            evaluation["details"]["error"] = f"元素ID {selected_id} 不存在"
            return evaluation
        
        element_content = selected_element['content']
        is_interactable = selected_element['interactivity'] == 'True'
        
        evaluation["details"]["selected_element"] = {
            "id": selected_id,
            "content": element_content,
            "interactable": is_interactable,
            "type": selected_element['type']
        }
        
        # 检查是否可交互
        if not is_interactable:
            evaluation["details"]["warning"] = "选中的元素不可交互"
            evaluation["score"] = 2
        else:
            evaluation["score"] = 5  # 基础分
        
        # 检查是否符合预期
        content_lower = element_content.lower()
        keywords = task["keywords"]
        
        # 检查关键词匹配
        keyword_match = any(keyword.lower() in content_lower for keyword in keywords)
        
        if keyword_match:
            evaluation["success"] = True
            evaluation["score"] = min(10, evaluation["score"] + 5)
            evaluation["details"]["match_reason"] = "关键词匹配"
        else:
            # 检查预期元素
            expected_elements = task["expected_elements"]
            element_match = any(expected.lower() in content_lower for expected in expected_elements)
            
            if element_match:
                evaluation["success"] = True
                evaluation["score"] = min(10, evaluation["score"] + 5)
                evaluation["details"]["match_reason"] = "预期元素匹配"
        
        return evaluation
    
    def run_manual_test(self, elements: List[Dict[str, Any]]):
        """运行手动测试（模拟LLM选择）"""
        print("\n🚀 开始LLM Google搜索操作测试")
        print("=" * 60)
        
        # 创建屏幕上下文
        screen_context = self.create_screen_context(elements)
        
        # 生成测试任务
        tasks = self.generate_test_tasks()
        
        # 执行测试
        for task in tasks:
            print(f"\n🎯 测试任务 {task['id']}: {task['task']}")
            print("-" * 40)
            
            # 显示测试提示词
            prompt = self.create_test_prompt(task, screen_context)
            print("📝 生成的测试提示词:")
            print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
            
            # 模拟LLM选择（基于关键词匹配）
            print("\n🤖 模拟LLM选择...")
            best_match_id = self.simulate_llm_choice(task, elements)
            
            if best_match_id is not None:
                # 评估选择
                evaluation = self.evaluate_response(task, best_match_id, elements)
                self.results.append(evaluation)
                
                # 显示结果
                if evaluation["success"]:
                    print(f"✅ 测试通过! 得分: {evaluation['score']}/10")
                else:
                    print(f"❌ 测试失败! 得分: {evaluation['score']}/10")
                
                elem = evaluation["details"]["selected_element"]
                print(f"   📍 选中元素: ID {elem['id']} - {elem['content']}")
                print(f"   🔧 可交互: {'是' if elem['interactable'] else '否'}")
                
                if "match_reason" in evaluation["details"]:
                    print(f"   ✨ 匹配原因: {evaluation['details']['match_reason']}")
            else:
                print("❌ 未找到合适的元素")
        
        # 生成测试报告
        self.generate_report()
    
    def simulate_llm_choice(self, task: Dict[str, Any], elements: List[Dict[str, Any]]) -> int | None:
        """模拟LLM的选择逻辑"""
        keywords = task["keywords"]
        best_score = 0
        best_id = None
        
        # 优先考虑可交互的元素
        interactive_elements = [e for e in elements if e['interactivity'] == 'True']
        
        for elem in interactive_elements:
            content_lower = elem['content'].lower()
            score = 0
            
            # 计算关键词匹配分数
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    score += 10
            
            # 检查预期元素
            expected_elements = task["expected_elements"]
            for expected in expected_elements:
                if expected.lower() in content_lower:
                    score += 15
            
            if score > best_score:
                best_score = score
                best_id = int(elem['ID'])
        
        return best_id
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        average_score = sum(r["score"] for r in self.results) / total_tests if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        print(f"平均得分: {average_score:.1f}/10")
        
        print(f"\n📋 详细结果:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} 任务{result['task_id']}: {result['task_name']} - {result['score']}/10")
        
        # 保存详细报告
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests/total_tests*100 if total_tests > 0 else 0,
                "average_score": average_score
            },
            "detailed_results": self.results
        }
        
        with open("llm_google_search_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存: llm_google_search_test_report.json")

def main():
    """主函数"""
    print("🔍 LLM Google搜索页面操作能力测试")
    print("=" * 50)
    
    # 检查CSV文件
    csv_file = "results_gpt4o_google_page.csv"
    if not os.path.exists(csv_file):
        print(f"❌ CSV文件 {csv_file} 不存在！")
        print("请先运行 demo_gpt4o.py 生成页面解析结果")
        return
    
    try:
        # 创建测试套件
        test_suite = GoogleSearchTestSuite()
        
        # 加载页面元素
        elements = test_suite.load_page_elements(csv_file)
        if not elements:
            return
        
        # 显示页面元素概览
        print("\n📊 页面元素统计:")
        text_count = len([e for e in elements if e['type'] == 'text'])
        icon_count = len([e for e in elements if e['type'] == 'icon'])
        interactive_count = len([e for e in elements if e['interactivity'] == 'True'])
        
        print(f"   📝 文本元素: {text_count} 个")
        print(f"   🎯 图标元素: {icon_count} 个")
        print(f"   🔧 可交互元素: {interactive_count} 个")
        
        # 运行模拟测试
        test_suite.run_manual_test(elements)
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 