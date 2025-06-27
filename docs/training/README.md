# OmniParser 文档目录

本目录包含OmniParser项目的详细技术文档和设计说明。

## 文档列表

### 📋 设计文档
- **[OutputFormat.md](./OutputFormat.md)** - 输出结构化结果格式设计说明
  - 详细描述OmniParser的输出数据结构
  - 包含完整的字段定义和示例
  - 适用于开发者集成和理解数据格式

### 🏗️ 模型训练文档
- **[ModelTraining.md](./ModelTraining.md)** - 英文版模型训练指南
- **[ModelTraining_CN.md](./ModelTraining_CN.md)** - 中文版模型训练指南
  - 涵盖YOLO检测模型和Florence2描述模型的训练
  - 包含数据准备、训练配置和评估方法

### 📊 评估文档
- **[Evaluation.md](./Evaluation.md)** - 模型评估指南
  - 性能评估方法和指标
  - 基准测试结果

## 文档使用指南

### 对于开发者
1. 首先阅读 `OutputFormat.md` 了解数据结构
2. 根据需要参考模型训练文档进行自定义训练
3. 使用评估文档验证模型性能

### 对于研究人员
1. 查看 `ModelTraining.md` 了解技术细节
2. 参考 `Evaluation.md` 进行性能对比
3. 基于设计文档理解系统架构

### 对于用户
1. 重点关注 `OutputFormat.md` 的应用场景部分
2. 了解数据格式以便进行后续处理

## 贡献指南

欢迎为文档贡献内容：
1. 发现错误或不清楚的地方，请提交Issue
2. 补充示例代码或使用案例
3. 翻译文档到其他语言
4. 添加新的技术说明文档

## 版本信息

- 当前版本: v2.0
- 最后更新: 2024年
- 维护者: OmniParser团队 