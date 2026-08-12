# md_kx 使用指南

md_kx 是 CommonMark 合规的 Markdown 格式化器（fork 自 hukkin/mdformat，二次开发增强）。提供 CLI、Python API 与 pre-commit hook 三种使用方式。

## 安装

### 全局 CLI（推荐）

```bash
cd /home/karon/karson_ubuntu/md_kx
uv tool install .
```

安装后注册 `md_kx` 全局命令（`~/.local/bin`），任意目录可用：

```bash
md_kx --version   # → md_kx 1.0.0
```

仓库更新后重装：

```bash
uv tool install . --reinstall
```

> **注意**：重装必须用 `--reinstall`（implies `--refresh`），不能用 `--force`。`--force` 会命中 uv 构建缓存，装入旧代码——现象是 `md_kx --version` 显示旧版本号但修复不生效。若装完仍见旧行为，检查安装环境：`~/.local/share/uv/tools/md-kx/lib/python*/site-packages/md_kx/renderer/_context.py`，确认含最新改动（如 `lazy table` 关键字），或用 `--reinstall` 强制刷新。

### 作为 Python 库

```bash
uv run --with-requirements tests/requirements.txt python -c "import md_kx; md_kx.text('# hi')"
```

或 `pip install .` / 加入项目 `pyproject.toml` 依赖。

## CLI 用法

### 格式化文件

```bash
md_kx README.md CHANGELOG.md   # 就地格式化指定文件
md_kx .                         # 递归格式化当前目录 .md 文件
md_kx -                         # 从 stdin 读，stdout 写
```

### 检查模式

```bash
md_kx --check README.md         # 只检查不改写；未格式化则 exit 1
```

### 常用选项

| 选项 | 说明 | 默认 |
| --- | --- | --- |
| `--check` | 只检查不修改 | 关 |
| `--wrap {keep,no,INTEGER}` | 段落折行宽度 | `keep` |
| `--number` | 有序列表连续编号 | 关 |
| `--end-of-line {lf,crlf,keep}` | 输出换行符 | `lf` |
| `--indent-width INTEGER` | 嵌套列表统一缩进宽度 | marker 对齐 |
| `--table-mode {none,pad,compact}` | 表格处理模式 | `none` |
| `--no-validate` | 跳过 HTML 一致性校验 | validate 开 |
| `--exclude PATTERN` | 排除匹配文件（Python 3.13+） | 空 |
| `--extensions` / `--codeformatters` | 启用插件扩展 | 全启用 |

## 本 fork 新增功能

### YAML front matter 保留

文档开头的 YAML front matter（`---` 包裹）自动识别并原样保留，不格式化、不破坏内部内容。普通 `---` 分隔线不会被误判。

```markdown
---
name: my-skill
description: 示例
---
# 标题
```

格式化后 front matter 与输入逐字节一致。

### 统一嵌套列表缩进

`--indent-width N` 让嵌套列表每层缩进统一为 N 空格（默认 marker 对齐）。适合文档风格统一：

```bash
md_kx --indent-width 4 file.md
```

代码块（\`\`\` 围栏）内容不受影响。

### 表格三态处理

`--table-mode` 控制表格输出：

- `none`（默认）：表格原样保留，内容不被触碰
- `pad`：单元格补空格对齐（各列等宽）
- `compact`：保持紧凑，不补空格

```bash
md_kx --table-mode compact file.md
```

三态下转义管道（`\|`）与对齐冒号（`:---`）均保留，二次格式化幂等。

## 配置文件 `.md_kx.toml`

CLI 选项可写入 `.md_kx.toml`，配置解析从被格式化文件位置开始向上级目录搜索，直到找到配置或到根；stdin 输入从当前工作目录解析。CLI 传参优先于配置文件。

完整默认值（等价于无配置文件）：

```toml
# .md_kx.toml
wrap = "keep"         # options: {"keep", "no", INTEGER}
number = false        # options: {false, true}
end_of_line = "lf"    # options: {"lf", "crlf", "keep"}
validate = true       # options: {false, true}
indent_width = 0      # options: 非负整数；0 = marker 对齐
table_mode = "none"   # options: {"none", "pad", "compact"}
# extensions = ["gfm", "toc"]       # 启用插件扩展
# codeformatters = ["python"]       # 启用代码格式化插件

# Python 3.13+ only:
exclude = []          # 文件路径 glob 模式列表
```

### exclude patterns（Python 3.13+）

Unix-style glob 匹配相对路径。`--exclude` 相对当前目录；配置文件相对其所在目录。匹配的文件**总是**被排除（即使命令行显式指定）。

```toml
exclude = [
    "CHANGELOG.md",        # 排除根级单文件
    "venv/**",             # 递归排除根级目录
    "**/node_modules/**",  # 递归排除任意层级目录
    "**/*.txt",            # 排除所有 txt
]
```

## Python API

```python
import md_kx

md_kx.text("## 未格式化标题\n")                    # 返回格式化文本
md_kx.file("README.md")                             # 就地格式化文件（str 或 pathlib.Path）
md_kx.text("# 标题\n", options={"indent_width": 4})  # 带配置
```

CLI 的所有风格选项在 API 中同名可用：

```python
md_kx.file(
    "FILENAME.md",
    options={
        "number": True,   # 有序列表连续编号
        "wrap": 60,       # 折行宽度 60
        "table_mode": "compact",
    },
)
```

## pre-commit hook

本仓库自带 pre-commit hook 元数据，接入其他仓库：

```yaml
repos:
- repo: /home/karon/karson_ubuntu/md_kx
  rev: <commit 或分支>
  hooks:
  - id: md_kx
    # 可选：附加插件依赖
    additional_dependencies:
    - md_kx-black
```

> 注意：mdformat 的格式化风格可能随版本变化，建议 pin 依赖版本（`rev` 固定 commit 或 tag）。

或本仓库内部直接使用：

```bash
pre-commit try-repo . md_kx --files README.md
```

## 常见问题

- **格式化结果不稳定 / HTML 不一致**：mdformat 默认 `validate` 会校验渲染 HTML 一致性，报错说明有 bug 或插件问题，可用 `--no-validate` 跳过。
- **front matter 未保留**：确认文档开头是 `---` 包裹的闭合块，且含 `key: value` 行；纯 `---` 分隔线不会被当作 front matter。
