# Task spec

## 背景

含「列表项段落后 0 缩进表格行」的文档，md_kx 格式化时 validate 报 `Could not format`（退出码 1）。根因：markdown-it 把该表格行解析为列表项 lazy continuation（并入段落 inline），renderer 统一加缩进前缀（`_context.py:606`），validate 二次解析时缩进行变列表项内 table，HTML 结构变化。见 p006 / d005。

## 契约区

### 范围

- 修复列表项 lazy continuation 表格行导致 validate 失败
- 保持 build_mdit 总是 enable table 的转义保留语义（t003 f001 不回退）
- 保持表格三态（none/pad/compact）与 indent_width 现有行为

### 非范围

- 不改变独立表格、列表内缩进表格的现有格式化
- 不改变正常多行段落列表项的缩进

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

- [ ] AC-001：含「列表项段落后 0 缩进表格行」的文档（如 `2. 项：\n|a|b|`），md_kx 格式化后 validate 通过（不报 `Could not format`），退出码 0，文件被格式化。
- [ ] AC-002：该文档格式化后渲染层级不变——表格行保持原列表外/列表内语义，HTML 与输入一致（`is_md_equal` True）。
- [ ] AC-003：none 模式转义保留不回退：`| x\|y |` 在默认模式格式化后保留 `\|`，幂等。
- [ ] AC-004：独立表格与列表内缩进表格在三种 table_mode 下行为不变（复用 test_table.py 全量通过）。
- [ ] AC-005：正常多行段落列表项（非表格续行）缩进行为不变（复用既有列表测试通过）。

### 可测试性声明

<!-- 规范（门禁必留，不得删除） -->
逐条说明哪些 AC 不可自动测试及原因；全部可测则写「全部 AC 可自动测试」。
<!-- /规范 -->

- 全部 AC 可自动测试。

## 上下文区

- 来源：p006（2026-08-12 复现分析；根因机制见 `docs/findings/d005`，spike `docs/spikes/s004`）

### 有意不测

<!-- 规范（门禁必留，不得删除） -->
已判定不写测试的分支与原因。reviewer 不得据此出 blocking finding。无则写「无」。
<!-- /规范 -->

- 无。

### 测试策略

<!-- 规范（门禁必留，不得删除） -->
mock 边界、fixture 来源、断言目标。无特殊约定写「按项目默认」。
<!-- /规范 -->

- 新增 `tests/test_list_table.py`：构造 p006 复现输入（列表项后 0 缩进表格行），断言 `md_kx.text` 后 `is_md_equal(orig, formatted)` True、CLI exit 0；补转义保留与列表缩进回归。复用 test_table.py 全量。

### 未知契约清单

<!-- 规范（门禁必留，不得删除） -->
尚未核实的外部 endpoint、API 形态、数据结构、第三方行为须分类标记；核实后删除标记，改为结论并注明验证方式。无则写「无」。
<!-- /规范 -->

- 区分「lazy 表格续行」与「正常段落续行」的实现方案：已验证（s005/d006，2026-08-12）。树/token 层无法区分（lazy 表格行并入段落 inline，无标记）；采用「续行行首 `|`（去空白）则不缩进」守卫于 `_context.py` list renderer 续行处理。副作用：行首 `|` 正常续行仅风格变化，validate 仍通过。

### 风险与回退

- 风险：区分两类续行的实现可能误伤正常段落续行缩进，或复杂化 renderer。
- 回退：AC-005 保证正常列表缩进不变；AC-003 保证转义保留；实现失败可回退至最小修复（仅对 lazy 表格行不缩进）。

### 依赖与约束

- 无前置；不引入新依赖；保持 build_mdit enable table（转义保留）。

### Finalization 时更新的 blueprint

- `docs/blueprint/domain.md`：如有表格/列表边界概念补充。
