#!/bin/bash
# Phoenix Vision FastMCP 服务器启动脚本
# 🔥 一键启动 Phoenix Vision FastMCP 服务器

echo "🔥 Phoenix Vision 服务启动器"
echo "============================================================"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SCRIPT_DIR/src/server/phoenix_vision_fastmcp_server.py"

# 检查Python
echo "🔍 检查Python环境..."
if ! command -v python &> /dev/null; then
    echo "❌ Python 未找到，请安装Python"
    exit 1
fi

PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  ✅ Python版本: $PYTHON_VERSION"

# 检查服务器脚本
echo "📁 检查服务器脚本..."
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo "❌ 服务器脚本不存在: $SERVER_SCRIPT"
    exit 1
fi
echo "  ✅ 服务器脚本: $SERVER_SCRIPT"

# 检查配置文件
CONFIG_FILE="$SCRIPT_DIR/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️  配置文件不存在: $CONFIG_FILE"
    echo "  服务器将使用默认配置"
else
    echo "  ✅ 配置文件: $CONFIG_FILE"
fi

# 检查模型文件
MODEL_FILE="$SCRIPT_DIR/weights/icon_detect/model.pt"
if [ ! -f "$MODEL_FILE" ]; then
    echo "⚠️  模型文件不存在: $MODEL_FILE"
    echo "  图像分析功能可能不可用"
else
    echo "  ✅ 模型文件: $MODEL_FILE"
fi

# 设置环境变量
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo ""
echo "🚀 启动 Phoenix Vision FastMCP 服务器..."
echo "============================================================"
echo "📍 服务器脚本: $SERVER_SCRIPT"
echo "📍 工作目录: $SCRIPT_DIR"
echo ""
echo "💡 使用说明:"
echo "  - 服务器通过stdio协议运行"
echo "  - 可以通过MCP客户端连接"
echo "  - 按 Ctrl+C 停止服务器"
echo ""
echo "============================================================"

# 切换到项目目录并启动服务器
cd "$SCRIPT_DIR"

# 捕获中断信号
trap 'echo -e "\n\n🛑 服务器已停止"; exit 0' INT

# 启动服务器
python "$SERVER_SCRIPT"

echo ""
echo "✅ 服务器启动完成" 