# d002 renderer 层统一列表缩进

- 来源：s002
- 结论：嵌套列表缩进由 renderer 层 `DEFAULT_RENDERERS["bullet_list"]`/`["ordered_list"]`（`_context.py`）的 `indent = " " * len(marker_type + first_line_indent)` 逐层递归累加决定。token 层只有 `level` 嵌套层级，原始缩进宽度在解析后被丢弃。统一缩进须改 renderer 的 indent 计算（从配置读宽度替代 marker 长度），token 层无可改对象。
- 证据：`.scratch/exp_token.py` dump token 无缩进宽度；`_context.py:492-493` indent 计算；`env["indent_width"]` 仅用于 wrap（`:397`）。
- 影响：t002 实现改 `_context.py` list renderer；`DEFAULT_RENDERERS` 是 mappingproxy 不可运行时 patch，须改源码。
- 现状：有效
