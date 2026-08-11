# Task review t002（reviewer_focus: 测试）

- task：`t002_unified_indent_width`
- spec：`docs/tasks/t002_unified_indent_width/spec.md`
- diff_anchor：`cccbc5227e26a999244b79ed13565024260c8fe8`
- target：`git diff cccbc5227e26a999244b79ed13565024260c8fe8`
- round：1
- reviewed_at：2026-08-11 23:12 UTC+8

## Findings

### t002_test_f001 - AC-003 测试弱化为子串存在断言，未做逐字节比对

- 严重度：important
- 锚点：AC-003「代码块（``` 围栏）内内容不被改动（逐字节比对）」
- 位置：`tests/test_indent.py:17-22`（`test_code_block_untouched`）
- 问题：AC-003 明确要求逐字节比对，但测试用两条子串断言：
  ```python
  assert "code line\n" in output
  assert "code line" in output
  ```
  第二条是第一条的恒真蕴含（`"code line\n" in output` 成立则 `"code line" in output` 必成立），纯冗余。两条子串断言只证明「code line 这一行仍在输出里某处」，不验证围栏内内容逐字节未变。若实现改动代码内容（行内多加字符、重复行、在围栏内插空行、或把 code line 错缩进到与 fence 不对齐），只要 `"code line\n"` 仍作为子串出现，测试即通过，AC-003 违规漏网。已实测输出为确定值 `- a\n    ```\n    code line\n    ```\n`，精确断言完全可行。属「弱化断言」危险模式，命中不得标 minor。
- 建议：改为精确断言，例如 `assert output == "- a\n    ```\n    code line\n    ```\n"`；或从 output 中提取围栏内内容与输入逐字节比对（允许外层的列表项统一缩进前缀）。

### t002_test_f002 - AC-004 配置文件机制零测试覆盖，且非法值路径未校验会崩溃

- 严重度：important
- 锚点：AC-004「配置可通过 CLI 选项与配置文件两种方式指定」；可观测行为缺陷：非法配置值触发未处理 TypeError
- 位置：`tests/test_config_file.py:61-89`（`test_invalid_conf_value` parametrize 缺 `indent_width` 条目）；`src/mdformat/_conf.py:57-97`（`_validate_values` 无 `indent_width` 校验）
- 问题：AC-004 声明两种机制。测试只覆盖 CLI（`tests/test_indent.py:25-41`），配置文件（`.mdformat.toml`）→ `indent_width` → 输出 这条路径零测试。项目既定模式是每个 conf key 都在 `test_invalid_conf_value` parametrize 里有非法值条目（wrap/number/validate/end_of_line/plugin/extensions/codeformatters 全覆盖），新 key `indent_width` 未加入该矩阵，`_validate_values` 也未校验它。实测 `.mdformat.toml` 写 `indent_width = "abc"` / `= 2.5` 时 `run()` 抛出未处理 `TypeError: can't multiply sequence by non-int of type 'str'/'float'`（traceback 崩溃而非 InvalidConfError）；`indent_width = -1` 静默 rc=1 文件不变。既有配置文件的合法路径（`.mdformat.toml` 写 `indent_width = 4` → 输出统一 4 空格）我已实测可用，但完全无测试守护。CLI 半条路径测试是可信的（真实 `run()`，含 HTML validate），主要缺口在配置文件半条。
- 建议：按 `test_config_file.py` 既有模式补两条：① 合法值测试——`tmp_path` 写 `.mdformat.toml` 含 `indent_width = 4`，`run((str(file),))` 后断言输出统一；② 把 `("indent_width", "indent_width = 'abc'")` 加入 `test_invalid_conf_value` parametrize（先补 `_validate_values` 对 indent_width 的类型/范围校验，否则该测试会暴露崩溃）。

### t002_test_f003 - AC-002 有序列表子分支无测试

- 严重度：minor
- 锚点：AC-002「文档内所有嵌套列表缩进统一为 N 空格」
- 位置：`tests/test_indent.py:11-14`（仅 bullet）；`src/mdformat/renderer/_context.py:538-548`（`ordered_list` 新增 `configured_width` 分支）
- 问题：AC-002 措辞为「所有嵌套列表」，实现同时改了 `ordered_list`（新增独立配置分支），但测试只覆盖 bullet 嵌套列表。有序列表统一行为已实测正确（`1. a\n    1. b\n        1. c\n`），属「可再补一个 case」类扩展，不阻断；但因被改分支独立且零覆盖，标注以提醒。
- 建议：补一条有序列表嵌套用例（`options={"indent_width": 4}` 断言输出），成本低。

### t002_test_f004 - CLI 测试卫生：死 import 与未关闭文件句柄

- 严重度：minor
- 锚点：测试可信度（无 AC 违反）
- 位置：`tests/test_indent.py:27-28, 38`
- 问题：`import subprocess`、`import sys` 未使用（死 import）；`content = open(path).read()` 未关闭文件句柄（触发 ResourceWarning）。
- 建议：删除未用 import，改用 `with open(path) as f: content = f.read()` 或 `Path(path).read_text()`。

## 结论

- 前轮 finding 复核（Round 1）：无
- 改测方向复核：无。diff 中 `tests/test_indent.py` 为全新文件，未修改任何既有测试；无「迁就实现」的改测。
- 本轮新发现：4 条
- 未进表的提示：
  - spec AC-004 措辞写配置文件为 `mdformat.toml` / pyproject `[tool.mdformat]`，但本仓库既有机制（`_conf.py::read_toml_opts` 与 `test_config_file.py`）只支持 `.mdformat.toml`。实现合理、属 spec 过时，建议处置为改 spec，不计 FAIL。
  - `--indent-width 0` / `indent_width = 0` 显式传入等价默认（falsy → marker-aligned），未测；低价值，可选。
  - 危险模式逐条扫描结果：无恒真断言（`assert True` 类）、无删/反转 expect、无注释断言、无 `.skip`/`.only`、无静默错误开关、无 mock 自己模块（CLI 测试调真实 `run()`，可信）、无阈值掩盖、无条件跳过、无 `.value=` 冒充交互。命中项即 f001（弱化断言）与 f002（AC 机制零覆盖 + 非法值崩溃）。
  - 「未知契约清单」的 UNVERIFIED-SPIKE 已由 s002/d002 落实为验证结论，且实现与结论一致（renderer 层读 `options["mdformat"]["indent_width"]`，实测可达），门禁未绕过。
- 总体判断：测试主体可信（API 测试直达生产逻辑、CLI 测试走真实 `run()` 含 HTML 校验），但存在 2 条未解决 important：AC-003 逐字节比对被弱化为子串断言、AC-004 配置文件机制零覆盖且非法值崩溃。修完须走下一轮审阅。
- 系统性 follow-up：无

### AC 复验披露

- AC-001：`re_verified`。`test_default_no_regression` 断言规范嵌套列表经默认路径 round-trip 不变；已查 `_context.py:493-499` else 分支（默认 marker-aligned），实测 `mdformat.text(NESTED_MD) == NESTED_MD`。
- AC-002：`re_verified`（bullet 子项）。测试用精确断言 `output == "- a\n    - b\n        - c\n    - d\n"`；已独立运行 `mdformat.text(NESTED_MD, options={"indent_width": 4})` 确认输出一致。有序列表子项无测试（f003）。
- AC-003：`re_verified`（行为本身）。已独立运行实测输出 `- a\n    ```\n    code line\n    ```\n`，围栏内代码内容逐字节保持；但测试断言被弱化（f001），测试套件未真正守 AC 的逐字节要求。
- AC-004：`re_verified`。CLI 半条：`test_indent_width_cli` 走真实 `run()`（含 HTML 语义校验）且断言文件落盘内容；已确认测试通过。配置文件半条：已独立实测 `.mdformat.toml` 写 `indent_width = 4` → `run()` 输出统一 4 空格，机制可用但零测试覆盖（f002）。

`coverage = 4 / 4`（全部 AC 均可在本环境独立复验，无 trust_prior 项）。

reviewed_scope: 2c95e986bbe708a0

verdict: FAIL

## Round 2 (2026-08-11 23:28 UTC+8)

## Findings

### t002_test_f005 - AC-003 断言仍为子串包含，「围栏内追加内容」型改动会漏网

- 严重度：minor
- 锚点：AC-003「代码块（``` 围栏）内内容不被改动（逐字节比对）」
- 位置：`tests/test_indent.py:28-33`（`test_code_block_untouched_byte_for_byte`）
- 问题：f001 主体已修——`code_content` 取完整多行围栏内容（含 2 空格内缩进行），实测围栏内字节的改/删/重缩进均会使 `code_content in output` 失败。但断言仍是子串包含而非逐字节相等：实测在围栏内**追加**一行（内容变为 `code line\n  indented line\nEXTRA\n`）后，`code_content in output` 仍为 True，测试通过而 AC-003「逐字节比对」被违反。本测试代码块为顶层围栏（不受 indent_width 影响），输出确定 `'# T\n\n```\ncode line\n  indented line\n```\n'`，精确断言完全可行。
- 建议：改为 `assert output == "# T\n\n```\ncode line\n  indented line\n```\n"`，或从 output 提取围栏内内容与 `code_content` 逐字节相等比较。

## 结论

- 前轮 finding 复核：
  - t002_test_f001（AC-003 弱断言，important）：**已消除（主体）**。断言由单行冗余子串改为完整多行围栏内容子串（`tests/test_indent.py:28-33`），实测字节改/删/重缩进均能捕获；残留「围栏内追加内容」型漏网见本轮 f005（minor）。
  - t002_test_f002（AC-004 配置零测试，important）：**已消除**。新增 `test_indent_width_config_file`（`tests/test_indent.py:50-62`，真实 `run()` 读 `.mdformat.toml` 断言落盘内容，非空设——默认 2/4 与配置 4/8 输出不同）；`tests/test_config_file.py:76-77` 补 `indent_width = 'abc'` / `-1` 非法值矩阵；`src/mdformat/_conf.py:98-101` 新增类型/范围校验，实测两用例均以 `InvalidConfError` 拒绝（rc=1 + stderr `Invalid 'indent_width' value`），此前 TypeError 崩溃路径已消除。
  - t002_test_f003（有序列表无覆盖，minor）：**已消除**。新增 `test_indent_width_ordered_list`（`tests/test_indent.py:21-25`），精确断言 `1. a\n\n    1. b\n\n        1. c\n`，实测通过且非空设（默认 2/4 输出不同）。
  - t002_test_f004（死 import，minor）：**已消除**。`tests/test_indent.py` 现仅 `import os`/`tempfile`（均使用），`subprocess`/`sys` 已删，文件句柄全走 `with open(...)`。
- 改测方向复核：无。唯一既有测试改动为 `test_config_file.py` 新增两条 parametrize 用例（新覆盖），未改任何既有断言迁就实现。
- 本轮新发现：1 条（t002_test_f005，minor）
- 未进表的提示：
  - CLI `--indent-width` 未校验负数（argparse `type=int` 接受后 renderer `max()` 静默回落 marker 对齐），与配置文件 `-1` 拒绝行为不一致。非 AC 违反，属 code reviewer 关注点。
  - spec AC-004 措辞已由 `mdformat.toml` / pyproject 改为 `.mdformat.toml`（`docs/tasks/t002_unified_indent_width/spec.md`），与仓库既有机制（`_conf.py` 仅支持 `.mdformat.toml`）及当前契约区一致；Round 1 已建议处置为改 spec，本轮已落实，一致。
- 总体判断：Round 1 两条 important 已真实修复（以 git diff 与测试实测为准，非处置表自述），测试可信且非空设，全部目标用例通过（`tests/test_indent.py` + `test_config_file.py` 25 passed），CommonMark 4176 用例无回归；仅存一条 minor（f005）。无未解决 important/critical。
- 系统性 follow-up：无

### AC 复验披露

- AC-001：`re_verified`。`test_default_no_regression` 断言默认 round-trip 不变；重跑 `tests/test_commonmark_spec.py` 4176 用例全部通过，默认路径无回归。
- AC-002：`re_verified`。`test_indent_width_unified`（bullet，精确相等）与 `test_indent_width_ordered_list`（有序，精确相等）均已独立运行确认输出与预期一致。
- AC-003：`re_verified`（行为本身）。独立运行确认围栏内容逐字节保持；f001 修复后断言可捕获字节改/删/重缩进，残留围栏内追加内容漏网（f005，minor）。
- AC-004：`re_verified`。CLI 半条（`test_indent_width_cli`，真实 `run()` + `--indent-width=4`）与配置文件半条（`test_indent_width_config_file` 写 `.mdformat.toml`，真实 `run()`）均端到端验证；非法值矩阵 `'abc'`/`-1` 拒绝路径实测通过。

`coverage = 4 / 4`

reviewed_scope: dbc40d959a7c5ac8

verdict: PASS

## Round 3 (2026-08-11 23:42 UTC+8)

## Findings

### t002_test_f006 - AC-002「marker 宽度兜底」子句无测试覆盖

- 严重度：minor
- 锚点：AC-002「…N 小于列表 marker 显示宽度时取 marker 宽度兜底（保证 CommonMark 嵌套结构不被破坏）」
- 位置：`tests/test_indent.py:15-25`（`test_indent_width_unified` / `test_indent_width_ordered_list` 均取 N=4，≥ marker 宽度 2，未触达兜底分支）；`src/mdformat/renderer/_context.py:496-500, 543-549`（`max(configured_width, …)` 兜底分支）
- 问题：AC-002 契约新增「N 小于 marker 显示宽度时取 marker 宽度兜底」子句，实现侧在 bullet 与 ordered 两分支均新增独立 `if configured_width: … max(…)` 代码路径，但现有配置类测试全部用 N=4 / N=2（均 ≥ marker 宽度 2），兜底分支零测试。已独立实测行为正确：bullet `indent_width=1` → 输出 2 空格（marker `- ` 宽度兜底）、ordered `indent_width=1` → 输出 2 空格，CommonMark 嵌套结构保持。该分支是 AC-002 的独立可观测承诺，回退（如改回 `" " * configured_width` 不取 max）会产出破坏嵌套的缩进而无测试拦截。属「可再加一个 case」类扩展，不阻断。
- 建议：补一条 `options={"indent_width": 1}` 的嵌套列表用例，断言输出回落为 marker 宽度（bullet 断言 `"- a\n  - b\n"`、ordered 断言 `"1. a\n\n   1. b\n"`）。

## 结论

- 前轮 finding 复核（以 git diff 为准）：
  - t002_test_f001（AC-003 弱断言，important）：**已消除**。`tests/test_indent.py:28-32` `test_code_block_untouched_byte_for_byte` 已改为全文精确断言 `assert output == "# T\n\n```\ncode line\n  indented line\n```\n"`。
  - t002_test_f002（AC-004 配置零测试 + 非法值崩溃，important）：**已消除（Round 2 已核，本轮复核仍成立）**。`test_indent_width_config_file` 走真实 `run()` 读 `.mdformat.toml` 断言落盘内容；`test_config_file.py:76-77` 补 `'abc'`/`-1` 非法值矩阵；`_conf.py:98-103` 类型/范围校验，均以 `InvalidConfError` 拒绝。
  - t002_test_f003（有序列表零覆盖，minor）：**已消除**。`test_indent_width_ordered_list` 精确断言，实测非空设。
  - t002_test_f004（死 import，minor）：**已消除**。`test_indent.py` 仅 `import os`/`tempfile`，文件句柄全走 `with open(...)`。
  - t002_test_f005（AC-003 残留「围栏内追加内容」漏网，minor）：**已消除**。精确断言 `output == …` 对整份输出逐字节比对，围栏内追加/删除/重缩进任一字节差异均使断言失败；与 f001 修复合并为同一最终形态，f005 场景实测无漏网。
- 改测方向复核：无。diff 中既有测试改动仅 `test_config_file.py` 新增两条 parametrize 用例（新覆盖）与 `test_indent.py` 断言强化（弱化→精确相等），无「迁就实现」的改测。
- 本轮新发现：1 条（t002_test_f006，minor）
- 未进表的提示：
  - 有序列表两位 marker（如 `10.`）在 N=2 时输出含 `01.` 序号，经核该行为在默认路径（未配置）同样存在，属 mdformat 既有行为，非本 task 回归。
  - CLI `--indent-width` 负数未校验，与配置文件 `-1` 拒绝行为不一致；非 AC 违反，属 code reviewer 关注点（Round 2 已提示）。
- 总体判断：Round 2 唯一 minor（f005）已真实修复（精确相等断言，diff 为准）；前轮 4 条 finding 全部按 diff 核实消除，无未解决 critical/important。全量测试 4674 passed / 5 skipped（skip 为既有 Python 3.13+ exclude 用例），CommonMark 用例无回归。仅新增一条 minor（f006，AC-002 兜底分支可补 case）。无 blocking finding，PASS。
- 系统性 follow-up：无

### AC 复验披露

- AC-001：`re_verified`。`test_default_no_regression` 默认 round-trip 精确断言；全量 `tests/test_commonmark_spec.py` 4176 用例通过，默认路径无回归。
- AC-002：`re_verified`。`test_indent_width_unified` / `test_indent_width_ordered_list` 精确相等断言，独立运行输出与预期一致；兜底子句行为已独立实测正确（N=1 回落 marker 宽度），但无测试守护（f006，minor）。
- AC-003：`re_verified`。`test_code_block_untouched_byte_for_byte` 全文精确相等断言，围栏内追加/删除/重缩进任一字节差异均失败；独立运行确认围栏内容逐字节保持。
- AC-004：`re_verified`。CLI 半条（`test_indent_width_cli`，真实 `run()` + `--indent-width=4`）与配置文件半条（`test_indent_width_config_file` 写 `.mdformat.toml`，真实 `run()`）均端到端验证；非法值矩阵 `'abc'`/`-1` 拒绝路径实测通过。

`coverage = 4 / 4`

reviewed_scope: 400d486b8620a876

verdict: PASS

## Round 4 (2026-08-11 23:46 UTC+8)

## Findings

本轮无新 finding。

## 结论

- 前轮 finding 复核（以 `git diff cccbc5227e26a999244b79ed13565024260c8fe8` 为准，本轮唯一测试改动为新增 `test_indent_width_below_marker_falls_back`）：
  - t002_test_f001（AC-003 弱断言，important）：**已消除**。`tests/test_indent.py:28-32` 全文精确相等断言 `assert output == "# T\n\n```\ncode line\n  indented line\n```\n"`，本轮 diff 未再改动，仍成立。
  - t002_test_f002（AC-004 配置零测试 + 非法值崩溃，important）：**已消除**。`test_indent_width_config_file`（`tests/test_indent.py:49-61`）走真实 `run()` 读 `.mdformat.toml` 断言落盘内容；`tests/test_config_file.py:76-77` 补 `'abc'`/`-1` 非法值矩阵；`src/mdformat/_conf.py:98-105` 类型/范围校验，均以 `InvalidConfError` 拒绝。本轮 diff 未改动。
  - t002_test_f003（有序列表零覆盖，minor）：**已消除**。`test_indent_width_ordered_list`（`tests/test_indent.py:21-25`）精确断言，实测非空设。
  - t002_test_f004（死 import，minor）：**已消除**。`test_indent.py` 仅 `import os`/`tempfile`（均使用），句柄全走 `with open(...)`。
  - t002_test_f005（AC-003 残留追加漏网，minor）：**已消除**。精确相等断言对整份输出逐字节比对，追加/删除/重缩进任一字节差异均使断言失败。
  - t002_test_f006（AC-002「marker 宽度兜底」零覆盖，minor）：**已消除（主体）**。新增 `test_indent_width_below_marker_falls_back`（`tests/test_indent.py:64-68`）：`options={"indent_width": 1}`（< marker 宽度 2），断言 `output == NESTED_MD`（`- a\n  - b\n    - c\n  - d\n`）。独立复验：该用例确定触达 `_context.py:496-500` bullet_list `if configured_width:` 兜底分支（`max(1, 2)`=2），输出恰为 NESTED_MD；非空设——若移除 `max()`（改 `" " * configured_width` = 1 空格/层），输出 `- a\n - b\n  - c\n - d\n` 与断言不符，测试即红。精确相等也锁定嵌套结构不被拍平（若兜底产出平铺 2/2/2 空格同样断言失败）。残留：ordered_list 兜底子分支（`_context.py:543-549` `if configured_width:` + `max`）仍无测试，独立实测行为正确（N=1 → `1. a\n\n   1. b\n`），属「可再补一个 case」类，不阻断（见未进表的提示）。
- 改测方向复核：无。本轮唯一测试改动是新增用例（新覆盖），未修改任何既有断言迁就实现；f006 修复后测试先行语义与实现一致。
- 本轮新发现：0 条
- 未进表的提示：
  - ordered_list 兜底子分支零测试：可选补一条 `options={"indent_width": 1}` 有序列表用例（断言回落 marker 宽度 `1. `=3 空格）。行为已独立实测正确，非 AC 违反。
  - CLI `--indent-width` 负数未校验（argparse `type=int` 接受后 renderer `max()` 静默回落 marker 对齐），与配置文件 `-1` 拒绝行为不一致；非 AC 违反，属 code reviewer 关注点（Round 2/3 已提示，仍存在）。
  - 危险模式逐条扫描：本轮新增测试用精确相等断言，无恒真断言、无删/反转 expect、无注释断言、无 `.skip`/`.only`、无静默错误开关、无 mock 自己模块、无阈值掩盖、无条件跳过、无 `.value=` 冒充交互。未命中任何危险模式。
- 总体判断：Round 3 唯一 minor（f006）已真实修复（以 diff 与独立复验为准），前轮 5 条 finding 全部按 diff 核实消除，无未解决 critical/important。全量测试 4675 passed / 5 skipped（skip 为既有 Python 3.13+ exclude 用例），较 Round 3 净增 1 条（f006 兜底用例），CommonMark 用例无回归。PASS。
- 系统性 follow-up：无

### AC 复验披露

- AC-001：`re_verified`。`test_default_no_regression` 默认 round-trip 精确断言；全量 `tests/test_commonmark_spec.py` 用例通过，默认路径无回归。
- AC-002：`re_verified`。`test_indent_width_unified` / `test_indent_width_ordered_list` 精确相等断言，独立运行输出与预期一致；兜底子句 `test_indent_width_below_marker_falls_back`（N=1）独立运行确认回落 marker 宽度，精确断言锁定嵌套结构，非空设。
- AC-003：`re_verified`。`test_code_block_untouched_byte_for_byte` 全文精确相等断言，围栏内追加/删除/重缩进任一字节差异均失败；独立运行确认围栏内容逐字节保持。
- AC-004：`re_verified`。CLI 半条（`test_indent_width_cli`，真实 `run()` + `--indent-width=4`）与配置文件半条（`test_indent_width_config_file` 写 `.mdformat.toml`，真实 `run()`）均端到端验证；非法值矩阵 `'abc'`/`-1` 拒绝路径实测通过。

`coverage = 4 / 4`

reviewed_scope: fbe60fac5ee05f65

verdict: PASS
