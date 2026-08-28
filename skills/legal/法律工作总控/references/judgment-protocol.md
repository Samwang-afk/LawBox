# 裁决协议

Judgment 不是摘要。它负责对 competing hypotheses 做裁决，并签发起草许可。仅对 L2/L3 强制。

可执行参照实现：`skills/legal/法律工作总控/scripts/reasoning_control.py judge` 和 `qa`。

## 一、输入

- Matter Model（facts/issues/legal_relationships/law/evidence/procedural）；
- Advocate 论证；
- Challenger 检查结果与 failure_conditions；
- 用户澄清回答与确认记录。

## 二、输出结构

```yaml
judgment:
  issue:

  competing_positions:
    - position:
      support:
      weakness:

  conclusion:

  status:
    supported | provisionally_supported | uncertain | unsupported | blocked

  confidence:
    level: high | medium | low
    reasons: []

  decisive_facts: []
  decisive_evidence: []
  decisive_law: []
  strongest_counterargument: []
  failure_conditions: []
  unresolved: []
  next_best_action: []

  drafting_permission: PASS | CONDITIONAL | BLOCKED

  assumptions: []
```

## 三、Confidence 规则

禁止虚构 `87.3%` 之类无依据数字。默认使用 HIGH / MEDIUM / LOW 并附理由。

```text
confidence 是 epistemic confidence（现有证据与推理对结论的支持程度），
不是胜诉概率。
```

- HIGH：决定性事实均为 CONFIRMED，要件均有证据支持，无可辩驳的相反解释；
- MEDIUM：结论成立但存在已披露的薄弱环节或需补强的证据；
- LOW：竞争性解释无法排除或关键环节仅有 ASSERTED 支持。

## 四、裁决顺序

```text
Facts → Issues → Analysis → Advocate → Challenger → Judgment → Decision Freeze → Drafting
```

必须避免"先写起诉状再反思"。Judgment 必须发生在正式起草之前。

## 五、起草许可

### PASS

已有充分事实基础和分析基础，可以进入正式业务起草。

### CONDITIONAL

可以继续形成内部草稿或带条件文稿，但必须明确标识：假设、用户主张、未确认事实、待补证据。不得悄悄把不确定信息写成确定事实。

### BLOCKED

关键事实 / 证据 / 法律关系 / 授权 / 程序问题仍未解决，正式起草可能导致实质错误。此时返回 `Clarification` / `Evidence` / `Research` / `Professional Analysis` 中的相应环节。

派生规则：

```text
1. Challenger 输出无效（泛化风险表述、无 failure_conditions）→ BLOCKED，重跑 Challenger；
2. 存在 materiality=critical 的未解决 unknown → 默认 BLOCKED；
   用户明确要求条件性内部草稿 → CONDITIONAL（条件与假设必须显式列明）；
3. 存在未缓解的 fatal failure condition → 默认 BLOCKED；
   用户明确要求条件性内部草稿 → CONDITIONAL；
4. 存在 fatal（已缓解）或 high failure condition → CONDITIONAL；
5. 其余 → PASS；存在需标注假设时仍为 CONDITIONAL。
```

## 六、Decision Freeze 与起草契约

- Judgment 完成后进入 Decision Freeze。
- 正式文书 Skill 不得自行推翻已形成的 Judgment；起草阶段只负责 expression。
- 起草中出现新材料或重大矛盾：重新打开 Matter Model → 重新分析 → 必要时重新 Judgment；禁止静默修改结论。
- 正式文书 Skill 在生成"事实与理由""诉讼请求"或关键法律论证正文前，必须检查 `drafting_permission`：
  - BLOCKED：停止起草，返回对应环节；
  - CONDITIONAL：显式标识假设/主张/未确认事实/待补证据；
  - PASS：正常起草。
- 交付质量门不因 Judgment PASS 而豁免：`法律文书出稿前审查`、`法律文书模板与导出`、`health_check` 继续强制运行。

## 七、Reasoning QA（与交付 QA 分离）

Reasoning QA 在 Judgment 阶段执行，检查：

1. 事实状态是否混淆（ASSERTED 写成 CONFIRMED）；
2. 关键争点是否漏掉；
3. 是否存在未暴露假设；
4. 是否考虑相反解释；
5. 举证责任是否正确分配；
6. 关键证据是否真的支持结论；
7. 结论是否超过证据；
8. 是否存在程序障碍（时效/管辖/主体）。

Delivery QA（格式、DOCX、模板、引用、内容完整性、交付版本、文件健康）继续由 `法律文书出稿前审查` 与 `法律文书模板与导出` 处理。两者不得合并成同一个模糊的 "review"。

Reasoning QA 发现 P0 问题时，不得签发 PASS。

## 八、记录

L3 的 Judgment 写入系统记录区 `推理记录/judgment.md`；L2 可在 `推理记录/matter-model.md` 的 `judgment` 段落记录，至少包含结论、状态、置信度、failure_conditions 与起草许可。推理记录不得交付客户，不得写入正式文书。
