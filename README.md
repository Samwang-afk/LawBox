<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/lawbox-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/lawbox-light.svg">
  <img width="100%" alt="LawBox" src="assets/lawbox-light.svg" />
</picture>

### 一个法律技能，覆盖完整法律工作流。

万物皆插件，越做越聪明的自我进化法律技能内核与框架，同时配备ludus轻量推理增强。

<p align="center">
  <img
    src="assets/lawbox-top10-cn-legal-skills.svg"
    alt="Top 10 CN Legal Skills"
  />
</p>

[![核心](https://img.shields.io/badge/核心-v1.0.0-7f1d1d)](#)
[![法律技能](https://img.shields.io/badge/法律技能-58-374151)](#)
[![许可](https://img.shields.io/badge/许可-PolyForm%20NC%201.0.0-374151)](LICENSE)

</div>

> **LawBox 不教 AI“像律师一样说话”，而是让智能体按法律工作的方式做事。**

AI 已经会写合同、总结案情、找法条、生成文书。

真正耗费时间的，往往是回答之后的工作：核对事实与法源、判断风险等级、把修改意见逐条写回合同、准备谈判回退方案、整理成 Word 或报告，再经过专业人员复核、流转与归档。

一段看起来不错的回答，距离一份可以提交、流转和真正使用的法律成果，中间还隔着完整的工作流程。

LawBox 把法律工作中最容易被模型跳过的部分——**澄清、事实状态、法律核验、反向复核、授权边界与交付质量**——变成智能体可以执行的工作协议。

**内置 58 个技能，可以随意添加，而不与 SOP 冲突。**  

---

## 一个法律技能，就够了

LawBox 的目标不是成为第 59 个 Legal Skill，而是替代“一个任务安装一个 Skill”的使用方式。

合同审查、诉讼分析、法律检索、文书起草、合规审核等通用法律工作，都从同一个入口进入；你不需要先学习几十个技能，再决定该调用哪一个。

```text
你
│
▼
LawBox
│
├─ 理解任务
├─ 判断风险与所需推理深度
├─ 只追问真正会改变结论的问题
├─ 路由专业法律能力
├─ 核验关键法律来源
├─ 反向复核当前结论
└─ 控制正式交付与外部动作
│
▼
法律工作成果
```

仓库根目录 [`SKILL.md`](SKILL.md) 提供统一入口；[`法律工作总控`](skills/legal/法律工作总控/SKILL.md) 负责路由与共享协议。

**复杂性应该留在系统内部，而不是留给使用者。**

### 58 个内置技能

| 01–10 | 11–20 | 21–30 | 31–40 | 41–50 | 51–58 |
| --- | --- | --- | --- | --- | --- |
| 法律工作总控 | 立案管理 | 案件沟通记录 | 简易速裁程序 | 产品法务 | 破产清算 |
| 法律文书出稿前审查 | 诉讼文书起草 | 案件讨论与提纲 | 特殊程序 | 广告合规审核 | 破产和解程序 |
| 法律文书模板与导出 | 调查取证与证据管理 | 刑事辩护总调度 | 劳动争议诉讼 | 预包装食品标签合规 | 破产法律分析 |
| 案件材料生成专业文档 | 庭前准备 | 案件承接与委托 | 劳动争议仲裁程序管理 | 监管合规监测 | 破产文书生成 |
| 法律咨询助手 | 庭审与庭后工作 | 侦查阶段辩护 | 劳动争议证据体系 | 破产申请与受理 | 审理报告 |
| 初步法律分析 | 调解与和解 | 审查起诉阶段辩护 | 劳动关系认定与经济补偿计算 | 管理人工作 | 民事判决书 |
| 法规案例检索 | 结案归档 | 一审阶段辩护 | 用人单位劳动合规 | 债权申报与审查 | 法律文本转 Markdown |
| 法律 Wiki 知识库查询 | 诉讼案件管理 | 二审阶段辩护 | 合同审查 | 债权人会议 | 微信文章转 Markdown |
| 法律文章去 AI 味道 | 诉讼分析工具 | 未成年人案件 | 合同起草 | 财产调查与管理 |  |
| 民事一审诉讼 | 诉讼可视化 | 死刑案件 | 委托合同管理 | 重整程序 |  |

---

## 在相信一个结论之前，先尝试推翻它

普通智能体往往是：

```text
问题 → 推理 → 答案
```

LawBox 在复杂事项中多一步：

```text
问题 → 推理 → 反向复核 → 裁决 → 起草
```

这来自 LawBox 中的轻量 **Ludus 对抗式复核**。

它不是为了机械生成“正方 / 反方”，也不是多智能体表演。

它只做一件事：**证伪**。

> 用户对法律关系的命名可能错吗？  
> 有没有另一套合理事实解释？  
> 对方最强的抗辩是什么？  
> 哪个事实、证据或法律要件一旦失败，结论就会倒塌？

复核最终要找到具体的**最小失败条件集合**，而不是一句“仍存在一定风险”。

简单问题不会被强行做重。LawBox 按 L0–L3 选择满足风险的最低充分推理等级。

**只使用足以覆盖当前风险的最小工作流。**

Skill内部使用的Gray Arch：

<img width="1672" height="941" alt="图片" src="https://github.com/user-attachments/assets/33488d57-e9d9-4377-be42-3ecaca9a7f83" />

---

## 万物皆插件

**核心只定义一件事：法律工作应该如何被完成。**

除核心工作协议外，专业知识、领域规则、模板、工具和组织经验都可以作为插件接入。

```text
LawBox Core
│
├─ Clarification
├─ Fact State
├─ Legal Verification
├─ Risk Control
├─ Ludus Review
├─ Authorization
└─ Delivery
    │
    ├── IP Law Plugin
    ├── Data & Privacy Plugin
    ├── Capital Markets Plugin
    ├── Cross-border Plugin
    └── Your Firm Plugin
```

在通用法律工作中，LawBox 可以直接替代传统 Legal Skills 的组合使用；进入知识产权、数据与隐私、证券与资本市场、跨境交易等高度专业领域时，只需要把对应能力作为插件插入。

插件负责增加这个领域需要的**知识、规则、模板和专业方法**，并继承 LawBox 已有的澄清、事实状态、法律核验、反向复核、授权与交付协议。

它扩展 LawBox **能做什么**，但不重新定义 LawBox **如何完成法律工作**。

因此，增加一个专业领域不需要复制一套新的 SOP，也不会让不同 Skill 各自携带互相冲突的提示词、风险标准和交付流程。

律所自己的模板、审查方法、内部标准和专业经验同样可以作为私有插件挂载，而无需侵入核心。

仓库已提供 [`packs/ip-law/`](packs/ip-law/) 作为插件包结构示例；当前仅为骨架，不包含完整知识产权法律内容。

**One core workflow. Any legal domain as a plugin.**

---

## 实际使用是什么感觉

### 诉讼

```text
“这是客户发来的微信、借条和转账记录。
帮我判断现在起诉最大的风险是什么。”
```

LawBox 不会直接给一个胜诉率。

它会先区分已确认事实、当事人陈述、争议事实与未知信息，再检查证据、法律关系与请求权基础；如果属于复杂事项，再主动寻找最可能推翻当前判断的路径。

### 合同审查

```text
“我是乙方，帮我审这份 SaaS 服务合同。”
```

LawBox 先确认立场，再进入专业合同审查；需要正式 Word 交付时，继续经过预审、导出与质量检查，而不是把“内容生成完成”当作“法律工作完成”。

---

## 架构

```text
用户
 │
 ▼
LawBox / 法律工作操作系统
 │
 ├─ 任务路由
 ├─ 事项与事实模型
 ├─ 最小必要澄清
 ├─ 法律来源核验
 ├─ 专业法律技能
 ├─ Ludus 反向复核
 ├─ 授权门
 └─ 交付质检
 │
 ▼
法律工作成果
```

关键协议位于 [`skills/legal/法律工作总控/references/`](skills/legal/法律工作总控/references/)。

测试入口：

```bash
python tests/run_all_tests.py
```

---

## 安装

```bash
git clone https://github.com/Samwang-afk/LawBox.git
```

将 `skills/legal/` 接入支持本地 Markdown 技能的智能体环境，或使用仓库中的 `.codex-plugin/plugin.json`。

然后直接描述你的法律任务。

不是：

```text
“我要先调用哪个技能？”
```

而是：

```text
“帮我处理这个案子。”
```

---

## 专业边界

LawBox 是法律工作辅助系统，不是“AI 律师”。

真实法律事项仍需要律师、法务或具备相应资格的专业人士完成事实判断、来源核验、策略选择、客户授权与最终文本复核。组织级利益冲突检索、商业数据库、外部系统写入等能力如果没有真实连接，LawBox 会明确标记未执行，而不是假装完成。

---

## 许可与归属

当前项目维护者拥有版权的新创作内容采用 [PolyForm Noncommercial License 1.0.0](LICENSE)。

本项目包含或衍生自 [`pa1nrui1/legal-skills`](https://github.com/pa1nrui1/legal-skills) 的 MIT 授权内容；相关上游权利、中间分支必要声明与其他第三方说明见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 和 [`LICENSES/`](LICENSES/)。

---

<div align="center">

**LawBox 负责把工作跑起来。**  
**Ludus 负责挑战结论。**  
**其余一切，皆可插件化。**

</div>
