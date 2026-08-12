# spec: 内置表格解析与三态表格处理

- 来源：t003（来自 p004，fork 二次开发需求 4）
- 生效日期：2026-08-12

## 行为

md_kx 内置表格解析（markdown-it-py 的 `table` 规则），提供 `table_mode` 配置项（CLI `--table-mode {none,pad,compact}` 或 `.md_kx.toml`）控制表格处理：

- `none`（默认）：表格内容不被触碰，输出与原输入语义一致（单元格文本、转义管道、对齐语义保留）
- `pad`：表格单元格补空格对齐（各列等宽）
- `compact`：表格保持紧凑，单元格不补空格对齐

三种模式下表格语法均正确、可被正常渲染，二次格式化幂等。不含表格的文档输出不变。

## 边界

- 对齐冒号（`:---` / `:---:` / `---:`）在各模式下保留
- 单元格内转义管道（`\|`）保留，不破坏表格边界
- `table_mode` 非法值经 `_validate_values` 拒绝

## 实现

`md_kx._util.build_mdit` 总是启用 `ruler.enable("table")`；`md_kx.renderer._context.table` 渲染器按 table_mode 输出（none/compact 紧凑、pad 对齐），`_table_aligns` 读 th token 的 `style:text-align` 保留对齐。`_conf.DEFAULT_OPTS` 默认 `none`。
