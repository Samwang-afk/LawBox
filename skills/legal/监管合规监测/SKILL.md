---
name: 监管合规监测
description: 中国境内重点监管动态监测与客户合规影响评估 Skill。用于监管动态、新规更新、政策变化、行业监管、法规政策分级、客户合规缺口核查、政策制度修改建议、整改清单、监管合规简报等任务。适用于用户要求监测某行业、某客户、某产品或某主题的法律法规、监管政策、部门规章、规范性文件、征求意见稿、执法动态，并判断新规要求、客户现有合规文件缺口和整改方案。
---


## 法律工作总控规则（强制）

执行本 Skill 前，必须先遵循：
- skills/legal/法律工作总控/references/practice-profile.md
- skills/legal/法律工作总控/references/matter-workspace-protocol.md
- skills/legal/法律工作总控/references/document-reading-protocol.md
- skills/legal/法律工作总控/references/source-boundary-protocol.md
- skills/legal/法律工作总控/references/ocr-correction-protocol.md
- skills/legal/法律工作总控/references/pkulaw-mcp-legal-verification-protocol.md
- skills/legal/法律工作总控/references/output-header-template.md

本 Skill 只处理中国境内法律、法规、规章、规范性文件、监管政策和监管动态。不得承诺全量、无遗漏、永久稳定监测；必须披露监测范围、成功来源、失败来源、未覆盖来源和核验状态。

# 监管合规监测

本 Skill 用于“重点监管动态监测与客户合规影响评估”，核心链路：

```text
确定行业/客户/产品/主题
  -> 官方公开源发现更新
  -> 北大法宝或其他数据库核验法规信息
  -> L0-L4 分级
  -> 读取客户现有合规文件
  -> 输出缺口、整改建议和政策修改稿
  -> 归档并衔接产品法务/劳动合规/合同审查等模块
```

## 启动询问（强制）

开始前必须确认：

- 监测对象：行业、具体客户、具体产品/业务线，还是单一主题。
- 行业/主题：数据合规、广告、金融、医疗、食品、劳动、AI、平台、电商、消费者权益等。
- 客户画像：客户名称、主营业务、地区、产品/服务、目标用户、业务模式。
- 监管地域：全国，还是吉林/广东/长春/深圳等特定地区。
- 监测期间：本周、本月、最近 90 天、指定日期后，或指定法规发布后。
- 客户现有合规文件路径：制度、隐私政策、用户协议、广告规则、合同模板、员工手册、流程图、培训记录、备案/许可材料等。
- 输出目的：内部简报、客户报告、整改清单、政策修改稿、正式法律意见。

用户只要求做行业测试或演示时，可以自行选择一个主题并说明假设；不得把测试结果包装成正式合规意见。

## 按需读取参考文件

- 启动询问：读取 [references/intake-questions.md](references/intake-questions.md)。
- 来源和接入边界：读取 [references/source-and-connector-protocol.md](references/source-and-connector-protocol.md)。
- 北大法宝 MCP/API：读取 [references/pkulaw-mcp-protocol.md](references/pkulaw-mcp-protocol.md)。
- 官方来源清单：读取 [references/official-source-watchlist.md](references/official-source-watchlist.md)。
- 监管分级：读取 [references/regulatory-classification.md](references/regulatory-classification.md)。
- 客户缺口核查：读取 [references/client-gap-assessment.md](references/client-gap-assessment.md)。
- 政策修改建议：读取 [references/policy-amendment-template.md](references/policy-amendment-template.md)。
- 报告模板：读取 [references/report-templates.md](references/report-templates.md)。

## 北大法宝接入

北大法宝 `get_law_list` 用作法规检索与核验层，不作为唯一更新发现层。

使用规则：
- API Key 或 Bearer Token 只能从环境变量或本机私有配置读取，不得写入 Skill 正文、归档或交付文件。
- 默认本机私有配置路径：`【法规检索凭证配置文件】`。
- 返回结果中的 `Gid`、`Title`、`DocumentNO`、`IssueDate`、`ImplementDate`、`IssueDepartment`、`TimelinessDic`、`Url` 写入核验记录。
- 如接口只支持关键词且默认前 10 条，应标注“非全量检索”，不得称为完整监管更新监测。

可使用脚本：

```bash
node scripts/pkulaw_get_law_list.mjs --title "个人信息保护" --fulltext "个人信息"
```

## 输出底线

不用模型记忆替代法律法规核验。

所有正式输出前必须先给出：

```markdown
## 输出说明
- 已监测来源：
- 成功核验来源：
- 未覆盖/失败来源：
- 北大法宝核验状态：
- 已读取客户材料：
- 未读取/缺失客户材料：
- 需要客户判断事项：
- 输出边界：
```

## 跨 Skill 衔接

- 影响产品功能、隐私、默认开启、上线流程的，联动 `产品法务`。
- 影响广告、营销文案、客户案例的，联动 `广告合规审核`。
- 影响劳动制度、员工手册、工资工时的，联动 `用人单位劳动合规`。
- 影响合同条款、用户协议、服务协议的，联动 `合同审查`。
- 影响行政处罚、诉讼或争议处理的，联动 `民事一审诉讼`。

读取其他模块档案时，必须标注“来源于产品法务档案”“来源于劳动合规档案”“来源于合同审查记录”等。

## 归档要求

涉及具体行业、客户或产品时，按总控事项工作区协议使用：

- 业务文件区：`【自定义工作目录】/监管合规/<行业或企业客户>/`
- 系统记录区：`【自定义工作目录】/_系统记录/监管合规/<行业或企业客户>/`

收到材料、完成抓取、完成北大法宝核验、形成法规政策卡片、发现客户缺口、提出整改建议或完成政策修改稿时，必须同步更新系统记录区对应记录。
