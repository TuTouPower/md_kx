# 架构

> 初稿：2026-08-11 按 mdformat 1.0.0 源码结构填写，任务完结时同步更新。

## 模块划分

- `mdformat/_cli.py` + `mdformat/__main__.py`：CLI 入口（`mdformat` 命令），参数解析、文件/目录遍历、`--check` / `--wrap` / `--number` 等选项处理
- `mdformat/_api.py`：Python API（`mdformat.text()` / `mdformat.file()`），返回格式化后的 Markdown 文本
- `mdformat/_conf.py`：配置读取（`mdformat.toml`、pyproject.toml `[tool.mdformat]`）
- `mdformat/plugins.py`：插件注册与发现（第三方 `mdformat-*` 插件、pre-commit hook 元数据）
- `mdformat/renderer/`：渲染器，把解析出的 token 流按样式规则重排为文本（`_tree.py` 树遍历、`_context.py` 渲染上下文、`_util.py` 辅助）
- `mdformat/codepoints/`：Unicode 标点 / 空白字符分类数据，供渲染与文本处理使用
- `mdformat/_util.py` / `_compat.py`：通用工具与兼容层

## 数据流

```
Markdown 文本 → markdown-it-py 解析 → token 流 → renderer 渲染 → 格式化 Markdown 文本
```

外部依赖：`markdown-it-py` 负责解析（mdformat 不自行实现解析器），渲染与重排由 `mdformat/renderer/` 完成。

## 进程 / 边界

- 进程形态：CLI 一次性进程；无常驻服务。
- 对外边界：CLI（`mdformat`）、Python API、pre-commit hook（`.pre-commit-hooks.yaml`，作为 `pre-commit` 插件被引用）。
- 对内边界：插件通过 `mdformat.plugins` 注册扩展（自定义渲染规则、代码围栏语言高亮钩子等）。

