# Task review t007（reviewer_focus: 测试）

- task：`t007_fix_list_table_lazy_continuation`
- spec：`docs/tasks/t007_fix_list_table_lazy_continuation/spec.md`
- diff_anchor：`b3e6991001d6b136b35e9a6b4c2b584130abde64`
- target：`git diff b3e6991001d6b136b35e9a6b4c2b584130abde64`
- round：1
- reviewed_at：2026-08-12 21:10 UTC+8

## Findings

### t007_test_f001 - AC-004「列表内缩进表格」无测试且被修复破坏（表格被拉出列表）

- 严重度：critical
- 锚点：AC-004「独立表格与列表内缩进表格在三种 table_mode 下行为不变」；spec 非范围「不改变独立表格、列表内缩进表格的现有格式化」
- 位置：`src/md_kx/renderer/_context.py:520`（bullet_list 守卫）、`_context.py:615`（ordered_list 守卫）；`tests/test_list_table.py`、`tests/test_table.py` 均无列表内缩进表格用例
- 问题：守卫 `line and line.lstrip().startswith("|")` 对列表项内**子块**渲染行同样去缩进，不止 lazy 表格续行。复现（base 与修复后各跑一遍）：
  - 输入 `1. 项\n\n   |a|b|\n   |--|--|\n   |1|2|\n`（列表内缩进表格，AC-004 明确要求行为不变）
  - base 三态输出表格行保持 3 空格缩进、表格留在 `<li>` 内，`is_md_equal` True
  - 修复后三态输出 `| a | b |...` 0 缩进，表格被拉出列表，HTML 由 `<ol><li>…<table>…</table></li></ol>` 变为 `<ol><li>项</li></ol><table>…</table>`，`is_md_equal` 三态全 False
  - 全量套件 4689 pass（含修复后），无任何用例触达该场景，回归完全静默
- 建议：补 AC-004 列表内缩进表格三态 `is_md_equal` 用例（红前绿后验证）；实现侧守卫须只作用于段落 inline 续行（lazy 表格行），不作用于 table/code 等子块渲染行

### t007_test_f002 - 守卫误伤列表内代码块中 `|` 开头代码行，代码块内容损坏

- 严重度：critical
- 锚点：可观测行为缺陷（wrong output），blocking 硬阈值 #2（无对应 AC 的真 bug）
- 位置：`src/md_kx/renderer/_context.py:520`、`_context.py:615`
- 问题：输入 `1. example\n\n   ```\n   |code line|\n   ```\n` 格式化后 `|code line|` 被去缩进，二次解析破坏代码块：HTML 由 `<li><p>example</p><pre><code>|code line|\n</code></pre></li>` 变为 `<li><p>example</p><pre><code></code></pre></li><p>|code line|</p><pre><code></code></pre>`——代码内容被逐出代码块、产生两个空 `<pre><code>`，且 `md_kx.text` 不报错（静默坏输出）。列表内任意以 `|` 开头的代码行均被破坏，无测试覆盖
- 建议：补列表内代码块含 `|` 行用例；实现侧守卫需避免作用于代码块内容（与 f001 同一根因，修复方向一致）

## 结论

- 前轮 finding 复核（Round 1）：无
- 改测方向复核：无。diff 未改动任何既有测试，`tests/test_list_table.py` 为全新文件，不存在「迁就实现」的改测
- 本轮新发现：2 条
- 未进表的提示：
  - AC-001 CLI 用例 `test_list_table_cli_exit_zero` 只断言退出码 0，未断言文件内容确被格式化；exit 0 已隐含 validate 通过，覆盖可接受（minor）
  - `test_table_modes_unchanged` 中 `assert "|" in out` 偏弱，配合幂等断言共同构成独立表格回归证据，不阻断（minor）
- 总体判断：AC-001/002/003/005 覆盖真实有效、base 红修复后绿；但 AC-004「列表内缩进表格」条款完全无测试且被实现破坏（表格拉出列表），另有列表内代码块 `|` 行损坏的静默回归，2 条未解决 critical → FAIL

### AC 复验披露

- AC-001：`re_verified`——重跑 `tests/test_list_table.py`（base 2 failed，fix 5 passed）；base CLI `rc=1`（Could not format）、fix `rc=0`
- AC-002：`re_verified`——`is_md_equal` True，断言直接对比输入/输出 HTML；实测 lazy 表格行保持 0 缩进
- AC-003：`re_verified`——默认模式 `x\|y` 保留且幂等；`tests/test_table.py::test_escaped_pipe_preserved` 三态覆盖
- AC-004：独立表格子句 `re_verified`（`test_table_modes_unchanged` + test_table.py 全量通过）；**列表内缩进表格子句复验结果为失败**（三态 `is_md_equal` False），且无测试，见 f001
- AC-005：`re_verified`——`test_multiline_list_item_unchanged` 断言 4 空格续行保留 + `is_md_equal` True

`coverage = 5 / 5`（AC-004 列表内缩进子句复验结论为失败，非通过）；`trust_prior = 0%`，无需人工抽查

- 系统性 follow-up：无

reviewed_scope: 839d2a3cd4ac8e49

verdict: FAIL

## Round 2 (2026-08-12 15:17 UTC+8)

## Findings

### t007_test_f003 - 列表项首行以 `|` 开头时 NUL 标记泄漏，validate/CLI 崩溃（修复引入的新回归）

- 严重度：important
- 锚点：可观测行为缺陷（崩溃）——blocking 硬阈值 #2，无对应 AC 的真 bug
- 位置：`src/md_kx/renderer/_context.py:486-498`（`render_child` 对段落**所有**行首 `|` 行加 `\x00` 标记，含段落首行）、`:530-534`（bullet_list 首行前缀直接拼接 first_line，无 `\x00` 剥离）、`:597-626`（ordered_list 首行同）、断言 `src/md_kx/renderer/__init__.py:101`（`assert "\x00" not in text`）
- 问题：`\x00` 标记在**列表项首行**未剥离即进入渲染文本，finalize 断言触发未处理 AssertionError。复现（当前工作区，默认与 number 选项均触发）：
  - `1. outer\n2. |x|y|\n`、`- outer\n  - |x|y|\n`、`1. outer\n\n   - inner\n\n   - |x|y|\n`
  - CLI 输出完整 traceback，`AssertionError: null bytes should be removed by now`，exit 1；`md_kx.text` 同样抛错
  - base（b3e6991）同输入全部正常格式化（exit 0），证明为本修复引入的回归
- 根因：`render_child` 对段落内首行 `|` 行也打标记；而 bullet/ordered_list 对**续行**做了 `line.startswith("\x00")` 剥离，首行却走 `f"{marker}{indent}{first_line}"` 直接拼接，无剥离。列表内任何「首行以 `|` 开头且非合法表格块」的段落（如 pipe 分隔值、`|x|y|` 单行）都崩溃
- 测试缺口：`tests/test_list_table.py` 无「列表项首行 `|`」用例，该崩溃路径无任何覆盖，全量套件 4691 pass 静默通过
- 建议：bullet_list / ordered_list 首行处理与续行一致地剥离 `\x00`（如 `first_line` 前缀前先 `removeprefix("\x00")`），并补「列表项首行以 `|` 开头」用例（红前绿后验证，确认不崩溃且 is_md_equal True）

## 结论

- 前轮 finding 复核（Round 1→2，以 git diff + 黑盒复验为准）：
  - t007_test_f001（嵌套表格回归，critical）：**已消除**。修复改为段落子块 `\x00` 标记（`_context.py:486`），守卫只作用于 paragraph child，table 子块不受影响。新增 `test_nested_table_in_list_kept` 真实验证：修复下 pass、重构 Round-1 朴素守卫时红（2 failed）、base 上 pass（base 无守卫天然通过）。黑盒复验 Round-1 原始输入 `1. 项\n\n   |a|b|...` 三态 is_md_equal 全 True、表格行保持 3 空格缩进
  - t007_test_f002（代码块 `|` 行损坏，critical）：**已消除**。同一机制，fence 非 paragraph child 不加标记。`test_pipe_line_in_list_code_block_kept` 修复下 pass、朴素守卫下红。黑盒复验 Round-1 原始输入（列表内代码块含 `|code line|` 行）输出与输入一致、is_md_equal True
  - 补充说明：两回归测试 pass-on-base 属预期（base 无守卫，本就有正确行为）；其价值在捕获「守卫误伤」形态（朴素守卫下均红），真实有效，非恒真/弱化断言
- 改测方向复核：无。diff 未改动任何既有测试，新增 `tests/test_list_table.py`（7 用例）为全新文件，无「迁就实现」的改测；前轮 2 条 critical 对应修复各带独立回归测试
- 本轮新发现：1 条（t007_test_f003）
- 未进表的提示：
  - Round-1 minor（AC-001 CLI 用例仅断言 exit 0 未断言文件内容被格式化；`test_table_modes_unchanged` 的 `assert "|" in out` 偏弱）仍成立，不阻断
  - f003 触发面（列表项首行 `|`）与 p006 懒表格行（续行 `|`）在代码上仅差「是否首行」，同一标记路径，修复时应统一首行/续行剥离逻辑
- 总体判断：f001/f002 两 critical 已真修，AC-001~005 覆盖完整（AC-004 列表内缩进表格缺口已由 `test_nested_table_in_list_kept` 补上）；但修复引入的新崩溃回归 f003 未解决 → FAIL

### AC 复验披露（Round 2）

- AC-001：`re_verified`——`test_list_table_validate_passes` + `test_list_table_cli_exit_zero`：base 源下 2 failed（validate 报 Could not format、CLI rc=1），修复下全绿（rc=0）
- AC-002：`re_verified`——`is_md_equal` True 断言直比输入/输出 HTML；黑盒复验 lazy 表格行保持 0 缩进
- AC-003：`re_verified`——`test_none_mode_escape_preserved`（`x\|y` 保留 + 幂等）；`tests/test_table.py` 全量通过
- AC-004：`re_verified`——独立表格 `test_table_modes_unchanged` 三态 + test_table.py 全量；列表内缩进表格子句由新增 `test_nested_table_in_list_kept` 覆盖，黑盒三态复验 is_md_equal 全 True（Round-1 缺口已补）
- AC-005：`re_verified`——`test_multiline_list_item_unchanged`（4 空格续行保留 + is_md_equal True）

`coverage = 5 / 5`；`trust_prior = 0%`，无需人工抽查

- 系统性 follow-up：无

reviewed_scope: 002861af456d54fb

verdict: FAIL

## Round 3 (2026-08-12 15:57 UTC+8)

## Findings

### t007_test_f004 - 守卫改为 softbreak 打 `\x00` 标记后，列表外段落/引用块续行 `|` 行 NUL 标记泄漏，直接崩溃（修复引入的新回归）

- 严重度：critical
- 锚点：可观测行为缺陷（未捕获 AssertionError 崩溃）——blocking 硬阈值 #2，无对应 AC 的真 bug
- 位置：`src/md_kx/renderer/_context.py:108-117`（softbreak 对**任何**「下个 sibling 行首 `|`」返回 `"\x00\n"`，不限列表）、`:517-531`（bullet_list 剥离）、`:578-628`（ordered_list 剥离）；泄漏抵达 `src/md_kx/renderer/__init__.py:101`（`assert "\x00" not in text`）
- 问题：`\x00` 标记只在 `bullet_list` / `ordered_list` 两个 renderer 里被剥离；**不在列表内**的段落、引用块以及「列表内块引用」里的 `|` 续行，标记一路泄漏到 finalize 断言触发未处理 AssertionError。复现（当前工作区，默认 wrap=keep）：
  - `foo\n|bar\n`（普通段落 + 行首 `|` 续行）→ `AssertionError: null bytes should be removed by now`
  - `> foo\n|bar\n`（引用块续行）→ 同崩溃
  - `- foo\n  > bar\n  > |baz\n`（列表内块引用续行）→ 同崩溃
  - CLI `run(['/tmp/leak_case.md'])` 抛未捕获 AssertionError（非 SystemExit/错误码），`md_kx.text` 同崩溃
  - **base（b3e6991）同一输入全部正常格式化**（`foo\n|bar\n`、`> foo\n|bar\n` 均 is_md_equal True），证明为本修复引入的回归
- 根因：Round-2 的 f003 修复把标记从 `render_child`（列表上下文）挪到 `softbreak`（全局），并将首行/续行剥离收口在 bullet/ordered list 内；但 `softbreak` 不区分容器，段落 / blockquote / 其它容器无剥离路径，`\x00` 直达 finalize
- 测试缺口：`tests/test_list_table.py` 的 9 用例全部是「列表项内」场景，`test_indented_paragraph_pipe_kept` 用 `- foo\n\n  |bar\n`（空行分隔的独立缩进段落，不触发 softbreak 标记）恰好绕过该路径；列表外 `|` 续行段落零覆盖，全量 4693 pass 静默
- 建议：softbreak 仅在段落位于 bullet_list / ordered_list 内时才打标记（如 `_in_block("bullet_list", node) or _in_block("ordered_list", node)` 守卫），或对非列表容器的 `\x00` 做兜底剥离；补「独立段落 `foo\n|bar`」「引用块 `> foo\n|bar`」「列表内块引用 `- foo\n  > bar\n  > |baz`」三用例（红前绿后，断言 is_md_equal True 且不崩溃）

## 结论

- 前轮 finding 复核（Round 2→3，以 git diff + 黑盒复验为准）：
  - t007_test_f001（嵌套表格回归，critical）：**已消除**。黑盒复验 `1. foo\n\n    | a | b |...` 三态 is_md_equal 全 True、表格行保持缩进；`test_nested_table_in_list_kept` 真实覆盖
  - t007_test_f002（代码块 `|` 行损坏，critical）：**已消除**。黑盒复验列表内代码块 `|code line|` 行保持缩进、is_md_equal True；`test_pipe_line_in_list_code_block_kept` 覆盖
  - t007_test_f003（列表项首行 `|` NUL 泄漏崩溃，important）：**已消除**。实现改为 softbreak 打标 + bullet/ordered 首行 `rstrip("\x00")`；黑盒复验 f003 三原始输入（`1. outer\n2. |x|y|`、`- outer\n  - |x|y|`、`1. outer\n\n   - inner\n\n   - |x|y|`）均 is_md_equal True 不崩溃；`test_list_item_first_line_pipe_no_crash` 覆盖。**但**该修复把标记逻辑挪到全局 softbreak，引入新回归 f004（列表外泄漏崩溃）
- 改测方向复核：无。diff 相对 base 仅新增 `tests/test_list_table.py`（全 9 用例为新文件），未改任何既有测试，无「迁就实现」的改测；TDD 红灯归因成立（base 源下 AC-001 相关 2 failed，修复下全绿）
- 本轮新发现：1 条（t007_test_f004）
- 未进表的提示：
  - 正常 `|` 续行被去缩进（`1. foo\n   |bar` → `1. foo\n|bar`）是 spec 未知契约清单已声明的副作用（「行首 `|` 正常续行仅风格变化，validate 仍通过」），已批准，不出 finding
  - Round-1 minor（CLI 用例仅断言 exit 0 未断言文件内容；`test_table_modes_unchanged` 的 `assert "|" in out` 偏弱）仍成立，非阻断
  - f004 与 f003 同源于「`\x00` 标记生命周期」：修复应统一标记的「打点-剥离」配对，保证任意容器不泄漏
- 总体判断：f001/f002/f003 均真修，AC-001~005 覆盖完整且断言真实有效；但修复引入的新崩溃回归 f004（列表外段落/引用块 `|` 续行直接 AssertionError，CLI 未捕获）未解决 → FAIL

### AC 复验披露（Round 3）

- AC-001：`re_verified`——`test_list_table_validate_passes`（text + is_md_equal + 0 缩进断言）+ `test_list_table_cli_exit_zero`（`run()==0`，CLI 层 validate 通过）；重跑 `tests/test_list_table.py` 9 passed
- AC-002：`re_verified`——`is_md_equal` True 直比输入/输出 HTML；黑盒复验 p006 输入 lazy 表格行保持 0 缩进
- AC-003：`re_verified`——`test_none_mode_escape_preserved`（`x\|y` 保留 + 幂等）；`tests/test_table.py` 全量通过
- AC-004：`re_verified`——独立表格 `test_table_modes_unchanged` 三态 + test_table.py 全量；列表内缩进表格 `test_nested_table_in_list_kept`，黑盒三态 is_md_equal 全 True
- AC-005：`re_verified`——`test_multiline_list_item_unchanged`（4 空格续行保留 + is_md_equal True）

`coverage = 5 / 5`；`trust_prior = 0%`，无需人工抽查

- 系统性 follow-up：无

reviewed_scope: 370e4abd9784e34c

verdict: FAIL

## Round 4 (2026-08-12 16:08 UTC+8)

## Findings

### t007_test_f005 - f004 修不彻底：列表内块引用 `|` 续行仍 NUL 泄漏崩溃，回归测试未覆盖该形态

- 严重度：critical
- 锚点：可观测行为缺陷（未捕获 AssertionError 崩溃，CLI `run()` 直接抛错，非 SystemExit/错误码）——blocking 硬阈值 #2，无对应 AC 的真 bug；即 f004 第三条复现输入
- 位置：`src/md_kx/renderer/_context.py:114-118`（softbreak 守卫用 `_in_block("list_item", node)`，沿 parent 链传递式上溯，列表内块引用的段落也命中）、`_context.py:333-342`（blockquote renderer 按行加 `> ` 前缀，无 `\x00` 剥离路径）、`tests/test_list_table.py:88`（`test_pipe_line_outside_list_no_crash`）
- 问题：当前守卫对「列表内块引用」段落同样打 `\x00` 标记，而 blockquote renderer 不剥 `\x00`，标记直达 finalize 断言。黑盒复现（当前工作区，默认选项）：
  - `- foo\n  > bar\n  > |baz\n` → `AssertionError: null bytes should be removed by now`
  - CLI `run([path])` 抛未捕获 AssertionError（非 SystemExit，无 rc）
  - `- foo\n  > bar\n  > |baz x\n`、`- a\n  > q\n  > |w\n- b\n  > r\n  > |e\n` 同崩溃
  - **base（b3e6991）同一输入正常格式化**（base softbreak 无 `\x00` 机制），证明为本修复引入的回归
  - 这正是 f004 明确列出的第三条复现输入；本轮修复仅把守卫收窄到 `_in_block("list_item")`，修掉前两条（普通段落、独立引用块），未落实 f004 建议的「非 bullet/ordered 容器的 `\x00` 兜底剥离」，列表内块引用仍泄漏
- 测试缺口：`test_pipe_line_outside_list_no_crash`（`tests/test_list_table.py:88`）只覆盖 `foo\n|bar\n` 与 `> foo\n> |bar\n` 两形态，未含 `- foo\n  > bar\n  > |baz` 列表内块引用形态——恰是该仍崩溃形态。此测试 pass 不能证明 f004 闭环；全量套件 4694 pass 静默通过（无用例触达该崩溃）
- 建议：softbreak 守卫改为「段落是 list_item 的直接子级」的非传递式判断（如 `node.parent.type == "paragraph"` 且该 paragraph 的 parent 为 list_item），或对非 bullet/ordered_list 容器统一兜底剥离 `\x00`（与 f004 建议一致，同一「打点-剥离」配对原则）；回归测试补 `- foo\n  > bar\n  > |baz\n` 用例（红前绿后，断言 `is_md_equal` True 且不崩溃）

## 结论

- 前轮 finding 复核（Round 3→4，以 git diff + 黑盒复验为准）：
  - t007_test_f001（嵌套表格回归，critical）：**已消除**。守卫只对段落子块生效，table 子块不受影响；黑盒复验 `1. foo\n\n    | a | b |...` 三态 is_md_equal 全 True、表格行保持缩进；`test_nested_table_in_list_kept`（`test_list_table.py:56`）真实覆盖
  - t007_test_f002（代码块 `|` 行损坏，critical）：**已消除**。黑盒复验列表内代码块 `|code line|` 行保持缩进、is_md_equal True；`test_pipe_line_in_list_code_block_kept`（`:65`）覆盖
  - t007_test_f003（列表项首行 `|` NUL 泄漏崩溃，important）：**已消除**。黑盒复验 f003 三原始输入（`1. outer\n2. |x|y|`、`- outer\n  - |x|y|`、`1. outer\n\n   - inner\n\n   - |x|y|`）均 is_md_equal True 不崩溃；`test_list_item_first_line_pipe_no_crash`（`:73`）覆盖
  - t007_test_f004（列表外段落/引用块 `|` 续行泄漏崩溃，critical）：**修不彻底**。普通段落 `foo\n|bar\n` 与独立引用块 `> foo\n|bar\n` 两形态已修复（黑盒 is_md_equal True）；**列表内块引用 `- foo\n  > bar\n  > |baz\n` 仍崩溃**（f005），修复只收窄守卫未堵住泄漏路径
- 改测方向复核：无。diff 相对 base 仅新增 `tests/test_list_table.py`（10 用例，新文件），未改任何既有测试，无「迁就实现」的改测。但 f004 的回归测试本身漏覆盖仍崩溃形态，属测试有效性缺口，见 f005
- 本轮新发现：1 条（t007_test_f005）
- 未进表的提示：
  - `test_pipe_line_outside_list_no_crash` 用 `> foo\n> |bar\n`（双 `>` 引用）而非 f004 原始懒续行 `> foo\n|bar\n`；两形态现均不崩，非阻断，但建议补懒续行形态以贴近 f004 原始复现
  - Round-1 minor（CLI 用例仅断言 exit 0 未断言文件内容被格式化；`test_table_modes_unchanged` 的 `assert "|" in out` 偏弱）仍成立，非阻断
  - f004/f005 同源于「`\x00` 标记打点-剥离不配对」：本轮守卫从「段落子块」移到「softbreak + list_item 传递式」，仍只堵住 bullet/ordered 两处剥离，其余容器（blockquote 等）无剥离路径
- 总体判断：f001/f002/f003 均真修，AC-001~005 覆盖完整且断言真实有效；但 f004 修复不彻底——列表内块引用 `|` 续行仍触发未捕获 AssertionError（CLI 直接抛错），且回归测试未覆盖该形态，1 条未解决 critical → FAIL

### AC 复验披露（Round 4）

- AC-001：`re_verified`——`test_list_table_validate_passes`（is_md_equal True + 0 缩进断言）+ `test_list_table_cli_exit_zero`（`run()==0`）；重跑 `tests/test_list_table.py` 10 passed
- AC-002：`re_verified`——`is_md_equal` True 直比输入/输出 HTML；黑盒复验 p006 输入 lazy 表格行保持 0 缩进
- AC-003：`re_verified`——`test_none_mode_escape_preserved`（`x\|y` 保留 + 幂等）；`tests/test_table.py` 9 passed
- AC-004：`re_verified`——独立表格 `test_table_modes_unchanged` 三态 + test_table.py 全量；列表内缩进表格 `test_nested_table_in_list_kept`，黑盒三态 is_md_equal 全 True
- AC-005：`re_verified`——`test_multiline_list_item_unchanged`（4 空格续行保留 + is_md_equal True）；全量套件 4694 passed、5 skipped

`coverage = 5 / 5`；`trust_prior = 0%`，无需人工抽查

- 系统性 follow-up：无

reviewed_scope: 7d9ed4f2a76058a5

verdict: FAIL

## Round 5 (2026-08-12 16:32 UTC+8)

## Findings

本轮无新 finding。f001-f005 全部经 git diff + 黑盒复验确认消除，见下「前轮 finding 复核」。

## 结论

- 前轮 finding 复核（Round 4→5，以 git diff + 黑盒复验为准）：
  - t007_test_f001（嵌套表格回归，critical）：**已消除**。守卫仅命中「paragraph 直接位于 list_item 内」形态（`_context.py:121` `node.parent.parent.parent.type == "list_item"`），table 子块不经 softbreak 打标。黑盒复验 `1. foo\n\n    | a | b |...` 三态 `is_md_equal` True、表格行保持 3 空格缩进；`test_nested_table_in_list_kept`（`test_list_table.py:56`）覆盖。
  - t007_test_f002（代码块 `|` 行损坏，critical）：**已消除**。fence 非 paragraph 子块，不入标记路径。黑盒复验列表内代码块 `|code line|` 行保持缩进、`is_md_equal` True；`test_pipe_line_in_list_code_block_kept`（`:65`）覆盖。
  - t007_test_f003（列表项首行 `|` NUL 泄漏崩溃，important）：**已消除**。标记只在 softbreak 续行产生，首行无 softbreak 前驱、不打标。黑盒复验 f003 三原始输入（`1. outer\n2. |x|y|`、`- outer\n  - |x|y|`、`1. outer\n\n   - inner\n\n   - |x|y|`）均 `is_md_equal` True 不崩溃；`test_list_item_first_line_pipe_no_crash`（`:73`）覆盖。
  - t007_test_f004（列表外段落/引用块 `|` 续行泄漏崩溃，critical）：**已消除**。守卫的非传递式三层判断使列表外段落（`parent.parent.parent`=root 或非 list_item）不打标。黑盒复验 `foo\n|bar\n`、`> foo\n|bar\n`（含懒续行形态）均 `is_md_equal` True、CLI `run()` rc=0；`test_pipe_line_outside_list_no_crash`（`:88`）覆盖两形态。
  - t007_test_f005（列表内块引用 `|` 续行泄漏崩溃，critical）：**已消除**。修复把守卫从 Round-4 的传递式 `_in_block("list_item")` 收窄为非传递式 `node.parent.parent.parent.type == "list_item"`：列表内块引用段落的三层祖先是 `blockquote`（非 `list_item`）→ 不打标 → 无 NUL 泄漏。黑盒复验 f005 三原始输入（`- foo\n  > bar\n  > |baz\n`、`- foo\n  > bar\n  > |baz x\n`、`- a\n  > q\n  > |w\n- b\n  > r\n  > |e\n`）均 `is_md_equal` True、CLI rc=0。**测试有效性已证明**：用脚本模拟 Round-4 传递式守卫渲染 f005_a，触发 `AssertionError: null bytes should be removed by now`（即 `test_pipe_in_list_blockquote_no_crash` 在修复前必红）；当前代码该测试绿。`test_pipe_in_list_blockquote_no_crash`（`:95`）精确覆盖原崩溃输入，断言 `"> |baz" in out` 校验内容保留。
- 改测方向复核：无。diff 相对 base 仅新增 `tests/test_list_table.py`（11 用例，新文件）与 `_context.py` 实现改动，未改任何既有测试，无「迁就实现」的改测。
- 本轮新发现：0 条
- 未进表的提示：
  - 嵌套列表 lazy 表格续行（`1. outer\n   - inner\n   |a|b|\n...`）无显式单测，黑盒复验 `is_md_equal` True（机制与 p006 同：paragraph 直接位于内层 list_item），可选补 case（minor）
  - `test_pipe_line_outside_list_no_crash` 用双 `>` 引用形态而非 f004 懒续行形态；懒续行形态（`> foo\n|bar\n`）黑盒复验 OK，可选补 case（minor）
  - Round-1 两条 minor（CLI 用例仅断言 exit 0 未断言文件内容；`test_table_modes_unchanged` 的 `assert "|" in out` 偏弱）仍成立，非阻断
  - 全量套件 4695 passed、5 skipped；wrap=no/88/40 三态下 p006 与 f001-f005 全部输入 `is_md_equal` True 不崩溃
- 总体判断：f001-f005 全部真修（含 f005 修复改为非传递式三层守卫，回归测试在模拟旧守卫下红、现绿），AC-001~005 覆盖完整且断言真实有效，无未解决 critical/important → PASS

### AC 复验披露（Round 5）

- AC-001：`re_verified`——`test_list_table_validate_passes`（is_md_equal True + 0 缩进断言）+ `test_list_table_cli_exit_zero`（`run()==0`）；重跑 `tests/test_list_table.py` 11 passed；base 红已由 Round 1-3 复验
- AC-002：`re_verified`——`is_md_equal` True 直比输入/输出 HTML；黑盒复验 p006 lazy 表格行保持 0 缩进
- AC-003：`re_verified`——`test_none_mode_escape_preserved`（`x\|y` 保留 + 幂等）；`tests/test_table.py` 9 passed
- AC-004：`re_verified`——独立表格 `test_table_modes_unchanged` 三态 + test_table.py 全量；列表内缩进表格 `test_nested_table_in_list_kept`，黑盒三态 `is_md_equal` 全 True
- AC-005：`re_verified`——`test_multiline_list_item_unchanged`（4 空格续行保留 + is_md_equal True）；全量套件 4695 passed、5 skipped

`coverage = 5 / 5`；`trust_prior = 0%`，无需人工抽查

- 系统性 follow-up：无

reviewed_scope: 6d3c42fe7576ae40

verdict: PASS
