# Task spec

## 背景

p008：表格格式化必须能明确选出三种输出风格，且三种风格的单元格空白规则互不相同。现状（t003 三态 `none`/`pad`/`compact`）中 `compact` 实际输出两侧各一空格（`| a | b |`），与所需 `spaced` 相同，「紧凑 = 不按列对齐」表述有歧义。本 task 将 `table_mode` 重定义为 `compact`（两侧零空格）/ `spaced`（两侧各一空格）/ `pad`（按列补齐）三风格，删除 `none`，默认值改为 `spaced`。用户已确认完全重定义并删除 `none`（2026-08-13 询问确认）。

## 契约区

### 范围

- 重定义 `table_mode` 配置项与 `--table-mode` CLI 选项：合法值 `compact` / `spaced` / `pad`，默认 `spaced`，删除 `none`
- 按三种风格的空白规则重写表格渲染（`renderer/_context.py` 的 `table` 渲染器及分隔行/对齐/空单元格处理）
- 同步更新配置校验（`_conf.py`）、CLI choices 与帮助文本（`_cli.py`）、现有测试（`tests/test_table.py`、`tests/test_list_table.py` 中的 `table_mode` 参数迁移）
- 更新已生效 spec `docs/specs/builtin_table_handling.md` 与用户文档（`docs/guides/style.md`、`docs/guides/usage.md`、README 中 `--table-mode` 相关描述）
- 同一次格式化中所有表用同一风格；风格只影响表格行的空白与列宽，不改变单元格有效文本、不改变表格行列结构、不改变表以外文档

### 非范围

- 不改表格解析：markdown-it 的 `table` 规则始终启用（`_util.py` 现状）保持不变
- 不做三种风格之外的表格功能（跨列 span、列合并、ragged 行数不齐表的语义变更等）
- 不新增其他风格名

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

- [ ] AC-001：同一输入表分别指定 `compact` / `spaced` / `pad`，输出分别符合 p008 三种风格示例的空白规则（compact 零空格、spaced 两侧各一空格、pad 按列补齐）
- [ ] AC-002：`compact` 输出中，单元格有效文本与两侧 `|` 之间无空格；分隔行两侧也无空格（`|a|b|`、`|---|---|`）
- [ ] AC-003：`spaced` 输出中，单元格有效文本与两侧 `|` 之间各恰好一个空格，同一列宽度可以不同；分隔行为 `| --- |`
- [ ] AC-004：`pad` 输出中，同一列各行（含分隔行）外层 `|` 对齐，有效文本两侧至少各一个空格；分隔行长度随列宽
- [ ] AC-005：含左/中/右对齐冒号的输入表，三种风格下输出均表示同一对齐语义；compact 冒号贴竖线内侧不加额外空格（`:---|`、`|:---:|`、`|---:`），spaced 冒号外侧各留一个空格，pad 在保留冒号前提下按列宽拉长分隔段
- [ ] AC-006：含转义竖线 `\|` 的单元格，三种风格下 `\|` 仍为单元格内容、不拆列
- [ ] AC-007：含空单元格的表，compact 输出相邻竖线 `||`，spaced 输出 `| |`，pad 按该列宽度补空格
- [ ] AC-008：同一风格下对输出再格式化一次，文件不发生变化（三种风格各自幂等）
- [ ] AC-009：不含表格的文档，三种风格下输出一致
- [ ] AC-010：未指定风格时（无 CLI 参数且无配置项），输出为 `spaced` 风格
- [ ] AC-011：CLI 与仓库配置均可指定风格，命令行优先于仓库配置
- [ ] AC-012：`none` 及三种风格之外的任何名字，在 CLI 与配置中均被拒绝并报错，文件不被修改

### 可测试性声明

<!-- 规范（门禁必留，不得删除） -->

逐条说明哪些 AC 不可自动测试及原因；全部可测则写「全部 AC 可自动测试」。

<!-- /规范 -->

- 全部 AC 可自动测试：AC-001 至 AC-010 用 `md_kx.text` 断言输出与幂等；AC-011 用临时目录写 `.md_kx.toml` 叠加 CLI 参数验证优先级；AC-012 用 CLI 非零退出码与配置解析 `InvalidConfError` 断言。

## 上下文区

- 来源：p008（2026-08-13 核实：现状为 t003 三态 `none`/`pad`/`compact`，`compact` 实际输出两侧一空格；用户确认按 p008 完全重定义并删除 `none`）

### 有意不测

<!-- 规范（门禁必留，不得删除） -->

已判定不写测试的分支与原因。reviewer 不得据此出 blocking finding。无则写「无」。

<!-- /规范 -->

- 行数不齐（ragged）表格：上游 markdown-it lenient 解析按表头列数截断，三种风格下均遵循该行为（见 `docs/findings/d004_ragged_table_gfm_semantics.md`），非本 task 引入的语义变更
- 非表格文档逐内容比对：AC-009 只需断言三风格输出两两一致，不逐 token 比对

### 测试策略

<!-- 规范（门禁必留，不得删除） -->

mock 边界、fixture 来源、断言目标。无特殊约定写「按项目默认」。

<!-- /规范 -->

- `tests/test_table.py` 按新三风格整体重写：原 `none`/旧 `compact` 语义测试失效，按项目 TDD 规则整体删除并写明理由，不就地改旧断言
- `tests/test_list_table.py` 中作为工具参数的 `table_mode="compact"` 迁移为 `"spaced"`（或按用例意图改用合法风格），lazy 表格行为测试意图不变
- fixture 用内联 Markdown 字符串（复用现有 `TABLE_MD` 风格），CLI 用例沿用 `run()` helper
- 对齐冒号、转义竖线、空单元格、幂等用例覆盖 AC-005 至 AC-008

### 未知契约清单

<!-- 规范（门禁必留，不得删除） -->

尚未核实的外部 endpoint、API 形态、数据结构、第三方行为须分类标记；核实后删除标记，改为结论并注明验证方式。无则写「无」。

<!-- /规范 -->

- 无

### 风险与回退

- 风险：破坏性变更——既有配置 `table_mode=none|compact` 用户的输出行为改变；`--table-mode none` 调用方会收到非法值报错；旧测试语义失效需整体迁移
- 回退：实现 commit 整体 revert 恢复 t003 三态；spec 与文档回退由 `finish` 前复核确认

### 依赖与约束

- `markdown-it-py` 的 `table` 规则始终启用（`src/md_kx/_util.py`）不变
- 配置非法值经 `_validate_values` 拒绝的机制沿用，仅更新合法值集合
- 旧测试语义失效时新增覆盖新语义的测试；旧测试原样保留或整体删除并写明理由，禁止就地改旧预期（项目 TDD 规则）
- 无前置 task 依赖

### Finalization 时更新的 blueprint

- `docs/specs/builtin_table_handling.md`：三态（none/pad/compact）改写为三风格（compact/spaced/pad），默认值改 spaced
- `docs/guides/style.md`：`table_mode` 描述更新（删除 none、compact 语义重定义、新增 spaced）
- `docs/guides/usage.md`：`--table-mode` 表格行、示例与配置示例更新
- `README.md`：若含 `--table-mode` 相关描述则同步更新
