#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图标坐标转换计算脚本
将相对坐标 [x_min, y_min, x_max, y_max] 转换为新分辨率下的绝对坐标
"""

def convert_relative_to_absolute(image_width, image_height, relative_coords):
    """
    将相对坐标转换为绝对坐标
    
    Args:
        image_width (int): 图像宽度
        image_height (int): 图像高度
        relative_coords (list): 相对坐标 [x_min, y_min, x_max, y_max]，值在0-1之间
        
    Returns:
        list: 绝对坐标 [x_min, y_min, x_max, y_max]，像素值
    """
    x_min_rel, y_min_rel, x_max_rel, y_max_rel = relative_coords
    
    # 转换为绝对坐标
    x_min_abs = int(x_min_rel * image_width)
    y_min_abs = int(y_min_rel * image_height)
    x_max_abs = int(x_max_rel * image_width)
    y_max_abs = int(y_max_rel * image_height)
    
    return [x_min_abs, y_min_abs, x_max_abs, y_max_abs]

def convert_absolute_to_relative(image_width, image_height, absolute_coords):
    """
    将绝对坐标转换为相对坐标
    
    Args:
        image_width (int): 图像宽度
        image_height (int): 图像高度
        absolute_coords (list): 绝对坐标 [x_min, y_min, x_max, y_max]，像素值
        
    Returns:
        list: 相对坐标 [x_min, y_min, x_max, y_max]，值在0-1之间
    """
    x_min_abs, y_min_abs, x_max_abs, y_max_abs = absolute_coords
    
    # 转换为相对坐标
    x_min_rel = x_min_abs / image_width
    y_min_rel = y_min_abs / image_height
    x_max_rel = x_max_abs / image_width
    y_max_rel = y_max_abs / image_height
    
    return [x_min_rel, y_min_rel, x_max_rel, y_max_rel]

def get_bbox_info(coords):
    """
    获取边界框信息
    
    Args:
        coords (list): 坐标 [x_min, y_min, x_max, y_max]
        
    Returns:
        dict: 包含宽度、高度、中心点等信息
    """
    x_min, y_min, x_max, y_max = coords
    
    width = x_max - x_min
    height = y_max - y_min
    center_x = x_min + width / 2
    center_y = y_min + height / 2
    area = width * height
    
    return {
        'width': width,
        'height': height,
        'center_x': center_x,
        'center_y': center_y,
        'area': area
    }

def main():
    """主函数 - 演示坐标转换"""
    
    # 示例数据
    image_width = 750
    image_height = 1636
    relative_coords = [0.223, 0.473, 0.383, 0.576]
    
    print("=" * 50)
    print("图标坐标转换计算器")
    print("=" * 50)
    
    print(f"图像尺寸: {image_width} x {image_height}")
    print(f"相对坐标: {relative_coords}")
    
    # 转换为绝对坐标
    absolute_coords = convert_relative_to_absolute(image_width, image_height, relative_coords)
    print(f"绝对坐标: {absolute_coords}")
    
    # 获取边界框信息
    bbox_info = get_bbox_info(absolute_coords)
    print("\n边界框信息:")
    print(f"  宽度: {bbox_info['width']} 像素")
    print(f"  高度: {bbox_info['height']} 像素")
    print(f"  中心点: ({bbox_info['center_x']:.1f}, {bbox_info['center_y']:.1f})")
    print(f"  面积: {bbox_info['area']} 平方像素")
    
    # 验证反向转换
    print("\n验证反向转换:")
    converted_back = convert_absolute_to_relative(image_width, image_height, absolute_coords)
    print(f"转换回相对坐标: {[round(x, 3) for x in converted_back]}")
    
    print("\n" + "=" * 50)
    print("交互式转换")
    print("=" * 50)
    
    while True:
        try:
            print("\n请选择转换类型:")
            print("1. 相对坐标 -> 绝对坐标")
            print("2. 绝对坐标 -> 相对坐标")
            print("3. 退出")
            
            choice = input("请输入选择 (1-3): ").strip()
            
            if choice == '3':
                print("再见！")
                break
            elif choice not in ['1', '2']:
                print("无效选择，请重新输入")
                continue
            
            # 输入图像尺寸
            width = int(input("请输入图像宽度: "))
            height = int(input("请输入图像高度: "))
            
            if choice == '1':
                # 相对坐标转绝对坐标
                coords_str = input("请输入相对坐标 (格式: x_min,y_min,x_max,y_max): ")
                coords = [float(x.strip()) for x in coords_str.split(',')]
                
                if len(coords) != 4:
                    print("坐标格式错误，请输入4个值")
                    continue
                
                result = convert_relative_to_absolute(width, height, coords)
                print(f"绝对坐标: {result}")
                
                # 显示详细信息
                bbox_info = get_bbox_info(result)
                print(f"边界框大小: {bbox_info['width']} x {bbox_info['height']} 像素")
                print(f"中心点: ({bbox_info['center_x']:.1f}, {bbox_info['center_y']:.1f})")
                
            else:
                # 绝对坐标转相对坐标
                coords_str = input("请输入绝对坐标 (格式: x_min,y_min,x_max,y_max): ")
                coords = [int(x.strip()) for x in coords_str.split(',')]
                
                if len(coords) != 4:
                    print("坐标格式错误，请输入4个值")
                    continue
                
                result = convert_absolute_to_relative(width, height, coords)
                print(f"相对坐标: {[round(x, 3) for x in result]}")
                
        except ValueError:
            print("输入格式错误，请重新输入")
        except KeyboardInterrupt:
            print("\n\n程序已退出")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main() 