# Spike report

## 问题

修复「列表项后 0 缩进表格行 validate 失败」（p006）。需确认最小修复方案，且不破坏 t003 的表格三态与转义保留。

## 成功判据

- 找到能消除 validate 失败且不回归的修复点
- 方案不破坏 none 模式转义保留（t003 f001）

## 尝试

- 候选 A（条件 enable table）：`table_mode != none` 才 enable。实验 `.scratch/bug/exp_cond_enable.py`：none 模式无表格 token → 走段落管线 → `\|` 转义被剥（t003 f001 复发）；且 p006 场景 enable 与否表格行都解析为 lazy continuation（无 table token），条件 enable **不修复 p006**。弃。
- 候选 B（renderer 不缩进续行）：手动构造不缩进 formatted，`is_md_equal` True（`.scratch/bug/exp_noshrink.py`）。证实根因在 `_context.py:606` 对段落续行加 indent_width 前缀，改变二次解析语义。但去掉缩进会破坏正常多行列表项格式。
- 机制确认：lazy continuation 表格行并入段落 inline，renderer 无法区分"段落续行"与"lazy 表格行"，统一加缩进。validate 二次解析时缩进行变 table。

## 证据

- `.scratch/bug/*.py`：exp_cond_enable（A 失效+破转义）、exp_noshrink（B 可行但破坏格式）、validate_analyze（HTML 差异）
- d005 记录机制

## 结论

根因是 renderer 对 lazy continuation 行统一缩进 + build_mdit 总是 enable table 的组合，导致一二次解析不一致。修复需**在不缩进 lazy 表格行的同时保留正常段落续行缩进**——具体实现方案（如何区分两类行）待 task-work 实验：候选① renderer 检测段落内换行后接表格行则不缩进；候选② 调整 lazy continuation 处理。修复必须保持 none 模式转义保留（t003 f001）与表格三态。

## 是否采纳

- 决定：是（问题确认，修复方案需 task-work 实验细化）
- 理由：机制已定位，实现细节需实验
- 后续 task：t007
