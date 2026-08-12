# 决策记录（ADR）

只记录已经确认、影响后续工作的非显然决策。追加新条目，不重写历史；决策被替代时，新条目通过“替代”字段引用旧编号。

每条结构：`## NNN 标题（YYYY-MM-DD）`，下接 `- 背景` / `- 选项` / `- 结论` / `- 替代` 四项；替代填旧编号，无则写「无」。

## 001 fork 改名 md_kx，插件协议随包名同步（2026-08-12）

- 背景：本仓库 fork 自 hukkin/mdformat，需改名为 md_kx（包名、CLI 命令、配置文件名均改，避免与 PyPI 官方 mdformat 冲突）。改名触及插件发现协议：entry_points group 原为 `mdformat.codeformatter` / `mdformat.parser_extension`。
- 选项：a) 保留 `mdformat.*` group，兼容既有 mdformat-* 第三方插件（mdformat-gfm 等）；b) 随包名改为 `md_kx.*` group，彻底改名但既有插件需重注册。
- 结论：b。用户明确要求"全都改"。fork 破坏性升级优先于兼容包袱；第三方插件如需适配，改其 entry_points group 注册到 `md_kx.*`。配置文件亦改为 `.md_kx.toml`。
- 替代：无
