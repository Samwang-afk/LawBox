# 北大法宝 MCP/API 协议

本文件仅说明监管合规监测中的使用方式。legal 文件夹通用法规核验规则以 `skills/legal/法律工作总控/references/pkulaw-mcp-legal-verification-protocol.md` 为准。

## 接入信息

- 服务地址：`https://apim-gateway.pkulaw.com/mcp-law`
- 连接类型：`streamablehttp`
- 认证方式：Bearer Token 或 API Key
- 凭证规则：只允许从环境变量或本机私有配置读取；不得写入 Skill 正文、归档文件或交付文件。
- 默认本机私有配置：`【法规检索凭证配置文件】`，权限应为 `600`。
- 跑通状态：已跑通，2026-05-17 使用 Token 认证成功调用 `get_law_list`。

## get_law_list

用途：查询法规列表，通过标题或正文关键词精确匹配法规，返回前 10 条结果。

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| title | string | 否* | 标题关键词 |
| fulltext | string | 否* | 正文关键词 |

`title` 和 `fulltext` 至少填写一个。

返回字段：

| 字段 | 说明 |
|---|---|
| Gid | 法规唯一标识 |
| Title | 法规标题 |
| DocumentNO | 发文字号 |
| Category | 法规分类 |
| SpecialType | 特殊类型标识 |
| EffectivenessDic | 效力级别 |
| ImplementDate | 实施日期 |
| IssueDate | 发布日期 |
| IssueDepartment | 发布机关 |
| TimelinessDic | 时效性：01=现行有效，02=废止或失效，03=已被修改 |
| FullText | 全文内容，列表接口通常为 null |
| Url | 北大法宝详情链接 |

## 使用定位

`get_law_list` 是法规检索与核验接口，不是唯一监管更新发现接口。

适用：
- 用户指定主题/行业时检索相关法规。
- 官方源抓到新规后，用标题反查北大法宝记录。
- 客户文件引用某法规时，核验法规名称、发文机关、发布日期、时效性。
- 做合规缺口核查时，补充适用规则清单。

限制：
- 未提供明确日期范围或更新时间筛选参数。
- 默认只返回前 10 条，宽泛关键词可能遗漏。
- 不能直接承诺“最近 7 天全部更新”。

## 本地脚本

```bash
node skills/legal/法律工作总控/scripts/pkulaw_get_law_list.mjs --title "数据安全" --fulltext "个人信息"
```

脚本输出 JSON，不保存凭证。
