#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
根据API测试结果修复配置的脚本
"""

import json
import os

def fix_config_based_on_error():
    """根据常见错误自动修复配置"""
    
    print("🛠️  配置修复向导")
    print("=" * 40)
    
    # 读取当前配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ 配置文件不存在！")
        return
    
    print("📋 当前配置:")
    print(f"   API端点: {config['openai']['base_url']}")
    print(f"   API密钥: {config['openai']['api_key'][:10]}...{config['openai']['api_key'][-10:]}")
    print(f"   模型: {config['openai']['model']}")
    
    print("\n🔍 常见问题修复选项:")
    print("1. 更新API密钥 (401错误)")
    print("2. 更换API端点 (连接失败)")
    print("3. 调整超时时间 (超时错误)")
    print("4. 更换模型名称 (模型不支持)")
    print("5. 重置为官方OpenAI API")
    print("0. 退出")
    
    choice = input("\n请选择修复选项 (0-5): ").strip()
    
    if choice == "1":
        new_key = input("请输入新的API密钥: ").strip()
        if new_key:
            config['openai']['api_key'] = new_key
            save_config(config)
            print("✅ API密钥已更新")
    
    elif choice == "2":
        new_url = input("请输入新的API端点 (如: https://api.openai.com/v1): ").strip()
        if new_url:
            config['openai']['base_url'] = new_url
            save_config(config)
            print("✅ API端点已更新")
    
    elif choice == "3":
        try:
            new_timeout = int(input("请输入新的超时时间(秒, 建议60): ").strip())
            config['openai']['request_timeout'] = new_timeout
            save_config(config)
            print("✅ 超时时间已更新")
        except ValueError:
            print("❌ 无效的超时时间")
    
    elif choice == "4":
        print("常用模型名称:")
        print("  - gpt-4o")
        print("  - gpt-4o-mini") 
        print("  - gpt-4-vision-preview")
        new_model = input("请输入新的模型名称: ").strip()
        if new_model:
            config['openai']['model'] = new_model
            save_config(config)
            print("✅ 模型名称已更新")
    
    elif choice == "5":
        # 重置为官方API
        config['openai']['base_url'] = "https://api.openai.com/v1"
        config['openai']['model'] = "gpt-4o"
        new_key = input("请输入官方OpenAI API密钥: ").strip()
        if new_key:
            config['openai']['api_key'] = new_key
            save_config(config)
            print("✅ 已重置为官方OpenAI API配置")
    
    elif choice == "0":
        print("👋 退出修复向导")
        return
    
    else:
        print("❌ 无效选择")
        return
    
    # 建议重新测试
    print("\n🧪 建议重新运行测试:")
    print("python test_api.py")

def save_config(config):
    """保存配置文件"""
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fix_config_based_on_error() 