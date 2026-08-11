# Task review t003（reviewer_focus: 代码）

- task：`t003_builtin_table_handling`
- spec：`docs/tasks/t003_builtin_table_handling/spec.md`
- diff_anchor：`ddcd76a5c2e605d6d6f3490e766b54bbf17676b8`
- target：`git diff ddcd76a5c2e605d6d6f3490e766b54bbf17676b8`
- round：1
- reviewed_at：2026-08-12 00:40 UTC+8

reviewed_scope: eb7752027c1bc5d0

## Findings

### t003_code_f001 - none 模式（默认）不保证表格原样输出，含转义管道/反斜杠的表格文本被段落管线改写

- 严重度：important
- 锚点：AC-001（表格开关为 none/默认时「表格内容不被触碰，原样输出」）
- 位置：`src/mdformat/_util.py:37-38`（none 态走「禁用 table 规则」路径，表格文本落入普通段落管线）；`src/mdformat/renderer/_context.py:633-638`
- 问题：none 模式通过禁用 markdown-it table 规则实现，表格行因此按普通 CommonMark 段落处理。段落/文本 renderer 会对转义做规范化：
  - 输入 `| a | b |\n| --- | --- |\n| x\|y | z |`（GFM 表格合法语法，`\|` 为单元格内转义管道）→ 输出 `| a | b |\n| --- | --- |\n| x|y | z |`，`\|` 被吞掉；
  - 输入含 `c\d` → 输出 `c\\d`，反斜杠被加倍。
  - 已确认 `a \| b` 段落本身就会变 `a | b`（`src/mdformat/renderer/_context.py:129` `text.replace("\\","\\\\")` + 反斜杠归一化），即该行为是既有段落行为；但 AC-001 明确承诺默认态表格「原样输出」，且 spike 报告（`docs/spikes/s003_table_parsing_render/report.md`）批准的设计是「不处理=原样跳过」。当前实现对该类表格既不原样，也未跳过，与 AC 与已批准设计均不符。
  - 可观测后果：默认设置格式化含转义管道表格的文件后，`\|` 被剥除；该文件此后按 GFM 渲染（或切换 pad/compact）时表格将错列、内容错位。属静默语义改动。
- 建议：二选一，处置时需明确——(a) none 态真正跳过表格块（需避免表格文本进入段落规范化管线，可能需在解析或渲染层识别表格块并原样输出）；(b) 若认定「none = 按普通文本处理，段落规范化照常」是预期语义，则修订 AC-001 措辞（如「表格不参与表格化处理」），并在 spec 明示转义会被规范化的边界。按当前 spec 文字，现状不满足 AC-001。

### t003_code_f002 - pad/compact 模式单元格内 `\|` 转义管道渲染后未再转义，破坏表格结构并丢失单元格内容

- 严重度：important
- 锚点：AC-004（三态下表格语法正确可渲染）；可观测行为缺陷（输入合法表格 → 输出结构损坏/内容丢失；非幂等）
- 位置：`src/mdformat/renderer/_context.py:615-620`（`_cell_text`）、`644-669`（compact/pad 行拼接）
- 问题：markdown-it 把单元格 `x\|y` 正确解析为单个单元格，td 的 inline 内容为 `x|y`（已用 token dump 确认）。`_cell_text` 经 `text` renderer 输出 `x|y`，但 `text` renderer 不转义 `|`，而 `table` renderer 用 `| ... |` 包 cell，导致输出表格把该管道当作列分隔符：
  - `mdformat.text("| a | b |\n| --- | --- |\n| x\|y | z |\n", options={"table_mode":"pad"})` → `| a | b |\n| --- | --- |\n| x|y | z |\n`（数据行变 3 列）。
  - 二次格式化 → `| a | b |\n| --- | --- |\n| x | y |\n`：`y` 升格为列、`z` 整格丢失，且输出非幂等（`text()` 两次运行结果不同）。
  - CLI 路径因 `is_md_equal` 校验不通过而报错 `Could not format ...`（rc=1），文件不落盘；但 `mdformat.text()` API 与 `--no-validate` 路径静默损坏。
- 建议：在 `_cell_text` 对单元格内容中的 `|` 转义为 `\|`（并可考虑对前导/尾随空格按 GFM 语义处理），确保 pad/compact 输出的表格结构稳定、幂等。修复后补充含 `\|` 单元格的 pad/compact 用例。

### t003_code_f003 - pad/compact 模式丢弃对齐冒号（`:---` / `:---:`）

- 严重度：minor
- 锚点：无直接 AC；可观测语义损失
- 位置：`src/mdformat/renderer/_context.py:650, 666-667`
- 问题：输入 `| a | b |\n| :--- | :---: |\n| 1 | 2 |`，pad/compact 输出分隔行均为 `| --- | --- |`，左/中对齐意图被静默丢弃，渲染后列对齐语义变化。表格仍为合法语法（满足 AC-004），但属格式化时的语义损失。spec 范围限定「表格语法子集」、非范围含 GFM 扩展语义，对齐冒号是否在范围内有解释空间——若不打算支持，建议在 spec 明示对齐冒号不保留；若支持，则生成分隔行时保留 `:`。
- 建议：确认对齐冒号是否纳入子集；纳入则保留，不纳入则写入 spec 边界。

### t003_code_f004 - `table()` renderer 中 `table_mode == "none"` 分支为不可达死代码

- 严重度：minor
- 锚点：无 AC；死代码
- 位置：`src/mdformat/renderer/_context.py:637-638`
- 问题：none 态在解析层即禁用 table 规则（`src/mdformat/_util.py:37-38`），因此 `table` token 只有在 mode != none 时才会产生，renderer 的 `if table_mode == "none": return ""` 分支在正常接线下不可达（两遍渲染复用同一 mdit/options，同样不可达）。该分支若经第三方扩展（启用 table 规则且未提供 renderer）触达，会静默删除整张表。建议删除或在注释中说明防御意图，避免误导读者以为 none 态走 renderer 路径（spike 报告表述为「三态开关由 renderer 控制输出」，与实现实际分层不符）。
- 建议：删除死分支，或更新 spike 文档说明 none 态实际在解析层处理。

## 结论

- 前轮 finding 复核（Round 1）：无前轮。
- 本轮新发现：4 条（f001、f002 important；f003、f004 minor）。
- 未进表的提示：
  - 文件过大（降级规则，不进表）：`src/mdformat/renderer/_context.py` 731 行（净增 58，≥400 minor 阈值，<800 未达 important）；`src/mdformat/_cli.py` 500 行（净增 5，≥400）。均未给出不可拆硬约束。仅提示，不构成缺陷。
  - 复杂度：`table()` 圈复杂度约 6，未达阈值；无提示。
  - 范围外观察：cell 内 code span 含管道（`` `x|y` ``）被 markdown-it-py 拆成两格（token dump 确认 inline `\`x` 与 `y\``），属上游解析器行为（不保护 code span 内管道，与 GFM spec 有差异），非本实现缺陷，按「解析边界误吞普通文本竖线」风险记录在结论。
  - README「Options」usage 块未收录 `--table-mode`（`README.md:74-108`）；与 t002 未收录 `--indent-width` 同况，README 为生成快照，非本 task AC，提示不改。
  - AC-004 测试 `tests/test_table.py:41-44` 断言 `"|" in out` 偏弱（toContain 式），是否充分覆盖 AC-004 交由 test reviewer 判定。
- AC 复验方式：
  - AC-001：re_verified——`.venv/bin/python` 复跑 `mdformat.text(TABLE_MD)==TABLE_MD` 通过（简单表）；但复验含 `\|`/反斜杠表格时输出被改写，判定 AC-001 对转义表格不满足。
  - AC-002：re_verified——复跑 pad 用例，输出列宽对齐正确（`| aaa | b |` / `| 1   | 2 |`）。
  - AC-003：re_verified——复跑 compact 用例，紧凑不 pad。
  - AC-004：re_verified——pad/compact/none 输出均能被再次解析且各态幂等（简单表），但 f002 的 `\|` 场景输出结构损坏，AC-004 不完全满足。
  - AC-005：re_verified——复跑无表格文档三态输出一致；全量测试 4682 passed / 5 skipped（含 commonmark spec）确认默认态无回归。
  - coverage = re_verified / 总 AC 数 = 5/5
- 总体判断：AC-001 默认态对转义表格不原样、pad/compact 对 `\|` 单元格破坏表格结构且非幂等，两个可观测缺陷未解决；仅有 minor 不阻断，但当前存在 2 个未解决 important → FAIL。
- 系统性 follow-up：无。

verdict: FAIL

## Round 2 (2026-08-12 00:39 UTC+8)

reviewed_scope: 6ebc6caae00baf0c

## 前轮 finding 复核（以 git diff 与复跑为准）

### t003_code_f001 - 修不彻底：转义管道剥除已修复，但默认态 AC-001「原样输出」仍不满足（对齐冒号在默认态被丢弃）

- 复核结论：核心失败场景（默认态 `\|` 被段落管线剥除）**已修复**。复跑：`| a | b |\n| --- | --- |\n| x\|y | z |` 默认输出 `| a | b |\n| --- | --- |\n| x\|y | z |`，`x\|y` 保留且幂等（`src/mdformat/_util.py:37-38` 无条件 `ruler.enable("table")` + `src/mdformat/renderer/_context.py:615-621` `_cell_text` 转义裸 `|`）。
- 但修复将 none 态从「段落回退」改为「table renderer 重组」，默认态因此对表格做结构规范化，**AC-001 仍不满足**，且引入新的默认态回归（见 f005）：`| :--- | :---: |` → `| --- | --- |`（`_context.py:668` 分隔行固定 `"---"`）；`|  a  | b |` → `| a | b |`（单元填充归一）；ragged 行补空单元格。Round 1 与 task 前基线（commonmark 段落回退）均保留对齐冒号，本次修复为**新引入**的默认态语义回归。
- 处置建议：f001 原建议二选一未落地——既未「真正跳过表格块」，也未修订 AC-001。修复仅解决了转义管道这一具体机制，AC-001「不被触碰，原样输出」的默认态承诺仍未达成。

### t003_code_f002 - 已修复

- 复核结论：`_cell_text` 转义裸管道后，pad/compact 输出 `x\|y` 保留且幂等。复跑：pad 态 `| x\|y | z |` 输出 `| x\|y | z |`、二次格式化相等；compact 同理。另验：表头 `\|`、单格多 `\|`、ragged 行（2 列体 vs 3 列表头）三态均幂等。

### t003_code_f003 - 仍存在（minor），范围扩大

- 复核结论：pad/compact 分隔行仍固定 `---`，对齐冒号丢弃如旧（`_context.py:657`、`668`）。维持 Round 1 minor 判定（处理态属 formatter 设计选择，spec 对对齐冒号有解释空间）。但其范围由处理态**扩大到默认态**（见 f005），默认态因 AC-001 直接约束，升级为 important。

### t003_code_f004 - 已修复

- 复核结论：`if table_mode == "none": return ""` 死分支已删除。`table()` 现按 `pad` / `none|compact` 两路处理（`_context.py:644-670`），none 态不再有不可达分支；`_util.py` 注释也明确「table renderer 处理三态（含 none 透传）」，与实现一致。

## 本轮新发现

### t003_code_f005 - none/默认态丢弃对齐冒号，AC-001「原样输出」被违反（修复引入的新回归）

- 严重度：important
- 锚点：AC-001（默认态「表格内容不被触碰，原样输出」）；可观测行为缺陷（默认格式化静默改变表格对齐语义）
- 位置：`src/mdformat/_util.py:37-38`（无条件启用 table 规则 → 默认态表格进入 table renderer）；`src/mdformat/renderer/_context.py:668`（分隔行固定 `"---"`，`markdown-it` 解析出的对齐信息被丢弃）
- 问题：输入 `| a | b |\n| :--- | :---: |\n| 1 | 2 |\n`，默认 `mdformat.text()` 输出 `| a | b |\n| --- | --- |\n| 1 | 2 |\n`，`:---`/`:---:` 被丢弃。Round 1 及 task 前基线中默认态表格回退到段落管线，对齐冒号原样保留；本次「always enable table」修复使默认态对表格做重组，对齐冒号成为**新引入**的默认态语义回归——默认格式化后 GFM 渲染列对齐（左/中/右）被静默改写。另默认态还规范化单元填充（`|  a  | b |` → `| a | b |`）与 ragged 结构（补空单元格），均与 AC-001「原样输出」字面不符（填充/ragged 无渲染语义变化，不单独计；对齐冒号有渲染语义变化，计 important）。
- 建议：二选一并明确处置——(a) none 态真正不触碰表格（保留对齐冒号，或对对齐列生成 `:---`/`---:` 分隔行，markdown-it 已解析 alignment 可用）；(b) 若认定对齐冒号属「GFM 扩展语义」不在子集内，则修订 AC-001 措辞，明示默认态对表格做结构规范化、对齐冒号不保留，消除「原样输出」承诺与实现的分歧。修复后补 `:---:` 默认态用例。

## 结论（Round 2）

- 前轮 finding 复核：f001 修不彻底（转义管道已修，默认态 AC-001 仍不满足，问题以 f005 形式延续）；f002 已消除；f003 仍存在（minor，范围扩大）；f004 已消除。
- 本轮新发现：1 条（f005，important）。
- 未进表的提示：
  - 文件过大（降级规则，不进表）：`src/mdformat/renderer/_context.py` 732 行（净增 59，≥400 minor 阈值，<800 未达 important）；`src/mdformat/_cli.py` 500 行（净增 5）。与 Round 1 同况，无不可拆硬约束。
  - 复杂度：`table()` 圈复杂度约 6，未达阈值；`_cell_text`、`_table_rows` 各约 2。无提示。
  - 范围外观察：与 mdformat-gfm 类插件并存时 `ruler.enable("table")` 二次启用为安全 no-op（复跑确认不抛错），双 renderer 冲突风险由 spike 已批准的插件并存策略覆盖，不另行出 finding。
- AC 复验方式：
  - AC-001：re_verified——复跑简单表默认态 round-trip 通过；对齐冒号表默认态输出被改写（`:---` → `---`），判定 AC-001 对对齐冒号表不满足。
  - AC-002：re_verified——复跑 pad 用例列宽对齐正确。
  - AC-003：re_verified——复跑 compact 紧凑不 pad。
  - AC-004：re_verified——三态含 `\|` 单元格、ragged 行均幂等（复跑 + `tests/test_table.py` 8 项全过）；f002 结构损坏场景已消除。
  - AC-005：re_verified——全量测试 4683 passed / 5 skipped，默认态无回归。
  - coverage = re_verified / 总 AC 数 = 5/5
- 总体判断：f002/f004 已真修，f001 的转义管道部分已真修；但默认态（none）AC-001「原样输出」仍不满足，且本次修复新引入对齐冒号丢弃这一默认态语义回归（f005，important 未解决）→ FAIL。
- 系统性 follow-up：无。

verdict: FAIL

## Round 3 (2026-08-12 00:57 UTC+8)

reviewed_scope: 30e7c3c590aa3a29

## 前轮 finding 复核（以 git diff 与复跑为准）

- **t003_code_f001 - 已消除（核心语义）**：转义管道剥除 Round 2 已修；本次 Round 3 修复默认态对齐冒号后，f001 的核心可观测缺陷（默认态表格语义被改写）不再存在。复跑：`| a | b |\n| :--- | :---: |\n| 1 | 2 |` 默认 `text()` round-trip 完全相等；`x\|y` 默认保留且幂等。残余 AC-001 字面「原样」偏差（dash 数 `:----`→`:---`、单元填充 `|  1  |`→`| 1 |`、反斜杠 `c\d`→`c\\d`）均无渲染语义变化（GFM 渲染结果一致，属既有 inline/text renderer 规范化），延续 Round 2 确立边界，处置为改 spec 措辞（见本轮 f006），不计 FAIL。
- **t003_code_f002 - 已消除**：`_cell_text`（`src/mdformat/renderer/_context.py:615-622`）转义裸管道后，pad/compact 输出 `x\|y` 保留且幂等，复跑确认。
- **t003_code_f003 - 已消除**：Round 3 修复后 pad/compact 分隔行均保留对齐冒号。复跑 f003 原始输入 `| a | b |\n| :--- | :---: |\n| 1 | 2 |`，pad 输出 `| a | b |\n| :--- | :---: |\n| 1 | 2 |`、compact 输出 `| a | b |\n| :--- | :---: |\n| 1 | 2 |`，均幂等。原 minor 判定随修复撤销。
- **t003_code_f004 - 已消除**：`if table_mode == "none": return ""` 死分支删除无回归；`table()` 现按 `pad` 与 `none|compact` 两路处理，none 态不再有不可达分支。
- **t003_code_f005 - 已消除**（本轮重点）：默认态对齐冒号已保留。机制：`src/mdformat/_util.py:37-41` 无条件 `ruler.enable("table")`；`_context.py:635-657` `_table_aligns` 读 markdown-it th token `style:text-align:*`（token dump 确认 th/td 均带 style 属性）；`_context.py:660-667` `_align_marker` 与 708-718 none/compact 分隔行按 align 分支生成 `:---`/`---:`/`:---:`/`---`。复跑验证：
  - 默认态精确输入 `| a | b |\n| :--- | :---: |\n| 1 | 2 |` 输出完全相等（原样）。
  - 默认态无冒号表 `| a | b |\n| --- | --- |\n| 1 | 2 |` 原样 round-trip。
  - 四对齐类型表（`:---`/`---:`/`:---:`/`---`）默认态全部保留；`\|` 单元格默认保留。
  - pad/compact 对齐冒号保留且各态二次格式化幂等。

## 本轮新发现

### t003_code_f006 - AC-001「原样输出」措辞与实现仍存字面差异，建议修订 spec 明确规范化边界

- 严重度：minor
- 锚点：AC-001 字面「表格内容不被触碰，原样输出」；无可观测语义缺陷（无渲染语义变化），处置为改 spec，不计 FAIL
- 位置：`src/mdformat/renderer/_context.py:620-621`（`_cell_text` 经 inline/text renderer 规范化）、`697`（pad sep 宽度 `max(widths[i], 3)`）、`708-718`（none/compact sep 固定 3 dash）
- 问题：f005 修复后默认态已保留对齐冒号与转义管道，但以下输入仍被规范化：`| :---- |` → `| :--- |`（dash 数归一）；`|  1  |` → `| 1 |`（单元填充归一）；`c\d` → `c\\d`（反斜杠加倍，text renderer 既有行为）。三者 GFM 渲染结果均不变（无渲染语义变化，不构成可观测行为缺陷），但与 AC-001「原样输出」字面不符。f001/f005 建议的 option (b)（修订 AC-001 措辞，明示默认态做结构规范化、对齐冒号与转义保留）仍未落地。
- 建议：修订 AC-001 措辞（如「表格不参与 pad/compact 表格化处理，表格结构与对齐语义原样保留；单元格内容经常规 inline 规范化」），消除承诺与实现分歧。修复后补 `:----`/带空格单元格默认态用例。

## 结论（Round 3）

- 前轮 finding 复核：f001 已消除（核心语义；残余字面偏差见 f006）；f002 已消除；f003 已消除；f004 已消除；f005 已消除。
- 本轮新发现：1 条（f006，minor）。
- 未进表的提示：
  - 文件过大（降级规则，不进表）：`src/mdformat/renderer/_context.py` 783 行（净增 110，其中 Round 3 增约 51；≥400 minor 阈值，<800 未达 important）；`src/mdformat/_cli.py` 500 行（净增 5）。
  - 复杂度：`table()` 约 8、`_table_aligns` 约 8，均未达阈值；无提示。
  - 测试强度观察（交 test reviewer）：`tests/test_table.py:74-85` `test_alignment_colons_preserved` 断言偏弱——`"---:" in out` 对 `:---:` 亦成立（子串重叠），无法区分 right 与 center；`":---" in out` 对 `:---:` 亦成立。实现本身正确（复跑 align-all 确认 `---:` 正确输出）。
  - 范围外观察：cell 内 code span 含管道（`` `x|y` ``）被 markdown-it 表解析按列分隔拆开（Round 1 已记录，上游行为，非本实现缺陷）。
  - README Options 未收录 `--table-mode`（生成快照，非 AC，Round 1/2 同况）。
  - 范围核对：diff 仅触及 `_cli.py`/`_conf.py`/`_util.py`/`renderer/_context.py`/`tests/test_table.py` 与流程文档，无本 task 范围外模块改动。
- AC 复验方式：
  - AC-001：re_verified——复跑 f005 精确输入默认态 round-trip 完全相等；对齐冒号默认态保留；无冒号表原样。残余 dash/填充/反斜杠归一无渲染语义变化。
  - AC-002：re_verified——复跑 pad 对齐正确（含对齐冒号 pad 输出列宽对齐）。
  - AC-003：re_verified——复跑 compact 紧凑不 pad。
  - AC-004：re_verified——三态含 `\|` 单元格、ragged 行、对齐冒号均幂等；`tests/test_table.py` 9 passed。
  - AC-005：re_verified——全量测试 4684 passed / 5 skipped，默认态无回归。
  - coverage = re_verified / 总 AC 数 = 5/5
- 总体判断：f005（important）已真修——默认态无冒号表原样、显式对齐保留、全态幂等；全部前轮 blocker 消除，本轮无新 blocker，仅有 1 条 minor（spec 措辞对齐）→ PASS。
- 系统性 follow-up：建议 follow-up 标题「修订 AC-001 措辞明确默认态表格规范化边界」（f006 处置=改 spec）。

verdict: PASS

## Round 4 (2026-08-12 01:04 UTC+8)

reviewed_scope: a1a758730674a090

## 前轮 finding 复核（以 git diff 与复跑为准）

- **t003_code_f006 - 已消除（本轮核心）**：AC-001 措辞已修订（`docs/tasks/t003_builtin_table_handling/spec.md:34`）为「输出与原输入语义一致（单元格文本、转义管道、对齐语义保留）」，与实现一致：
  - 对齐语义保留：默认态 `| a | b |\n| :--- | :---: |\n| 1 | 2 |` round-trip 完全相等（`src/mdformat/renderer/_context.py` `_table_aligns` + `_align_marker` 按 markdown-it th style 生成 `:---`/`:---:`/`---:`）；无冒号表原样。
  - 转义管道保留：默认态 `x\|y` 原样输出且幂等（`_cell_text` 转义裸 `|`）。
  - 单元格文本：默认态 `:----`→`:---`（dash 归一）、`|  1  |`→`| 1 |`（填充归一）、`c\d`→`c\\d`（反斜杠加倍）仍经 inline/text renderer 规范化，均无渲染语义变化；新措辞「语义一致」不再要求字节级原样，f006 建议的规范边界落地。
  - 本轮 src 未变（`src/mdformat/_util.py:37-41` 无条件 enable table、`_context.py` table renderer 与 Round 3 审阅版本同）。
- 前轮 f001/f002/f003/f004/f005：Round 3 已确认消除，src 未变，全量测试结果与 Round 3 一致，复核维持消除。

## 本轮新发现

- 无。新增改动仅为 spec AC-001 措辞与 `tests/test_table.py` 断言修复，无新行为。

## 结论（Round 4）

- 前轮 finding 复核：f001/f002/f003/f004/f005 已消除（src 未变，全量测试一致）；f006 经 spec 措辞修订已消除。
- 本轮新发现：0 条。
- 未进表的提示：
  - 契约区 drift 核对：AC-001 措辞变更即 f006（minor，处置=改 spec）的落实，已入处置表（t003_code_f006 已修），属 review 驱动的 spec 对齐而非未经确认的 AC 变更；新措辞把承诺收敛到实现实际保证的语义（单元格文本/转义管道/对齐语义保留），不扩大也不削弱契约，不计 blocking。
  - 文件过大（降级规则，不进表）：`src/mdformat/renderer/_context.py` 783 行、`src/mdformat/_cli.py` 500 行，与 Round 3 同况，本轮 src 无净增。
  - 范围核对：diff 相对上轮仅 spec.md（AC-001 措辞）与 `tests/test_table.py`（t003_test_f003 断言改为完整分隔行匹配 `"| :--- | :---: | ---: |" in out`，`tests/test_table.py:81`，区分左/中/右对齐）变化，无本 task 范围外改动。
- AC 复验方式：
  - AC-001：re_verified——默认态对齐冒号表、无冒号表、`\|` 单元格均 round-trip 相等；dash/填充/反斜杠归一无渲染语义变化，与修订后措辞一致。
  - AC-002：re_verified——pad 对齐正确（`tests/test_table.py` 9 passed）。
  - AC-003：re_verified——compact 紧凑不 pad。
  - AC-004：re_verified——三态幂等 + 对齐冒号完整分隔行断言；`tests/test_table.py` 9 passed。
  - AC-005：re_verified——全量测试 4684 passed / 5 skipped，默认态无回归（与 Round 3 完全一致，佐证 src 未变）。
  - coverage = re_verified / 总 AC 数 = 5/5
- 总体判断：f006（spec 措辞）经修订消除，spec 措辞与实现一致；本轮无新 finding、无未解决 blocker → PASS。
- 系统性 follow-up：无。

verdict: PASS
