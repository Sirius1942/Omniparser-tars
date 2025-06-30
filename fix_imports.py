#!/usr/bin/env python3
"""
修复项目重构后的导入路径
将 'from src.utils.' 替换为 'from src.utils.'
"""

import os
import re
import sys

def fix_imports_in_file(filepath):
    """修复单个文件中的导入路径"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 记录原始内容
        original_content = content
        
        # 替换导入路径
        # from src.utils.xxx import yyy -> from src.utils.xxx import yyy
        content = re.sub(r'from util\.', 'from src.utils.', content)
        
        # import src.utils.xxx -> import src.utils.xxx
        content = re.sub(r'import util\.', 'import src.utils.', content)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 修复: {filepath}")
            return True
        else:
            print(f"⏭️  跳过: {filepath} (无需修改)")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {filepath} - {e}")
        return False

def find_python_files(directory):
    """递归查找所有Python文件"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过 .git, __pycache__ 等目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """主函数"""
    project_root = os.getcwd()
    print(f"🔧 开始修复项目导入路径: {project_root}")
    print("=" * 50)
    
    # 查找所有Python文件
    python_files = find_python_files(project_root)
    print(f"📁 找到 {len(python_files)} 个Python文件")
    print()
    
    # 修复每个文件
    fixed_count = 0
    for filepath in python_files:
        if fix_imports_in_file(filepath):
            fixed_count += 1
    
    print()
    print("=" * 50)
    print(f"🎉 修复完成! 共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    main() 