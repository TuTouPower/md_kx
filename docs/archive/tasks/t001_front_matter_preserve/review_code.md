# Task review t001（reviewer_focus: 代码）

- task：`t001_front_matter_preserve`
- spec：`docs/tasks/t001_front_matter_preserve/spec.md`
- diff_anchor：`2586c5769c2e76c40010c1b6771922611f160b0d`
- target：`git diff 2586c5769c2e76c40010c1b6771922611f160b0d`
- round：1
- reviewed_at：2026-08-11 22:15 UTC+8

## Findings

### t001_code_f001 - CRLF front matter 未识别，front matter 被破坏

- 严重度：important
- 锚点：AC-001（front matter 输出后与输入逐字节一致）+ AC-004（front matter 内容不被格式化或改写）
- 位置：`src/mdformat/_api.py:22`、`src/mdformat/_api.py:25`
- 问题：首行判定 `lines[0].rstrip("\n") != "---"` 与闭合行判定 `lines[i].rstrip("\n") == "---"` 只剥离 `\n`。CRLF 文档行末为 `\r\n`，`rstrip("\n")` 残留 `\r`，导致判定失败，front matter 不被剥离，整篇进入 markdown-it 渲染，`---` 被解析为 thematic break、键值行被合成标题，front matter 内容被破坏后经 `file()` 回写磁盘（数据损坏）。

  复现（本机 `.venv/bin/python`，`src/mdformat` 为当前工作区代码）：
  - `mdformat.text('---\r\nname: x\r\ndescription: y\r\n---\r\n# Title\r\n\r\nSome **bold** text.\r\n')` → `'_____…\n\n## name: x description: y\n\n# Title\n\nSome **bold** text.\n'`
  - `mdformat.file(p, options={'end_of_line': 'keep'})` 后 `p` 内容：`_____…\r\n\r\n## name: x description: y\r\n…`，原 front matter 已被改写。

  mdformat 原生把 CRLF 作为一等输入：`_conf.py` `end_of_line` 支持 `crlf/keep`、`_util.py detect_newline_type`、`tests/test_api.py::test_eol__crlf` 与 `test_eol__keep_crlf`（CLI 同）。故带 front matter 的 CRLF 文档属受支持输入类，AC-001/AC-004 对 LF 成立、对 CRLF 不成立。

  注意第二层陷阱：即使将上述判定改为识别 CRLF，`file()` 中 `formatted_md = formatted_md.replace("\n", newline)`（`src/mdformat/_api.py:99`）会把保留的 `\r\n` front matter 再翻成 `\r\r\n`。修复需把剥离保留的 front matter 换行统一到输出换行类型（或调整 newline 归一方式）。

- 建议：分隔行判定改为 `lines[i].rstrip("\r\n") == "---"`（首行同理），并处理 `file()` newline 归一化对保留 front matter 的二次转换；补充 CRLF front matter 用例。

## 结论

- 前轮 finding 复核：本轮（Round 1），无。
- 本轮新发现：1 条（f001，important）。
- 未进表的提示：
  - 已验收的歧义行为：文档开头 `---` 后含第二个 `---`（如 `---\n\n---\n\n# Title\n` 或 `---\nThis is a paragraph.\n---\n`）会被判为 front matter 并原样保留，与改动前输出（`---` 归一为 `___`、setext 解析）不同。属 spec 风险区「front matter 识别与普通 `---` 分隔线歧义」已接受的判定边界（s001 已验证「空 front matter / 前后空行边界」），不回退。但 AC-003 测试仅覆盖非开头 `---`，未覆盖该「误吞」边界；建议 test reviewer 补该边界的期望行为用例。
  - 测试观察（test reviewer 职责，仅交接）：`test_front_matter.py::test_no_front_matter_unchanged` 首断言 `mdformat.text(md) == mdformat.text(md)` 恒真，AC-003 的「行为不变」未被有效断言；且普通 `---` 分隔线用例在开头、未覆盖上述歧义边界。
  - 复杂度 / 文件过大：`_strip_front_matter` CC≈4、`_api.py` 102 行、测试 49 行，均未达阈值。
  - 不偏航：src 仅改 `_api.py`，无范围外改动；s001/d001 文档与实现一致。
- 总体判断：实现符合 s001 预处理剥离方案，LF 路径 AC-001~004 均可观测成立；但 CRLF（mdformat 一等支持输入）front matter 被破坏并回写，违反 AC-001/AC-004，存在未解决 important，FAIL。
- AC 复验方式：
  - AC-001：`re_verified` — LF front matter 逐字节保留（本机 `mdformat.text` 验证）；CRLF 破坏（f001）。
  - AC-002：`re_verified` — 剥离后 body 走 mdit 管线；`test_front_matter.py::test_body_formatted` 断言 `# Title\n\nSome **bold** text.\n`，本机验证成立。
  - AC-003：`re_verified` — 无开头 `---` 时 `_strip_front_matter` 返回 `(md, None)`，body 即原文，行为不变；空文档 / 未闭合 / 非开头分隔线均本机验证不变。
  - AC-004：`re_verified` — LF front matter 内容不被改写（含 `|` 块值）；CRLF 破坏（f001）。
  - coverage = 4/4
- 系统性 follow-up：无。

reviewed_scope: 3e84a9c4abb39eb1

verdict: FAIL

## Round 2 (2026-08-11 22:26 UTC+8)

reviewed_scope: bc065a595b0ec5b7

### 前轮 finding 复核

- t001_code_f001（important，CRLF front matter 破坏）——**修不彻底**。第一层已修，第二层残余仍为可观测缺陷。
  - 第一层（CRLF 分隔行识别）：**已修**。`_strip_front_matter` 首行与闭合行判定均改 `rstrip("\r\n")`（`src/mdformat/_api.py:23`、`:26`），不再因残留 `\r` 误判。本机复验 `text()` 对 CRLF 文档 front matter 逐字节保留：`'---\r\nname: x\r\ndescription: y\r\n---\r\n# Title\n\nSome **bold** text.\n'`。
  - 第二层（`file()`/CLI 写回时 newline 归一化二次破坏保留的 CRLF front matter）：**仍存在**。`src/mdformat/_api.py:100` `formatted_md = formatted_md.replace("\n", newline)` 与 `src/mdformat/_cli.py:143` 同构代码，在 CRLF 文档 + `end_of_line: keep|crlf` 时 `detect_newline_type` 返回 `\r\n`，把 front matter 中保留的 `\r\n` 再翻成 `\r\r\n`。
  - 复现（工作区代码）：`mdformat.file(p, options={'end_of_line': 'keep'})` 后 `p` 内容为 `'---\r\r\nname: x\r\r\ndescription: y\r\r\n---\r\r\n# Title\r\n…'`，front matter 被改写；CLI 等价路径（`text()` 后 `replace("\n", newline)`）结果相同。
  - f001 原文把第二层列为同一缺陷并要求修复（"修复需把剥离保留的 front matter 换行统一到输出换行类型（或调整 newline 归一方式）"）。处置表 `fix_ref` 仅指向 `src/mdformat/_api.py:22` 判定改动，归一化路径未动。
  - 新增测试 `tests/test_front_matter.py::test_front_matter_crlf_preserved`（`:53`）仅覆盖 `text()` 入口，未覆盖 `file()`/CLI 写回路径，残余缺陷无测试拦截。

### 本轮新发现

- 无独立新 finding（第二层残余归入 f001 复核）。

### 结论

- 前轮 finding 复核：f001 第一层（CRLF 识别）已修；第二层（`file()`/CLI newline 归一化）仍存在，复现确认 `\r\r\n` 数据破坏 → 修不彻底，important 未消除。
- 本轮新发现：0 条。
- 未进表的提示：
  - CRLF 文档 + 默认 `end_of_line: lf` 走 `file()` 时，输出 front matter 保持 CRLF、正文归一 LF，全文件混合行尾。此系 AC-001「front matter 逐字节一致」的直接推论，不判缺陷；f001 建议的换行统一策略可一并决策。
  - `_api.py` 103 行、`_strip_front_matter` CC≈3、`test_front_matter.py` 60 行，均未达阈值。
- 总体判断：CRLF 识别已修复，但 f001 第二层陷阱（`file()`/CLI 写回把保留的 CRLF front matter 翻成 `\r\r\n`）仍存在，CRLF 输入类违反 AC-001/AC-004，存在未解决 important，FAIL。
- AC 复验方式：
  - AC-001：`re_verified` — LF 路径逐字节保留；CRLF 经 `text()` 保留、经 `file()`+keep 破坏为 `\r\r\n`（本机复现）。
  - AC-002：`re_verified` — `text()` 正文格式化断言本机执行通过。
  - AC-003：`re_verified` — 无 front matter 文档走原管线行为不变；`test_no_front_matter_unchanged` 恒真幂等断言已去除（`:29`）。
  - AC-004：`re_verified` — LF front matter 内容不改写；CRLF 经 `file()`+keep 改写（同 f001）。
  - coverage = 4/4（CRLF 子类失败已计入 f001）
- 系统性 follow-up：无。

verdict: FAIL

## Round 3 (2026-08-11 22:46 UTC+8)

reviewed_scope: 3e4000b4da879b9e

### 前轮 finding 复核

- t001_code_f001（important，CRLF front matter 破坏）——**已修**，两层均真修（以 diff + 本机执行复验，不采信处置表自述）。
  - 第一层（CRLF 分隔行识别）：`_api.py:28,31` 首行与闭合行判定均用 `rstrip("\r\n")`，无残留 `\r` 误判。本机复验 `text()` 对 CRLF fm 文档正确剥离。
  - 第二层（`file()`/CLI newline 归一化二次破坏）：`_api.py:42` `front_matter = "".join(lines[:j]).replace("\r\n", "\n")` 将剥离保留的 front matter 统一归一为 LF；`file()`（`_api.py:113`）与 CLI（`_cli.py:143`）的 `formatted_md.replace("\n", newline)` 只做一次转换，不再把既有 `\r\n` 翻成 `\r\r\n`。本机执行复验：
    - `file()` + `end_of_line: keep` 于 CRLF fm 文档 → 写回 `'---\r\nname: x\r\n---\r\n# Title\r\n\r\nSome text.\r\n'`，fm 段与输入逐字节一致，`\r\r\n` 不存在。
    - `file()` 默认 lf → 全文档统一 LF，fm 段无 CRLF 残留、无混行尾。
    - CLI 等价路径（`text()` 后 `replace("\n", newline)`）→ 同 `file()`，无 `\r\r\n`。
    - LF 输入 + `end_of_line: crlf` → 统一 CRLF，fm 段 `'---\r\nname: x\r\n---\r\n'`。
  - Round 2 指出 file() 路径无测试覆盖：已补 `tests/test_front_matter.py:70-90` `test_file_crlf_end_of_line_keep`（file()+keep 写回，断言 `\r\r\n` 不存在），另有 `test_front_matter_crlf_preserved`（text() 路径）。8 条测试本机逐条执行全部通过。
- 顺带核对 test reviewer 同根因 f003/f004（代码层证据）：浅 YAML 判定（`_api.py:34-38` 要求块内含至少一行 `key: value`）使正文开头 `---` 不再被误吞；f003 实测输入 `'---\n\n#a\n\n---\n\n# B\n'` 现输出为两处 thematic break（`___` 串）+ 格式化正文。f004 同 f001 第二层修复，`test_file_crlf_end_of_line_keep` 覆盖 file() 写回。

### 本轮新发现

- 无独立新 finding。扫描修复引入的新问题：
  - 浅 YAML 判定把误吞边界收窄为「块内含 `:` 行」。spec AC-001 定义 front matter 为「含 `name:`/`description:` 等键值」，判定与该定义一致；残留歧义（`---` 包 `: ` 行的非 fm 文档）属 spec 风险区已接受边界。commonmark spec 唯一以 `---` 开头的示例 96/98 及既有全部 fixture 均无 `:` 闭块，行为不变。
  - `text()` 对 CRLF fm 输出 LF 归一，符合 `text()` 恒 LF 输出契约，并消除 Round 2 所述「默认 lf 时 fm 段 CRLF + 正文 LF 混行尾」现象（现统一 LF）。
  - 空块 `---\n---\n`、未闭合 `---\nname: x\n`、block scalar `|` 值、fm 后空行保留等边界本机复验均正确。

### 结论

- 前轮 finding 复核：f001 两层均真修，无残留。
- 本轮新发现：0 条。
- 未进表的提示：
  - 文件大小：`src/mdformat/_api.py` 115 行、`tests/test_front_matter.py` 90 行，均低于阈值；`_strip_front_matter` CC≈7，低于 10。
  - 范围外观察：`_strip_front_matter` 对无 fm 文档每次 `splitlines` 建列表（O(n) 内存），一行判定即返回，开销可忽略；不判 finding。
  - 不偏航：src 仅改 `_api.py`；docs 更新（spec 未知契约已验证、task 处置表、s001/d001）与实现一致。
- 总体判断：f001 二层陷阱均已消除，LF/CRLF × keep/crlf/lf 各组合下 front matter 内容逐字节保留、行尾归一一致，无未解决 critical/important。
- AC 复验方式：
  - AC-001：`re_verified` — LF fm 逐字节保留（`test_front_matter_preserved_byte_for_byte` 通过）；CRLF 经 `file()`+keep 写回与输入逐字节一致、无 `\r\r\n`（本机执行复验）。
  - AC-002：`re_verified` — `test_body_formatted` 对正文切片精确断言，本机执行通过。
  - AC-003：`re_verified` — 无开头 `---` 文档走原管线；正文开头 `---` 误吞子类已消除（`---\n\n#a\n\n---\n\n# B\n` 渲染为 thematic break + 格式化正文）；commonmark 96/98 行为不变。
  - AC-004：`re_verified` — `|` 块值与 block scalar fm 内容不改写，本机执行复验。
  - coverage = 4/4
- 系统性 follow-up：无。

verdict: PASS
