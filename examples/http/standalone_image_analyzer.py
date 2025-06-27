#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立图像分析器
基于 HTTP API 的图像分析服务，可接收图片并返回分析结果和标注图片
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import os
import json
import base64
import time
import tempfile
from typing import Dict, Any
from flask import Flask, request, jsonify, send_file
from PIL import Image
import io

# 导入图像分析器
from src.utils.image_element_analyzer import ImageElementAnalyzer

app = Flask(__name__)
analyzer = None

def initialize_analyzer():
    """初始化图像分析器"""
    global analyzer
    
    if analyzer is not None:
        return True
    
    try:
        print("🚀 正在初始化图像分析器...")
        
        # 检查模型和配置文件
        model_path = 'weights/icon_detect/model.pt'
        config_path = "config.json"
        
        if not os.path.exists(model_path):
            print(f"❌ 模型文件不存在: {model_path}")
            return False
            
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return False
        
        analyzer = ImageElementAnalyzer(model_path, config_path)
        success = analyzer.initialize()
        
        if success:
            print("✅ 分析器初始化成功")
            return True
        else:
            print("❌ 分析器初始化失败")
            return False
            
    except Exception as e:
        print(f"❌ 初始化分析器时出错: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    device_info = {}
    try:
        import torch
        device_info = {
            "device": 'cuda' if torch.cuda.is_available() else 'cpu',
            "cuda_available": torch.cuda.is_available(),
        }
        if torch.cuda.is_available():
            device_info.update({
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_count": torch.cuda.device_count()
            })
    except:
        pass
    
    return jsonify({
        "status": "healthy",
        "analyzer_ready": analyzer is not None and analyzer._initialized,
        "device_info": device_info,
        "timestamp": time.time()
    })

@app.route('/analyze_file', methods=['POST'])
def analyze_image_file():
    """分析图像文件"""
    if not initialize_analyzer():
        return jsonify({
            "success": False,
            "error": "分析器初始化失败"
        }), 500
    
    try:
        data = request.get_json()
        if not data or 'image_path' not in data:
            return jsonify({
                "success": False,
                "error": "缺少 image_path 参数"
            }), 400
        
        image_path = data['image_path']
        box_threshold = data.get('box_threshold', 0.05)
        save_annotated = data.get('save_annotated', True)
        output_dir = data.get('output_dir', './results')
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return jsonify({
                "success": False,
                "error": f"图像文件不存在: {image_path}"
            }), 400
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🖼️  分析图像: {os.path.basename(image_path)}")
        
        # 执行分析
        result = analyzer.analyze_image(
            image_path,
            box_threshold=box_threshold,
            save_annotated=save_annotated,
            output_dir=output_dir,
            verbose=True
        )
        
        # 添加时间戳
        result["timestamp"] = time.time()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"分析图像时出错: {str(e)}",
            "timestamp": time.time()
        }), 500

@app.route('/analyze_base64', methods=['POST'])
def analyze_image_base64():
    """分析 Base64 编码的图像"""
    if not initialize_analyzer():
        return jsonify({
            "success": False,
            "error": "分析器初始化失败"
        }), 500
    
    try:
        data = request.get_json()
        if not data or 'image_base64' not in data:
            return jsonify({
                "success": False,
                "error": "缺少 image_base64 参数"
            }), 400
        
        image_base64 = data['image_base64']
        box_threshold = data.get('box_threshold', 0.05)
        save_annotated = data.get('save_annotated', True)
        output_dir = data.get('output_dir', './results')
        
        # 移除可能的前缀
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        # 解码图像
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # 保存临时文件
        timestamp = int(time.time() * 1000)
        temp_path = f"temp_standalone_{timestamp}.png"
        image.save(temp_path)
        
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"🖼️  分析 Base64 图像 (大小: {image.size})")
            
            # 执行分析
            result = analyzer.analyze_image(
                temp_path,
                box_threshold=box_threshold,
                save_annotated=save_annotated,
                output_dir=output_dir,
                verbose=True
            )
            
            # 添加时间戳
            result["timestamp"] = time.time()
            
            return jsonify(result)
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"分析 Base64 图像时出错: {str(e)}",
            "timestamp": time.time()
        }), 500

@app.route('/annotated_image/<filename>', methods=['GET'])
def get_annotated_image(filename):
    """获取标注后的图像"""
    try:
        # 在结果目录中查找文件
        results_dir = './results'
        file_path = os.path.join(results_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/png')
        else:
            return jsonify({
                "success": False,
                "error": f"文件不存在: {filename}"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取图像时出错: {str(e)}"
        }), 500

@app.route('/results', methods=['GET'])
def list_results():
    """列出分析结果"""
    try:
        results_dir = './results'
        if not os.path.exists(results_dir):
            return jsonify({
                "success": True,
                "files": [],
                "count": 0
            })
        
        files = []
        for filename in os.listdir(results_dir):
            file_path = os.path.join(results_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "name": filename,
                    "size": stat.st_size,
                    "modified": time.ctime(stat.st_mtime)
                })
        
        return jsonify({
            "success": True,
            "files": files,
            "count": len(files),
            "directory": os.path.abspath(results_dir)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"列出结果时出错: {str(e)}"
        }), 500

def main():
    """启动服务器"""
    print("🎯 独立图像分析器 HTTP 服务")
    print("=" * 50)
    
    # 显示设备信息
    try:
        import torch
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🖥️  设备: {device}")
        if torch.cuda.is_available():
            print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("💻 使用 CPU 模式")
    except:
        print("💻 PyTorch 未安装，使用基础模式")
    
    print("\n📋 可用 API 端点:")
    print("   • GET  /health - 健康检查")
    print("   • POST /analyze_file - 分析图像文件")
    print("   • POST /analyze_base64 - 分析 Base64 图像")
    print("   • GET  /annotated_image/<filename> - 获取标注图像")
    print("   • GET  /results - 列出分析结果")
    
    print(f"\n🌐 服务地址: http://localhost:8080")
    print("=" * 50)
    
    # 启动 Flask 服务器
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == "__main__":
    main() 