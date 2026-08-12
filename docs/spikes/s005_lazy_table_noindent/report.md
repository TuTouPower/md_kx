# Spike report

## 问题

实现 p006 修复：区分「lazy 表格续行」与「正常段落续行」，只对前者不缩进。

## 成功判据

- 找到 renderer 层可识别 lazy 表格行的方案
- 方案不误伤正常段落续行与转义保留

## 尝试

- 树/token 层识别：lazy 表格行并入段落 inline，仅 softbreak/text 分隔，无类型标记（`.scratch/exp_lazy.py`、`exp_token.py`）。无法区分。
- 守卫方案：`ordered_list`/`bullet_list` 续行处理（`_context.py:606`）检测续行行首 `|`，是则不缩进。验证：
  - lazy 表格行不缩进 → `is_md_equal` True（修复成功）
  - 正常段落续行缩进 → `is_md_equal` True（不变）
  - 行首 `|` 的正常段落续行不缩进 → 仍 `is_md_equal` True（validate 通过，风格略变可接受）
- 根本差异：缩进对段落续行无害（二次解析仍段落），对 lazy 表格行有害（二次解析变 table）。守卫用行首 `|` 特征识别表格行。

## 证据

- `.scratch/exp_guard.py`：表格行 0 缩进 is_md_equal True，缩进 False
- `.scratch/exp_boundary*.py`：正常续行与行首 | 段落边界

## 结论

采用「续行行首 `|` 则不缩进」守卫。实现于 `_context.py` list renderer 续行处理：检测每行是否 `|` 开头（去空白后），是则保持原缩进（不追加 indent_width 前缀）。副作用小（行首 `|` 正常续行仅风格变化）。保持 enable table（转义保留）与三态。

## 是否采纳

- 决定：是
- 理由：树层无法区分，行首特征守卫最简可行
- 后续 task：t007
