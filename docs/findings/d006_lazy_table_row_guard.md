# d006 列表 lazy 表格行行首守卫

- 来源：s005（2026-08-12 实验确认）
- 结论：列表项 lazy 表格行（0 缩进并入段落 inline）在 renderer 层无法与正常段落续行区分（树/token 均无标记）。修复用「续行行首 `|`（去空白）则不缩进」守卫：`_context.py` list renderer 续行处理检测行首，是则不追加 indent_width 前缀。验证：lazy 表格行不缩进 → `is_md_equal` True；正常续行缩进不变；行首 `|` 正常段落不缩进仍 validate 通过（风格略变）。
- 证据：`.scratch/exp_guard.py`、`exp_boundary*.py`。
- 影响：t007 实现；副作用小（行首 `|` 续行仅风格变化）。
- 现状：有效
