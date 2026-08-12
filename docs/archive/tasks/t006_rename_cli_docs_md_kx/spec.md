# Task spec

## 背景

t004 已把包与 entry point 改名 md_kx（CLI 命令 `md_kx`）。本 task 同步 CLI 命令在 CI、pre-commit hook、README/docs 的呈现，以及产品品牌引用。

## 契约区

### 范围

- `.github/workflows/tests.yaml`：`mdformat --check` 命令改 `md_kx --check`；`pre-commit try-repo . mdformat` 改 `md_kx`
- `.pre-commit-hooks.yaml`：hook id、name、entry 改 md_kx
- `README.md`：CLI 用法示例、品牌描述改 md_kx（保留"fork 自上游 mdformat"指代）
- `docs/blueprint/*.md`、`docs/specs/*.md`：产品名品牌改 md_kx
- pyproject 中 tox env 描述、命令引用

### 非范围

- src/ 包与 import（t004 已改）
- tests/（t005 已改）
- 上游 mdformat-gfm 插件测试（用户决策删除——fork 改名后插件 group 为 md_kx.*，mdformat-gfm 不再适用）

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

- [ ] AC-001：`README.md`、`docs/blueprint/`、`docs/specs/` 中产品名/命令引用改为 md_kx（除"fork 自上游 mdformat"历史指代）。
- [ ] AC-002：`.pre-commit-hooks.yaml` hook id/name/entry 为 md_kx，`pre-commit validate-manifest` 通过。
- [ ] AC-003：`.github/workflows/tests.yaml` 的 `md_kx --check` 命令生效（本地等价 `python -m md_kx --check README.md` 通过）。
- [ ] AC-004：README 的 CLI usage 快照与实际 `md_kx --help` 输出一致。

### 可测试性声明

<!-- 规范（门禁必留，不得删除） -->
逐条说明哪些 AC 不可自动测试及原因；全部可测则写「全部 AC 可自动测试」。
<!-- /规范 -->

- 全部 AC 可自动测试。

## 上下文区

- 来源：用户提出（fork 改包名，2026-08-12；t004 前置已改 entry point）

### 有意不测

<!-- 规范（门禁必留，不得删除） -->
已判定不写测试的分支与原因。reviewer 不得据此出 blocking finding。无则写「无」。
<!-- /规范 -->

- 无。

### 测试策略

<!-- 规范（门禁必留，不得删除） -->
mock 边界、fixture 来源、断言目标。无特殊约定写「按项目默认」。
<!-- /规范 -->

- 按项目默认：`pre-commit run -a` 全绿（含 validate-manifest）、`python -m md_kx --check README.md` 通过、README usage 与实际 --help 比对。

### 未知契约清单

<!-- 规范（门禁必留，不得删除） -->
尚未核实的外部 endpoint、API 形态、数据结构、第三方行为须分类标记；核实后删除标记，改为结论并注明验证方式。无则写「无」。
<!-- /规范 -->

- 无。

### 风险与回退

- 风险：README/docs 品牌改漏或误改上游指代；hook entry 改后旧 mdformat 命令失效。
- 回退：git 历史可回滚；grep 校验确保品牌引用一致。

### 依赖与约束

- 依赖 t004（entry point 已改名 md_kx）；不引入新依赖。

### Finalization 时更新的 blueprint

- `docs/blueprint/domain.md`：产品名 mdformat → md_kx。
