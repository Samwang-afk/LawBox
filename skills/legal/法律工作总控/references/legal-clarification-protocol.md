# 法律澄清协议

本协议控制"什么时候问用户、问什么、问几个"。核心原则：

> **Missing Information ≠ Blocking Unknown**

不得因为信息缺失就问用户。只有当缺失信息可能改变以下任一内容时，才考虑提问：

```text
法律关系 / 请求权基础 / 法律要件 / 诉请 / 抗辩 / 举证责任 /
事实评价 / 证据评价 / 当事人法律身份 / 时效 / 管辖 / 金额 / 期限 /
程序路径 / 授权范围 / 合同审查立场 / 重大风险判断 / 不可逆行为 /
最终正式交付内容
```

可执行参照实现：`skills/legal/法律工作总控/scripts/reasoning_control.py clarify`。

## 一、提问前必须先自行获取

向用户提问前，Agent 必须依次检查：

1. 当前对话上下文；
2. `_系统记录/当前事项.md` 与当前事项系统记录区（`事件记录.md`、`材料清单.md`、`事实时间线.md`、`缺口归档.md`、`工作笔记.md` 等）；
3. 业务文件区中用户已上传的材料；
4. 已读取文件、证据、表格、合同（结合 `document-reading-protocol.md` 的读取复查摘要）；
5. 法律数据库/法规案例检索结果、Wiki、网页检索结果；
6. 其他已获得上下文。

能从现有材料确定的信息，不得再问用户。凡判定为 `from_material` 或 `search` 的 unknown，先执行读取或检索，再评估是否仍需要问。

## 二、Blocking Unknown 结构

```yaml
unknown:
  question: 款项性质是什么
  fact: 2025-03-01 甲向乙转账 20 万元

  possible_values: [借款, 投资, 货款, 垫付, 其他]

  affects:
    - legal_relationship
    - cause_of_action
    - evidence_requirement

  materiality: critical

  resolution: from_material | search | ask_user | assumption_allowed

  status: open | resolved

  depends_on: 可选，本问题是否有赖于另一 unknown 先解决
```

只有同时满足：

```text
decision-relevant（可能改变法律关系/请求权/要件/诉请/抗辩/举证责任/程序路径/交付内容）
+
无法通过现有信息解决（from_material/search 已穷尽或不可行）
```

才进入 `ask_user`。

materiality 定级：

- `critical`：答案直接改变法律关系或请求权选择；
- `high`：改变诉请/抗辩/要件评价；
- `medium`：改变证据安排或风险提示；
- `low`：只影响表述或补充说明。

`medium`、`low` 默认不阻塞、不提问，写入缺口归档并继续。

## 三、Question Budget

- 单轮原则上 1–5 个问题。
- 排序：Decision-changing > Scope-changing > Evidence-changing > Output-changing > Formatting。
- 如果问题 A 的答案会使问题 B/C/D 失去意义，则本轮只问 A。
- 优先多选、简短事实问题、可直接回答的问题；每个问题带"不确定"选项。
- 不得机械问卷化。

## 四、用户回答后的重新推理

澄清不是问完就结束。用户回答后必须：

```text
更新 Matter Model
→ 重新检查法律关系的候选与 current_view
→ 重新检查受影响 Issues
→ 重新检查推理等级是否需要升级
→ 重做受影响的分析部分
```

示例：用户最初说"他欠我20万元"，系统假设可能是借贷；用户随后回答"这是让我入股的钱"时，必须 REOPEN 法律关系，不得继续沿用民间借贷假设。

## 五、允许假设的边界

`assumption_allowed` 仅用于：

- materiality 为 medium/low；
- 或用户明确授权"按假设继续"；
- 假设必须显式记录在 Matter Model 的 `inferred` 或 `unknown.assumption` 中，并在交付说明中披露。

关键法律关系、请求权基础、授权、金额、期限、不可逆行为不得假设。

## 六、与既有确认机制的衔接

- 合同审查立场确认继续按 `contract-workflow-protocol.md` 第 0 节执行，本协议不替代。
- 金额、期限、诉请、授权等会改变最终交付的选择，除本协议外仍需写入 `用户确认记录`（`法律文书出稿前审查` 的 `required_confirmations` 继续生效）。
