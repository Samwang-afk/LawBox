# Changelog

## Core v1.0.0 (2026-08-28)

Legal Work OS Core（法律百宝箱 Core v1）首次发布。本项目是在上游 `legal-skills`（MIT License）工作流基础上重建的独立仓库。

### 重建

- 从上游完整迁移 58 个专业法律 Skill、模板、脚本、DOCX/redline/QC 管线与质量门。
- 移除上游个人品牌、作者简介、联系方式、个人官网与宣传内容（合规保留的许可通知见 `THIRD_PARTY_NOTICES.md`）。
- 修正损坏的目录名（法律文章quai味道 → 法律文章去AI味道）。

### 新增

- Legal Clarification（缺失≠阻塞、Ask 前必须先 Read、Question Budget 1–5）。
- Ludus Adversarial Review（反向复核协议：五条固定检查、Minimum Failure Set、falsification 目标）。
- Intake / Conflict 协议（九项最低检查、组织级冲突检索不做假）。
- Matter Lifecycle 协议（INTAKE / ACTIVE / WAITING / REVIEW / DELIVERED / CLOSED 六态）。
- Action / Approval Gate（分析 ≠ 授权执行）。
- SOP Contract（WHEN / INPUT / DO / DECIDE / APPROVE / OUTPUT / CLOSE）。
- Hermes-style Post-task Reflection 与 `knowledge/lessons.md`（Agent 绝不自动修改 Skill）。
- 事实状态区分：CONFIRMED / ASSERTED / DISPUTED / INFERRED / UNKNOWN。

### 变更

- 总控工作流重构：简单任务保持简单（L0 直接回答），复杂事项才走澄清/复核/审批。
- 对抗审议协议合并为 `adversarial-review-protocol.md`（轻量反向复核）。
- 认知状态命名 ESTABLISHED → CONFIRMED（协议、脚本、测试同步更新）。
- 每个 Skill 启动声明精简为法律工作辅助声明，许可证信息不再随任务刷屏。

### 许可证

- 新创作内容：PolyForm Noncommercial License 1.0.0（见 `LICENSE`）。
- 上游 MIT 内容：保留原始 MIT License（见 `LICENSES/upstream-MIT.txt`）。
- 第三方归属与必要通知：见 `THIRD_PARTY_NOTICES.md`。

### 测试

- 新增根级行为测试基准（`tests/`，20+ 用例）。
- 保留并回归运行既有推理控制与 DOCX/redline 管线测试。
