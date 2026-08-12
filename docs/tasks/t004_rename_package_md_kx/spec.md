# Task spec

## 背景

本仓库是 mdformat 的 fork，需改名为 md_kx（包名与 CLI 命令均改，避免与 PyPI 官方 mdformat 冲突）。本 task 先改核心包层：src 目录、包内 import、pyproject 元数据与打包配置。

## 契约区

### 范围

- `src/mdformat/` 目录重命名为 `src/md_kx/`
- 包内自引用 import（`mdformat._api` 等）改为 `md_kx.*`
- pyproject：`name`、entry point（`md_kx = "md_kx.__main__:run"`）、isort `known_first_party`、coverage `source`
- `.bumpversion.cfg` 路径
- 仓库内其他 Python 文件对 `mdformat` 包的 import（fuzzer、scripts 等）

### 非范围

- tests/ 目录（t005 负责）
- CLI 命令名在 CI/README/docs 的呈现（t006 负责）
- 上游 mdformat-gfm 插件的测试（CI 中保留）

### 验收标准

<!-- 规范（门禁必留，不得删除） -->
只写用户或调用方可观察行为，每条可独立验证。普通版本号、底层库和目录结构不作为验收标准；需要长期约束后续工作的技术选择写入 `docs/blueprint/decisions.md`。
<!-- /规范 -->

<!-- 规范（门禁必留，不得删除） -->
需真实部署或人工环境才能验证的条目加 `[deploy]` 前缀，标明 agent 无法自证。
<!-- /规范 -->

<!-- 规范（门禁必留，不得删除） -->
每条 AC 条目带稳定编号 `AC-NNN`（三位十进制、task 内从 001 顺序编号、唯一、删除不复用）；收尾时 `handoff.json` 的 `ac_evidence` 须精确覆盖本区全部编号。编号约定见 `docs/blueprint/conventions.md`。
<!-- /规范 -->

- [ ] AC-001：`src/md_kx/` 存在，`src/mdformat/` 不存在，`python -c "import md_kx"` 成功。
- [ ] AC-002：`src/md_kx/` 内无残留 `import mdformat` 或 `from mdformat` 引用。
- [ ] AC-003：pyproject `name = "md_kx"`，entry point 为 `md_kx = "md_kx.__main__:run"`，coverage/isort 引用 md_kx。
- [ ] AC-004：`uv run --with-requirements tests/requirements.txt python -m md_kx --version` 可运行（CLI 入口可用）。

### 可测试性声明

<!-- 规范（门禁必留，不得删除） -->
逐条说明哪些 AC 不可自动测试及原因；全部可测则写「全部 AC 可自动测试」。
<!-- /规范 -->

- 全部 AC 可自动测试。

## 上下文区

- 来源：用户提出（fork 改包名，2026-08-12；全库引用面已检索：29 个 py、pyproject/.bumpversion.cfg 等）

### 有意不测

<!-- 规范（门禁必留，不得删除） -->
已判定不写测试的分支与原因。reviewer 不得据此出 blocking finding。无则写「无」。
<!-- /规范 -->

- 无。

### 测试策略

<!-- 规范（门禁必留，不得删除） -->
mock 边界、fixture 来源、断言目标。无特殊约定写「按项目默认」。
<!-- /规范 -->

- 按项目默认：改名后跑既有 pytest（tests 引用 t005 改，本 task 后 tests 会失败，故黑盒用 `python -c import md_kx` + CLI --version 验证）。

### 未知契约清单

<!-- 规范（门禁必留，不得删除） -->
尚未核实的外部 endpoint、API 形态、数据结构、第三方行为须分类标记；核实后删除标记，改为结论并注明验证方式。无则写「无」。
<!-- /规范 -->

- 无。

### 风险与回退

- 风险：改名后 tests 仍引用旧名导致 pytest 失败（依赖 t005 跟进）；入口点改后旧命令失效。
- 回退：git 历史可回滚；t005/t006 链式跟进补齐。

### 依赖与约束

- 无前置；不引入新依赖。

### Finalization 时更新的 blueprint

- `docs/blueprint/architecture.md`：模块路径 mdformat → md_kx。
