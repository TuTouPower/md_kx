# Task spec

## 背景

t004 已把包从 mdformat 改名 md_kx。tests/ 目录仍有大量 `import mdformat` / `mdformat.text` / `mdformat._cli` 引用，需同步改名使测试可用。

## 契约区

### 范围

- `tests/` 下全部 `mdformat` import 改为 `md_kx`
- `tests/` 下全部 `mdformat.text()` / `mdformat._cli` 等方法/模块引用改为 `md_kx.*`
- `tests/requirements.txt` 等测试依赖文件中的 mdformat 引用（如有）

### 非范围

- src/ 包本体（t004 已改）
- CI / README / docs 品牌（t006 负责）

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

- [ ] AC-001：`tests/` 下无残留 `mdformat` import 或 `mdformat.` 引用（grep 确认）。
- [ ] AC-002：`uv run --with-requirements tests/requirements.txt pytest tests -q` 全量通过（4668+ passed）。
- [ ] AC-003：既有测试覆盖的三态/缩进/front matter 功能测试仍通过（test_table/test_indent/test_front_matter）。

### 可测试性声明

<!-- 规范（门禁必留，不得删除） -->
逐条说明哪些 AC 不可自动测试及原因；全部可测则写「全部 AC 可自动测试」。
<!-- /规范 -->

- 全部 AC 可自动测试。

## 上下文区

- 来源：用户提出（fork 改包名，2026-08-12；t004 前置已改包）

### 有意不测

<!-- 规范（门禁必留，不得删除） -->
已判定不写测试的分支与原因。reviewer 不得据此出 blocking finding。无则写「无」。
<!-- /规范 -->

- 无。

### 测试策略

<!-- 规范（门禁必留，不得删除） -->
mock 边界、fixture 来源、断言目标。无特殊约定写「按项目默认」。
<!-- /规范 -->

- 按项目默认：改名后跑全量 pytest 确认无回归。

### 未知契约清单

<!-- 规范（门禁必留，不得删除） -->
尚未核实的外部 endpoint、API 形态、数据结构、第三方行为须分类标记；核实后删除标记，改为结论并注明验证方式。无则写「无」。
<!-- /规范 -->

- 无。

### 风险与回退

- 风险：改名遗漏导致 pytest 收集失败；`mdformat-gfm` 插件测试（CI 中）依赖官方包名。
- 回退：git 历史可回滚；grep 校验确保无残留。

### 依赖与约束

- 依赖 t004（包已改名）；不引入新依赖。

### Finalization 时更新的 blueprint

- 无。
