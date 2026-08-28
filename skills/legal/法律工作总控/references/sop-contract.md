# SOP Contract

完整业务 SOP 应尽量能回答以下七项。不要求 30 字段 schema，不强制重写现有 Skill；新增 SOP 遵循本 contract，现有核心 Skill 明显缺某项时补最小内容即可。

```text
WHEN     什么时候使用？
         触发条件与不适用场景（简单任务不得被本 SOP 复杂化）。

INPUT    需要什么？
         材料、上下文、前置协议、授权范围。

DO       怎么做？
         最短充分执行步骤。

DECIDE   哪里存在分支判断？
         分支条件与选择依据；出现多种可能时如何选择。

APPROVE  哪里必须人工确认？
         必须经过用户/律师确认才能继续的动作或结论。

OUTPUT   产出什么？
         成果类型（草稿 / 内部报告 / 正式材料 / Word 正式交付物等）与命名、路径、来源披露要求。

CLOSE    什么时候算完成？
         完成标准与验证方式：必须实际可验证（材料读取、来源校验、交付检查等），
         不得因"步骤执行完了"就声称完成。
```

## 与总控共享协议的分工

- 总控共享协议回答横向问题：是否应该做（Clarification / Conflict）、有没有想错（Ludus Review）、能不能执行（Action Gate）、什么时候完成（Lifecycle）。
- 专业 SOP 只回答"这类法律工作具体怎么做"。
- 专业 SOP 不得自行重新实现 Clarification、Conflict、Adversarial Review、Reflection、Approval 等总控协议。

## Domain Pack 挂载约定（万物皆插件）

专业领域扩展（IP、M&A、税务、证券、数据隐私等）以 Domain Pack 形式挂载，不修改 Core：

- 位置：`packs/<pack-id>/`，自带 `pack.json` 清单与 `skills/` 目录。
- 清单最小字段：`id / name / version / description / skills_dir / routes`。
- 安装：把 pack 目录放入 `packs/`，将其 `routes` 追加到总控 `routing-map.md`（写入前需用户确认）。
- 启用规则：pack 内 Skill 自动继承总控全部共享协议（澄清、复核、授权、生命周期、反思、交付门）；pack 只写专业内容，不得重新实现总控协议。
- 卸载：删除目录并移除对应路由条目。
- Core 不包含 pack 运行时加载器；pack 是"目录 + 清单 + 路由条目"的约定，不是新框架。
