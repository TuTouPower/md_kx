# spec: YAML front matter 识别但不格式化

- 来源：t001（来自 p001，fork 二次开发需求 1）
- 生效日期：2026-08-11

## 行为

mdformat 识别文档开头的 YAML front matter 块（`---` 包裹，内含至少一行 `key: value` 形式键值，兼容 LF/CRLF 行尾），原样保留不格式化；front matter 之后正文照常按现有规则格式化。无 front matter（或块内无键值行）的文档行为不变。

- front matter 输出与输入逐字节一致（`text()` 返回 LF 归一 front matter，`file()` 按目标 newline 转换）
- 普通 `---` 分隔线、正文开头 `---` 不被误判为 front matter
- 不解析 front matter 内部 YAML 语义

## 边界

- 仅识别文档开头闭合 `---` 块；无闭合或非开头不剥离
- front matter 后空行连带剥离，重组时保留

## 实现

`mdformat._api.text()` 入口经 `_strip_front_matter()` 剥离 front matter，正文走 markdown-it-py 管线，重组 front matter + 渲染结果。
