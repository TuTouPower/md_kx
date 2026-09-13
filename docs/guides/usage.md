# md_kx 使用指南

md_kx 是 CommonMark 合规的 Markdown 格式化器（fork 自 hukkin/mdformat，二次开发增强）。提供 CLI、Python API 与 pre-commit hook 三种使用方式。

## 安装

包已发布到 PyPI：**发行名 `md-kx`**，安装后命令名为 **`md_kx`**（注意下划线）。要求 Python >= 3.10。

### 全局 CLI（推荐）

用 [uv](https://docs.astral.sh/uv/) 或 [pipx](https://pipx.pypa.io/) 装成全局命令，互不污染项目环境：

```bash
uv tool install md-kx        # 或：pipx install md-kx
```

安装后注册 `md_kx` 全局命令（uv 默认 `~/.local/bin`），任意目录可用：

```bash
md_kx --version   # → md_kx 1.0.0
```

升级到 PyPI 上的最新版：

```bash
uv tool upgrade md-kx        # 或：pipx upgrade md-kx
```

锁定/回退到指定版本：

```bash
uv tool install --reinstall md-kx==1.0.0
```

> `uv tool install` 默认不覆盖已装版本；升级用 `uv tool upgrade`，强制重装用 `--reinstall`。

### 本仓库开发者的全局更新

改完本仓代码、要更新全局 `md_kx` 时：

```bash
bash scripts/update_global.sh              # 从 PyPI 装最新版 + 自动验证
bash scripts/update_global.sh --version 1.0.0   # 装指定版本
```

脚本执行两步：`uv tool install --reinstall md-kx` → 自动验证（`--table-mode` 合法值与默认风格、行为冒烟、已装文件内容检查），任一项不符即失败退出。

> **场景区分**：
>
> - **开发测试**：用仓库内 `.venv`（editable 安装，改动即时生效），不要跑本脚本。
> - **开发完成 → 发布**：改版本 → 打 tag → CI 发布到 PyPI（见 `docs/blueprint/decisions.md` ADR 002）；发布后 `scripts/update_global.sh` 从 PyPI 更新全局，与仓库 `.venv` 是两个独立环境。
>
> 该脚本不再本地打包；全局命令只来自 PyPI 发布版，因此发布前必须先完成版本发布。

### 作为 Python 库

```bash
pip install md-kx            # 或：uv add md-kx
```

```python
import md_kx

md_kx.text("# hi\n")
```

开发本仓库时用 editable 安装（改动即时生效）：

```bash
uv venv && uv pip install -e . -r tests/requirements.txt
.venv/bin/python -c "import md_kx; print(md_kx.text('# hi'))"
```

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
| `--table-mode {compact,spaced,pad}` | 表格输出风格 | `spaced` |
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

### 表格三种输出风格

`--table-mode` 控制表格输出：

- `compact`：单元格两侧零空格（`|a|b|`）
- `spaced`（默认）：单元格两侧各一个空格，不按列对齐（`| a | b |`）
- `pad`：按列补齐，外层竖线对齐（含分隔行）

```bash
md_kx --table-mode compact file.md
```

三种风格下转义管道（`\|`）与对齐冒号（`:---`）均保留，二次格式化幂等。

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
table_mode = "spaced" # options: {"compact", "spaced", "pad"}
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

本仓库自带 pre-commit hook 元数据，接入其他仓库（从 PyPI 安装，无需本地路径）：

```yaml
repos:
- repo: https://github.com/TuTouPower/md_kx
  rev: 1.0.0    # 固定 tag 或 commit
  hooks:
  - id: md_kx
    # 可选：附加插件依赖
    additional_dependencies:
    - md_kx-black
```

> 注意：格式化风格可能随版本变化，建议 pin 版本（`rev` 固定 commit 或 tag）。

或本仓库内部直接使用：

```bash
pre-commit try-repo . md_kx --files README.md
```

## 常见问题

- **格式化结果不稳定 / HTML 不一致**：mdformat 默认 `validate` 会校验渲染 HTML 一致性，报错说明有 bug 或插件问题，可用 `--no-validate` 跳过。
- **front matter 未保留**：确认文档开头是 `---` 包裹的闭合块，且含 `key: value` 行；纯 `---` 分隔线不会被当作 front matter。
