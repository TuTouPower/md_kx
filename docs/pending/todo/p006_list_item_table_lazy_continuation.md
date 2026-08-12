# p006 列表项后 0 缩进表格行 validate 失败

- 现象：含「列表项段落后紧跟 0 缩进表格行」的文档，md_kx 格式化时 validate 报 `Could not format`（HTML 不一致），退出码 1，文件不写回。最小复现：
  ```
  2. `review_level` 按风险判：
  |level|适用|
  |------|------|
  |`full`|安全|
  ```
  任一格式化选项（含仅 `--number`）均触发。
- 影响：任何含该写法的 Markdown 文档无法格式化。repo_template 的 `.agents/skills/*/SKILL.md`（13 个）普遍使用「列表项下 0 缩进表格」写法，全部命中；md_kx 仓库自身文档当前未命中（表格已规范缩进）。触发功能：格式化 + validate 全链路。
- 根因：t003 使 `build_mdit` **总是启用 markdown-it table 规则**（为保留转义）。输入中表格行 0 缩进紧跟在列表项段落后，markdown-it 将其作为列表项的 **lazy continuation**（段落文本，不解析为 table）；mdformat renderer 格式化时把该文本行缩进到列表项内容位（marker 对齐或 indent-width）；validate 二次渲染格式化结果时，缩进后的表格行被解析为**列表项内 table**（enable table 生效）。original HTML（表格行=段落文本）与 formatted HTML（`<table>`）结构不同 → `is_md_equal` False → validate 拦截。分类：产品缺陷（解析与渲染不对称）。已确认同类位点：机制为全局 enable table + lazy continuation，任何该写法的文档均触发（单点机制，非分散位点）。
- 测试缺口：`tests/test_table.py` 现有用例只测独立表格、列表项内缩进表格、转义管道、对齐冒号，**无「列表项段落后 0 缩进表格行」边界**。补测：构造该写法的输入，断言 `is_md_equal(orig, formatted)` 为 True（格式化后 validate 通过），且渲染层级不变。
- 线索：`.scratch/bug/orig.md`（最小复现）、`.scratch/bug/validate_analyze.py`（HTML 差异分析）
- 处理：未开
