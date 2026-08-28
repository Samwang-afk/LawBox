# ip-law Domain Pack（示例骨架）

这是"万物皆插件"约定的示例骨架，用于说明 Domain Pack 的最小结构。当前不含实际 IP 法律内容。

## 结构

```text
packs/ip-law/
├── pack.json          # 清单：id/name/version/description/skills_dir/routes
├── README.md          # 本文件
└── skills/            # 放置本 pack 的专业 Skill 目录（每个 Skill 一个子目录 + SKILL.md）
```

## 使用方法

1. 在 `skills/` 下添加专业 Skill（按总控 `sop-contract.md` 的七项 contract 编写）。
2. 把 `pack.json` 中 `routes` 的目标改为真实 Skill 路径（移除 `"example": true`）。
3. 把 routes 追加到 `skills/legal/法律工作总控/references/routing-map.md`（写入前需用户确认）。
4. pack 内 Skill 自动继承总控全部共享协议（澄清 / 反向复核 / 授权 / 生命周期 / 反思 / 交付门），只写专业内容，不得重新实现总控协议。

卸载 = 删除本目录 + 移除 routing-map 中的对应路由条目。

约定全文见 `skills/legal/法律工作总控/references/sop-contract.md` 的"Domain Pack 挂载约定"。
