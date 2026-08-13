# spec: 内置表格解析与三种输出风格

- 来源：t008（来自 p008，supersedes t003 的三态 `none`/`pad`/`compact`）
- 生效日期：2026-08-13

## 行为

md_kx 内置表格解析（markdown-it-py 的 `table` 规则），提供 `table_mode` 配置项（CLI `--table-mode {compact,spaced,pad}` 或 `.md_kx.toml`）选择表格输出风格。同一次格式化中所有表用同一风格。风格只影响表格行的空白与列宽，不改变单元格有效文本、不改变表格行列结构、不改变表以外的文档。

三种风格：

- `compact`：单元格两侧零空格，分隔行用固定标记且两侧零空格（`|a|b|`、`|---|---|`）
- `spaced`（默认）：单元格两侧各恰好一个空格，不按列宽补空格（`| a | b |`、`| --- | --- |`）
- `pad`：先按 spaced 方式留空格，再按列把单元格补到该列最宽，分隔段随列宽拉长，外层竖线对齐

三种风格下表格语法均正确、可被正常渲染，二次格式化幂等。不含表格的文档输出与风格选择无关。CLI 优先于仓库配置；`none` 及三种之外的风格名在 CLI（argparse choices）与配置（`InvalidConfError`）中均被拒绝，文件不被修改。

## 边界

- 对齐冒号（`:---` / `:---:` / `---:`）在各风格下语义保留：compact 贴竖线内侧不加空格，spaced 冒号外侧各留一个空格，pad 在保留冒号前提下按列宽拉长分隔段
- 单元格内转义管道（`\|`）保留，不破坏表格边界、不拆列
- 空单元格：compact 相邻竖线（`||`），spaced 两侧各一空格（`|  |`），pad 按该列宽度补空格
- `table_mode` 非法值经 argparse choices / `_validate_values` 拒绝

## 实现

`md_kx._util.build_mdit` 总是启用 `ruler.enable("table")`；`md_kx.renderer._context.table` 渲染器按 table_mode 输出（compact/spaced 用固定标记、pad 用 `_align_marker` 全宽标记与 `_min_marker_width` 列宽下限），`_table_aligns` 读 th token 的 `style:text-align` 保留对齐。`_conf.DEFAULT_OPTS` 默认 `spaced`。
