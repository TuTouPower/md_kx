# Spike report

## 问题

mdformat 内置表格解析的最小接入路径是什么？markdown-it-py 是否提供可复用的 table 规则（不算新依赖）？mdformat renderer 如何渲染表格 token 回 Markdown？

## 成功判据

- 确认启用表格解析不引入新依赖
- 确认 renderer 需新增哪些 token 渲染
- 明确三态开关（不处理/pad/紧凑）落在哪层

## 尝试

- markdown-it-py `commonmark` preset 的 block ruler 含 `table` 规则（`get_all_rules` 列出），默认禁用。`mdit.block.ruler.enable("table")` 启用，无需新依赖。
- 启用后 parse 产生 token：`table_open → thead → tr → th/inline → tbody → tr → td/inline → table_close`（9 类 token，th/td 内容为 inline）。
- mdformat renderer 无 table 渲染器：`mdit.render(md)` 报 `KeyError 'table'`（`DEFAULT_RENDERERS` 缺 table token type）。
- 结论：接入需两段——解析层 `build_mdit` 启用 table 规则；渲染层 `DEFAULT_RENDERERS` 新增 table 系列 token 渲染器（table_open/thead/tbody/tr/th/td 等）把 token 重组为 Markdown 表格文本。

## 证据

- `.scratch/exp_table*.py`：enable table → token dump；mdformat render → KeyError 'table'。
- token 结构 dump 见 `.scratch/exp_tokens.py`。

## 结论

采用「启用 markdown-it-py table 规则 + 新增 mdformat renderer」路径。解析层 `build_mdit` 条件启用（配合三态开关），渲染层写 table 系列 renderer 按三态输出（不处理=原样跳过、pad=对齐、紧凑=不 pad）。markdown-it-py 已内置，不引新依赖。

## 是否采纳

- 决定：是
- 理由：markdown-it-py 内置 table 规则可复用，无需自研解析
- 后续 task：t003
