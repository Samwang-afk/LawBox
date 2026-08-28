# Redline Plan 协议

本协议规定合同审核修订稿的中间数据格式。业务 Skill 负责形成法律判断和审查问题；红线执行器只按 `redline-plan.json` 在 DOCX 中落批注、修订痕迹并生成执行日志。

## 目录

- 一、文件位置
- 二、Plan 结构
- 三、字段规则
- 四、审查人、上线期和 Doc 路径
- 五、动作分流规则
- 六、解析方式
- 七、执行命令
- 八、执行后检查

## 一、文件位置

推荐保存位置：

```text
业务文件区：
合同/<客户或项目>/<合同编号-合同简称>/02-工作版本/
  <合同编号>_审核修订稿.docx

系统记录区：
_系统记录/合同/<客户或项目>/<合同编号-合同简称>/
  redline-plan.json
  redline-execution-log.json
  redline-qa-report.md
```

原合同必须保留在 `01-客户材料/` 或用户原始提交位置，不得覆盖。

## 二、Plan 结构

```json
{
  "meta": {
    "contract_id": "客户-合同关键词-01",
    "contract_name": "合同名称",
    "client_name": "客户名称",
    "reviewer": "【律师姓名】",
    "reviewer_organization": "【律所名称】",
    "reviewer_contact": "【联系电话】 / 【电子邮箱】",
    "party_role": "甲方 / 乙方 / 中立 / 其他",
    "party_role_confirmed": true,
    "party_role_confirmation_source": "用户确认：YYYY-MM-DD 对话",
    "review_intensity": "克制 / 常规 / 强势",
    "edit_policy": "balanced",
    "review_deadline": "2026-06-30 18:00",
    "business_launch_date": "如涉及上线、投放、签署或履行节点，在此填写",
    "source_docx": "原合同路径",
    "matter_path": "事项路径",
    "system_record_path": "系统记录路径"
  },
  "summary": {
    "contract_type": "服务合同",
    "contract_amount": "未提及/待补充",
    "contract_term": "未提及/待补充",
    "business_overview": "合同交易结构摘要",
    "key_milestones": [
      "合同生效",
      "交付/验收/付款/上线节点"
    ],
    "formal_opinion_path": "审查意见书或飞书审查报告路径"
  },
  "findings": [
    {
      "id": "Q001",
      "handling_advice": "必须修改",
      "internal_priority": "P0",
      "clause": "第5条第2款",
      "original_text": "甲方验收合格后支付尾款。",
      "issue": "验收标准不明确",
      "legal_risk": "验收标准、期限和异议机制缺失，可能导致尾款支付条件争议。",
      "business_risk": "服务方可能已完成工作但尾款长期无法回收。",
      "action": "replace",
      "target_text": "甲方验收合格后支付尾款。",
      "replacement_text": "甲方应在收到乙方提交的交付成果及完整验收资料后5个工作日内完成验收。验收标准以本合同附件一《服务成果验收标准》为准。甲方认为不合格的，应在验收期内一次性书面列明不合格事项及依据；乙方完成整改后，甲方应在3个工作日内复验。甲方逾期未提出书面异议的，视为验收合格。",
      "comment": "建议补充验收标准、验收期限、书面异议和逾期视为验收合格规则。",
      "comment_required": true,
      "source": "合同原文第5条第2款"
    }
  ]
}
```

## 三、字段规则

- `id`：必须稳定唯一，建议与问题卡编号一致。
- `handling_advice`：只使用 `必须修改 / 建议修改 / 需客户确认 / 可优化`。
- `internal_priority`：内部排序字段，可用 `P0 / P1 / P2`，不得进入客户正式问题卡正文。
- `original_text`：用于记录完整条款原文、审查对象和上下文，可以是完整段落。
- `target_text`：用于定位原合同中实际要删除或替换的最小文本；不得把完整条款原文直接复制为 `target_text`，除非整段确需废止重写并显式标记 `allow_full_paragraph_replace=true`。
- `replacement_text`：`replace` 或 `insert` 的落文文本。
- `comment`：写入 Word 批注的短文本；未提供时执行器可根据问题字段生成。
- `comment_required`：直接修订后仍需保留解释性批注时设为 `true`；轻微错字、编号、术语统一等确定性修订通常不设置。
- `allow_full_paragraph_replace`：仅在整段条款确需整体删除重写时使用；必须同步说明原因。默认不得使用。
- `allow_unconfirmed_revision`：仅在用户明确授权可把待补事实、占位项或需确认事项直接落入正文时使用。默认转为批注。
- `allow_direct_revision`：仅在 `handling_advice=可优化` 但用户明确要求正文直接优化时使用。默认 `report-only`。
- `occurrence`：同一 `target_text` 出现多次时，从 1 开始指定第几处。
- `selector.contains`：可替代 `target_text`，用于定位包含某段文字的段落。
- `selector.paragraph_index`：从 1 开始指定段落序号；用于 `target_text` 重复出现且段落位置已知的场景。
- `report-only` 项仍应写入 plan，以便审查意见书和执行日志保持一致。

## 四、审查人、上线期和 Doc 路径

生成 `redline-plan.json` 前，必须把以下信息固定在 `meta` 或 `summary` 中：

1. 审查人信息：默认使用【律师姓名】、【律所名称】、【联系电话】、【电子邮箱】；用户另行指定时以本次确认记录为准。
2. 审查立场：必须来自用户明确确认，写入 `party_role`、`party_role_confirmed=true` 和 `party_role_confirmation_source`。未确认时不得生成 redline-plan，也不得执行红线稿；不得写成 `待补充` 后继续执行。
3. 审查时限：用户给出截止时间、签署时间、上线期、投放期或履行启动期时，写入 `review_deadline` 或 `business_launch_date`；没有则写 `未提及/待补充`。
4. 文档路径：`source_docx` 指向原合同；`formal_opinion_path` 指向飞书审查报告、审查意见书或本地意见稿；`output_docx` 在执行日志中生成，不写回原合同。
5. 路径边界：红线稿、执行日志和 QA 报告属于修订执行链路；正式审查意见书仍按法律工作总控和法律文书模板与导出链路处理。

## 五、动作分流规则

执行器处理 `action=auto` 时，按以下顺序判断：

1. 留空、占位、待补事实、需客户确认：`comment`。
2. `handling_advice=可优化`：`report-only`。
3. 有 `replacement_text` 且属于确定性改文：`replace`。
4. `handling_advice=必须修改` 且改文明确：`replace`。
5. 其他情形：`comment`。

即使 `action` 被手动写成 `replace` / `insert` / `delete`，执行器也应执行以下保护：

- 涉及留空、占位、待补事实或 `handling_advice=需客户确认` 的，除非 `allow_unconfirmed_revision=true`，否则降级为 `comment`。
- `handling_advice=可优化` 的，除非 `allow_direct_revision=true`，否则降级为 `report-only`。
- `target_text` 命中内容接近完整段落且未设置 `allow_full_paragraph_replace=true` 的，执行失败并提示拆成局部修改。

若定位不唯一且未提供 `occurrence`，执行器必须失败该项并写入日志，不得静默修改第一处。

## 六、解析方式

解析合同时，按以下顺序把审查结论转为 `redline-plan.json`：

1. 从合同原文抽取段落文本，优先保留完整条款号、条款名和原文摘录。
2. 将飞书问题卡或本地 `审查问题清单.md` 的每个问题映射为一个 `finding`，保持问题编号稳定一致。
3. 对每项问题先判断 `handling_advice`，再按 `references/修订策略.md` 选择 `action`。
4. 对正文修订项填写最小粒度 `target_text` 和 `replacement_text`；完整条款原文只放入 `original_text`。例如只改“律师费”为“律师服务费”时，`target_text` 只能写“律师费”，不得写完整付款条款。
5. 对留空、事实缺口、商业授权不明、需客户判断事项，使用 `comment`，不直接替客户落文。
6. 对纯格式或低必要性优化，使用 `report-only`，只进入审查意见书或飞书问题卡。
7. 对重大直接修订，设置 `comment_required=true` 或显式提供 `comment`；轻微确定性修订通常只留修订痕迹。
8. 生成后必须运行红线 QA；如出现整段替换、长文本删除插入或红线噪音过高，必须拆分为局部修改或改为批注后重新生成。

## 七、执行命令

```bash
python scripts/redline/apply_redline_plan.py \
  --input 原合同.docx \
  --plan redline-plan.json \
  --output 合同_审核修订稿.docx \
  --log redline-execution-log.json \
  --author "【律师姓名】" \
  --organization "【律所名称】"
```

## 八、执行后检查

执行完成后至少检查：

- `word/settings.xml` 存在 `w:trackRevisions`。
- 需要修订的项目在 `word/document.xml` 中形成 `w:ins` / `w:del`。
- 需要批注的项目存在 `word/comments.xml`、关系文件和正文锚点。
- 执行日志中不存在未披露的 `failed` 项。
- 接受修订后的临时清洁文本已复核关键条款、编号、交叉引用、签署页和附件。
- 红线稿已渲染并逐页检查。
