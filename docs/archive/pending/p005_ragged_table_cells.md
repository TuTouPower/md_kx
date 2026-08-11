# p005 ragged 表格单元格处理

- 现象：行内单元格数不齐的表格（`| a |\n| --- |\n| 1 | b |`），pad/compact 模式静默丢弃多余单元格
- 影响：输入本身非 GFM 合法表格（超出语法子集），markdown-it 上游截断；丢弃行为可接受但未固化测试
- 根因：markdown-it table 规则对 ragged 行的截断行为
- 测试缺口：无覆盖
- 线索：t003_test_f002
- 处理：t003-verified-gfm
