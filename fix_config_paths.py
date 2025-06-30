#!/usr/bin/env python3
"""
修复配置文件路径问题
将硬编码的 "config.json" 替换为相对于项目根目录的路径
"""

import os
import re
import sys

def fix_config_path_in_file(filepath, project_root):
    """修复单个文件中的配置文件路径"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 计算相对于项目根目录的路径
        rel_path = os.path.relpath(project_root, os.path.dirname(filepath))
        
        # 构建正确的配置文件路径
        if rel_path == '.':
            config_path = '"config.json"'
        else:
            config_path = f'os.path.join(project_root, "config.json")'
        
        # 只在examples目录下的文件中修改，并且确保有project_root变量
        if 'examples/' in filepath and 'project_root' in content:
            # 替换硬编码的配置文件路径
            patterns_to_replace = [
                (r'config_path\s*=\s*"config\.json"', f'config_path = {config_path}'),
                (r'open\s*\(\s*"config\.json"', f'open(os.path.join(project_root, "config.json")'),
                (r'open\s*\(\s*\'config\.json\'', f'open(os.path.join(project_root, "config.json")'),
                (r'get_config\s*\(\s*"config\.json"', f'get_config(os.path.join(project_root, "config.json")'),
                (r'get_config\s*\(\s*\'config\.json\'', f'get_config(os.path.join(project_root, "config.json")'),
                (r'exists\s*\(\s*"config\.json"', f'exists(os.path.join(project_root, "config.json")'),
                (r'exists\s*\(\s*\'config\.json\'', f'exists(os.path.join(project_root, "config.json")'),
            ]
            
            for pattern, replacement in patterns_to_replace:
                content = re.sub(pattern, replacement, content)
        
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

def should_fix_file(filepath, project_root):
    """判断文件是否需要修复"""
    # 只修复examples目录下的Python文件
    rel_path = os.path.relpath(filepath, project_root)
    if not rel_path.startswith('examples/'):
        return False
    
    # 跳过__init__.py文件
    if os.path.basename(filepath) == '__init__.py':
        return False
    
    return True

def main():
    """主函数"""
    project_root = os.getcwd()
    print(f"🔧 开始修复配置文件路径: {project_root}")
    print("=" * 50)
    
    # 查找所有需要修复的Python文件
    python_files = []
    for root, dirs, files in os.walk(project_root):
        # 跳过 .git, __pycache__ 等目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if should_fix_file(filepath, project_root):
                    python_files.append(filepath)
    
    print(f"📁 找到 {len(python_files)} 个需要检查的文件")
    print()
    
    # 修复每个文件
    fixed_count = 0
    for filepath in python_files:
        if fix_config_path_in_file(filepath, project_root):
            fixed_count += 1
    
    print()
    print("=" * 50)
    print(f"🎉 修复完成! 共修复了 {fixed_count} 个文件")

if __name__ == "__main__":
    main() 