# Task Plan: 优化 miaodong-finance-writer skill 工作流程

## Goal
重构 miaodong-finance-writer skill，实现六步完整工作流：
1. 学习写作风格规范
2. 调用小红书MCP获取爆款笔记
3. 采访用户想法观点
4. 列出提纲并确认
5. 写作笔记
6. 自我校验质量

## Phases
- [x] Phase 1: 研究现有 skill 结构
- [x] Phase 2: 设计新工作流架构
- [x] Phase 3: 实现 prompt 重构
- [x] Phase 4: 测试验证（详见交付文档）
- [x] Phase 5: 文档更新（已完成交付文档）

## Key Questions
1. 当前 skill 的核心 prompt 结构是什么？
2. 如何优雅地集成小红书 MCP 调用？
3. 如何保持 skill 的简洁性和高效性？
4. 六个阶段的状态管理如何设计？

## Decisions Made
- 待填充

## Errors Encountered
- 待填充

## Decisions Made
- **采用渐进式重构**: 保持现有知识库不变，仅优化 Workflow 和 Prompt 逻辑
- **新增小红书 MCP 集成**: 在第二步调用搜索获取爆款笔记
- **新增提纲确认环节**: 在第四步列出提纲并等待用户确认
- **保持简洁性**: 不引入复杂的状态管理，使用自然的对话流程

## Status
**Currently in Phase 2** - 正在研究现有结构并设计新工作流架构
