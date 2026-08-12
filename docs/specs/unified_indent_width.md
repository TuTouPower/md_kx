# spec: 统一缩进宽度配置

- 来源：t002（来自 p002，fork 二次开发需求 2）
- 生效日期：2026-08-11

## 行为

md_kx 提供 `indent_width` 配置项（CLI `--indent-width INTEGER` 或 `.md_kx.toml`），统一嵌套列表的缩进宽度。设置后嵌套列表每层缩进为该宽度；未设置（默认 0）时保持现有 marker 对齐语义。N 小于列表 marker 显示宽度时取 marker 宽度兜底，保证 CommonMark 嵌套结构不被破坏。

- 代码块（``` 围栏内）内容不被改动
- 默认行为不变（未配置时无回归）

## 边界

- `indent_width` 须为非负整数；非法值（负数、非 int）经 `_validate_values` 拒绝
- 兜底：N < marker 宽度时每层用 marker 宽度

## 实现

`md_kx.renderer._context` 的 `bullet_list`/`ordered_list` 读 `context.options["md_kx"]["indent_width"]`，configured 时用 `max(configured, default_width)` 作每层缩进；未设时保持原 marker 计算。`_conf.DEFAULT_OPTS` 默认 0。
