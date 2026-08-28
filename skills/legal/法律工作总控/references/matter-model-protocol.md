# 事项模型协议

Matter Model 是整个推理体系的知识窄腰：所有 L1–L3 案件型任务围绕同一套事实与争点模型工作，不同专业 Skill 读取和更新同一个 Matter Model。禁止形成多个互相冲突、无人维护的案件事实副本。

可执行参照实现：`skills/legal/法律工作总控/scripts/reasoning_control.py validate`（schema 与认知状态校验）。

## 一、知识沙漏

```text
RAW INPUT
├── 用户陈述 / 案件文件 / 合同 / 证据
├── 时间线 / 法规 / 案例 / 程序信息
        │
        ▼
    CONTEXT（读取与抽取）
        │
        ▼
   MATTER MODEL（窄腰，单一事实源）
        │
        ▼
┌───────┼────────┐
│       │        │
请求权A 请求权B 程序路径
│       │        │
支持    反对     替代解释
└───────┼────────┘
        │
        ▼
    JUDGMENT
```

- 业务 Skill 从 Matter Model 读取事实与争点，不自行重新理解案件。
- 业务 Skill 的分析结论回写 Matter Model（`legal_relationships`、`issues`、`law`、`evidence`、`uncertainties`）。
- `初步法律分析` 的六来源体系、请求权基础 6 步法、要件审判九步法是领域推理；Matter Model 是认知架构。二者不互相取代。

## 二、Canonical Schema

不必每个任务都真实生成完整 JSON，但协议定义 canonical schema；L2/L3 的结构化记录必须覆盖下列字段。

```yaml
matter:
  meta:
    matter_id:
    reasoning_mode:        # L1 | L2 | L3
    procedural_stage:
    last_updated:

  objective:
    user_goal:
    desired_output:
    decision_required:

  parties:
    - name:
      role:
      legal_status:
      source:

  facts:
    confirmed: []   # 见第三节认知状态
    asserted: []
    disputed: []
    inferred: []
    unknown: []

  timeline:            # 与系统记录区 事实时间线.md 保持同一事实源
    - date:
      event:
      source:
      status:          # confirmed | asserted | ...

  legal_relationships:
    candidates: []
    current_view:
    confidence:        # high | medium | low
    competing_view:

  issues:
    - id:
      question:
      candidate_positions: []
      elements: []
      burden_of_proof:
      facts_supporting: []
      facts_against: []
      evidence_supporting: []
      evidence_against: []
      law_supporting: []
      law_against: []
      cases_supporting: []
      cases_against: []
      missing_information: []
      provisional_conclusion:
      confidence:

  evidence:
    - id:
      description:
      source:
      proves:
      limitations:
      authenticity_status:

  law:
    - id:
      authority:
      proposition:
      status:           # verified | unverified
      verified:         # 必须与 法规校验摘要 一致

  procedural:
    jurisdiction:
    limitation:
    preservation:
    deadlines:
    procedure_options:

  strategy:
    options: []
    constraints: []
    tradeoffs: []

  uncertainties: []

  user_confirmations: []

  judgment:            # 仅 L2/L3；见 judgment-protocol.md
    status:
    drafting_permission:
```

## 三、认知状态（强制区分）

任何案件事实必须标注以下状态之一：

```text
CONFIRMED  已由文件/证据/核验记录确定的客观事实（转账记录、合同原文、裁判文书等）
ASSERTED     一方当事人主张但无独立证据支持的事实
DISPUTED     双方立场对立且均未证实的事实
INFERRED     从既有事实推理得到的结论性事实
UNKNOWN      影响决策但尚不清楚的事实
```

绝对禁止：

```text
用户说："他借我20万元"
→ 错误：Agent 写成 "被告向原告借款20万元"
```

正确做法：

```text
ASSERTED:   用户主张款项性质为借款
CONFIRMED: 存在20万元转账（银行流水）
UNKNOWN:    双方是否存在借款合意
```

- `CONFIRMED` 必须绑定来源（文件/证据/核验记录）；仅有用户口述的事实不得标 CONFIRMED。
- `ASSERTED` 必须记录 `asserted_by`。
- `INFERRED` 必须记录 `based_on`。
- 起草文书时不得把 ASSERTED / INFERRED / UNKNOWN 写成无条件事实；确因诉讼立场必须陈述时，使用"当事人主张""原告主张""根据现有材料"等身份表述。

## 四、竞争性假设

Matter Model 允许多个 competing hypothesis 共存：

```text
20万元款项性质：
H1 民间借贷
H2 投资
H3 合作经营垫款
```

- 不得过早 collapse；只有事实、证据、法律足够时才选择 current_view。
- 无法排除竞争性解释时，`legal_relationships.current_view` 保持空缺或标记 low confidence，由 Judgment 保留 UNCERTAIN。
- 用户标签（如"这是借款"）是 ASSERTED 事实，不自动成为 legal_relationship 结论；出现相反材料（如"利润五五分"）时必须保留竞争假设并升级推理等级。

## 五、持久化分级

- L0：不持久化。
- L1：内部工作上下文维护简化 Matter Model；要点写入系统记录区 `工作笔记.md`。
- L2：系统记录区 `推理记录/matter-model.md`。
- L3：系统记录区 `推理记录/matter-model.md`、`review.md`、`judgment.md`。

`推理记录/` 位于当前事项的系统记录区（复用 `matter-workspace-protocol.md` 双路径，不新建根级目录体系），属于内部分析层，不得交付客户。

## 六、与既有记录的衔接（单一事实源）

- `事实时间线.md` 仍是业务侧事实记录；Matter Model 的 `timeline` 与其保持一致，每条事实带状态与来源。两边冲突时以来源证据为准并同步校正。
- `缺口归档.md` 与 Matter Model 的 `unknown` 对应：材料缺口写入缺口归档并提示用户；决策性 unknown 同时进入澄清流程。
- `法规校验摘要` 是 `law.verified` 的唯一依据；`案例检索` 结果写入 `issues.cases_supporting/against` 并标注来源。
- 推理产物（matter-model / review / judgment）与正式文书隔离；不得写入 `draft.html`、`complaint-data.json` 或任何正式交付文件。

## 七、更新纪律

- 新事实、新证据、用户澄清回答：先更新 Matter Model，再决定是否重做受影响分析。
- 业务 Skill 完成后：回写 `legal_relationships`、`issues`、`elements`、`burden_of_proof`、`law`、`evidence`、`uncertainties`。
- 起草过程中出现新材料或重大矛盾：重新打开 Matter Model → 重新分析 → 必要时重新 Judgment；禁止静默修改已冻结结论。
