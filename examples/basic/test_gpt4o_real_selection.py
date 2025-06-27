#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GPT-4o真实选择测试脚本
发送页面元素信息给GPT-4o，让它选择要点击的元素，并在图片上可视化标记结果
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import os
import json
import csv
import re
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont

class GPT4oRealSelectionTest:
    """GPT-4o真实选择测试类"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化"""
        self.config_path = config_path
        self.config = None
        
        # 加载配置
        if os.path.exists(config_path):
            try:
                from src.utils.config import get_config
                self.config = get_config(config_path)
                print("✅ 配置文件加载成功")
            except Exception as e:
                print(f"❌ 配置文件加载失败: {e}")
        else:
            print("❌ 配置文件不存在")
    
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
    
    def create_elements_description(self, elements: List[Dict[str, Any]]) -> str:
        """创建元素描述给GPT-4o"""
        description = "Google搜索页面元素信息:\n\n"
        
        # 只显示可交互的元素
        interactive_elements = [e for e in elements if e['interactivity'] == 'True']
        
        description += f"可交互元素列表 (共{len(interactive_elements)}个):\n"
        description += "=" * 50 + "\n"
        
        for elem in interactive_elements:
            bbox = elem['bbox'].strip('[]').split(',')
            x1, y1, x2, y2 = [float(x.strip()) for x in bbox]
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            description += f"ID: {elem['ID']}\n"
            description += f"内容: {elem['content']}\n"
            description += f"类型: {elem['type']}\n"
            description += f"位置: 左上({x1:.3f}, {y1:.3f}) 右下({x2:.3f}, {y2:.3f})\n"
            description += f"中心点: ({center_x:.3f}, {center_y:.3f})\n"
            description += "-" * 30 + "\n"
        
        return description
    
    def create_gpt4o_prompt(self, task: Dict[str, Any], elements_description: str) -> str:
        """创建发送给GPT-4o的提示词"""
        prompt = f"""你是一个专业的网页自动化测试专家。我需要你帮我在Google搜索页面上完成一个特定任务。

**任务**: {task['task']}
**任务描述**: {task['description']}

**页面元素信息**:
{elements_description}

**你的任务**:
1. 仔细分析所有可交互元素
2. 根据任务要求，选择最合适的元素进行点击
3. 解释你的选择理由
4. 只能选择上面列出的可交互元素

**重要要求**:
- 必须从上述元素列表中选择一个元素
- 选择的元素必须与任务最相关
- 给出详细的选择理由

请严格按照以下JSON格式回复：
```json
{{
    "selected_element_id": 选中元素的ID号(整数),
    "element_content": "选中元素的内容描述",
    "reasoning": "详细解释为什么选择这个元素，它如何帮助完成任务",
    "confidence": 你的信心程度(1-10的整数),
    "click_strategy": "点击策略说明"
}}
```

请务必严格按照JSON格式回复，不要添加任何其他文字！"""
        return prompt
    
    def call_gpt4o_api(self, prompt: str) -> Optional[str]:
        """调用GPT-4o API"""
        if not self.config:
            print("❌ 配置未加载，无法调用API")
            return None
        
        try:
            from openai import OpenAI
            
            # 创建客户端（简化初始化）
            client = OpenAI(
                api_key=self.config.get_openai_api_key(),
                base_url=self.config.get_openai_base_url(),
                timeout=30
            )
            
            print("🤖 正在调用GPT-4o API...")
            response = client.chat.completions.create(
                model=self.config.get_openai_model(),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ GPT-4o API调用失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_gpt4o_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析GPT-4o响应"""
        if not response:
            return None
        
        try:
            # 提取JSON内容
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析整个响应
                json_str = response.strip()
            
            parsed = json.loads(json_str)
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始响应: {response}")
            return None
    
    def visualize_selection(self, image_path: str, selected_element: Dict[str, Any], 
                          task_name: str, gpt4o_response: Dict[str, Any]) -> str:
        """在图片上可视化标记GPT-4o的选择"""
        try:
            # 加载原始图片
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            width, height = image.size
            
            # 解析选中元素的坐标
            bbox_str = selected_element['bbox']
            bbox = eval(bbox_str)  # [x1, y1, x2, y2] 相对坐标
            x1, y1, x2, y2 = bbox
            
            # 转换为像素坐标
            px1, py1 = int(x1 * width), int(y1 * height)
            px2, py2 = int(x2 * width), int(y2 * height)
            
            # 计算中心点
            center_x = (px1 + px2) // 2
            center_y = (py1 + py2) // 2
            
            # 绘制选中元素的边框 (红色)
            draw.rectangle([px1, py1, px2, py2], outline='red', width=4)
            
            # 绘制点击中心点 (红色圆圈)
            radius = 8
            draw.ellipse([center_x - radius, center_y - radius, 
                         center_x + radius, center_y + radius], 
                        fill='red', outline='darkred', width=2)
            
            # 添加选择信息文本
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                # 如果找不到字体，使用默认字体
                font = ImageFont.load_default()
            
            # 在图片顶部添加信息
            info_text = f"GPT-4o选择: ID {selected_element['ID']} - {selected_element['content'][:30]}..."
            confidence_text = f"信心度: {gpt4o_response.get('confidence', 'N/A')}/10"
            
            # 绘制白色背景
            text_bbox = draw.textbbox((10, 10), info_text, font=font)
            draw.rectangle([5, 5, text_bbox[2] + 10, text_bbox[3] + 35], fill='white', outline='black')
            
            # 绘制文本
            draw.text((10, 10), info_text, fill='black', font=font)
            draw.text((10, 30), confidence_text, fill='black', font=font)
            
            # 在选中元素附近添加ID标签
            label_text = f"ID: {selected_element['ID']}"
            label_x = max(10, min(px1, width - 80))
            label_y = max(10, py1 - 25)
            
            # 绘制标签背景
            label_bbox = draw.textbbox((label_x, label_y), label_text, font=font)
            draw.rectangle([label_x - 5, label_y - 5, label_bbox[2] + 5, label_bbox[3] + 5], 
                          fill='yellow', outline='red')
            draw.text((label_x, label_y), label_text, fill='red', font=font)
            
            # 保存标记后的图片
            output_filename = f"gpt4o_selection_{task_name.replace(' ', '_')}.png"
            image.save(output_filename)
            print(f"✅ 可视化结果已保存: {output_filename}")
            
            return output_filename
            
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            return None
    
    def run_real_test(self, csv_path: str, image_path: str):
        """运行真实的GPT-4o测试"""
        print("🎯 开始GPT-4o真实选择测试")
        print("=" * 60)
        
        if not self.config:
            print("❌ 配置未加载，无法进行测试")
            return
        
        # 加载页面元素
        elements = self.load_page_elements(csv_path)
        if not elements:
            return
        
        # 创建元素描述
        elements_description = self.create_elements_description(elements)
        
        # 定义测试任务
        test_tasks = [
            {
                "id": 1,
                "task": "搜索Python编程教程",
                "description": "用户想要在Google搜索框中输入'Python编程教程'进行搜索"
            },
            {
                "id": 2,
                "task": "使用手气不错功能",
                "description": "用户想要点击'I'm Feeling Lucky'按钮直接跳转到第一个搜索结果"
            },
            {
                "id": 3,
                "task": "登录Google账户",
                "description": "用户想要点击登录按钮来访问自己的Google账户"
            }
        ]
        
        results = []
        
        # 执行每个测试任务
        for task in test_tasks:
            print(f"\n🎯 任务 {task['id']}: {task['task']}")
            print("-" * 40)
            
            # 创建提示词
            prompt = self.create_gpt4o_prompt(task, elements_description)
            
            # 调用GPT-4o API
            gpt4o_response = self.call_gpt4o_api(prompt)
            
            if not gpt4o_response:
                print("❌ GPT-4o API调用失败")
                continue
            
            print(f"📄 GPT-4o原始响应: {gpt4o_response[:200]}...")
            
            # 解析响应
            parsed_response = self.parse_gpt4o_response(gpt4o_response)
            
            if not parsed_response:
                print("❌ GPT-4o响应解析失败")
                continue
            
            # 查找选中的元素
            selected_id = parsed_response.get('selected_element_id')
            selected_element = None
            
            for elem in elements:
                if int(elem['ID']) == selected_id:
                    selected_element = elem
                    break
            
            if selected_element:
                print(f"✅ GPT-4o选择: ID {selected_id} - {selected_element['content']}")
                print(f"🤖 信心度: {parsed_response.get('confidence', 'N/A')}/10")
                print(f"💭 选择理由: {parsed_response.get('reasoning', 'N/A')}")
                
                # 生成可视化图片
                viz_file = self.visualize_selection(
                    image_path, selected_element, 
                    f"task_{task['id']}", parsed_response
                )
                
                # 记录结果
                result = {
                    "task_id": task['id'],
                    "task_name": task['task'],
                    "task_description": task['description'],
                    "selected_element_id": selected_id,
                    "element_content": selected_element['content'],
                    "confidence": parsed_response.get('confidence', 0),
                    "reasoning": parsed_response.get('reasoning', ''),
                    "success": True
                }
                
                results.append(result)
                
            else:
                print(f"❌ 未找到ID为 {selected_id} 的元素")
                results.append({
                    "task_id": task['id'],
                    "task_name": task['task'],
                    "task_description": task['description'],
                    "selected_element_id": selected_id,
                    "element_content": "元素未找到",
                    "success": False
                })
        
        # 保存JSON结果
        with open("gpt4o_real_selection_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("\n🎉 GPT-4o真实选择测试完成！")
        print("📁 查看结果文件:")
        print("   - gpt4o_real_selection_results.json (JSON数据)")
        print("   - gpt4o_selection_task_*.png (可视化图片)")

def main():
    """主函数"""
    print("🚀 GPT-4o Google搜索页面真实选择测试")
    print("=" * 50)
    
    # 检查必要文件
    csv_file = "results_gpt4o_google_page.csv"
    image_file = "imgs/google_page.png"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV文件 {csv_file} 不存在！")
        print("请先运行 demo_gpt4o.py 生成页面解析结果")
        return
    
    if not os.path.exists(image_file):
        print(f"❌ 图片文件 {image_file} 不存在！")
        print("请确保图片文件存在")
        return
    
    try:
        # 创建测试实例
        tester = GPT4oRealSelectionTest()
        
        if tester.config:
            # 运行真实测试
            tester.run_real_test(csv_file, image_file)
        else:
            print("❌ 配置加载失败，无法进行测试")
    
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 