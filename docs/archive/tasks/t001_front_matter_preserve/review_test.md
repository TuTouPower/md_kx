# Task review t001（reviewer_focus: 测试）

- task：`t001_front_matter_preserve`
- spec：`docs/tasks/t001_front_matter_preserve/spec.md`
- diff_anchor：`2586c5769c2e76c40010c1b6771922611f160b0d`
- target：`git diff 2586c5769c2e76c40010c1b6771922611f160b0d`
- round：1
- reviewed_at：2026-08-11 22:10 UTC+8

## Findings

### t001_test_f001 - `test_no_front_matter_unchanged` 断言恒真空转，AC-003 无有效证据

- 严重度：important
- 锚点：AC-003（无 front matter 文档行为与格式化结果不变）
- 位置：`tests/test_front_matter.py:29-34`（`test_no_front_matter_unchanged`）
- 问题：
  1. `tests/test_front_matter.py:32`：`assert mdformat.text(md) == mdformat.text(md)  # 幂等` 对确定性纯函数恒真（同一入参两次调用的结果必然相等）。注释声称测「幂等」，但幂等断言应为 `mdformat.text(mdformat.text(md)) == mdformat.text(md)`。该断言零证据，命中危险模式「恒真断言」。
  2. `tests/test_front_matter.py:34`：`assert "---" in mdformat.text(md) or "___" in mdformat.text(md)` 是弱化断言（包含式 + `or` 双渲染容忍）。实测该输入 `# A header\n\n---\n\n# B header\n` 的输出为 `'# A header\n\n____（76 下划线）\n\n# B header\n'`——此断言只证明「分隔线以某种形式渲染」，既未比对改动前行为，也未验证正文格式化结果，AC-003「行为与格式化结果不变」得不到验证。
- 建议：改为精确输出断言（如 `assert mdformat.text(md) == "# A header\n\n___...\n\n# B header\n"`，或至少断言两个 ATX 标题与分隔线的结构化输出）；幂等断言改为 `mdformat.text(mdformat.text(md)) == mdformat.text(md)` 或删除。

### t001_test_f002 - CRLF front matter 不被识别，AC-001/AC-004 对 CRLF 文档失效且无覆盖

- 严重度：important
- 锚点：AC-001（front matter 与输入逐字节一致）、AC-004（front matter 内部不被改写）
- 位置：`src/mdformat/_api.py:22,25`（`_strip_front_matter` 分隔符判定用 `.rstrip("\n")`）；`tests/test_front_matter.py` 全文件无 CRLF 用例
- 问题：CRLF 文档首行 `"---\r\n"` 经 `.rstrip("\n")` 得 `"---\r"`，永不等 `"---"`，front matter 不剥离 → 进渲染管线被破坏。实测 `mdformat.text('---\r\nname: x\r\n---\r\n# Title\r\n')` 输出 `'___...\n\n## name: x\n\n# Title\n'`，front matter 完全丢失（被解析成 thematic break + 标题）。mdformat 整体显式支持 CRLF（`src/mdformat/_util.py:120 detect_newline_type`、`tests/test_api.py:100 test_eol__keep_crlf`、`end_of_line` 选项），AC-001 逐字节保留对 CRLF 文档同样应成立。属可观测行为缺陷：输入 CRLF fm 文档 → front matter 数据丢失。
- 建议：分隔符判定兼容 `\r\n`（如 `.rstrip("\r\n")` 或先规范化行尾再剥离），并补一条 CRLF front matter 保留测试。

## 结论

- 前轮 finding 复核：Round 1，无前轮。
- 改测方向复核：无。本轮只新增 `tests/test_front_matter.py`，未修改任何既有测试，无「迁就实现」改测。
- 本轮新发现：2 条。
- 未进表的提示：
  - 单 `\r` 行尾（旧 Mac 风格）与 CRLF 同根因，不被识别，属 f002 同一修复面。
  - AC-003「纯正文」子类由既有 4663 条测试隐式覆盖（非 `---` 开头文档走改动前相同代码路径，全套 `pytest tests/` 4663 passed / 5 skipped），故未单独出 finding；问题仅在「普通 `---` 分隔线」子类的显式断言空转（f001）。
  - `test_front_matter_trailing_blank_line_preserved`（精确全量相等）与 `test_body_formatted`（精确正文）为强断言，值得保留。
- 总体判断：AC-001/002/004 测试可信（真实 `mdformat.text()` 入口、逐字节断言），但 AC-003 显式测试恒真空转（f001），且 CRLF front matter 数据丢失无覆盖（f002），两条未解决 important → FAIL。
- 系统性 follow-up：无。

### AC 复验披露

- AC-001：`re_verified` — 独立重跑 `pytest tests/test_front_matter.py`（5 passed）；实验确认 LF fm 逐字节保留（`mdformat.text('---\nname: x\n---\n# Title\n')` 输出 `'---\nname: x\n---\n# Title\n'`）。
- AC-002：`re_verified` — `test_body_formatted` 对正文切片断言精确规范输出，pytest 通过。
- AC-003：`re_verified` — 重跑通过，但实测确认该测试断言为空转（见 f001），AC-003 无有效证据。
- AC-004：`re_verified` — `test_front_matter_content_not_formatted` 对 `|` 块值逐字节断言，pytest 通过；实验确认缩进 `---` 不误判为闭合符。

`coverage = re_verified / 总 AC 数 = 4 / 4`

reviewed_scope: 3e84a9c4abb39eb1

verdict: FAIL

## Round 2 (2026-08-11 22:30 UTC+8)

### t001_test_f003 - AC-003 误判子类（正文开头 `---`）仍无覆盖，实测格式化结果发散

- 严重度：important
- 锚点：AC-003（无 front matter 的文档（普通 `---` 分隔线）行为与格式化结果不变）；spec 风险/回退「识别逻辑误吞正文开头分隔线……识别失败场景由该 AC 测试覆盖」
- 位置：`tests/test_front_matter.py:29-35`（`test_no_front_matter_unchanged`）；根因 `src/mdformat/_api.py:22-31`（`_strip_front_matter`）
- 问题：f001 恒真断言已消除，但 AC-003 测试输入首行是 `# A header`，`_strip_front_matter` 在第一行判定即返回（`_api.py:23`），完全未触达「正文开头 `---` 被误吞」这一 spec 明确列出的风险路径。实测 `mdformat.text('---\n\n#a\n\n---\n\n# B\n')` 输出 `'---\n\n#a\n\n---\n\n# B\n'`——整块 `---\n\n#a\n\n---` 被当作 front matter 原样保留、格式化被跳过；基线（无 front matter 支持）下该输入应把两处 `---` 渲染为 thematic break 并对正文走格式化管线。该输入无 YAML front matter 意图，属「普通 `---` 分隔线」文档，AC-003「格式化结果不变」不满足。spec 回退声明该识别失败场景由 AC-003 测试覆盖，当前测试未覆盖。
- 建议：补一条「正文开头为 `---`（且后续另有 `---`）」的 AC-003 用例（断言两处 `---` 渲染为 thematic break、正文格式化生效），或显式声明该歧义场景接受整块保留并写入 spec「有意不测」。
- 备注：该输入同时可读作 YAML front matter（`---` 为 YAML 文档标记），属设计固有歧义；但 spec 已声明由 AC-003 覆盖，缺口在测试侧，由 implementer 二选一处置。

### t001_test_f004 - CRLF front matter 经 `file()`/CLI 路径字节损坏（`\r\r\n`）或拒绝格式化，CRLF 测试未覆盖文件路径

- 严重度：critical
- 锚点：AC-001（front matter 与输入逐字节一致）；破坏既有行尾契约（`tests/test_api.py:100 test_eol__crlf`、`tests/test_api.py:114 test_eol__keep_crlf` 证明 `file()` 整文档行尾归一是已文档化行为）
- 位置：根因 `src/mdformat/_api.py:13-31`（`_strip_front_matter` 把原文 `\r\n` 原样保留进 front_matter 串，使 `text()` 输出不再恒为 LF）与 `src/mdformat/_api.py:100`（`file()` 对全串 `formatted_md.replace("\n", newline)`，把 fm 段既有 `\r\n` 加倍为 `\r\r\n`）；测试缺口 `tests/test_front_matter.py:53-60`（`test_front_matter_crlf_preserved` 只走 `text()`）
- 问题（实测）：
  1. `mdformat.file(p, options={'end_of_line':'crlf'})` 处理 CRLF fm 文档 → 文件写为 `'---\r\r\nname: x\r\r\n---\r\r\n# Title\r\n'`，fm 段出现双 `\r`，字节损坏，AC-001 逐字节一致不成立；`end_of_line='keep'` 同样损坏。
  2. CLI `mdformat --end-of-line crlf|keep <CRLF fm 文件>` → 报「Formatted Markdown renders to different HTML」拒绝格式化（HTML 一致性校验对比损坏输出失败），exit 1，CRLF fm 文档无法经 CLI 格式化。
  3. 默认 eol（lf）不报错，但 fm 段保持 CRLF、正文归一为 LF，行尾混用，与 mdformat 整文档归一契约不符。
  现有 `test_front_matter_crlf_preserved` 只调用 `mdformat.text()`（不经 eol 转换），f002 的「CRLF 支持」看似有测试实则未触达用户主路径（`file()`/CLI），构成假覆盖。
- 建议：修复 `_strip_front_matter` 与 `file()` 的行尾协作（如 `text()` 输出统一 LF 后再重组 fm，或 `file()` 转换前先将 fm 段行尾归一），并补 `file()`/CLI 路径的 CRLF fm 用例（含 `end_of_line='crlf'/'keep'`）。

## Round 2 结论

- 前轮 finding 复核：
  - t001_test_f001：已修。恒真断言 `mdformat.text(md) == mdformat.text(md)` 与弱化 `or` 包含断言均已删除，替换为有意义断言 `assert "## " not in out`（`test_front_matter.py:34`）与 `assert out.startswith("# A header\n\n")`（`:35`）。实测对正确输出成立；若分隔线被误解析为标题或开头标题被改写则断言失败，非空转。AC-003 剩余误判子类覆盖缺口另立 f003。
  - t001_test_f002：修不彻底。`text()` 路径 CRLF 识别已修复（`_api.py:23,26` 用 `.rstrip("\r\n")`），新增 `test_front_matter_crlf_preserved`（`test_front_matter.py:53-60`）通过且有实际断言；但 `file()`/CLI 路径对 CRLF fm 文档仍破坏 AC-001（`\r\r\n` 损坏 / 拒绝格式化 / 默认混行尾），且新测试未覆盖该路径，见 f004。
- 改测方向复核：无迁就实现改测。f001 测试改动方向为「删除恒真/弱断言、替换为有意义断言」，属加强而非迁就实现。
- 本轮新发现：2 条（f003 important、f004 critical）。
- 未进表的提示：
  - f004 的默认 eol 混行尾（fm 段 CRLF + 正文 LF）与 `\r\r\n` 损坏同根因，修复应一并处理。
  - 单 `\r` 行尾（旧 Mac 风格）与 CRLF 同根因（`_api.py:23` 的 `.rstrip("\r\n")` 不剥离孤立 `\r`），随 f004 修复面一并评估，未单独立 finding。
  - AC-003「纯正文」子类仍由既有全量测试隐式覆盖，未单独出 finding。
- 总体判断：f001 恒真断言已真修，但 f003（AC-003 误判子类无覆盖且实测发散）与 f004（CRLF fm 经 `file()`/CLI 字节损坏或拒绝格式化，测试未触达该路径）为未解决的重要/严重 finding → FAIL。
- 系统性 follow-up：无。

### AC 复验披露（Round 2）

- AC-001：`re_verified` — 重跑 `pytest tests/test_front_matter.py`（6 passed）；实验确认 `text()` 对 LF/CRLF fm 逐字节保留；但经 `file()`/CLI + `end_of_line='crlf'/'keep'` 时 fm 段损坏为 `\r\r\n` 或拒绝格式化，AC-001 经文件路径不成立（f004）。
- AC-002：`re_verified` — `test_body_formatted` 对正文切片精确断言，pytest 通过。
- AC-003：`re_verified` — 重跑通过且断言非恒真；但正文开头 `---` 误判子类无覆盖且实测发散（f003），AC-003 证据不全。
- AC-004：`re_verified` — `test_front_matter_content_not_formatted` 对 `|` 块值逐字节断言，pytest 通过。

`coverage = re_verified / 总 AC 数 = 4 / 4`

reviewed_scope: bc065a595b0ec5b7

verdict: FAIL

## Round 3 (2026-08-11 22:47 UTC+8)

本轮无新 finding。前轮 f003/f004 均已核实真修（以 `git diff 2586c5769c2e76c40010c1b6771922611f160b0d` 与实测为准）。

### t001_test_f003 - AC-003 误判子类已修（浅 YAML 判定 + 真测试）

- 复核：已消除。
- 证据：
  1. 实现侧新增浅 YAML 判定（`src/mdformat/_api.py:32-38`）：`---` 闭合块内须含至少一行 `key: value`（`":" in line`）才视为 front matter，否则整串原样走渲染。实测 `mdformat.text('---\n\n# A header\n\n---\n\n# B header\n')` 输出为 76 下划线 thematic break 开头的规范格式化结果，不再整块吞入。
  2. 测试侧新增 `test_blank_separator_not_front_matter`（`tests/test_front_matter.py:64-71`），断言 `output.startswith("_")`、两个标题均格式化、无 `##`。若误吞回归，输出会以 `---` 开头，`startswith("_")` 立即失败——断言非空转，能捕获 swallow 回归。
- 结论：AC-003 误吞边界现既有覆盖、又测真行为，finding 消除。

### t001_test_f004 - CRLF 经 file()/CLI 字节损坏已修（LF 归一化根因）

- 复核：已消除。
- 证据（根因变更在 `src/mdformat/_api.py`）：
  1. `_strip_front_matter` 返回前对 front_matter 做 `.replace("\r\n", "\n")`（`_api.py:42`），fm 段统一为 LF；`file()` 再对全串 `.replace("\n", newline)`（`_api.py:113`），三态均归一，不再 `\r\r\n` 加倍。
  2. 实测三态全过：`end_of_line='crlf'` 输出单 `\r\n`、无 `\r\r\n`；默认 eol(lf) 输出统一 LF、无混行尾；`end_of_line='keep'` 保留 CRLF。CLI `python -m mdformat --end-of-line crlf <CRLF fm 文件>` exit 0，写回单 `\r\n`，不再拒绝格式化。
  3. 测试侧新增 `test_file_crlf_end_of_line_keep`（`tests/test_front_matter.py:74-90`），直接断言 `content.startswith("---\r\nname: x\r\n---\r\n")` 且 `"\r\r\n" not in content`，针对 f004 的损坏断言有效。
- 结论：f004 三个失败模式（`crlf` 加倍 / CLI 拒绝 / 默认混行尾）全部实测修复，finding 消除。

### f001/f002 连带复核

- t001_test_f001（AC-003 恒真断言）：仍保持已修。`test_no_front_matter_unchanged`（`tests/test_front_matter.py:34-35`）为 `assert "## " not in out` + `assert out.startswith("# A header\n\n")`，非恒真、可失败。
- t001_test_f002（CRLF 未识别）：随 f004 一并彻底修复。`text()` 路径 `.rstrip("\r\n")` 识别（`_api.py:28,31`）配合 `test_front_matter_crlf_preserved`（`:53-61`）；file()/CLI 路径由 f004 修复覆盖。Round 2 所述「修不彻底」的 file() 侧缺口已闭合。

## Round 3 结论

- 前轮 finding 复核：
  - t001_test_f001：已消除（自 Round 1 起保持，本轮再次核实断言非恒真）。
  - t001_test_f002：已消除（本轮确认 file()/CLI 路径缺口已随 f004 修复闭合）。
  - t001_test_f003：已消除（浅 YAML 判定 + `test_blank_separator_not_front_matter` 真测试，实测不再误吞）。
  - t001_test_f004：已消除（fm 段 LF 归一根因修复，`crlf`/`keep`/默认 eol 及 CLI 实测均无 `\r\r\n` 损坏、不混行尾、不拒绝格式化）。
- 改测方向复核：无迁就实现改测。本轮相对 Round 2 仅新增 2 条测试（`test_blank_separator_not_front_matter`、`test_file_crlf_end_of_line_keep`）与实现侧浅 YAML 判定，无修改既有测试预期迁就当前实现。
- 本轮新发现：0 条。
- 未进表的提示：
  - `test_file_crlf_end_of_line_keep` 只覆盖 `end_of_line='keep'`，f004 建议含 `'crlf'` 变体；但 `'crlf'`/默认 eol 实测已由同一 `.replace("\n", newline)` 机制验证通过，属「可再加 case」级补充，非缺口。
  - 含冒号行的混合歧义输入（如 `---\nname: x\n\n# A header\n\n---\n`）按 spec AC-001 定义（`---` 包裹 + key:value）本就应视为 front matter 保留，浅 YAML 判定行为符合契约，非缺陷。
  - CLI CRLF fm 路径实测通过但无自动化用例，依赖 `file()` 同路径覆盖，如需可后续补充，不阻断。
- 总体判断：前轮 4 条 finding（含 1 critical 1 待核 important）经 diff 与实测全部真修，无未解决 critical/important，本轮无新 blocker → PASS。
- 系统性 follow-up：无。

### AC 复验披露（Round 3）

- AC-001：`re_verified` — `pytest tests/test_front_matter.py` 8 passed；实测 `text()` 对 LF/CRLF fm 逐字节保留，`file()`/CLI + `crlf`/`keep`/默认 eol 输出单 `\r\n`、无 `\r\r\n`、不混行尾。
- AC-002：`re_verified` — `test_body_formatted` 对正文切片精确断言（`# Title\n\nSome **bold** text.\n`），pytest 通过。
- AC-003：`re_verified` — `test_no_front_matter_unchanged` 断言非恒真；`test_blank_separator_not_front_matter` 实测输出以下划线 thematic break 开头、正文格式化，误吞边界有真覆盖。
- AC-004：`re_verified` — `test_front_matter_content_not_formatted` 对 `|` 块值逐字节断言，pytest 通过；`test_front_matter_crlf_preserved` 验证 CRLF fm 内容不被改写。

`coverage = re_verified / 总 AC 数 = 4 / 4`

reviewed_scope: 3e4000b4da879b9e

verdict: PASS
