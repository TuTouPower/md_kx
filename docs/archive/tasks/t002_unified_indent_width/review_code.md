# Task review t002（reviewer_focus: 代码）

- task：`t002_unified_indent_width`
- spec：`docs/tasks/t002_unified_indent_width/spec.md`
- diff_anchor：`cccbc5227e26a999244b79ed13565024260c8fe8`
- target：`git diff cccbc5227e26a999244b79ed13565024260c8fe8`
- round：1
- reviewed_at：2026-08-11 23:35 UTC+8

## Findings

### t002_code_f001 - indent_width 无下界校验/clamp，宽度小于 marker 显示宽度时输出破坏 CommonMark 结构（API 路径静默）

- 严重度：important
- 锚点：AC-002「设置缩进宽度为 N 后，文档内所有嵌套列表缩进统一为 N 空格」+ spec「风险与回退」明确点名的「强制统一缩进破坏 CommonMark『marker 对齐内容』语义」；可观测行为缺陷
- 位置：`src/mdformat/renderer/_context.py:496-499`（`bullet_list`）、`:541-548`（`ordered_list`）；`src/mdformat/_cli.py:244-249`（`--indent-width` 无范围校验，`type=int` 任意值放行）
- 问题：`configured_width` 为正时无条件 `indent = " " * configured_width`，未与 marker 显示宽度对齐。marker 宽度：bullet `- ` = 2；ordered `N. ` = `len(str(N)) + 2`；consecutive numbering 补零后更宽。当 `configured_width` 小于 marker 宽度，嵌套块（嵌套列表、列表内代码块）落在 CommonMark 内容列（marker 后）以内，解析为段落续行而非嵌套结构。实测（`is_md_equal` 即 CLI validate 同口径）：
  - `mdformat.text("- a\n  - b\n", options={"indent_width": 1})` → `- a\n - b\n`，HTML 不等。
  - `mdformat.text("1. a\n   1. nested\n", options={"indent_width": 2})` → `1. a\n  1. nested\n`，HTML 不等。
  - `mdformat.text("10. a\n    1. nested\n", options={"indent_width": 3})` → `10. a\n   1. nested\n`，HTML 不等（start=10 的 ordered marker 4 字符，width=3 很常见即可触发）。
  - CLI 靠 `opts["validate"]` 的 `is_md_equal` 兜底报「Could not format」、文件不落盘；但 `mdformat.text()` / `mdformat.file()`（`_api.py:84-115`，无 HTML 校验）静默产出与输入语义不同的文档，库用户无警告。
  - 低宽度非恶意输入：`--indent-width 2` 配任意 ordered 列表即触发；spec 未限定 N 下界，help 只写「INTEGER」。
- 建议：在 CLI 与 `_conf.py` 增加下界校验并拒绝（报 `argparse.error` / `InvalidConfError`，如 `indent_width` 须 ≥ 2，ordered 场景按最大 marker 宽度动态判定）；或 renderer 保底 `max(configured_width, marker_width)`——注意后者使输出宽度 ≠ 配置 N，与 AC-002「统一为 N 空格」措辞冲突，需同步 spec 明确定义。推荐前者（校验拒绝）并补一句 spec 说明。

### t002_code_f002 - `_validate_values` 缺 indent_width 校验分支，非法 toml 值触发未捕获 TypeError 崩溃、负值放行

- 严重度：important
- 锚点：可观测行为缺陷（崩溃）；与 `_conf.py` 其余 conf key 校验模式不一致
- 位置：`src/mdformat/_conf.py:57-97`（`_validate_values` 无 `indent_width` 分支）
- 问题：`indent_width` 加入 `DEFAULT_OPTS` 使 `_validate_keys` 放行（方向正确），但 `_validate_values` 未加校验分支。`.mdformat.toml` 写 `indent_width = "abc"` → renderer `" " * "abc"` 抛未捕获 `TypeError: can't multiply sequence by non-int of type 'str'`，`run()` 直接 traceback 崩溃（实测），而非像 wrap/number/validate/end_of_line/plugin/extensions/codeformatters 那样抛干净的 `InvalidConfError`。`indent_width = -2` 亦放行（`" " * -2` 为空串），CLI 靠 validate 报错、API 静默破坏性输出。`--indent-width` 的 `type=int` 只拦非 int，不拦负值与过小值。
- 建议：`_validate_values` 补分支：`if "indent_width" in opts: if not isinstance(opts["indent_width"], int) or opts["indent_width"] <= 0: raise InvalidConfError(...)`（下界按 f001 定）。
- 备注：test reviewer 已独立观测到该崩溃（review_test.md t002_test_f002，从「配置文件零测试覆盖」角度），此处从代码缺陷（校验分支缺失）角度标注；两条 finding 同根，修复一处可同时消除。

## 结论

- 前轮 finding 复核（Round 1）：无
- 本轮新发现：2 条
- 未进表的提示：
  - 文件过大（仅结论列出，命中「已达阈值且本 task 净增」）：`src/mdformat/renderer/_context.py` 666 行（≥400 minor 阈值，task 净增 ~15 行）；`src/mdformat/_cli.py` 495 行（≥400，净增 6 行）。均非生成物，diff 未给「协议一体/工具强制」硬约束说明。未因过大直接观测到行为缺陷，故不入 finding 表。
  - 复杂度：`bullet_list`/`ordered_list` 各新增 1 个 `if` 分支（CC 基数 +1），远低于 10/15 阈值，不进表。
  - 范围外观察（不阻断）：
    - spec AC-004 措辞写配置文件为 `mdformat.toml` / pyproject `[tool.mdformat]`，但本仓库既有机制只读 `.mdformat.toml`（`_conf.py:read_toml_opts`）。实现合理、属 spec 过时（预存机制），建议处置为改 spec，不计 FAIL。与 test reviewer 结论一致。
    - wrap 交互：`paragraph`（`_context.py:397`）`wrap_mode -= env["indent_width"]`，大宽度 + 深层嵌套 + 整数 wrap 时 wrap 宽度被压到 1（每词一行）。仅同时设 wrap 整数与过大 indent_width 触发，非 AC 域，观察提示。
    - DRY：`configured_width` 查找在 `bullet_list`/`ordered_list` 两处 verbatim 重复（各 3 行），沿用项目既有 `options.get("mdformat", {}).get(...)` 风格，2 处且无行为分叉，miner 不进表。
    - AC-003 测试弱化为子串断言：已由 test reviewer t002_test_f001 覆盖，本报告不重复；实现层已实测围栏内容相对 fence 逐字节保持，代码无缺陷。
- 总体判断：AC 主体实现正确（默认无回归、宽度统一、代码块内容保持、CLI 与配置路径均可达），但存在 2 条未解决 important：配置宽度无下界处理致输出破坏 CommonMark 结构（API 静默）、配置值无类型/范围校验致崩溃。修完须走下一轮审阅。
- 系统性 follow-up：无

### AC 复验披露

- AC-001：`re_verified`。默认路径 else 分支保留原 `" " * len(marker_type + first_line_indent)` 计算（`_context.py:498-499`），结构未变；跑全量 `tests/test_commonmark_spec.py` 4176 通过、核心 86 通过；实测 `mdformat.text("- a\n  - b\n    - c\n  - d\n")` 逐字节不变。
- AC-002：`re_verified`。实测 width=4 下 bullet/ordered/三层嵌套输出统一 4 空格且 HTML 等价（`- a\n    - b\n        - c\n    - d\n` 等）。边界：width < marker 宽度破坏结构（f001）。
- AC-003：`re_verified`。实测列表内代码块 width=4 输出 `- a\n    ```\n    code line\n    ```\n`，围栏内容相对 fence 逐字节保持（`_context.py:194` fence 渲染不触碰 code_block，缩进前缀统一加在每行）；顶层代码块不动。测试断言弱化由 test reviewer f001 承担。
- AC-004：`re_verified`。CLI：实测 `--indent-width=4` 落盘统一（新测试 `test_indent_width_cli` + 手动 run 均通过）；配置文件：实测 `.mdformat.toml` 写 `indent_width = 4` → `run()` 输出统一 4 空格。spec 措辞与项目实际配置文件名不一致属 spec 过时（见上）。

`coverage = 4 / 4`（全部 AC 均可在本环境独立复验，无 trust_prior 项）。

reviewed_scope: 2c95e986bbe708a0

verdict: FAIL

## Round 2 (2026-08-11 23:33 UTC+8)

reviewed_scope: dbc40d959a7c5ac8

### 前轮 finding 复核（以 git diff 为准）

- **t002_code_f001（important，下界无校验致结构破坏）— 功能缺陷已消除，残余 spec 措辞未同步（minor）**。修复采用保底方案：`bullet_list` `src/mdformat/renderer/_context.py:496-501`、`ordered_list` `:543-549` 以 `max(configured_width, default_width)` 替代无条件 `" " * configured_width`，default_width 与默认 marker 宽度计算逐字符一致（consecutive 用 `list_len+starting_number-1` 补零宽度，非 consecutive 用 `starting_number`）。实测原三个复现用例全部 HTML 等价、结构保留：`indent_width=1` bullet → `- a\n  - b\n`；`indent_width=2` ordered → 3 空格；start=10、`indent_width=3` → 4 空格。边界：width=marker 精确、3 位 marker（`123. a`）width=4、consecutive numbering width=1、width=0（当未设置处理）均正确。API 路径不再静默产出结构破坏文档。**残余**：Round 1 明确注明选保底方案「需同步 spec 明确定义」，`spec.md` 仅改了 AC-004 配置文件名与 spike 状态，AC-002「统一为 N 空格」未补充 N<marker 时取 marker 宽度兜底的语义说明。属「实现合理但 spec 描述过时」→ 处置为改 spec，不计 FAIL。功能 blocker 已消除。
- **t002_code_f002（important，_validate_values 缺 indent_width 校验致崩溃）— 已修，无残余**。`src/mdformat/_conf.py:98-101` 新增分支：`isinstance(indent_value, int) and not isinstance(indent_value, bool) and indent_value >= 0`，非法值抛 `InvalidConfError`。实测 `'abc'`/`-2`/`3.5`/`True` 均抛干净错误（不再 `TypeError: can't multiply sequence` 崩溃），`4`/`0` 放行；0 与 `DEFAULT_OPTS["indent_width"]=0` 的「未设置」语义一致，renderer 走默认分支。bool 拒绝（`bool` 为 `int` 子类）是防御加分。修复完整。

### 本轮新发现

### t002_code_f003 - _conf.py 新增校验行超项目 flake8 上限（108 > 88）

- 严重度：minor
- 锚点：代码质量（lint 门禁）；无 AC 违反、无可观测运行时缺陷，不满足 blocking 硬阈值
- 位置：`src/mdformat/_conf.py:100`
- 问题：Round 2 新增行 `if not (isinstance(indent_value, int) and not isinstance(indent_value, bool) and indent_value >= 0):` 108 字符，超项目 `.flake8` `max-line-length = 88`，且无 `# noqa: E501`（`_conf.py` 现无任何 E501 noqa；`_cli.py` 既有超行均带 noqa）。`.pre-commit-config.yaml` 强制 flake8。实测 `flake8 src/mdformat/_conf.py` → `100:89: E501 line too long (108 > 88 characters)`。会破坏项目 lint 门禁。
- 建议：拆行或加 `# noqa: E501`，保持与仓库既有风格一致。

## 结论

- 前轮 finding 复核（Round 2）：f001 功能缺陷已消除（保底生效，HTML 等价），残余为 AC-002 兜底语义未同步 spec（minor，改 spec）；f002 已修（校验分支生效，崩溃消除）。两条 important blocker 均不再构成未解决 blocking。
- 本轮新发现：1 条（t002_code_f003，minor）。
- 未进表的提示：
  - 文件过大：与 Round 1 相同（`_context.py` 666 行净增 ~15、`_cli.py` 495 行净增 6），本轮无净增，不重复。
  - 复杂度：`_validate_values` 增 1 分支（已有 `# noqa: C901` 抑制），renderer 各增 1 if，远低于阈值。
  - CLI/toml 校验口径不一致（观察）：`--indent-width -2` 经 renderer `max()` 静默兜底为 marker 宽度（安全不崩），toml 负值报 `InvalidConfError`。无可观测缺陷，不阻断；如需一致可在 CLI `type=int` 基础上加范围校验。
  - DRY：`configured_width` 读取在 `bullet_list`/`ordered_list` 两处 verbatim 重复（沿用项目风格，2 处无行为分叉），Round 1 已提示，不改。
  - 范围外观察（供 test reviewer 核对）：implementer `task.md` 处置表称 t002_test_f001「AC-003 改逐字节断言」已修，但 `tests/test_indent.py:30` 仍为 `assert code_content in output` 子串断言，非逐字节。该 finding 属 test reviewer 范畴，本报告不重复裁定。
  - spec AC-004 措辞已按 Round 1 方向同步为 `.mdformat.toml`（预存机制），处置合规。
- 总体判断：两条 Round 1 important 功能缺陷均已消除（保底 + 校验，实测验证），本轮仅 1 条 minor（超行 lint），无未解决 critical / important，可 PASS。
- 系统性 follow-up：无

### AC 复验披露（Round 2 增补）

- AC-001：`re_verified`。全量 `tests/test_commonmark_spec.py` 4176 通过；`tests/test_indent.py::test_default_no_regression` 通过；`mdformat.text('- a\n  - b\n')` 逐字节不变。
- AC-002：`re_verified`。f001 三复现用例 + 边界（width=marker、3 位 marker、consecutive width=1、width=0）全部结构保留、N≥marker 时精确 N 空格；`test_indent_width_unified`/`test_indent_width_ordered_list` 通过。N<marker 兜底语义未入 spec（见 f001 残余）。
- AC-003：`re_verified`。`test_code_block_untouched_byte_for_byte` 通过；实现层 fence 渲染不触碰 code_block（Round 1 已实测逐字节保持）。该测试断言仍为子串，强度由 test reviewer 复核。
- AC-004：`re_verified`。`test_indent_width_cli`、`test_indent_width_config_file` 通过（Round 2 复跑 6 passed）。

`coverage = 4 / 4`。

verdict: PASS

## Round 3 (2026-08-11 23:42 UTC+8)

reviewed_scope: 400d486b8620a876

### 前轮 finding 复核（以 git diff 为准）

- **t002_code_f001（important）— 已消除，残余 spec 同步亦完成**。功能缺陷自 Round 2 起经 `max(configured_width, default_width)` 保底消除，本轮实测原三个复现用例（`indent_width=1` bullet、`=2` ordered、start=10 `=3`）输出 `- a\n  - b\n` / `1. a\n   1. nested\n` / `10. a\n    1. nested\n` 全部 `is_md_equal` True、结构保留；`indent_width=0`（未设置语义）与 consecutive numbering 兜底亦正确。Round 2 遗留的「AC-002 兜底语义未同步 spec（minor，改 spec）」本轮已落实：`docs/tasks/t002_unified_indent_width/spec.md` AC-002 追加「N 小于列表 marker 显示宽度时取 marker 宽度兜底（保证 CommonMark 嵌套结构不被破坏）」，与实现逐字一致。f001 无残余。
- **t002_code_f002（important）— 已修，仍完好**。`src/mdformat/_conf.py:98-105` `indent_width` 校验分支（非 bool 的 int 且 ≥0，否则 `InvalidConfError`）仍在；`tests/test_config_file.py` 新增 `indent_width = 'abc'` / `indent_width = -1` 两条无效值用例均 PASS（`test_invalid_conf_value[indent_width-...]`）。崩溃消除无回退。
- **t002_code_f003（minor E501）— 已修**。`src/mdformat/_conf.py:100-103` 校验条件拆为多行，`awk` 复查全文件无 >88 字符行；`uv run --with flake8 flake8 src/mdformat/_conf.py src/mdformat/renderer/_context.py src/mdformat/_cli.py` 零违规；`uv run --with black black --check` 三文件 unchanged。`_cli.py` 仅存的超长行（:168/:303）为锚点前既有且带 `# noqa: E501`，非本 task 引入。

### 本轮新发现

无。Round 2 两处 minor 修复（E501 拆行、AC-002 兜底语义同步）均为纯格式与措辞调整，未引入逻辑变更；复验未见新问题。

## 结论

- 前轮 finding 复核（Round 3）：f001（功能 + 残余 spec 同步）已消除、f002 已修仍完好、f003 已修（flake8/black 双验通过）。无未解决 critical / important。
- 本轮新发现：0 条。
- 未进表的提示：
  - 契约区 drift（AC-002 追加兜底语义、AC-004 配置文件名改为 `.mdformat.toml`）：两处均为前轮已批准方向的 spec 校正（Round 1 判 AC-004 spec 过时建议改 spec、Round 1 f001 明确注明保底方案需同步 spec 定义），非未经确认的需求变更，不构成 blocking。当前契约区与注入契约区逐字一致。
  - 文件过大：`_context.py` 666 行 / `_cli.py` 495 行与 Round 1 相同，本轮无净增；`_conf.py` 因拆行净增 ~3 行，均远低于重要阈值，不重复。
  - 复杂度：`_validate_values` 增 1 分支（已有 `# noqa: C901`），renderer 各增 1 if，远低于阈值。
  - 范围外观察（不阻断）：CLI `--indent-width -2` 经 `max()` 静默兜底为 marker 宽度（与 AC-002 兜底语义一致、结构不破坏），toml 负值抛 `InvalidConfError`，两条路径口径不一致但均安全，Round 2 已提示，不改。
- 总体判断：前两轮全部 finding（f001/f002/f003）均已真实修复且经独立复验，Round 2 minor 修复未引入新问题，无未解决 critical / important，PASS。
- 系统性 follow-up：无

### AC 复验披露（Round 3 增补）

- AC-001：`re_verified`。全量 `tests/test_commonmark_spec.py` 4176 passed；`test_default_no_regression`（`mdformat.text("- a\n  - b\n    - c\n  - d\n")` 逐字节不变）PASS。
- AC-002：`re_verified`。f001 三复现用例 + `indent_width=0` + consecutive numbering 兜底全部 `is_md_equal` True；`test_indent_width_unified` / `test_indent_width_ordered_list` PASS；spec 兜底语义与 `max()` 实现逐字一致。
- AC-003：`re_verified`。`test_code_block_untouched_byte_for_byte` 以精确等值断言 PASS；实现层 fence 渲染不触碰 code_block（Round 1 已实测逐字节保持）。
- AC-004：`re_verified`。`test_indent_width_cli`（`--indent-width=4` 落盘）、`test_indent_width_config_file`（`.mdformat.toml` 写入）PASS；`_validate_values` 无效值用例 PASS。

`coverage = 4 / 4`（无 trust_prior 项）。

verdict: PASS

## Round 4 (2026-08-11 23:53 UTC+8)

reviewed_scope: fbe60fac5ee05f65

### 范围核对

Round 3（指纹 400d486b8620a876）后 diff 唯一增量：`tests/test_indent.py` 新增 `test_indent_width_below_marker_falls_back`（`:64-68`，AC-002 兜底用例，N=1 < marker 宽度 2）。`src/` 三文件（`_cli.py` / `_conf.py` / `renderer/_context.py`）、`tests/test_config_file.py`、`spec.md` 相对 Round 3 描述逐字节未变（当前 diff 与 Round 3 记录的 f001/f002/f003 修复形态一致）。当前指纹 fbe60fac5ee05f65 与注入 prompt 一致。

### 前轮 finding 复核（以 git diff 与实测为准）

- **t002_code_f001（important，下界无校验致结构破坏）— 仍消除**。`_context.py:496-501`（bullet_list）、`:543-549`（ordered_list）`max(configured_width, default_width)` 保底仍在，src 未变。实测本轮复现：`indent_width=1` bullet → `- a\n  - b\n    - c\n  - d\n`（兜底 2 空格，结构保留）；`indent_width=1` ordered → `1. a\n\n   1. b\n\n      1. c\n`；`indent_width=4` 统一 4 空格。spec AC-002 兜底子句已与实现逐字一致。
- **t002_code_f002（important，_validate_values 缺校验致崩溃）— 仍消除**。`_conf.py:98-105` 校验分支（非 bool 的 int 且 ≥0，否则 `InvalidConfError`）仍在，src 未变；`test_config_file.py` 非法值用例照旧 PASS。
- **t002_code_f003（minor E501）— 仍消除**。`_conf.py` 校验条件已拆多行，src 未变；无新增超行。

### 本轮新发现

无。新增测试仅覆盖既有 fallback 行为（断言 `output == NESTED_MD`，非空设：移除 `max()` 则 1 空格/层使断言失败），不触 src，未引入逻辑变更。

## 结论

- 前轮 finding 复核（Round 4）：f001 / f002 / f003 均按 diff 与实测核实仍消除（src 自 Round 3 起未变）。
- 本轮新发现：0 条。
- 未进表的提示：
  - 范围：本轮唯一 diff 为测试层新增（test reviewer 职责）；代码角度无 src 改动。
  - 文件过大 / 复杂度：src 未变，与 Round 3 相同，不重复。
- 总体判断：src 零改动、零回归，新增测试与既有 fallback 行为一致，无未解决 critical / important，PASS。
- 系统性 follow-up：无

### AC 复验披露（Round 4 增补）

- AC-001：`re_verified`。全量 `tests/test_commonmark_spec.py` 含 `- a\n  - b\n` 逐字节不变；本轮全量 4675 passed / 5 skipped（skip 为既有 Python 3.13+ exclude 用例），较 Round 3 净增 1 条新测试。
- AC-002：`re_verified`。本轮实测 `indent_width=1` bullet/ordered 均兜底 marker 宽度、结构保留（is_md_equal 等价）；`indent_width=4` 统一 4 空格；新 `test_indent_width_below_marker_falls_back` 精确断言 `output == NESTED_MD` 通过。
- AC-003：`re_verified`。本轮实测 `indent_width=4` 下 `# T\n\n```\ncode line\n  indented line\n```\n` 逐字节不变；`test_code_block_untouched_byte_for_byte` 精确等值断言 PASS。
- AC-004：`re_verified`。`test_indent_width_cli`（`--indent-width=4` 落盘）、`test_indent_width_config_file`（`.mdformat.toml` 写入）PASS；`_validate_values` 非法值用例 PASS。

`coverage = 4 / 4`（无 trust_prior 项）。

verdict: PASS
