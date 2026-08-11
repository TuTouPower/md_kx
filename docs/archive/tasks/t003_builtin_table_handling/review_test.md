# Task review t003（reviewer_focus: 测试）

- task：`t003_builtin_table_handling`
- spec：`docs/tasks/t003_builtin_table_handling/spec.md`
- diff_anchor：`ddcd76a5c2e605d6d6f3490e766b54bbf17676b8`
- target：`git diff ddcd76a5c2e605d6d6f3490e766b54bbf17676b8`
- round：1
- reviewed_at：2026-08-12 00:21 UTC+8

## Findings

### t003_test_f001 - AC-004 断言 `"|" in out` 为弱存在性断言，未验证输出可再解析为合法表格

- 严重度：minor
- 锚点：AC-004
- 位置：`tests/test_table.py:42`（`test_table_syntax_valid`）
- 问题：AC-004 要求"三态下表格语法正确、可正常渲染"，测试仅断言 `"|" in out`。该断言在三态下近乎必然为真（none 原样输出含竖线、pad/compact 渲染器输出含竖线），不独立验证"输出仍是有表头分隔行的合法表格"。例如 renderer 若输出 `| a | b |\n| 1 | 2 |`（丢了分隔行），此测试与 AC-002/003 的子串断言都不会失败。属危险模式清单中"纯存在性断言/存在即通过"的低危变体。
- 建议：改为对输出再 parse 一次确认 table 语义仍在（如启用 table 规则二次 parse 后 `table` token 非空），或将三态下期望的完整输出以相等断言固化。判定 minor 而非 important 的理由：AC-004 的具体形态已由 AC-001（完整相等）、AC-002/003（逐行精确子串）覆盖，本测试仅为跨态冒烟，非该 AC 唯一证据。

### t003_test_f002 - 行数不齐（ragged）表格边界未覆盖，pad/compact 静默丢弃多余单元格

- 严重度：minor
- 锚点：AC-002/AC-004 行为面（内容保留）
- 位置：`tests/test_table.py` 全文件；涉及渲染 `src/mdformat/renderer/_context.py:634-640`（`_table_rows`）
- 问题：所有用例均为行列规整的方形表。对行单元格数不齐的输入 `| a |\n| --- |\n| 1 | b |`：none 模式原样输出（保留 `b`），pad/compact 模式 `b` 被静默丢弃（实测输出 `| a |\n| --- |\n| 1 |`）。该截断源于上游 markdown-it 的 lenient 表格解析（按表头列数截断），非 mdformat renderer 自身逻辑。上下文区"有意不测：无"，此边界无测试也无说明。
- 建议：minimal 处置为在测试中补一个规整表外的行数不齐用例，固化当前行为（none 保留、pad/compact 截断），或在 spec 上下文区"有意不测"登记该分支并说明。判定 minor 依据：该输入不符合 GFM 表格规则（各行列数不一致时非合法表格，属"现有表格语法子集"外），数据丢弃为上游解析器特性，非 mdformat 引入的 AC 缺口，不满足 blocking 硬阈值。

## 结论

- 前轮 finding 复核（Round N≥2 才写）：本报告为首轮，无前轮。
- 改测方向复核：无。`git diff ddcd76a5c2e605d6d6f3490e766b54bbf17676b8` 未修改任何既有测试文件，仅新增 `tests/test_table.py`；无"迁就实现"式改测。
- 本轮新发现：2 条（均 minor）。
- 未进表的提示：`docs/findings/d003_table_rule_enable.md` 报告"需在 DEFAULT_RENDERERS 新增 table 系列 token 渲染器（table_open/thead/tbody/tr/th/td）"，实际仅注册 `table` 一个渲染器。经核查可行：`SyntaxTreeNode` 将 `table_open/thead_open/tr_open/...` 开闭 token 归一为 `table/thead/tr/th/td/inline`，`table` 渲染器自行遍历子节点并只渲染 inline 内容，中间节点不再单发，故不触发 KeyError，与 spike 描述无矛盾。`_table_rows` 对空表、仅表头表、空单元格（`|   |`）均实测无异常。三态输出均经手测复核与实现一致。
- 总体判断：5 条 AC 全部经公共接口（`mdformat.text` / CLI `run`）有测试，无 mock、无 skip/only、无删断言，测试可信；无未解决 critical / important，仅 2 条 minor 可选增强。
- 系统性 follow-up：无。

### AC 复验披露

- AC-001：`re_verified` — 重跑 `test_table_none_untouched` / `_explicit`，并手测默认与显式 none 下 `mdformat.text(TABLE_MD) == TABLE_MD` 成立。
- AC-002：`re_verified` — 重跑 `test_table_pad_aligned`；手测 pad 输出 `| aaa | b |\n| --- | --- |\n| 1   | 2 |` 与实现计算一致。
- AC-003：`re_verified` — 重跑 `test_table_compact`；手测 compact 输出 `| a | b |\n| --- | --- |\n| 1 | 2 |` 无补空格。
- AC-004：`re_verified` — 重跑 `test_table_syntax_valid`（断言强度见 f001）。
- AC-005：`re_verified` — 重跑 `test_no_table_no_regression`；另跑全量 `pytest -q` 4682 passed / 5 skipped（skip 均为既有 3.13 `exclude` 用例，与本 task 无关），无回归。

coverage = 5 / 5

reviewed_scope: eb7752027c1bc5d0

verdict: PASS

## Round 2 (2026-08-12 00:36 UTC+8)

### 前轮 finding 复核（以 git diff 与当前 worktree 为准，不采信处置表自述）

- **t003_test_f001**（AC-004 弱断言 `"|" in out`，minor；处置表 status=已修）：**已修**。当前 `tests/test_table.py:36-43` `test_table_syntax_valid` 断言已改为两段：`out2 = mdformat.text(out, options={"table_mode": mode})` 后 `assert out == out2`（二次格式化幂等）+ `assert "| --- |" in out`（分隔行存在）。Round 1 报告记载的旧 `"|" in out` 近恒真断言已不在文件内（tests/test_table.py 为相对 anchor 的整文件新增，diff 全文见当前 worktree 内容）。修复非「弱化换另一种弱化」：`"| --- |" in out` 直接捕获 f001 所述失败场景（renderer 丢分隔行 → 输出无 `| --- |` → 断言失败），已用只读脚本验证（丢分隔行样本断言为 False，合法表格样本为 True）；幂等断言额外捕获输出再解析不稳定场景。重跑 `uv run --with-requirements tests/requirements.txt pytest tests/test_table.py -q` → 8 passed，无红灯。
- **t003_test_f002**（ragged 边界无覆盖，minor；处置表 status=遗留 fix_ref=p005）：**已按 minor 遗留规则登记**。`docs/pending/todo/p005_ragged_table_cells.md` 存在且字段齐全（现象/影响/根因 markdown-it 上游截断/测试缺口/线索 t003_test_f002/处理「t003 遗留登记」）；处置表行 status=遗留、fix_ref=p005 合法。minor 遗留不阻断，符合「遗留登记到 pending/todo」要求。

### 改测方向复核

- 无「迁就实现」式改测。f001 修复方向是把弱断言改为更强的结构断言（新增幂等 + 分隔行存在），非把预期改向当前实现输出；无既有测试被就地改写为迁就实现。

### 本轮新发现

- 0 条。危险模式扫描（恒真断言 / 删反转 expect / 注释断言 / 弱化断言 / .skip / .only / 静默错误 / mock 误用 / 阈值掩盖 / 条件跳过 / 程序赋值替代真实交互 / 存在即通过）对当前 `tests/test_table.py` 全部 8 个用例逐条过筛无命中。测试全部经公共接口（`mdformat.text` / CLI `run`）触达生产实现，无 mock、无 skip/only、无删断言、无 try/except 吞错。

### 未进表的提示

- `test_table_pad_aligned` / `test_table_compact` 用子串断言，Round 1 已判定可接受（AC-001 完整相等锚定整体，子串验证 pad/compact 具体变换），非本轮新问题。
- 可选覆盖扩展（minor 级，不阻断）：compact 与 none 在已紧凑输入上输出相同，`test_table_compact` 无法区分 compact 主动去 pad 与 none 原样保留；若要更严，可加「输入已补空格、compact 折叠」用例。同属「可再加 case」类，不构成 blocking finding。

### AC 复验披露（Round 2）

- AC-001：`re_verified` — `test_table_none_untouched` / `_explicit` 完整相等断言，重跑 8 passed。
- AC-002：`re_verified` — `test_table_pad_aligned` 断言补空格输出，重跑通过。
- AC-003：`re_verified` — `test_table_compact` 断言无补空格，重跑通过。
- AC-004：`re_verified` — f001 修复后「幂等 + 分隔行存在」断言，已只读脚本验证分隔行断言能捕获丢分隔行失败场景；测试通过。
- AC-005：`re_verified` — `test_no_table_no_regression` 三态下与 baseline 相等，重跑通过。

coverage = 5 / 5

### 总体判断

前轮 2 条 minor 均闭环：f001 断言实质加强且经验证有效，f002 已登记 p005。无未解决 critical / important，本轮无新发现。本轮 PASS。

reviewed_scope: 6ebc6caae00baf0c

verdict: PASS

## Round 3 (2026-08-12 00:56 UTC+8)

### 前轮 finding 复核（以 git diff 与当前 worktree 为准，不采信处置表自述）

- **t003_test_f001**（AC-004 弱断言 `"|" in out`，minor；处置表 status=已修）：**已消除**。当前 `tests/test_table.py:41-43` `test_table_syntax_valid` 仍为「二次格式化幂等 `assert out == out2` + 分隔行存在 `assert "| --- |" in out`」两段断言，f001 所述旧近恒真 `"|" in out` 断言不在文件内。Round 2 已实证分隔行断言能捕获「renderer 丢分隔行」失败场景，本轮复跑 `pytest tests/test_table.py -q` → 9 passed，无红灯。修复未退化、未换形式弱化。
- **t003_test_f002**（ragged 无覆盖，minor；处置表 status=遗留 fix_ref=p005）：**已按 minor 遗留规则登记**。`docs/pending/todo/p005_ragged_table_cells.md` 存在且字段齐全（现象/影响/根因/测试缺口/线索 t003_test_f002/处理「t003 遗留登记」）。minor 遗留不阻断。

### 改测方向复核

- 无「迁就实现」式改测。相对 Round 2 仅新增 `test_alignment_colons_preserved`（`tests/test_table.py:78-85`）为纯新增用例，未就地改写任何既有测试的预期；f001 修复保持 Round 2 已核实的加强形态。

### 本轮新发现

- 1 条（important）：t003_test_f003。

### t003_test_f003 - `test_alignment_colons_preserved` 子串断言重叠，无法独立验证左/右对齐保留

- 严重度：important
- 锚点：危险模式「弱化断言 / 存在即通过」（降低行为覆盖、掩盖失败，禁止标 minor）；AC-001 none 态原样输出保留表内容、AC-004 对齐语义行为面
- 位置：`tests/test_table.py:83-85`（`test_alignment_colons_preserved`）
- 问题：三条断言 `assert ":---" in out` / `assert ":---:" in out` / `assert "---:" in out` 存在子串重叠——`:---` 与 `---:` 均为 `:---:` 的子串，只要输出含一个居中标记 `:---:`，三条断言即同时成立，左对齐 `:---`、右对齐 `---:` 是否真实保留未被独立验证。已用只读 mutation 实证：将 `_table_aligns` 改为对每列返回 center 后，三态输出均变为 `| :---: | :---: | :---: |`（左/右对齐坍缩为居中），`test_alignment_colons_preserved` 三条断言在 none/pad/compact 下全部通过。即该测试只能捕获「对齐冒号全丢」（输出无冒号 → `:---` 缺失）这类灾难性回归，无法捕获「左/右对齐坍缩为居中」的对齐语义回归；断言消息自称检测「左对齐冒号丢失 / 右对齐冒号丢失」，与实际检测能力不符。以子串存在性断言充当逐列对齐保留的证据，无正当理由。
- 建议：改为断言完整分隔行，一次性独立验证三种对齐——`assert "| :--- | :---: | ---: |" in out`（已实测三态真实输出均为该串，不脆）；或对 none 态补完整输出相等断言（对齐表 `mdformat.text(md) == md`）锚定 AC-001 原样输出。

### 未进表的提示

- AC-001 的 `test_table_none_untouched` 用无冒号 `TABLE_MD` 断言完整相等；对齐表在 none 态的原样输出（`mdformat.text(md) == md`）可作覆盖扩展，与 f003 修复重合，属「可再加 case」级。
- Round 2 已提示的 compact/none 在已紧凑输入上不可区分问题仍存在，非本轮新增，不阻断。

### AC 复验披露（Round 3）

- AC-001：`re_verified` — `test_table_none_untouched`/`_explicit` 完整相等断言；重跑 `pytest tests/test_table.py -q` → 9 passed。对齐表 none 态手测 `mdformat.text(md)==md` 成立。
- AC-002：`re_verified` — `test_table_pad_aligned` 断言补空格输出，重跑通过；手测 pad 对齐表输出分隔行 `| :--- | :---: | ---: |` 与实现一致。
- AC-003：`re_verified` — `test_table_compact` 断言无补空格，重跑通过。
- AC-004：`re_verified` — `test_table_syntax_valid`「幂等 + 分隔行存在」断言（f001 修复形态）；对齐表三态输出手测均再解析为合法表格。
- AC-005：`re_verified` — `test_no_table_no_regression` 三态与 baseline 相等；全量 `pytest -q` 4684 passed / 5 skipped，无回归。

coverage = 5 / 5

### 总体判断

f001 修复经 diff 复核确认消除且未弱化，f002 已登记 p005。新增 `test_alignment_colons_preserved` 存在结构弱点：子串断言重叠使其无法检测「左/右对齐坍缩为居中」的回归（mutation 实证三态断言全通过），按危险模式「弱化断言 / 存在即通过」最低 important。存在 1 条未解决 important → 本轮 FAIL。

reviewed_scope: 30e7c3c590aa3a29

verdict: FAIL

## Round 4 (2026-08-12 01:04 UTC+8)

### 前轮 finding 复核（以 git diff 与当前 worktree 为准，不采信处置表自述）

- **t003_test_f001**（AC-004 弱断言 `"|" in out`，minor；处置表 status=已修）：**已消除**。`tests/test_table.py:36-43` `test_table_syntax_valid` 仍为「二次格式化幂等 `assert out == out2` + 分隔行存在 `assert "| --- |" in out`」两段断言，Round 1 记载的旧近恒真 `"|" in out` 不在文件内。Round 2/3 已实证分隔行断言能捕获「丢分隔行」失败场景，修复未回退、未弱化。重跑 `pytest tests/test_table.py -q` → 9 passed，无红灯。
- **t003_test_f002**（ragged 边界无覆盖，minor；处置表 status=遗留 fix_ref=p005）：**已按 minor 遗留规则登记**。`docs/pending/todo/p005_ragged_table_cells.md` 存在且字段齐全（现象/影响/根因/测试缺口/线索 t003_test_f002/处理「t003 遗留登记」）。minor 遗留不阻断。
- **t003_test_f003**（`test_alignment_colons_preserved` 子串断言重叠，important）：**已消除**。当前 `tests/test_table.py:78-84` 该用例断言已改为完整分隔行 `assert "| :--- | :---: | ---: |" in out`。只读 mutation 复核（内存 monkeypatch `_table_aligns` 全列返回 center，不改文件）：
  - 基线：三态输出均为 `| :--- | :---: | ---: |`，完整行匹配 True——修复断言与真实输出一致，非脆。
  - mutation（左/右对齐坍缩为居中）：三态输出均变为 `| :---: | :---: | :---: |`，完整行匹配全 False——即 Round 3 实证「旧三条子串断言全通过」的同一坍缩回归，现三态全部被此断言捕获。修复后测试能独立区分左/中/右对齐，非「换形式弱化」。

### 改测方向复核

- 无「迁就实现」式改测。f003 修复方向是把三条重叠子串断言替换为一条完整分隔行断言，断言强度严格增强（一条完整行同时锁定左/中/右三种对齐的精确排列，非三条子串可被单一 `:---:` 同时满足），且三态真实输出与该行完全一致；非把预期改向当前实现输出。相对 Round 3 仅此一处测试改动（`tests/test_table.py` 第 84 行），无既有测试被就地改写为迁就实现。

### 本轮新发现

- 0 条。危险模式扫描（恒真断言 / 删反转 expect / 注释断言 / 弱化断言 / .skip / .only / 静默错误 / mock 误用 / 阈值掩盖 / 条件跳过 / 程序赋值替代真实交互 / 存在即通过）对当前 9 个用例逐条过筛无命中。全量 `pytest -q` → 4684 passed / 5 skipped（skip 均为既有 3.13 `exclude` 用例，与本 task 无关），无回归。

### 未进表的提示

- `test_alignment_colons_preserved` 断言消息 `f"mode={mode} 对齐冒号丢失: {out!r}"` 措辞（「冒号丢失」）与实际检测能力（整行不匹配）有轻微出入，纯注释级措辞，不构成 finding。
- 前轮已记录的 compact/none 在已紧凑输入上输出相同、不可区分主动去 pad 与原样保留问题仍存在，非本轮新增，不阻断。

### AC 复验披露（Round 4）

- AC-001：`re_verified` — `test_table_none_untouched`/`_explicit` 完整相等断言，重跑 9 passed。
- AC-002：`re_verified` — `test_table_pad_aligned` 断言补空格输出，重跑通过。
- AC-003：`re_verified` — `test_table_compact` 断言无补空格，重跑通过。
- AC-004：`re_verified` — `test_table_syntax_valid`「幂等 + 分隔行存在」；对齐表三态输出手测均再解析为合法表格；f003 mutation 验证完整分隔行断言能捕获「对齐坍缩为居中」回归。
- AC-005：`re_verified` — `test_no_table_no_regression` 三态与 baseline 相等；全量 `pytest -q` 4684 passed / 5 skipped，无回归。

coverage = 5 / 5

### 总体判断

前轮 3 条 finding 均闭环：f001/f003 修复经 diff 与只读 mutation 复核确认已消除且未弱化（f003 完整分隔行断言在三态下均能独立区分左/中/右对齐，同一坍缩回归 mutation 下旧断言全过、新断言三态全败）；f002 已按 minor 遗留登记 p005。无未解决 critical / important，本轮无新发现 → 本轮 PASS。

reviewed_scope: a1a758730674a090

verdict: PASS
