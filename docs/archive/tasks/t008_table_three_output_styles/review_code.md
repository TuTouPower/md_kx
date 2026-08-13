# Task review t008（reviewer_focus: 代码）

- task：`t008_table_three_output_styles`
- spec：`docs/tasks/t008_table_three_output_styles/spec.md`
- diff_anchor：`d00127287022ce001bcacb946562d71a6c2dca45`
- target：`git diff d00127287022ce001bcacb946562d71a6c2dca45`
- round：1
- reviewed_at：2026-08-13 14:48 UTC+8
reviewed_scope: b4700a4556a92ef3

## Findings

### t008_code_f001 - pad 风格分隔行未按列宽拉长分隔段（dash），冒号位置错位

- 严重度：important
- 锚点：AC-005「pad 在保留冒号前提下按列宽拉长分隔段」
- 位置：`src/md_kx/renderer/_context.py:759-770`（`table()` pad 分支，其中 `:767` 用 `cell.ljust(widths[i])` 生成分隔 cell）；正确实现 `_align_marker`（`:693-707`）与 `_separator_row` 的 widths 分支（`:719-733`）成死代码，从未被接线
- 问题：pad 分支先取定长 marker（`_separator_row(aligns, num_cols)` 不传 widths，返回 `:---`/`:---:`/`---:` 等固定 3-4 字符段），再 `ljust(widths[i])` 补空格。当任一列宽超过 marker 固有长度时，分隔段（dash）不拉长、冒号不贴边界，与 AC-005「按列宽拉长分隔段」不符。实测复现：
  - 右对齐、列宽 6：`'| x    | y      |'` / `'| :--- | ---:   |'` / `'| aa   | bbbbbb |'`——分隔 cell 为 `---:  `（3 dash + 冒号 + 2 空格），冒号未贴右边界；正确应为 `-----:`（5 dash + 冒号）
  - 居中、列宽 8：`'| h        |'` / `'| :---:    |'` / `'| abcdefgh |'`——分隔 cell 为 `:---:   `，右侧冒号后 3 空格；正确应为 `:------:`
  - 左对齐、列宽 5：`'| :---  |'`——dash 未延伸至右边界；正确应为 `:----`
  - 现有测试 `test_alignment_colons_pad`、`test_pad_separator_tracks_column_width`、`test_pad_aligned`、`test_empty_cells` 的输入列宽均恰好等于 marker 长度（3/4/5），ljust 与 dash 拉长结果无差异，故测试全绿但未覆盖该语义（测试层问题归 test reviewer，本 finding 只锚定实现）
- 建议：pad 分支改为 `sep_cells = _separator_row(aligns, num_cols, widths)`（widths 分支已用 `_align_marker` 正确拉长 dash），`sep` 直接 `"| " + " | ".join(sep_cells) + " |"` 拼装，删除对 sep_cells 的 `ljust`；同时消除 `_align_marker` 死代码

## 结论

- 前轮 finding 复核：无（round 1）
- 本轮新发现：1 条
- 未进表的提示：
  - 文件过大：`src/md_kx/renderer/_context.py` 共 837 行（≥800 阈值），本 task 净增 17 行（+46/-29）；未发现由过大直接导致的可观测缺陷，故不单独出 finding
  - 范围外观察：`src/md_kx/_util.py:40` 注释「The table renderer handles all three modes, including "none" (pass-through)」已过时——`none` 已删除，现为三风格。`_util.py` 未被本 diff 触及，属范围外，建议随文档更新一并处理
  - 复杂度：`table()` 三分支 if/elif/else、`_separator_row` 单循环+单分支，均远低于阈值；`_validate_values` 的 `noqa: C901` 为既有代码，未新增分支
- AC 复验方式：
  - AC-001（re_verified）：实跑 `md_kx.text` 三风格断言空白规则，compact 零空格 / spaced 两侧一空格 / pad 按列补齐（数据行）成立
  - AC-002（re_verified）：compact 输出 `|x|y|`、`|---|---|`，repr 确认
  - AC-003（re_verified）：spaced 输出 `| x | y |`、`| --- | --- |`，同列宽度可不一致（`| a | bb |` 原样保持）
  - AC-004（re_verified）：pad 外层 `|` 对齐，repr 逐字符比对分隔行与数据行宽度一致，有效文本两侧 ≥1 空格
  - AC-005（re_verified，部分违反）：compact/spaced 冒号位置符合（`|:---|`、`|:---:|`、`|---:|` 与 `| :--- |`、`| :---: |`、`| ---: |`）；pad 分隔段未按列宽拉长，见 f001
  - AC-006（re_verified）：`x\|y` 三种风格下保留、不拆列
  - AC-007（re_verified）：compact `||`、spaced `|  |`、pad 按列宽补空格
  - AC-008（re_verified）：三种风格二次格式化输出不变（实跑断言 True）
  - AC-009（re_verified）：非表格文档三风格输出两两一致
  - AC-010（re_verified）：API 无 options 与 CLI 无参数无配置时均为 spaced
  - AC-011（re_verified）：`.md_kx.toml` 写 `table_mode="pad"` 生效，叠加 `--table-mode compact` 时 CLI 覆盖配置
  - AC-012（re_verified）：CLI `--table-mode none` argparse 拒绝 exit 2；配置 `table_mode="none"` 抛 `InvalidConfError` exit 1，文件未被修改
  - coverage = 12 / 12
- 总体判断：AC-001~004、006~012 实现与 spec 一致；AC-005 的 pad 分隔段拉长语义未实现（`_align_marker` 正确实现未接线），存在 1 条未解决 important
- 系统性 follow-up：无

verdict: FAIL

## Round 2 (2026-08-13 14:56 UTC+8)

- round：2
- reviewed_at：2026-08-13 14:56 UTC+8
- reviewed_scope: 92d0c12fc32fa787
- 审查对象：`git diff d00127287022ce001bcacb946562d71a6c2dca45`（含 f001 修复的工作区现状）

## Findings

本轮新发现：0 条。

## 结论

- 前轮 finding 复核（以 diff 与实测为准，不采信处置表自述）：
  - **t008_code_f001（important，pad 分隔行未拉长、冒号错位）→ 已消除**。修复路径与 Round 1 建议一致：
    - `src/md_kx/renderer/_context.py:777` pad 分支改为 `sep_cells = _separator_row(aligns, num_cols, widths)`，`:781` 直接 `"| " + " | ".join(sep_cells) + " |"` 拼装，对 sep_cells 的 `ljust` 已删除；`_align_marker` 经 `:740` widths 分支接线，Round 1 指出的死代码已消除。
    - `_min_marker_width`（`:719-726`）提供列宽下限，与 `_fixed_marker` 长度一致（center=5、left/right=4、none=3），窄列时分隔 marker 不塌缩。
    - 实测复现 Round 1 三个失败场景：右对齐列宽 6 → `| -----: |`（5 dash + 冒号贴边）；居中列宽 8 → `| :------: |`；左对齐列宽 5 → `| :---- |`。数据行、分隔行外层 `|` 对齐，行为与 AC-005「pad 在保留冒号前提下按列宽拉长分隔段」一致。
    - 修复引入的边界扫描：`_separator_row` 返回类型 str→list[str] 变更，`_context.py` 内 3 处调用点（`:767` compact、`:777` pad、`:782` spaced）全部同步，无外部引用；`widths[i]` 索引在 pad 分支构建 `len(widths)==num_cols`，安全；`max(widths[i], 3)` 为双保险。未发现新问题。
  - 结论：处置表「已修」与代码及实测一致，f001 彻底消除，无「修不彻底」。
- 本轮新发现：0 条
- 未进表的提示：
  - 文件过大：`src/md_kx/renderer/_context.py` 共 847 行（≥800 阈值），修复轮净增 10 行；未发现由过大直接导致的可观测缺陷（沿用 Round 1 判定）
  - 范围外观察：`src/md_kx/_util.py:39` 注释「The table renderer handles all three modes, including "none" (pass-through)」仍过时（`none` 已删），`_util.py` 未被本 diff 触及，建议随文档更新一并处理（Round 1 已提示，仍存在）
  - 范围外观察：pad 列宽按 `len(cell)` 字符数计，CJK 等宽字符在等宽终端显示下不严格对齐；与上游 mdformat 行为一致、spec 未要求，非本 task 引入
  - 复杂度：`table()` 三分支、`_separator_row` 单循环单分支，远低于阈值
- AC 复验方式（本轮独立重跑）：
  - AC-001（re_verified）：实测三风格输出，compact 零空格 / spaced 两侧各一空格 / pad 按列补齐
  - AC-002（re_verified）：compact 输出 `|a|b|`、`|---|---|`（实测 + `test_compact_zero_padding`）
  - AC-003（re_verified）：spaced `| a | b |`、`| --- | --- |`，同列宽可不一致（`test_spaced_one_padding`）
  - AC-004（re_verified）：pad 外层 `|` 对齐含分隔行（实测宽列 + `test_pad_wide_column_separator_stretches`、`test_pad_separator_tracks_column_width`）
  - AC-005（re_verified）：compact `|:---|`/`|:---:|`/`|---:|`、spaced `| :--- |`、pad 宽列拉长冒号贴边（实测 f001 三场景 + `test_pad_center_marker_stretches`）
  - AC-006（re_verified）：`x\|y` 三风格保留、不拆列、幂等（实测 + `test_escaped_pipe_preserved`）
  - AC-007（re_verified）：compact `||`、spaced `|  |`、pad 按列宽补空格（实测 + `test_empty_cells`）
  - AC-008（re_verified）：三风格幂等，含宽列 pad 5 场景手工验证（`test_idempotent` 之外补验）
  - AC-009（re_verified）：无表格文档三风格输出两两一致（实测 True + `test_no_table_output_identical`）
  - AC-010（re_verified）：API 无 options 与 CLI 无参数均为 spaced（`test_default_mode_is_spaced`）
  - AC-011（re_verified）：`.md_kx.toml` 写 `table_mode='pad'` 生效，`--table-mode=spaced` 覆盖配置（实测 + `test_cli_override_conf`）
  - AC-012（re_verified）：CLI `--table-mode=none` exit 2、配置 `table_mode="none"` exit 1 且文件未被修改（实测 + 两个 reject 测试）
  - coverage = 12 / 12
- 总体判断：f001 已按建议彻底修复并经实测确认，修复未引入新问题；AC-001~012 全部满足，无未解决 critical / important，无 minor。
- 系统性 follow-up：无

verdict: PASS

## Round 3 (2026-08-13 15:02 UTC+8)

- round：3（轻量复核轮）
- reviewed_at：2026-08-13 15:02 UTC+8
- reviewed_scope: cff7f86cc3de4ef7
- 审查对象：`git diff d00127287022ce001bcacb946562d71a6c2dca45` 当前工作区现状（Round 2 PASS 后仅补测试断言）
- 本轮指纹 `cff7f86cc3de4ef7` ≠ Round 2 `92d0c12fc32fa787`，差异来源为 `tests/test_table.py` 新增断言（tests 计入指纹，非流程文件），生产代码未变（下述锚点核对）；报告末条 reviewed_scope 已更新为本轮指纹，`check_review_status.py` 将判 ok

## Findings

本轮新发现：0 条。

## 结论

- 前轮 finding 复核（Round 2 结论是否仍成立，以代码与实测为准）：
  - **生产代码未变确认**：`src/md_kx/renderer/_context.py` 与 Round 2 描述逐条吻合——`table()` 三风格分支 `:765-782`（compact `:767` / pad `:777` / spaced `:782` 三调用点）、`_separator_row` widths 分支 `:740` 经 `_align_marker` 接线、`_min_marker_width` `:719`、`_align_marker` `:693`、`_fixed_marker` `:708`；文件总行数 847 与 Round 2 记录一致。`_conf.py`（默认 `spaced`、合法值集合 `{compact, spaced, pad}`）、`_cli.py`（choices 与帮助文本）亦与 Round 1/2 审查对象一致，diff 无新增。
  - **t008_code_f001（important）→ 仍为已消除**：Round 2 确认修复的生产路径（pad 分支 `sep_cells = _separator_row(aligns, num_cols, widths)` + 直接拼装、`_align_marker` 接线）逐字存在，无回退。
- 本轮变化扫描（Round 2 之后）：
  - `tests/test_table.py` 新增 3 用例，均为精确整行字符串断言，无恒真/弱化/条件跳过等 anti-pattern，语义与生产实现及 AC 一致：
    - `test_pad_right_marker_stretches`（AC-005）：右对齐宽列 8 → 期望 `| :--- | -------: |`（7 dash + 冒号贴右边界），与 `_align_marker("right", 8)` = `"-"*7 + ":"` 一致
    - `test_pad_plain_wide_column`（AC-004）：无对齐宽列 6 → 期望 `| ------ | --- |`，与 `_align_marker("none", 6)` = `"-"*6` 一致
    - `test_pad_wide_column_idempotent`（AC-008）：混合对齐宽列二次格式化无 diff
  - `tests/test_list_table.py` 无新变化（Round 2 已含 `spaced` 迁移）。
- 实测验证：`pytest tests/test_table.py` 20 passed；全量 `pytest tests/` 4723 passed, 5 skipped（skip 均为 `exclude` 配置 Python 3.13 条件跳过 `test_config_file.py:82/120/142`、`test_cli.py:389`，与本 task 无关）。
- 本轮新发现：0 条
- 未进表的提示：
  - 文件过大：`src/md_kx/renderer/_context.py` 847 行（≥800 阈值），本 task 未再净增（沿用 Round 1/2 判定，无由过大直接导致的可观测缺陷）
  - 范围外观察：`src/md_kx/_util.py:39` 注释「including "none" (pass-through)」仍过时（`none` 已删），`_util.py` 未被本 diff 触及，建议随文档更新一并处理（Round 1/2 已提示，仍存在）
  - 复杂度：`table()` 三分支、`_separator_row` 单循环单分支，远低于阈值
- AC 复验方式（本轮轻量复核）：
  - AC-001~012（re_verified，全部）：生产代码与 Round 2 锚点逐条一致未变，Round 2 的逐 AC 实测结论继承；本轮新增断言覆盖 AC-004/005/008 并实跑通过（`test_pad_right_marker_stretches`、`test_pad_plain_wide_column`、`test_pad_wide_column_idempotent`），全量 4723 passed 无回归
  - coverage = 12 / 12
- 总体判断：Round 2 PASS 结论仍成立——生产代码未变，新增测试断言精确且与 AC 语义一致，无未解决 critical / important，无 minor。
- 系统性 follow-up：无

verdict: PASS
