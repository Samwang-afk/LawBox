# 事项生命周期协议

本协议是横向统一框架，只管理"事项处于什么状态、下一步做什么"。领域细节仍由专业 Skill（如 `民事一审诉讼`、`劳动争议诉讼`、`刑事辩护总调度`、`诉讼案件管理`）负责。

不引入复杂 BPM 系统。

## 一、统一状态

```text
INTAKE     接案阶段：委托方、对方、事项类型、目标、期限、授权范围与利益冲突确认中
ACTIVE     办理中：专业工作推进中
WAITING    等待中：等待用户补充材料、确认、授权或其他输入
REVIEW     复核中：产出进入反向复核或出稿前审查
DELIVERED  已交付：正式交付完成，待结案确认
CLOSED     已结案
```

## 二、每个 Matter 最低维护字段

```text
status        当前状态（上述六选一）
next_action   下一步动作
pending_from  等待对象（用户 / 对方 / 法院 / 仲裁机构 / 行政机关 / 第三方）
deadline      关键期限
owner         主办方（承办律师或团队；由用户配置）
```

写入当前事项系统记录区（`_系统记录/`），与 `matter-workspace-protocol.md` 的双路径结构保持一致。不要求新建独立数据库或台账系统。

## 三、状态流转规则

- 新正式事项经 `intake-conflict-protocol.md` 确认后建档，状态为 `ACTIVE`。
- 任务完成但需要用户确认、补充材料或授权时，状态转 `WAITING`，并写明 `pending_from` 与 `next_action`。
- 进入反向复核或出稿前审查时，状态转 `REVIEW`。
- 正式交付完成（过完对应交付硬闸门）后，状态转 `DELIVERED`。
- 用户确认结案后，状态转 `CLOSED`，由 `结案归档` 专业 Skill 完成归档。
- 简单咨询、知识问答不建档，不使用本协议。

## 四、更新纪律

- 每次任务结束或状态变化时，更新 `status` / `next_action` / `pending_from` / `deadline`。
- 状态词必须用大写原文（INTAKE / ACTIVE / WAITING / REVIEW / DELIVERED / CLOSED），不得改写。
- 状态与专业 Skill 的状态链（如劳动争议诉讼的状态链定义表）可以并存；专业 Skill 的细分状态映射到本协议的六种统一状态，不得互相矛盾。
