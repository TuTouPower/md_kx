# Task review t008（reviewer_focus: 测试）

- task：`t008_table_three_output_styles`
- spec：`docs/tasks/t008_table_three_output_styles/spec.md`
- diff_anchor：`d00127287022ce001bcacb946562d71a6c2dca45`
- target：`git diff d00127287022ce001bcacb946562d71a6c2dca45`
- round：1
- reviewed_at：2026-08-13 14:50 UTC+8

reviewed_scope: b4700a4556a92ef3

## Findings

### t008_test_f001 - pad 分隔行「随列宽」关键行为无有效测试（假绿）

- 严重度：important
- 锚点：AC-004「分隔行长度随列宽；同一列各行（含分隔行）外层 `|` 对齐」、AC-005「pad 在保留冒号前提下按列宽拉长分隔段」
- 位置：`tests/test_table.py:36`（test_pad_separator_tracks_column_width）、`tests/test_table.py:29`（test_pad_aligned）、`tests/test_table.py:58`（test_alignment_colons_pad）
- 问题：三个 pad 用例的输入列宽全部 ≤ 固定 marker 长度（无对齐时 `---`=3，带冒号时 4/5），分隔行从未真正「随列宽拉长」。`test_pad_separator_tracks_column_width` 用 `TABLE_MD`（内容 1 字符、分隔段 3 宽），列宽恰好等于 marker 长度，断言 `| --- | --- |` 无法区分「分隔行长度随列宽」与「分隔行固定 3 宽」的退化实现——若实现把分隔行硬编码 3 宽（列宽 5 时外层 `|` 不对齐、违反 AC-004），此测试照常通过，属「测试存在但验证的是假行为」。实测复验：列宽 5 的输入 pad 输出为 `| aaaaa | b   |\n| ---   | --- |\n| 1     | 2   |\n`——分隔行以尾部补空格达列宽（`---  `），`-` 段并未拉长，与 AC-005「拉长分隔段」文字存在偏差，该行为无任何断言锚定，AC-004 的「含分隔行外层对齐」在列宽 > marker 场景同样零覆盖。注：实现与 spec 文字的符合度由 code reviewer 裁决，本 finding 锚定的是「覆盖假绿 + 行为无测试锚定」这一测试侧事实。
- 建议：新增列宽 > 3 的 pad 用例（纯文本列 + 左/中/右冒号列），精确断言分隔行形态、外层 `|` 对齐及二次格式化幂等。

### t008_test_f002 - AC-006 转义竖线断言过弱，未验证「不拆列」；转义场景幂等覆盖被删

- 严重度：minor
- 锚点：AC-006「`\|` 仍为单元格内容、不拆列」
- 位置：`tests/test_table.py:67`（test_escaped_pipe_preserved）
- 问题：`assert "x\\|y" in out` 只验证内容包含：若渲染把 `x\|y` 单元格拆成多列（`x\|y` 字符串仍出现在某列），断言照常通过，「不拆列」未获验证。旧版该测试含二次格式化幂等断言（`out2 = md_kx.text(out, ...); assert out == out2`），新版删除后转义竖线场景的幂等无覆盖（`test_idempotent` 用无转义 `TABLE_MD`）。
- 建议：改为整行精确输出断言（或断言列数/结构），并恢复转义竖线场景的幂等断言。

### t008_test_f003 - 旧测试整体删除未写明理由

- 严重度：minor
- 锚点：spec 上下文区「测试策略」——「原 `none`/旧 `compact` 语义测试失效，按项目 TDD 规则整体删除并写明理由，不就地改旧断言」
- 位置：`tests/test_table.py`（文件头无删除说明注释）、`docs/tasks/t008_table_three_output_styles/task.md`（实施笔记为「无」）
- 问题：删除本身合法（`none` 已删除、旧 `compact` 语义重定义为 spaced，语义失效且 spec 已批准整体重写），等价测试（对齐冒号、转义竖线、幂等、无表文档、CLI 指定）均已迁移或新建。但「写明理由」未落实：测试文件与 task.md 均无任何删除说明。
- 建议：在 `tests/test_table.py` 头部或 task.md 实施笔记补一句整体重写理由（旧 none/compact 语义失效）。

## 结论

- 前轮 finding 复核（Round N≥2 才写）：Round 1，无
- 改测方向复核：无「迁就实现」的改测。`tests/test_list_table.py` 的 `compact`→`spaced` 迁移属 spec 测试策略批准的语义迁移（工具参数/默认值变化，lazy 表格行为断言意图未变）；`tests/test_table.py` 整体重写按新三风格语义新建精确断言，旧测试整体删除而非就地改旧预期。
- 本轮新发现：3 条
- 未进表的提示：
  - AC-010 仅有 API 层默认断言（`test_default_mode_is_spaced`，等价差分断言可证伪默认值偏离）；CLI 无参数且无配置的默认路径无直接测试，但 CLI 与 API 共享 `DEFAULT_OPTS["table_mode"]`，风险低，可选扩展。
  - `tests/test_list_table.py:50` 的 `assert "|" in out` 为存在性断言（旧测试迁移保留，非新增）；能捕获渲染返回空串，幂等断言为主体，未进表。
  - pad 宽列输出 `| ---   |`（补空格而非 `-` 拉长）与 AC-005 文字偏差，建议 code reviewer 核实实现与 spec 符合度并裁决是否改 spec 表述。
- 总体判断：AC-004/AC-005 的关键行为（分隔行随列宽、含分隔行的外层对齐）存在假绿测试，且实测宽列行为无任何测试锚定，未解决 important 1 条。
- 系统性 follow-up：无

### AC 复验披露

- AC-001：`re_verified`——三种风格各自精确字符串断言（`tests/test_table.py:15-33`），重跑 `pytest tests/test_table.py tests/test_list_table.py -q` 全绿（27 passed）。
- AC-002：`re_verified`——断言 `|a|b|\n|---|---|\n|1|2|\n`（`tests/test_table.py:18`）。
- AC-003：`re_verified`——断言 `spaced` 输出 == `TABLE_MD` 及 `| a | bb |...` 原样输出（同列宽度不同不补齐，`tests/test_table.py:23-26`）。
- AC-004：`re_verified`（有缺口）——列宽 3 场景的「有效文本两侧至少一空格、外层对齐」有精确断言；「分隔行长度随列宽 / 含分隔行外层对齐」在列宽 > marker 场景无测试，见 f001。
- AC-005：`re_verified`（有缺口）——compact/spaced/pad 冒号位置均有精确断言（`tests/test_table.py:44-64`）；pad「按列宽拉长分隔段」场景（列宽 > marker）无覆盖，见 f001。
- AC-006：`re_verified`——三风格循环断言 `x\|y` 内容保留（`tests/test_table.py:67-72`）；「不拆列」为弱断言，见 f002。
- AC-007：`re_verified`——compact `||`、spaced `|  |`、pad 按列宽补空格均有精确断言（`tests/test_table.py:75-84`）。
- AC-008：`re_verified`——三种风格各自二次格式化无 diff（`tests/test_table.py:87-92`），重跑通过。
- AC-009：`re_verified`——三风格输出两两一致断言（`tests/test_table.py:95-99`），符合「有意不测」声明（不逐 token 比对）。
- AC-010：`re_verified`——API 默认输出 == 显式 spaced 输出（`tests/test_table.py:10-12`），可证伪默认值偏离；CLI 纯默认路径无直接测试（结论段已提示，共享 `DEFAULT_OPTS`）。
- AC-011：`re_verified`——tmp_path 真实 `.md_kx.toml`（pad）叠加 CLI `--table-mode=compact` 断言 CLI 优先，去掉 CLI 参数断言配置生效（`tests/test_table.py:102-111`），真实文件读写非 mock。
- AC-012：`re_verified`——CLI 非法值抛 `SystemExit` 且文件未改（`tests/test_table.py:114-121`）；配置非法值 `run` 返回 1、stderr 含 `Invalid 'table_mode' value` 且文件未改（`tests/test_table.py:124-132`），重跑通过。

coverage = 12 / 12

verdict: FAIL

## Round 2 (2026-08-13 14:57 UTC+8)

reviewed_scope: 92d0c12fc32fa787

## Findings（Round 2 新增）

### t008_test_f004 - f002 修不彻底：「不拆列」断言换成行数断言，对拆列恒真（锚错维度）

- 严重度：minor
- 锚点：AC-006「`\|` 仍为单元格内容、不拆列」
- 位置：`tests/test_table.py:98-99`（`len(out.splitlines()) == 3` 与注释「拆列会新增行」）
- 问题：拆列改变的是列数而非行数，行数断言对「不拆列」无区分力。实证反例：`| a | b |\n| --- | --- |\n| x | y | z |\n`（`x\|y` 被拆成 `x`、`y` 两列）行数仍为 3，`len(...) == 3` 通过；注释「拆列会新增行」推理错误。f002 建议的「整行精确输出断言（或断言列数/结构）」未落实，只是把无区分力的维度从「内容包含」换成「行数」。另一半已修：幂等断言恢复（`tests/test_table.py:100`）。注：`assert "x\\|y" in out`（:97）仍能捕获转义丢失（`x|y` 不含 `x\|y`）与字面拆列，AC-006 整体覆盖未假绿，故不升级。
- 建议：改为整行精确断言（各风格预期输出逐字比对）或断言输出列数与表头列数一致；顺带修正注释。

### t008_test_f005 - f001 修复未完全落实：right 冒号列与纯文本列超宽拉长、宽列输出幂等仍无锚定

- 严重度：minor
- 锚点：AC-004「分隔行长度随列宽」、AC-005「pad 保留冒号前提下按列宽拉长分隔段」（f001 建议矩阵「纯文本列 + 左/中/右冒号列 + 二次格式化幂等」）
- 位置：`tests/test_table.py:49-57`（test_pad_wide_column_separator_stretches）、`tests/test_table.py:60-66`（test_pad_center_marker_stretches）
- 问题：新测试只覆盖 left 冒号列超宽（列 1 宽 6 > min 4，断言 `:-----`）与 center 超宽（列 2 宽 8 > min 5，断言 `:------:`）。right 冒号列超宽（列宽 6 时 `---:` 应拉长为 `----:`）与纯文本列超宽（列宽 6 时 `---` 应拉长为 `------`）无用例，若实现把这两类分隔段做成「定长 marker + 补空格」无测试红；f001 建议的「二次格式化幂等」在宽列场景亦未断言（`test_idempotent` 仅用无冒号 `TABLE_MD`，列宽 = marker 3）。核心 left/center 拉长与外层 `|` 对齐已锚定，此缺口不阻断。
- 建议：补 right 冒号列与纯文本列宽 > marker 的分隔段精确断言；宽列 pad 输出再格式化一次断言无 diff。

## 结论（Round 2）

- 前轮 finding 复核（以 diff 与代码核实，不采信处置表自称「已修」）：
  - **t008_test_f001（important）：已消除**。`test_pad_wide_column_separator_stretches` 列 1（left，宽 6）断言 `| :----- |`、`test_pad_center_marker_stretches` 列 2（center，宽 8）断言 `| :------: |`。退化实证（模拟渲染逻辑）：定长 marker（`| :--- ... |`）、定长 + ljust 补空格（`| :---     ... |`）、旧式冒号外接（`| :--------: |`）均 ≠ 测试断言期望 → 退化实现必红；「随列宽拉长」与「定长 marker + 补空格」可区分。外层对齐由 `lines[0]`/`lines[2]` 整行精确断言锚定。残余覆盖缺口见 f005（minor）。
  - **t008_test_f002（minor）：部分修复**。幂等断言已恢复（`tests/test_table.py:100`）；「不拆列」改由行数断言承担但对拆列恒真，修不彻底，以新 finding t008_test_f004 记录。
  - **t008_test_f003（minor）：已消除**。`tests/test_table.py:1-4` 头部注释写明整体删除重写理由（none 删除、compact 语义重定义、整体删除而非就地改预期）。
- 改测方向复核：无「迁就实现」的改测。`tests/test_list_table.py` 的 `compact`→`spaced` 迁移属 spec 测试策略批准的语义迁移（lazy 表格行为意图不变）；`tests/test_table.py` 整体重写有理由注释，非就地改旧预期。
- 本轮新发现：2 条（t008_test_f004、t008_test_f005，均 minor）
- 未进表的提示：
  - AC-010 CLI 纯默认路径（无参数且无配置）无直接测试，仅 API 层差分断言与共享 `DEFAULT_OPTS` 兜底（Round 1 已披露，无变化）。
  - `tests/test_list_table.py:50` 的 `assert "|" in out` 为存在性断言（旧测试迁移保留，非本轮新增），幂等断言为主体，维持 Round 1 不入表判定。
  - `test_pad_separator_tracks_column_width`（`tests/test_table.py:41-46`）列宽 = marker 宽，本身仍无法区分拉长与定长，但该区分职责已由两个宽列新测试承接，旧用例保留为基础形态断言，不构成新 finding。
- 总体判断：前轮 important（f001）与 minor（f003）已真修，f002 部分修复（沿 minor），本轮新增 2 条 minor；无未解决 critical / important。
- 系统性 follow-up：无

### AC 复验披露（Round 2）

- AC-001：`re_verified`——compact/spaced/pad 各自整行精确断言（`tests/test_table.py:20-38`），重跑 `pytest tests/test_table.py tests/test_list_table.py -q` 29 passed。
- AC-002：`re_verified`——`test_compact_zero_padding` 断言 `|a|b|\n|---|---|\n|1|2|\n`。
- AC-003：`re_verified`——`test_spaced_one_padding` 断言 `== TABLE_MD` 及 `| a | bb |` 同列宽度不一致不补齐。
- AC-004：`re_verified`（有残余 minor 缺口）——外层对齐与 left/center 拉长由宽列测试精确断言（f001 已修，实证退化必红）；right/纯文本列超宽缺口见 f005。
- AC-005：`re_verified`（有残余 minor 缺口）——compact/spaced 冒号整行断言、pad 冒号保留 + left/center 拉长（`tests/test_table.py:69-89`、49-66）；right 超宽见 f005。
- AC-006：`re_verified`（断言维度有 minor 缺陷）——内容保留 + 幂等断言有效；「不拆列」行数断言无区分力（实测 `| x | y | z |` 3 行通过），见 f004。
- AC-007：`re_verified`——compact `|a||`、spaced `| a |  |`、pad 补空格整行精确断言（`tests/test_table.py:103-112`）。
- AC-008：`re_verified`——`test_idempotent` 三风格二次格式化无 diff + 转义场景幂等（`tests/test_table.py:100`、115-120）。
- AC-009：`re_verified`——三风格输出两两一致（`tests/test_table.py:123-127`），符合「有意不测」声明。
- AC-010：`re_verified`——API 层差分断言可证伪默认偏离（`tests/test_table.py:15-17`）；CLI 纯默认路径无直接测试（结论段已提示）。
- AC-011：`re_verified`——tmp_path 真实 `.md_kx.toml`（pad）叠加 CLI `--table-mode=compact` 断言 CLI 优先、去 CLI 参数断言配置生效（`tests/test_table.py:130-139`），真实文件读写非 mock。
- AC-012：`re_verified`——CLI 非法值（none/wide/空格）`SystemExit` 且文件不改；配置非法值 run 返回 1、stderr 含 `Invalid 'table_mode' value` 且文件不改（`tests/test_table.py:142-160`）。

coverage = 12 / 12

verdict: PASS

## Round 3 (2026-08-13 15:00 UTC+8)

reviewed_scope: cff7f86cc3de4ef7

## Findings（Round 3 新增）

本轮无新 finding。

## 结论（Round 3）

- 前轮 finding 复核（以 diff 与代码核实，不采信处置表自称「已修」）：
  - **t008_test_f004（minor）：已消除**。`test_escaped_pipe_preserved`（`tests/test_table.py:117-132`）已落实整行精确断言：expected 字典给出 compact/spaced/pad 三种完整输出，`assert out == expected[mode]` 逐字比对，行数断言已废除。拆列必然改变输出行内容与结构，预期不匹配必红——Round 2 实证反例 `| x | y | z |`（行数 3 仍通过）在当前断言下不可能通过。幂等断言保留（`tests/test_table.py:130-132`，`text(out+"\n") == text(md)` 差分式，两侧输入不同、输出不一致则红）。f002 建议的两点（整行精确断言 + 恢复转义幂等）完整落实，错误注释（「拆列会新增行」）已随重写移除。
  - **t008_test_f005（minor）：已消除**。三个缺口全补，且各断言独立可证伪：
    - `test_pad_right_marker_stretches`（`tests/test_table.py:69-75`）：right 冒号列超宽（列 2 宽 8）断言 `| :--- | -------: |`（7 dash + ':'）。退化实现「定长 marker + 补空格」输出 `---     ` ≠ 预期 → 必红。
    - `test_pad_plain_wide_column`（`tests/test_table.py:78-84`）：纯文本列超宽（列 1 宽 6）断言 6 dash `| ------ |`，定长+补空格（`---   `）必红。
    - `test_pad_wide_column_idempotent`（`tests/test_table.py:87-91`）：宽列（left 冒号列宽 6）pad 二次格式化无 diff，宽列幂等已有锚定。
    - 预期值均按列宽规则独立推导（列宽 = max(内容宽, marker 宽)；left/center/right marker 定宽 4/5/4），非抄实现输出。
  - 前两轮其他 finding：f001（important）、f002（幂等部分）、f003 复核结论维持，无回退。
- 改测方向复核：无「迁就实现」的改测。f004/f005 修复均为断言增强方向（包含→整行精确、补缺失 case），`tests/test_list_table.py` 的 `compact`→`spaced` 迁移属 spec 测试策略批准的语义迁移（lazy 表格行为意图不变），维持 Round 1/2 判定。
- 本轮新发现：0 条
- 未进表的提示（维持 Round 1/2 披露，无变化）：
  - AC-010 CLI 纯默认路径（无参数且无配置）无直接测试，仅 API 层差分断言与共享 `DEFAULT_OPTS` 兜底。
  - `tests/test_list_table.py:50` 的 `assert "|" in out` 为存在性断言（旧测试迁移保留，幂等断言为主体）。
  - `test_pad_separator_tracks_column_width`（`tests/test_table.py:41-46`）列宽 = marker 宽，为基础形态断言，拉长/定长区分职责已由宽列测试承接。
- 总体判断：重跑 `pytest tests/test_table.py tests/test_list_table.py -q` 32 passed；前轮 2 条 minor 均真修，修复未以弱化形式替换、无恒真/无区分力断言，无未解决 critical / important。
- 系统性 follow-up：无

### AC 复验披露（Round 3）

- AC-001：`re_verified`——compact/spaced/pad 三风格整行精确断言（`tests/test_table.py:23`、28-31、38），重跑 32 passed。
- AC-002：`re_verified`——`test_compact_zero_padding` 断言 `|a|b|\n|---|---|\n|1|2|\n`。
- AC-003：`re_verified`——`test_spaced_one_padding` 断言 `== TABLE_MD` 与 `| a | bb |` 同列宽不一致不补齐。
- AC-004：`re_verified`——pad 外层对齐含分隔行（:38）、分隔行随列宽（:45-46）、纯文本/left 冒号宽列拉长（:56、84）整行断言。
- AC-005：`re_verified`——compact/spaced 冒号整行断言（:98、105），pad 保留冒号 + left/center/right 超宽拉长（:56、66、75、113-114）。
- AC-006：`re_verified`——`test_escaped_pipe_preserved` 三风格整行精确断言 + 幂等（:117-132），「不拆列」可证伪。
- AC-007：`re_verified`——`test_empty_cells` 三风格整行断言（:138-144）。
- AC-008：`re_verified`——`test_idempotent`（:149-152）+ `test_pad_wide_column_idempotent`（:87-91）+ 转义场景幂等（:130-132）。
- AC-009：`re_verified`——`test_no_table_output_identical` 三风格输出两两一致（:158-159），符合「有意不测」声明（不逐 token 比对）。
- AC-010：`re_verified`——API 默认输出 == 显式 spaced 输出（:17），可证伪默认偏离；CLI 纯默认路径无直接测试（结论段已提示，共享 `DEFAULT_OPTS`）。
- AC-011：`re_verified`——tmp_path 真实 `.md_kx.toml`（pad）叠加 CLI `--table-mode=compact` 断言 CLI 优先、去 CLI 参数断言配置生效（:162-171），真实文件读写非 mock。
- AC-012：`re_verified`——CLI 非法值（none/wide/空格）`SystemExit` 且文件不改（:174-181）；配置非法值 run 返回 1、stderr 含 `Invalid 'table_mode' value` 且文件不改（:184-192）。

coverage = 12 / 12

verdict: PASS
