#!/usr/bin/env python3
"""
OmniParser检测结果应用示例
展示如何使用OmniParser的检测结果进行各种实际应用
"""

import pandas as pd
import ast
import time
from typing import List, Tuple, Dict, Optional, Union
import json

# 可选导入
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("警告: pyautogui未安装，自动化功能将不可用")

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.font_manager import FontProperties
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("警告: 可视化库未安装，可视化功能将不可用")


class OmniParserResultProcessor:
    """OmniParser结果处理器"""
    
    def __init__(self, csv_file: str, image_file: Optional[str] = None, 
                 screen_size: Optional[Tuple[int, int]] = None):
        """
        初始化结果处理器
        
        Args:
            csv_file: CSV结果文件路径
            image_file: 原始图片文件路径（可选）
            screen_size: 屏幕尺寸 (width, height)，如果None则自动获取
        """
        self.csv_file = csv_file
        self.image_file = image_file
        self.df = pd.read_csv(csv_file)
        
        # 获取屏幕尺寸
        if screen_size is None and PYAUTOGUI_AVAILABLE:
            self.screen_size = pyautogui.size()
        elif screen_size is None:
            self.screen_size = (1920, 1080)  # 默认尺寸
        else:
            self.screen_size = screen_size
            
        # 解析边界框坐标
        self._parse_bboxes()
        
    def _parse_bboxes(self):
        """解析CSV中的边界框字符串为坐标列表"""
        self.df['bbox_coords'] = self.df['bbox'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
        
    def normalize_to_screen_coords(self, bbox: List[float]) -> Tuple[int, int, int, int]:
        """
        将归一化坐标转换为屏幕坐标
        
        Args:
            bbox: [x1, y1, x2, y2] 归一化坐标 (0-1)
            
        Returns:
            (x1, y1, x2, y2) 屏幕坐标
        """
        x1, y1, x2, y2 = bbox
        screen_x1 = int(x1 * self.screen_size[0])
        screen_y1 = int(y1 * self.screen_size[1])
        screen_x2 = int(x2 * self.screen_size[0])
        screen_y2 = int(y2 * self.screen_size[1])
        return screen_x1, screen_y1, screen_x2, screen_y2
        
    def get_center_point(self, bbox: List[float]) -> Tuple[int, int]:
        """获取边界框的中心点屏幕坐标"""
        x1, y1, x2, y2 = self.normalize_to_screen_coords(bbox)
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return center_x, center_y

    def find_elements_by_content(self, search_text: str, exact_match: bool = False) -> pd.DataFrame:
        """
        根据内容搜索元素
        
        Args:
            search_text: 搜索文本
            exact_match: 是否精确匹配
            
        Returns:
            匹配的元素DataFrame
        """
        if exact_match:
            mask = self.df['content'].str.contains(search_text, case=False, na=False)
        else:
            mask = self.df['content'].str.contains(search_text, case=False, na=False, regex=False)
        
        return self.df[mask]
    
    def find_interactive_elements(self) -> pd.DataFrame:
        """获取所有可交互的元素"""
        return self.df[self.df['interactivity'] == True]
    
    def find_elements_by_type(self, element_type: str) -> pd.DataFrame:
        """根据类型筛选元素"""
        return self.df[self.df['type'] == element_type]

    def click_element_by_content(self, search_text: str, delay: float = 1.0) -> bool:
        """
        根据内容点击元素
        
        Args:
            search_text: 要点击的元素内容
            delay: 点击前等待时间
            
        Returns:
            是否成功点击
        """
        if not PYAUTOGUI_AVAILABLE:
            print("pyautogui未安装，无法执行点击操作")
            return False
            
        elements = self.find_elements_by_content(search_text)
        interactive_elements = elements[elements['interactivity'] == True]
        
        if interactive_elements.empty:
            print(f"未找到可交互的元素: {search_text}")
            return False
            
        # 选择第一个匹配的元素
        element = interactive_elements.iloc[0]
        center_x, center_y = self.get_center_point(element['bbox_coords'])
        
        print(f"点击元素: {element['content']} 位置: ({center_x}, {center_y})")
        
        time.sleep(delay)
        pyautogui.click(center_x, center_y)
        return True
    
    def hover_element_by_content(self, search_text: str, delay: float = 1.0) -> bool:
        """根据内容悬停元素"""
        if not PYAUTOGUI_AVAILABLE:
            print("pyautogui未安装，无法执行悬停操作")
            return False
            
        elements = self.find_elements_by_content(search_text)
        
        if elements.empty:
            print(f"未找到元素: {search_text}")
            return False
            
        element = elements.iloc[0]
        center_x, center_y = self.get_center_point(element['bbox_coords'])
        
        print(f"悬停元素: {element['content']} 位置: ({center_x}, {center_y})")
        
        time.sleep(delay)
        pyautogui.moveTo(center_x, center_y)
        return True

    def get_element_info(self, search_text: str) -> Dict:
        """获取元素详细信息"""
        elements = self.find_elements_by_content(search_text)
        
        if elements.empty:
            return {}
            
        element = elements.iloc[0]
        bbox = element['bbox_coords']
        screen_coords = self.normalize_to_screen_coords(bbox)
        center = self.get_center_point(bbox)
        
        return {
            'content': element['content'],
            'type': element['type'],
            'interactivity': element['interactivity'],
            'source': element['source'],
            'normalized_bbox': bbox,
            'screen_coords': screen_coords,
            'center_point': center,
            'width': screen_coords[2] - screen_coords[0],
            'height': screen_coords[3] - screen_coords[1]
        }

    def visualize_results(self, save_path: Optional[str] = None, show_labels: bool = True):
        """
        可视化检测结果
        
        Args:
            save_path: 保存路径，如果None则显示
            show_labels: 是否显示标签
        """
        if not VISUALIZATION_AVAILABLE:
            print("可视化库未安装，无法生成可视化图像")
            return
            
        if self.image_file is None:
            print("需要提供原始图片文件才能可视化")
            return
            
        # 读取图片
        img = cv2.imread(self.image_file)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]
        
        # 创建matplotlib图形
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.imshow(img)
        
        # 设置中文字体
        try:
            font_prop = FontProperties(fname='C:/Windows/Fonts/simhei.ttf', size=8)
        except:
            font_prop = FontProperties(size=8)
        
        # 绘制边界框和标签
        colors = {'icon': 'red', 'text': 'blue', 'button': 'green'}
        
        for _, row in self.df.iterrows():
            bbox = row['bbox_coords']
            x1, y1, x2, y2 = [coord * w if i % 2 == 0 else coord * h 
                             for i, coord in enumerate(bbox)]
            
            color = colors.get(row['type'], 'orange')
            
            # 绘制边界框
            rect = patches.Rectangle((x1, y1), x2-x1, y2-y1, 
                                   linewidth=2, edgecolor=color, facecolor='none')
            ax.add_patch(rect)
            
            # 添加标签
            if show_labels and pd.notna(row['content']):
                content = str(row['content'])[:20] + ('...' if len(str(row['content'])) > 20 else '')
                ax.text(x1, y1-5, content, fontproperties=font_prop, 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7),
                       color='white', fontsize=8)
        
        ax.set_title('OmniParser检测结果', fontproperties=font_prop, fontsize=14)
        ax.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"可视化结果已保存到: {save_path}")
        else:
            plt.show()

    def generate_report(self) -> Dict:
        """生成检测结果报告"""
        total_elements = len(self.df)
        interactive_elements = len(self.df[self.df['interactivity'] == True])
        
        type_counts = self.df['type'].value_counts().to_dict()
        source_counts = self.df['source'].value_counts().to_dict()
        
        report = {
            'total_elements': total_elements,
            'interactive_elements': interactive_elements,
            'non_interactive_elements': total_elements - interactive_elements,
            'type_distribution': type_counts,
            'source_distribution': source_counts,
            'interactive_rate': f"{interactive_elements/total_elements*100:.1f}%" if total_elements > 0 else "0%"
        }
        
        return report
    
    def print_report(self):
        """打印详细报告"""
        report = self.generate_report()
        
        print("="*50)
        print("OmniParser检测结果报告")
        print("="*50)
        print(f"总元素数量: {report['total_elements']}")
        print(f"可交互元素: {report['interactive_elements']}")
        print(f"非交互元素: {report['non_interactive_elements']}")
        print(f"交互率: {report['interactive_rate']}")
        print()
        
        print("元素类型分布:")
        for elem_type, count in report['type_distribution'].items():
            print(f"  {elem_type}: {count}")
        print()
        
        print("来源分布:")
        for source, count in report['source_distribution'].items():
            print(f"  {source}: {count}")
        print()
        
        print("可交互元素详情:")
        interactive_df = self.find_interactive_elements()
        for _, row in interactive_df.iterrows():
            print(f"  [{row['type']}] {row['content']}")

    def export_to_json(self, output_file: str):
        """导出结果为JSON格式"""
        results = []
        
        for _, row in self.df.iterrows():
            bbox = row['bbox_coords']
            screen_coords = self.normalize_to_screen_coords(bbox)
            center = self.get_center_point(bbox)
            
            result = {
                'id': row['ID'],
                'type': row['type'],
                'content': row['content'],
                'interactivity': row['interactivity'],
                'source': row['source'],
                'coordinates': {
                    'normalized': bbox,
                    'screen': screen_coords,
                    'center': center
                }
            }
            results.append(result)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"结果已导出到: {output_file}")


def demo_automation_scenarios():
    """演示自动化场景"""
    
    # 使用你的检测结果
    processor = OmniParserResultProcessor('results_gpt4o_windows_home.csv')
    
    print("="*60)
    print("OmniParser结果应用演示")
    print("="*60)
    
    # 1. 显示检测报告
    processor.print_report()
    
    # 2. 搜索特定元素
    print("\n" + "="*50)
    print("搜索示例")
    print("="*50)
    
    # 搜索浏览器相关元素
    browser_elements = processor.find_elements_by_content("浏览器")
    print(f"找到 {len(browser_elements)} 个浏览器相关元素:")
    for _, elem in browser_elements.iterrows():
        print(f"  - {elem['content']}")
    
    # 搜索开始菜单
    start_menu = processor.find_elements_by_content("开始菜单")
    if not start_menu.empty:
        info = processor.get_element_info("开始菜单")
        print(f"\n开始菜单详细信息:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # 3. 导出结果
    print("\n" + "="*50)
    print("导出结果")
    print("="*50)
    processor.export_to_json('windows_home_results.json')
    
    # 4. 模拟交互（不实际执行）
    print("\n" + "="*50)
    print("可能的自动化操作")
    print("="*50)
    
    interactive_elements = processor.find_interactive_elements()
    print("可以自动点击的元素:")
    for _, elem in interactive_elements.iterrows():
        center = processor.get_center_point(elem['bbox_coords'])
        print(f"  - {elem['content']} (点击位置: {center})")
    
    return processor


def demo_click_automation(processor: OmniParserResultProcessor):
    """演示点击自动化（谨慎使用）"""
    
    if not PYAUTOGUI_AVAILABLE:
        print("pyautogui未安装，跳过点击演示")
        return
    
    print("\n" + "="*50)
    print("自动化点击演示（5秒后开始）")
    print("="*50)
    print("警告: 即将开始自动点击操作，请确保这是你想要的！")
    print("如需取消，请在5秒内按Ctrl+C")
    
    try:
        for i in range(5, 0, -1):
            print(f"倒计时: {i}")
            time.sleep(1)
        
        # 示例: 点击开始菜单
        print("尝试点击开始菜单...")
        success = processor.click_element_by_content("开始菜单", delay=1.0)
        
        if success:
            print("开始菜单点击成功！")
            time.sleep(2)
            
            # 按ESC键关闭菜单
            pyautogui.press('escape')
            print("已关闭开始菜单")
        
    except KeyboardInterrupt:
        print("\n操作已取消")


if __name__ == "__main__":
    # 安全设置
    if PYAUTOGUI_AVAILABLE:
        pyautogui.FAILSAFE = True  # 移动鼠标到屏幕角落可以停止程序
        pyautogui.PAUSE = 0.5     # 每个操作间隔0.5秒
    
    # 运行演示
    processor = demo_automation_scenarios()
    
    # 询问是否要运行点击演示
    if PYAUTOGUI_AVAILABLE:
        response = input("\n是否要运行自动点击演示？(y/N): ").lower().strip()
        if response == 'y':
            demo_click_automation(processor)
        else:
            print("跳过自动点击演示")
    
    print("\n演示完成！") 