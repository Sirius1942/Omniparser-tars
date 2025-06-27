# LLM Google搜索页面操作测试脚本

本项目提供了两个测试脚本，用于测试LLM在Google搜索页面中选择正确按钮操作的能力。

## 脚本文件

### 1. `test_llm_google_search.py` - 基础测试脚本
- **功能**: 基于CSV解析结果模拟LLM选择页面元素
- **特点**: 
  - 使用简单的关键词匹配算法
  - 生成详细的测试报告
  - 包含5个测试任务
  - 输出JSON格式的测试结果

### 2. `test_llm_google_search_advanced.py` - 高级测试脚本
- **功能**: 可选择真实LLM API调用或模拟测试
- **特点**: 
  - 支持真实LLM API测试
  - 更完整的测试评估系统
  - 可配置的测试任务
  - 详细的评分机制

## 使用方法

### 前提条件
1. 确保已运行 `demo_gpt4o.py` 生成 `results_gpt4o_google_page.csv` 文件
2. 如需使用真实LLM API，请确保 `config.json` 文件配置正确

### 运行基础测试
```bash
python test_llm_google_search.py
```

### 运行高级测试
```bash
python test_llm_google_search_advanced.py
```

## 测试任务

### 包含的测试任务：
1. **搜索任务**: 在Google搜索框中搜索'Python编程'
2. **Lucky按钮**: 点击'I'm Feeling Lucky'按钮
3. **登录任务**: 登录Google账户
4. **Gmail访问**: 打开Gmail邮箱
5. **语音搜索**: 使用语音搜索功能

### 测试逻辑
- 基于页面元素的`interactivity`字段判断是否可交互
- 通过关键词匹配确定最合适的元素
- 计算匹配度得分（1-10分）
- 生成详细的测试报告

## 输出文件

### 测试报告
- `llm_google_search_test_report.json` - 基础测试报告
- `advanced_llm_google_search_test_report.json` - 高级测试报告

### 报告内容
```json
{
  "summary": {
    "total_tests": 5,
    "successful_tests": 5,
    "success_rate": 100.0,
    "average_score": 10.0
  },
  "detailed_results": [
    {
      "task_id": 1,
      "task_name": "搜索任务",
      "success": true,
      "score": 10,
      "details": {
        "selected_element": {
          "id": 10,
          "content": "Google Search",
          "interactable": true
        }
      }
    }
  ]
}
```

## 评分标准

### 基础分数
- 可交互元素: +3分
- 关键词匹配: +4分
- 预期元素匹配: +3分
- 任务类型一致性: +2分

### 成功标准
- 7分及以上算作测试通过
- 最高分10分

## 扩展说明

### 添加新测试任务
在 `generate_test_tasks()` 函数中添加新的测试任务：

```python
{
    "id": 6,
    "task": "新的测试任务",
    "description": "任务描述",
    "expected_elements": ["预期元素"],
    "keywords": ["关键词1", "关键词2"],
    "action_type": "操作类型"
}
```

### 调整评分标准
修改 `evaluate_response()` 函数中的评分逻辑以适应不同的测试需求。

## 注意事项

1. CSV文件必须包含BOM，脚本会自动处理编码问题
2. 测试依赖于OmniParser的解析结果质量
3. 真实LLM API测试需要有效的API配置
4. 建议先运行基础测试确保环境正常

## 测试结果示例

```
🎯 测试任务 1: 在Google搜索框中搜索'Python编程'
✅ 测试通过! 得分: 10/10
   📍 选中元素: ID 10 - Google Search
   🔧 可交互: 是
   ✨ 匹配原因: 关键词匹配
```

这些测试脚本帮助评估LLM在实际网页自动化任务中的表现，为改进AI助手的操作准确性提供数据支持。 