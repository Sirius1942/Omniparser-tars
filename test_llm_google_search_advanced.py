#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高级LLM Google搜索页面操作测试脚本
可以与真实LLM API交互进行测试
"""

import os
import json
import csv
import re
from typing import Dict, List, Any, Optional

class AdvancedGoogleSearchTestSuite:
    """高级Google搜索页面LLM操作测试套件"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化测试套件"""
        self.config_path = config_path
        self.config = None
        self.results = []
        
        # 加载配置
        if os.path.exists(config_path):
            try:
                from util.config import get_config
                self.config = get_config(config_path)
                print("✅ 配置文件加载成功")
            except Exception as e:
                print(f"⚠️  配置文件加载失败: {e}")
    
    def load_page_elements(self, csv_path: str) -> List[Dict[str, Any]]:
        """加载页面元素数据"""
        try:
            elements = []
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    elements.append(row)
            print(f"✅ 成功加载 {len(elements)} 个页面元素")
            return elements
        except Exception as e:
            print(f"❌ 加载CSV文件失败: {e}")
            return []
    
    def generate_test_tasks(self) -> List[Dict[str, Any]]:
        """生成测试任务"""
        return [
            {
                "id": 1,
                "task": "搜索'Python编程教程'",
                "description": "用户想要在Google中搜索Python编程教程",
                "expected_elements": ["Google Search", "搜索功能"],
                "keywords": ["search", "搜索", "google search"],
                "action_type": "search"
            },
            {
                "id": 2,
                "task": "点击'I'm Feeling Lucky'按钮",
                "description": "用户想要使用Google的'手气不错'功能",
                "expected_elements": ["I'm Feeling Luckye"],
                "keywords": ["feeling lucky", "手气不错", "lucky"],
                "action_type": "click"
            },
            {
                "id": 3,
                "task": "登录Google账户",
                "description": "用户想要登录到自己的Google账户",
                "expected_elements": ["Sign in"],
                "keywords": ["sign in", "登录", "login"],
                "action_type": "login"
            }
        ]
    
    def simulate_llm_choice(self, task: Dict[str, Any], elements: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """模拟LLM的选择逻辑"""
        keywords = task["keywords"]
        best_score = 0
        best_element = None
        
        # 优先考虑可交互的元素
        interactive_elements = [e for e in elements if e['interactivity'] == 'True']
        
        for elem in interactive_elements:
            content_lower = elem['content'].lower()
            score = 0
            
            # 关键词匹配分数
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    score += 10
            
            # 预期元素匹配分数
            expected_elements = task["expected_elements"]
            for expected in expected_elements:
                if expected.lower() in content_lower:
                    score += 15
            
            if score > best_score:
                best_score = score
                best_element = elem
        
        if best_element:
            return {
                "selected_element_id": int(best_element['ID']),
                "element_content": best_element['content'],
                "reasoning": f"基于关键词匹配选择了最相关的元素",
                "confidence": min(10, best_score // 2),
                "alternative_elements": [],
                "action_plan": f"点击元素: {best_element['content']}"
            }
        
        return None
    
    def run_tests(self, elements: List[Dict[str, Any]]):
        """运行测试"""
        print("\n🚀 开始高级LLM Google搜索操作测试")
        print("=" * 60)
        
        tasks = self.generate_test_tasks()
        
        for task in tasks:
            print(f"\n🎯 测试任务 {task['id']}: {task['task']}")
            print("-" * 40)
            
            # 模拟LLM选择
            print("🤖 模拟LLM选择...")
            response = self.simulate_llm_choice(task, elements)
            
            if response:
                selected_id = response["selected_element_id"]
                selected_elem = next((e for e in elements if int(e['ID']) == selected_id), None)
                
                if selected_elem:
                    print(f"✅ 选中元素: ID {selected_id} - {selected_elem['content']}")
                    print(f"   🔧 可交互: {'是' if selected_elem['interactivity'] == 'True' else '否'}")
                    print(f"   💭 选择理由: {response['reasoning']}")
                else:
                    print("❌ 未找到选中的元素")
            else:
                print("❌ 未找到合适的元素")

def main():
    """主函数"""
    print("🔍 高级LLM Google搜索页面操作能力测试")
    print("=" * 50)
    
    csv_file = "results_gpt4o_google_page.csv"
    if not os.path.exists(csv_file):
        print(f"❌ CSV文件 {csv_file} 不存在！")
        return
    
    try:
        test_suite = AdvancedGoogleSearchTestSuite()
        elements = test_suite.load_page_elements(csv_file)
        
        if elements:
            test_suite.run_tests(elements)
            print("\n🎉 测试完成！")
    
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main() 