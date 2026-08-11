# d003 markdown-it-py 内置 table 规则可复用

- 来源：s003
- 结论：markdown-it-py `commonmark` preset 的 block ruler 含 `table` 规则（默认禁用），`mdit.block.ruler.enable("table")` 即可启用，无需新依赖。启用后 parse 产生 `table_open/thead/tbody/tr/th/td` 系列 token。mdformat renderer 缺 table 渲染器（`KeyError 'table'`），需在 `DEFAULT_RENDERERS` 新增 table 系列 token 渲染器，把 token 重组为 Markdown 表格文本。
- 证据：`.scratch/exp_table*.py` enable table → token dump 正常；mdformat render → KeyError。token 结构见 `.scratch/exp_tokens.py`。
- 影响：t003 实现需两段——解析层启用 table 规则 + 渲染层新增 renderer；三态开关由 renderer 控制输出。
- 现状：有效
