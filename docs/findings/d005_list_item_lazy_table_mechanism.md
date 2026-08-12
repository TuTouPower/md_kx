# d005 列表项 lazy continuation 表格行 validate 失败机制

- 来源：p006 / s004（2026-08-12 复现分析）
- 结论：含「列表项段落后 0 缩进表格行」的文档，md_kx 格式化 validate 报 `Could not format`（退出码 1）。机制：
  1. markdown-it 解析：表格行 0 缩进紧跟在列表项段落后，被当作列表项 **lazy continuation**，并入段落 inline（无 table token，任何选项都如此）
  2. renderer 的 `ordered_list`/`bullet_list`（`_context.py:606`）把段落续行统一加 `" " * indent_width` 前缀
  3. validate 二次渲染格式化结果：缩进后的表格行被解析为**列表项内 table**（build_mdit 总是 enable table）
  4. original（表格行=段落文本）vs formatted（`<table>`）HTML 结构不同 → `is_md_equal` False → validate 拦截
- 证据：`.scratch/bug/validate_analyze.py`（HTML 差异）；`.scratch/bug/exp_noshrink.py`（renderer 不缩进续行时 `is_md_equal` True）；`.scratch/bug/exp_cond_enable.py`（条件 enable table 不修复 p006 且破坏 none 转义）。
- 影响：任何含该写法的文档无法格式化；repo_template 13 个 SKILL.md 命中。分类：产品缺陷（解析与渲染不对称）。
- 现状：有效
