# d004 ragged 表格多余 cell 截断是 GFM 规范行为

- 来源：p005 核实（t003 遗留，2026-08-12 main 上验证）
- 结论：GFM 表格中行内 cell 数超出表头列数时，多余 cell 被截断（信息丢失）；列数不足时补空 cell。这是 GFM 规范行为，markdown-it 与所有 GFM 实现一致，非 mdformat 缺陷。表头列数决定表格列数。
- 证据：`mdformat.text('| a |\n| --- |\n| 1 | b |\n')` 输出 `| 1 |`（b 截断）；反向 `| a | b |\n| --- | --- |\n| 1 |` 输出 `| 1 |  |`（补空）。markdown-it `rules_block/table.py` 对超出列数 cell 不补全。
- 影响：p005 已闭环不改代码；`table_mode` 三种风格（compact/spaced/pad，t008 后无 none）均遵循此行为。若需保留超出 cell，须预处理补列（违背 GFM）。
- 现状：有效
