# p007 多行列表项段落后 0 缩进表格行崩溃

- 现象：含「多行列表项段落（首行后软换行续行）+ 紧接 0 缩进表格行」的文档，md_kx 崩溃 `AssertionError: null bytes should be removed by now`，退出码 1，文件不写回。最小复现：
  ```
  2. `review_level`
  按风险判：
  |level|适用|
  |------|------|
  |`full`|安全|
  ```
  有序/无序列表均触发；单行列表项段落 + 紧接表格（p006 已修形态）不触发。
- 影响：任何含该写法的 Markdown 无法格式化。触发功能：格式化全链路（崩溃而非优雅报错）。与 p006 同源（lazy 表格行 `\x00` 标记），p006 修复后此形态漏网。
- 根因：p006 修复的 `\x00` 标记机制，续行循环只在 `previous_line_ends_in_zero` 分支剥行尾 `\x00`，但**普通续行分支未剥自身行尾 `\x00`**。当段落含「普通续行 + 后续 lazy 表格行」时，普通续行（如 `按风险判：`）被 softbreak 标记 `\x00`（因下一行是 `|` 开头），续行循环缩进它但保留行尾 `\x00` → finalize 断言触发。单行段落形态无普通续行，不触发。分类：产品缺陷（p006 修复遗漏形态）。
- 测试缺口：`test_list_table.py` 原用例只覆盖单行段落 + 表格行；多行段落（首行后软换行续行）形态无测试。补：`test_multiline_paragraph_lazy_table_no_crash` 已加（主仓直接修复时补），断言 validate 通过 + 续行缩进 + 表格行 0 缩进。
- 线索：`.scratch/bug2/multi.md`（最小复现）、`.scratch/bug2/trace2.py`（item_text 泄漏定位）
- 处理：t007-followup
