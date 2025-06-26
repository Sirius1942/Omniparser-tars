#!/bin/bash

echo "🎉 btop++ 演示脚本"
echo "=================="
echo ""

# 显示版本信息
echo "📋 btop++ 版本信息:"
btop --version
echo ""

echo "🚀 btop++ 演示命令:"
echo ""

echo "1. 基础启动命令:"
echo "   btop"
echo "   - 启动btop++的默认界面"
echo ""

echo "2. 调试模式:"
echo "   btop --debug"
echo "   - 启动调试模式，显示额外的日志和指标"
echo ""

echo "3. 不同的颜色主题和预设:"
echo "   btop --preset 0  # 默认主题"
echo "   btop --preset 1  # 主题1"
echo "   btop --preset 2  # 主题2"
echo "   btop --preset 3  # 主题3"
echo "   btop --preset 4  # 主题4"
echo ""

echo "4. 自定义更新频率:"
echo "   btop --update 500   # 500毫秒更新一次"
echo "   btop --update 2000  # 2秒更新一次"
echo ""

echo "5. 低色彩模式:"
echo "   btop --low-color    # 使用256色模式"
echo "   btop --tty          # 强制TTY模式，使用16色"
echo ""

echo "6. 自定义配置文件:"
echo "   btop --config ~/.config/btop/custom.conf"
echo ""

echo "⌨️  btop++ 界面内快捷键:"
echo "=============================="
echo "导航控制:"
echo "  h, ←     - 向左移动"
echo "  l, →     - 向右移动"
echo "  j, ↓     - 向下移动"
echo "  k, ↑     - 向上移动"
echo "  PgUp     - 向上翻页"
echo "  PgDn     - 向下翻页"
echo "  Home     - 跳到顶部"
echo "  End      - 跳到底部"
echo ""

echo "功能控制:"
echo "  q        - 退出btop++"
echo "  ESC      - 返回主界面"
echo "  m        - 切换主菜单"
echo "  p        - 暂停/恢复更新"
echo "  +/-      - 增加/减少更新间隔"
echo "  t        - 切换树形视图"
echo "  f        - 过滤进程"
echo "  r        - 反向排序"
echo "  c        - 按CPU使用率排序"
echo "  n        - 按名称排序"
echo "  i        - 按PID排序"
echo "  s        - 按状态排序"
echo ""

echo "进程管理:"
echo "  Enter    - 选择进程"
echo "  d        - 详细信息"
echo "  k        - 终止进程(SIGKILL)"
echo "  t        - 终止进程(SIGTERM)"
echo "  i        - 中断进程(SIGINT)"
echo ""

echo "视图切换:"
echo "  1        - 显示CPU"
echo "  2        - 显示内存"
echo "  3        - 显示网络"
echo "  4        - 显示磁盘"
echo "  TAB      - 切换焦点"
echo ""

echo "主题和外观:"
echo "  F1       - 帮助"
echo "  F2       - 选项"
echo "  F3       - 更改主题"
echo "  F4       - 更改颜色主题"
echo "  F5       - 切换所有图表"
echo "  F6       - 切换温度单位"
echo ""

echo "🎨 主题演示:"
echo "============"
echo "让我为您展示不同的主题效果..."
echo ""

# 演示不同主题
for i in {0..4}; do
    echo "🎭 主题 $i:"
    echo "   运行命令: gtimeout 3 btop --preset $i"
    echo "   (按 Ctrl+C 提前退出)"
    echo ""
    
    # 短暂延迟
    sleep 1
done

echo "💡 使用建议:"
echo "============"
echo "1. 首次使用建议直接运行: btop"
echo "2. 按 F1 查看完整帮助"
echo "3. 按 F2 进入选项配置"
echo "4. 按 F3 选择您喜欢的主题"
echo "5. 按 q 退出程序"
echo ""

echo "🔧 高级用法:"
echo "============"
echo "1. 创建自定义配置:"
echo "   mkdir -p ~/.config/btop"
echo "   btop --config ~/.config/btop/myconfig.conf"
echo ""

echo "2. 监控特定进程:"
echo "   启动btop后按 'f' 键进行过滤"
echo ""

echo "3. 导出配置:"
echo "   btop的配置文件通常在 ~/.config/btop/btop.conf"
echo ""

echo "📊 现在让我们实际运行btop++..."
echo "================================="
echo "提示: 按 'q' 退出btop++"
echo ""

# 等待用户按键
read -p "按Enter键启动btop++演示..."

# 启动btop++
btop --preset 0 