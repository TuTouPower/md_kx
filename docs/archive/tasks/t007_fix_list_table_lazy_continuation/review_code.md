# Task review t007（reviewer_focus: 代码）

- task：`t007_fix_list_table_lazy_continuation`
- spec：`docs/tasks/t007_fix_list_table_lazy_continuation/spec.md`
- diff_anchor：`b3e6991001d6b136b35e9a6b4c2b584130abde64`
- target：`git diff b3e6991001d6b136b35e9a6b4c2b584130abde64`
- round：1
- reviewed_at：2026-08-12 17:30 UTC+8

## Findings

### t007_code_f001 - 列表内缩进表格被守卫误降为 0 缩进，嵌套语义破坏

- 严重度：important
- 锚点：AC-004「列表内缩进表格在三种 table_mode 下行为不变」；非范围「不改变独立表格、列表内缩进表格的现有格式化」。
- 位置：`src/md_kx/renderer/_context.py:520`（`bullet_list`）、`_context.py:615`（`ordered_list`）
- 问题：守卫 `if line and line.lstrip().startswith("|")` 无法区分「lazy 表格行」与「列表内合法缩进嵌套表格行」——两者进入续行循环时源缩进已被 `list_item.render()` 剥掉，行首均为 `|`。复现输入：

  ```
  1. foo

      | a | b |
      | --- | --- |
      | 1 | 2 |
  ```

  格式化后表格行被降为 0 缩进：

  ```
  1. foo

  | a | b |
  | --- | --- |
  | 1 | 2 |
  ```

  二次解析 HTML 从「table 嵌套于 `<li>` 内」变为「table 移到 `<ol>` 外」（逐元素比对确认），`is_md_equal` False。基线 `b3e69910` 同一输入 `is_md_equal` True 且幂等（输出 `1. foo\n\n   | a | b |\n...`）。三种 table_mode（none/pad/compact）均复现；ordered、bullet、嵌套列表内表格均受影响。s005/d006 已批准副作用仅覆盖「行首 `|` 正常续行仅风格变化」，嵌套表格是独立块（非续行），不在已批准取舍内。
- 建议：守卫须基于源行真实缩进判定——仅当续行源缩进不足以构成嵌套块（真正 lazy 行）才不缩进；renderer 层需在续行处理时保留「该行属于首行段落（lazy 续行）还是后续子块（嵌套表格）」的归属信息，或改用「紧随首行、同块内」识别，而不是对所有 `|` 行首一刀切。

### t007_code_f002 - 守卫逻辑在 bullet_list / ordered_list 两处 verbatim 重复

- 严重度：minor
- 锚点：DRY（重复逻辑新增，未造成行为分叉，故 minor）
- 位置：`src/md_kx/renderer/_context.py:516-523`、`611-618`
- 问题：注释、条件、分支三处完全一致地重复。当前两处行为一致（spec「两处续行处理一致」满足），但后续若只改一处即产生行为分叉；f001 修复也需同步改两处，重复放大修改面。
- 建议：提取共用 helper（如 `_continuation_line(line, indent)`）单点承载守卫。

### t007_code_f003 - 测试未覆盖「列表内缩进表格」，f001 回归漏检

- 严重度：minor
- 锚点：覆盖可更广（非 blocking）
- 位置：`tests/test_list_table.py`
- 问题：AC-004/非范围明确把「列表内缩进表格」列为在范围内必须不变的行为，但 `test_table_modes_unchanged` 只测独立表格，新测试集无「列表项内缩进表格 is_md_equal」用例，导致 f001 回归未被测试捕获。
- 建议：补「列表项内缩进表格」在三种 table_mode 下的 `is_md_equal` 用例。

## 结论

- 本轮新发现：3 条（f001 important / f002 minor / f003 minor）
- 未进表的提示：
  - 文件过大：`src/md_kx/renderer/_context.py` 799 行（≥ minor 阈值 400，本 task 净增 10 行；未达 important 阈值 800）。按降级规则列于此，不进 finding 表。`tests/test_list_table.py` 53 行，未超阈值。
  - 复杂度：两处循环为既有结构，守卫未新增分支级复杂度，无函数达阈值。
  - 范围外观察：列表项 lazy 表格行内转义竖线（`2. 项：\n| x\|y | z |...`）输出丢失 `\`——基线 `b3e69910` 同样丢失，属既有行为（lazy 行按段落 inline 渲染），非本 diff 引入，未出 finding。
- AC 复验方式：
  - AC-001 `re_verified`：重跑 `tests/test_list_table.py` 两用例通过（p006 输入 `is_md_equal` True；CLI `--table-mode=compact --number` 退出码 0）。
  - AC-002 `re_verified`：p006 文档格式化后 `is_md_equal` True，表格行 0 缩进。注：f001 使「列表内缩进表格」场景不满足「表格行保持原列表外/列表内语义」，该项语义由 AC-004/非范围约束，已在 f001 记录。
  - AC-003 `re_verified`：默认（none）模式 `| x\|y |` 输出保留 `\|` 且幂等。
  - AC-004 `re_verified`（部分）：独立表格三态 `tests/test_table.py` 全量通过；「列表内缩进表格」分支被 f001 违反。
  - AC-005 `re_verified`：正常多行段落列表项缩进不变（`test_multiline_list_item_unchanged` 通过；全量 `tests/` 4689 passed, 5 skipped）。
  - coverage = 5 / 5
- 总体判断：核心 lazy 表格修复（AC-001/002）达成，但守卫对「列表内缩进表格」产生可复现回归，违反 AC-004 与非范围，须修复后再合并。
- 系统性 follow-up：无

reviewed_scope: 839d2a3cd4ac8e49

verdict: FAIL

## Round 2 (2026-08-12 15:19 UTC+8)

## Findings

### t007_code_f004 - 列表项首行以 `|` 开头时 `\x00` 标记泄漏，格式化器崩溃

- 严重度：important
- 锚点：可观测行为缺陷（基线回归）——`b3e69910` 对 `- |a|b|` 正常格式化（输出不变、`is_md_equal` True），当前实现 `AssertionError: null bytes should be removed by now` 直接崩溃。
- 位置：`src/md_kx/renderer/_context.py:493`（`list_item.render_child` 对段落所有行首 `|` 行加 `\x00`，含段落首行）、`_context.py:530-534`（`bullet_list` 首行发射）与 `_context.py:597-626`（`ordered_list` 首行发射）不剥 `\x00`；崩溃点 `src/md_kx/renderer/__init__.py:101`
- 问题：标记只在续行循环剥除，首行发射路径原样输出，`\x00` 泄漏进最终文本触发 assert。复现输入（均为有效 markdown，任一即崩溃）：`- |a|b|`、`* |a|b|`、`1. |a|b|`、`3. |a|b|`、`1. x\n   - |a|b|`、`- |a|b|\n\n  second`。CLI `md_kx --table-mode=compact <file>` 未捕获 AssertionError traceback，exit 1。基线同输入正常输出。三态无关（标记在 `list_item` 层，先于 table_mode）。
- 建议：两处首行发射路径同样剥首字符 `\x00`；或 `render_child` 只对段落非首行加标记（lazy 续行行必然不是列表项首行）。

### t007_code_f005 - 列表内独立缩进段落（首字符 `|`）被误降 0 缩进，HTML 变化

- 严重度：important
- 锚点：可观测行为缺陷（基线回归）；f001 同类根因未根治——守卫仍无法区分「lazy 续行」与「列表项内合法嵌套段落块」。
- 位置：`src/md_kx/renderer/_context.py:493`
- 问题：`render_child` 对段落子块**所有**行首 `|` 行加标记，包含「非首个、空行分隔的独立缩进段落」。该段落是列表项内合法嵌套块（非 lazy 续行），被降到 0 缩进后重解析 HTML 变化。复现（none/pad/compact 三态均复现）：
  - `- foo\n\n  |bar\n` → 输出 `- foo\n\n|bar\n`，`is_md_equal` **False**；基线 `- foo\n\n  |bar\n` 输出不变、True。
  - `- foo\n\n  |bar\n\n  baz\n` → 输出 `- foo\n\n|bar\n\n  baz\n`，`is_md_equal` False 且**非幂等**（二次格式化再变）。
  - 对照：同段内 lazy 续行 `- foo\n  |bar` 输出 `- foo\n|bar` 属「已知契约清单」已批准副作用（`is_md_equal` True、validate 通过），不在本 finding 范围。
- 建议：标记仅作用于「紧随段落首行的 lazy 续行」；空行分隔的嵌套段落块不标记。

## 结论（Round 2）

- 前轮 finding 复核（以 `git diff b3e69910...` 与代码/测试为准）：
  - f001（important，嵌套表格误伤）：**已消除**（嵌套 table 场景）。守卫移入 `list_item.render_child` 且限定 `child.type == "paragraph"`，table 子块不再被标记；`1. foo\n\n    |a|b|...` 三态 `is_md_equal` True 且幂等，新增 `test_nested_table_in_list_kept` 覆盖。但**根因未根治**：嵌套 table 之外的「嵌套段落首字符 `|`」仍被误伤（新 f005），列表项首行 `|` 段还触发崩溃（新 f004）。
  - f002（minor，DRY）：**已消除**。判定逻辑收敛到 `list_item.render_child` 单点承载；两个 list renderer 仅剩各一处 2 行 `\x00` 剥除分支，无可观行为分叉风险。
  - f003（minor，测试缺失）：**已消除**。新增 `test_nested_table_in_list_kept`、`test_pipe_line_in_list_code_block_kept`，覆盖列表内嵌套表格与列表内代码块 `|` 行。
- 本轮新发现：2 条（f004 important / f005 important）
- 未进表的提示：
  - 文件过大：`src/md_kx/renderer/_context.py` 812 行（≥ minor 阈值 400，本 task 净增 9 行；未达 important 阈值 800）。按降级规则列于此，不进 finding 表。`tests/test_list_table.py` 71 行，未超阈值。
  - 复杂度：守卫为两处简单循环内分支，无函数达阈值。
  - 范围外观察：列表项 lazy 表格行内转义竖线（`2. 项：\n| x\|y | z |`）输出丢失 `\`——基线同样丢失，属既有行为，非本 diff 引入。
- AC 复验方式：
  - AC-001 `re_verified`：`tests/test_list_table.py` 7 用例全过；独立重跑 p006 输入 `md_kx.text` → `is_md_equal` True、CLI 退出码 0。
  - AC-002 `re_verified`：目标输入格式化后 `is_md_equal` True、幂等、表格行 0 缩进。
  - AC-003 `re_verified`：`test_none_mode_escape_preserved` 通过；独立重跑 `| x\|y |` 默认模式保留 `\|` 且幂等。
  - AC-004 `re_verified`：`tests/test_table.py` 全量通过（三态）；独立重跑列表内缩进表格三态 `is_md_equal` True。
  - AC-005 `re_verified`：`test_multiline_list_item_unchanged` 通过；全量 `tests/` 4691 passed, 5 skipped。
  - coverage = 5 / 5
  - 注：五条 AC 全过，但 f004/f005 为 AC 集合之外、基线之上的新回归，仍须处理。
- 总体判断：f001/f002/f003 已按 diff 消除，但修复引入两个新阻断回归（列表项首行 `|` 崩溃、嵌套段落 `|` HTML 变化），PASS 条件不满足。
- 系统性 follow-up：无

reviewed_scope: 002861af456d54fb

verdict: FAIL

## Round 3 (2026-08-12 15:55 UTC+8)

## Findings

### t007_code_f006 - softbreak 的 `\x00` 标记在列表外上下文泄漏，任意「软换行后 `|` 行首」段落崩溃

- 严重度：important
- 锚点：可观测行为缺陷（基线回归）——`b3e69910` 对 `foo\n|bar` 正常格式化，当前实现 `AssertionError: null bytes should be removed by now` 直接崩溃；同 crash 多场景见下。
- 位置：`src/md_kx/renderer/_context.py:108-117`（`softbreak` 全局返回 `"\x00\n"`）；`\x00` 剥除仅存在于 `bullet_list`/`ordered_list` 续行循环（`517-531`、`578-628`）；崩溃点 `src/md_kx/renderer/__init__.py:101`
- 问题：`softbreak` 是全局 renderer（`_context.py:759` 主 renderer，`_context.py:250` image alt 的 inline_context 同样注册）。标记判定不看是否位于列表项，`\x00` 剥除却只在两个 list renderer 做——任何非列表上下文的「软换行 → 下一行行首 `|`」都泄漏 `\x00` 到最终文本触发 assert。复现（`do_wrap=False` 默认选项下，均有效 markdown，基线均正常格式化）：
  - `foo\n|bar\n`（普通段落 lazy 续行）
  - `foo\n\n|bar\n` 之外：`x\n|y\n\nz\n`
  - `> foo\n> |bar\n`（引用内段落）
  - `# h\n\nfoo\n|bar\n`（标题后段落）
  - `![alt\n|text](/img.png)`（image alt 内联）
  - `foo\n| *bar* |\n`、`foo\n|a\|b|\n`（续行含强调/转义竖线）
  - CLI 同路径：`md_kx .scratch/crash.md` 打印 AssertionError traceback（render/__init__.py:101），格式化失败。
  - 基线实测：同输入全部 OK 且输出不变。`wrap` 开启时走 `do_wrap` 早退（`_context.py:109`）不产生该标记，故仅默认（wrap 关闭）受影响——正是默认配置。
- 建议：标记判定加容器约束——仅当 softbreak 处于 list_item 的 paragraph 子块时才返回 `"\x00\n"`；或对最终文本在 assert 前统一剥除/替换非列表上下文残留的 `\x00`。并补非列表上下文回归用例。

### t007_code_f007 - 续行消费逻辑在 bullet_list / ordered_list 两处重复（f002 残留）

- 严重度：minor
- 锚点：DRY（f002 曾收敛到 `render_child` 单点，本轮改到 `softbreak` 后消费侧重新两处重复；两处行为一致未分叉，故 minor）
- 位置：`src/md_kx/renderer/_context.py:517-531`、`578-628`
- 问题：`previous_line_ends_in_zero` 追踪 + `rstrip("\x00")` + 0 缩进分支共 5 行在 `bullet_list` 与 `ordered_list` 逐字重复（仅缩进前缀表达式不同）。本轮改动后判定逻辑虽已单点化到 `softbreak`，但消费侧重复仍在；后续单改一处即产生行为分叉。
- 建议：提取共用 helper（如 `_emit_continuation_lines(line_iter, indent)`）单点承载。

## 结论（Round 3）

- 前轮 finding 复核（以 `git diff b3e69910...` 与代码/测试为准）：
  - f001（important，嵌套表格误伤）：**已消除**。标记改由 `softbreak` 在段落 inline 内下（`nxt.content.lstrip().startswith("|")`），嵌套 table 是 list_item 的 block 子块、不经 softbreak，不被标记；实测 `1. foo\n\n    | a | b |\n...` 三态（none/pad/compact）`is_md_equal` True 且表格行保持 `   |` 3 空格缩进。
  - f002（minor，DRY）：**核心已消除、残留 minor**。判定收敛到 `softbreak` 单点；但两 list renderer 的消费循环重新出现 5 行重复，以新 finding f007（minor）记录。
  - f003（minor，测试缺失）：**已消除**。新增 `test_nested_table_in_list_kept`、`test_pipe_line_in_list_code_block_kept`、`test_list_item_first_line_pipe_no_crash`、`test_indented_paragraph_pipe_kept`，覆盖列表内嵌套表格 / 代码块 / 首行 `|` / 独立缩进段落。
  - f004（important，首行 `|` 崩溃）：**已消除**。`\x00` 只在 softbreak（续行）产生，列表项首行无前驱 softbreak 故不标记；实测 `- |a|b|`、`1. |a|b|`、`3. |a|b|`、`1. x\n   - |a|b|`、`- |a|b|\n\n  second` 全部正常输出且 `is_md_equal` True。
  - f005（important，独立缩进段落 `|` HTML 变化）：**已消除**。空行分隔的嵌套段落为独立 block 子块、无 softbreak 标记；实测 `- foo\n\n  |bar\n` 与 `- foo\n\n  |bar\n\n  baz\n` 保持 `  |bar` 缩进、`is_md_equal` True 且幂等。
- 本轮新发现：2 条（f006 important / f007 minor）
- 未进表的提示：
  - 文件过大：`src/md_kx/renderer/_context.py` 现 809 行（≥ minor 阈值 400，本 task 净增约 25 行；未达 important 阈值 800）。按降级规则列于此，不进 finding 表。`tests/test_list_table.py` 87 行，未超阈值。
  - 复杂度：`softbreak` 与两处续行循环新增分支均为简单守卫，无函数达阈值。
  - 范围外观察：wrap 模式（`do_wrap` True）下 lazy 表格行并入段落重排成单行（`2. 项\n|a|b|` + `wrap:40` → `2. 项 |a|b|`），基线行为一致，非本 diff 引入。列表项 lazy 表格行内转义竖线输出丢失 `\` 亦为既有行为，未出 finding。
- AC 复验方式：
  - AC-001 `re_verified`：`tests/test_list_table.py` 9 用例全过；独立重跑 p006 输入（`--table-mode=compact --number`）输出 0 缩进表格行、CLI 退出码 0、`is_md_equal` True。
  - AC-002 `re_verified`：目标输入格式化后 `is_md_equal` True、幂等、表格行 0 缩进。
  - AC-003 `re_verified`：`test_none_mode_escape_preserved` 通过；独立重跑 `| x\|y |` 默认模式保留 `\|` 且幂等。
  - AC-004 `re_verified`：`tests/test_table.py` 全量通过（三态）；独立重跑列表内缩进嵌套表格三态 `is_md_equal` True 且保持列表内缩进。
  - AC-005 `re_verified`：`test_multiline_list_item_unchanged` 通过；全量 `tests/` 4693 passed, 5 skipped。
  - coverage = 5 / 5
  - 注：五条 AC 全过，但 f006 为 AC 集合之外、基线之上的新崩溃回归，仍须处理。
- 总体判断：f001/f003/f004/f005 已按 diff 消除，f002 残留为 minor；但新 f006（列表外任意软换行 `|` 段落 `\x00` 泄漏崩溃）是基线之上的阻断回归，PASS 条件不满足。
- 系统性 follow-up：无

reviewed_scope: 370e4abd9784e34c

verdict: FAIL

## Round 4 (2026-08-12 16:10 UTC+8)

## Findings

### t007_code_f008 - blockquote 嵌套于列表项内时 softbreak 标记仍泄漏 `\x00`，崩溃

- 严重度：important
- 锚点：可观测行为缺陷（基线回归崩溃）——`b3e69910` 对 `- foo\n  > bar\n  > |baz\n` 正常格式化（输出不变、`is_md_equal` True），当前实现 `AssertionError: null bytes should be removed by now` 直接崩溃；CLI 同路径未捕获 traceback。
- 位置：`src/md_kx/renderer/_context.py:114-118`（`softbreak` 判定 `_in_block("list_item", node)`）、`_context.py:529-533` / `626-630`（两 list renderer 消费侧）；崩溃点 `src/md_kx/renderer/__init__.py:101`
- 问题：f006 修复加 `_in_block("list_item", node)` 只挡住「列表外」上下文，但 `_in_block` 沿**所有**祖先上溯，blockquote 内段落的软换行（blockquote → list_item）同样命中，标记仍被下发。消费侧只认「上一行以 `\x00` 结尾」的当前行并剥除（`_context.py:529-533`）；而 blockquote renderer（`_context.py:336-341`）把段落 inline 输出 `bar\x00\n|baz` 按行重前缀为 `> bar\x00\n> |baz`，`\x00` 落在「> bar」行尾，该行处理时 `previous_line_ends_in_zero=False`，按 `f"{indent}{line}"` 原样发射 → `\x00` 泄漏进最终文本触发 assert。复现输入（均为有效 markdown，基线实测全部 OK 且输出不变）：
  - `- foo\n  > bar\n  > |baz\n`（blockquote 内 lazy 续行行首 `|`）
  - `- foo\n\n  > bar\n  > |baz\n`（空行分隔）
  - `1. foo\n   > bar\n   > |baz\n2. qux\n`（ordered，多列表项）
  - `1. a\n   1. b\n   > c\n   > |d\n`、`- a\n  - b\n    > c\n    > |d\n`（嵌套列表内 blockquote）
  - `1. x\n|y|\n   > q\n   > |r\n`（lazy 表格行 + blockquote 混合）
  - 对照：blockquote 内**表格块**（`> | a | b |` 多行，非 softbreak）不崩，正常输出；列表项自身段落 lazy 行（`2. 项：\n|a|b|`）正常。崩溃仅发生在「列表项内 blockquote 的段落 lazy 续行行首 `|`」。
- 根因：判定需区分「段落直接子块于 list_item」与「段落嵌套于 list_item 内其他块（blockquote）」；`_in_block` 无法表达「直接」关系。
- 建议：`softbreak` 判定收紧为「软换行所在段落是 list_item 的直接子块」（如 `node.parent.type == "paragraph"` 且其父 `type == "list_item"`，或检查最近 block 祖先序列）；或对最终文本在 assert 前统一替换非消费路径残留的 `\x00`。补「blockquote 嵌套于列表项内 + 行首 `|` 续行」回归用例。

## 结论（Round 4）

- 前轮 finding 复核（以 `git diff b3e69910...` 与代码/测试为准）：
  - f001（important，嵌套表格误伤）：**已消除**。表格是 list_item 的 block 子块、不经 softbreak；实测 `1. foo\n\n    | a | b |\n...` 三态 `is_md_equal` True 且表格行保持 `   |` 3 空格缩进。
  - f002（minor，DRY）：**已消除**。判定收敛到 `softbreak` 单点；残留消费侧重复以 f007 记录。
  - f003（minor，测试缺失）：**已消除**。`tests/test_list_table.py` 现 10 用例，覆盖嵌套表格 / 代码块 / 首行 `|` / 独立缩进段落 / 非列表上下文。
  - f004（important，首行 `|` 崩溃）：**已消除**。实测 `- |a|b|`、`1. |a|b|` 等正常输出。
  - f005（important，独立缩进段落 `|`）：**已消除**。实测 `- foo\n\n  |bar\n` 保持 `  |bar` 缩进、`is_md_equal` True。
  - f006（important，列表外泄漏）：**六场景已消除**，但根因未根除。本轮复核：顶部段落 / 多段 / 引用块 / 标题后段落 / image alt / 强调与转义竖线 6 场景全部正常（无崩溃、无 `\x00`、`is_md_equal` True），列表外泄漏已挡；但「列表项内 blockquote 段落行首 `|` 续行」仍触发同类泄漏崩溃，以新 f008 记录。
  - f007（minor，消费侧 DRY 重复）：**仍存在**。`_context.py:519-533` 与 `_context.py:580-630` 的 `previous_line_ends_in_zero` 追踪 + `rstrip("\x00")` + 0 缩进分支仍逐字重复；两处行为一致未分叉，维持 minor，需入 `task.md` 处置表。
- 本轮新发现：1 条（f008 important）
- 未进表的提示：
  - 文件过大：`src/md_kx/renderer/_context.py` 现 818 行（≥ minor 阈值 400，本 task 净增约 28 行；未达 important 阈值 800）。按降级规则列于此，不进 finding 表。`tests/test_list_table.py` 95 行，未超阈值。
  - 复杂度：`softbreak` 与两处续行循环新增分支均为简单守卫，无函数达阈值。
  - 范围外观察：wrap 模式（`do_wrap` True）下 lazy 表格行并入段落重排（既有行为）；列表项 lazy 表格行内转义竖线输出丢 `\`（既有行为），均非本 diff 引入。blockquote 内表格块（`> | a | b |`）正常，不受影响。
- AC 复验方式：
  - AC-001 `re_verified`：`tests/test_list_table.py` 10 用例全过；独立重跑 p006 输入（`--table-mode=compact --number`）CLI 退出码 0、输出 0 缩进表格行；二次格式化幂等。
  - AC-002 `re_verified`：目标输入 `is_md_equal` True 且幂等（逐元素 HTML 一致）。
  - AC-003 `re_verified`：默认（none）模式 `| x\|y |` 输出保留 `\|` 且幂等。
  - AC-004 `re_verified`：`tests/test_table.py` 9 用例全过（三态）；独立重跑列表内缩进嵌套表格三态 `is_md_equal` True 且保持列表内缩进。
  - AC-005 `re_verified`：`test_multiline_list_item_unchanged` 通过；全量 `tests/` 4694 passed, 5 skipped。
  - coverage = 5 / 5
  - 注：五条 AC 全过，但 f008 为 AC 集合之外、基线之上的新崩溃回归，仍须处理。
- 总体判断：f001-f005 已按 diff 消除，f006 六场景已修；但 f006 同类泄漏未根除——列表项内 blockquote 段落行首 `|` 续行仍崩溃（新 f008，基线正常），f007 minor 遗留。PASS 条件不满足。
- 系统性 follow-up：无

reviewed_scope: 7d9ed4f2a76058a5

verdict: FAIL

## Round 5 (2026-08-12 16:32 UTC+8)

## Findings

本轮无新 finding。f008（本轮核心）已按 diff 消除；其余前轮 finding 均已解决或为既有 minor。

## 结论（Round 5）

- 前轮 finding 复核（以 `git diff b3e69910...` 与代码/测试为准）：
  - f001（important，嵌套表格误伤）：**已消除**。`1. foo\n\n    | a | b |...` 三态（none/pad/compact）`is_md_equal` True 且表格行保持 `   |` 3 空格缩进。
  - f002（minor，DRY）：**核心已消除**。判定收敛到 `softbreak` 单点；消费侧重复以 f007 记录。
  - f003（minor，测试缺失）：**已消除**。`tests/test_list_table.py` 现 11 用例，覆盖嵌套表格 / 代码块 / 首行 `|` / 独立缩进段落 / 非列表上下文 / 列表内 blockquote。
  - f004（important，首行 `|` 崩溃）：**已消除**。`- |a|b|`、`1. |x|y|` 等正常输出、不崩溃。
  - f005（important，独立缩进段落 `|`）：**已消除**。`- foo\n\n  |bar\n` 保持 `  |bar` 缩进、`is_md_equal` True 且幂等。
  - f006（important，列表外泄漏）：**已消除**。顶部段落 / 多段 / 引用块 / 标题后段落 / image alt / 强调与转义竖线 6 场景全部正常（无崩溃、无 `\x00` 泄漏）。
  - f007（minor，消费侧 DRY 重复）：**仍存在**。`_context.py:524-538`（bullet_list）与 `_context.py:585-635`（ordered_list）的 `previous_line_ends_in_zero` 追踪 + `rstrip("\x00")` + 0 缩进分支仍逐字重复（仅缩进前缀表达式不同）；两处行为一致未分叉，维持 minor，需入 `task.md` 处置表。
  - f008（important，blockquote 嵌套于列表项内 `\x00` 泄漏）：**已消除（本轮核心修复）**。`softbreak` 标记条件（`_context.py:114-122`）由 f006 的 `_in_block("list_item", node)`（沿所有祖先上溯）精化为 `node.parent.parent.parent.type == "list_item"`。实测父链为 `softbreak→inline→paragraph→父块`，`node.parent.parent.parent` 即段落父块：段落直接子块于 list_item（lazy 表格行）→ `list_item` → 标记（AC-001 所需）；段落嵌套于 blockquote → `blockquote` → 不标记；列表外段落 → `root` → 不标记。Round 4 列出的全部复现输入（`- foo\n  > bar\n  > |baz`、空行分隔、ordered 多列表项、嵌套列表 blockquote、lazy 表格行混合等 6 场景）现均正常格式化、无 `\x00` 泄漏、`is_md_equal` True，且输出与基线 `b3e69910` 完全一致（恢复基线行为）。另补验证：列表内 blockquote 深嵌套、blockquote>list>list_item lazy 行、嵌套列表 lazy 行、blockquote 表格块、wrap 模式交互，均无崩溃、无泄漏。
- 本轮新发现：0 条
- 未进表的提示：
  - 文件过大：`src/md_kx/renderer/_context.py` 816 行（≥ minor 阈值 400，本 task 净增约 14 行；未达 important 阈值 800）。按降级规则列于此，不进 finding 表。`tests/test_list_table.py` 103 行，未超阈值。
  - 复杂度：`softbreak` 与两处续行循环分支均为简单守卫，无函数达阈值。
  - 范围外观察：`docs/findings/d006` 机制描述略滞后（写「list renderer 行首检测，是则不追加 indent_width 前缀」，实际实现为 `softbreak` `\x00` 标记 + list renderer 消费，且限定「段落直接子块于 list_item」）；findings 属过程/证据文档、不计入 scope 指纹，非阻塞，建议就地修订描述。转义竖线丢失（`foo\n|a\|b|` → `|a|b|`）基线同丢（已用锚点 worktree 实测确认），非本 diff 引入。
  - 处置表阻塞（implementer 侧，非本 diff）：`task.md` Review 处置表多条 rationale 含裸 ` | `（Round 1 f003/test_f002、Round 2 test_f003、Round 4 test_f005），`check_review_status.py` 按 `|` 拆列判「列数与表头不一致」报错，无法输出 overall 状态。`task.md` 不在 scope 指纹内、非代码缺陷，但会阻塞 Step 6 处置与 finish，建议转义或改写 rationale。另注意：处置表将 f007 标「已修」，但代码核对两处消费循环仍逐字重复（`_context.py:524-538` / `585-635`），f007 实际仍存在（minor，不阻断）。
- AC 复验方式：
  - AC-001 `re_verified`：`tests/test_list_table.py` 11 用例全过；独立重跑 p006 输入（`--table-mode=compact --number`）输出 `|level|` 0 缩进、CLI 退出码 0。
  - AC-002 `re_verified`：目标输入格式化后 `is_md_equal` True 且幂等（二次格式化输出不变）。
  - AC-003 `re_verified`：默认（none）模式 `| x\|y |` 输出保留 `\|` 且幂等。
  - AC-004 `re_verified`：独立表格三态幂等；列表内缩进嵌套表格三态 `is_md_equal` True 且保持 `   |` 列表内缩进；全量 `tests/` 4695 passed, 5 skipped。
  - AC-005 `re_verified`：`test_multiline_list_item_unchanged` 通过；全量测试通过。
  - coverage = 5 / 5
- 总体判断：f001-f008 全部前轮重要缺陷已按 diff 消除（含本轮核心 f008 blockquote 泄漏修复，复现场景全部恢复基线行为），仅剩 f007 minor（消费侧 DRY）待处置表登记，无未解决 critical / important。
- 系统性 follow-up：无

reviewed_scope: 6d3c42fe7576ae40

verdict: PASS
