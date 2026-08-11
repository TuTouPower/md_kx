# Spike report

## 问题

统一嵌套列表缩进应改哪层：renderer 输出层还是解析 token 层？改 renderer 是否破坏内容块语义？

## 成功判据

- 确定缩进统一的最小改动位置
- 确认 token 层是否含原始缩进宽度（决定能否在 renderer 层改）

## 尝试

- 解析 token 层：dump markdown-it-py tokens，`bullet_list_open` 只有 `level`（嵌套层级），`attrs`/`map` 无缩进宽度。原始缩进宽度在解析后被丢弃，token 层无可统一的对象。
- renderer 层：`DEFAULT_RENDERERS["bullet_list"]`/`["ordered_list"]`（`_context.py`）用 `indent = " " * len(marker_type + first_line_indent)` 计算每层缩进，逐层递归累加决定嵌套列表缩进。token 无原始宽度，renderer 输出完全自控。
- patch 实验：尝试 patch `_context.bullet_list`（不生效，MDRenderer 用 `DEFAULT_RENDERERS` 快照）与 `DEFAULT_RENDERERS`（mappingproxy 不可变）——确认改法须改 `_context.py` 源码里 list renderer 的 indent 计算，而非运行时 patch。

## 证据

- token dump：`bullet_list_open` level 0/2/4，attrs 空，无缩进宽度（`.scratch/exp_token.py`）
- renderer indent 计算：`_context.py:492-493` `indent = " " * len(marker_type + first_line_indent)`
- `env["indent_width"]` 仅用于 wrap（`_context.py:397`），与列表缩进无关

## 结论

统一缩进须改 renderer 层 `bullet_list`/`ordered_list` 的 `indent` 计算：从配置读统一宽度替代 `len(marker)`。token 层无原始缩进（丢弃），不改解析。renderer 输出自控，逐层累加统一宽度即可，内容块缩进随每层统一宽度重排。改 `_context.py` 源码（非运行时 patch）。

## 是否采纳

- 决定：是
- 理由：token 层无缩进宽度，renderer 层是唯一可控点
- 后续 task：t002
