# Task review t005（reviewer_focus: 代码）

- task：`t005_rename_tests_md_kx`
- spec：`docs/tasks/t005_rename_tests_md_kx/spec.md`
- diff_anchor：`71a49c1457fd53f26442fd49a58130b1c257b97b`
- target：`git diff 71a49c1457fd53f26442fd49a58130b1c257b97b`
- round：1
- reviewed_at：2026-08-12 20:40 UTC+8

reviewed_scope: a9404b54543ba19d

## Findings

无。clean review（0 finding）。

逐维度核对结论（无 blocking 且无 minor）：

- **AC-001（无残留 mdformat import / `mdformat.` 引用）**：`grep -rni "mdformat" tests/`（含 `data/`、`e2e/`、`unit/`、`integration/`、`repo_template/`、`conftest.py` 全子树）仅剩四类许可例外：
  - `test_cli.py:160,168` 上游 issue 链接 `https://github.com/hukkin/mdformat/issues`；
  - `test_cli.py:362,363,369,372` 第三方插件名 `mdformat-tables` / `mdformat-black`；
  - `test_plugins.py:389,405,414` 第三方插件发行名 `mdformat_gfm-0.3.6.dist-info` / `Name: mdformat-gfm` / `dist_infos` 断言键。
  其余零命中。
- **范围（不偏航 / 不自由发挥）**：diff 仅触 tests/ 全部 .py 与 task.md（流程文件）。src/、CI、README 未动，符合非范围。`.mdformat.toml`→`.md_kx.toml`、`opts["mdformat"]`→`opts["md_kx"]`、entry point group `[md_kx.parser_extension]`、`src/mdformat`→`src/md_kx` 路径断言、version 前缀、错误文案 `bug in mdformat`→`bug in md_kx` 等改动均在 tests/ 内且为改名后的必然结果，与 src（`_conf.py:39` 用 `.md_kx.toml`、`plugins.py:60/89/99` 用 `md_kx` 命名空间、`_cli.py:220` version 文案）一致，非范围外行为。
- **wrap 期望更新合理（改名引起 72 列分界变化）**：`test_cli.py:152` 用 `wrap_paragraphs`（`_cli.py:434`，width=72 走 `terminal_width` 分支，`cached_textwrapper` `break_long_words=False`）对 `md_kx` 段落重算：三行长度 63 / 70 / 47，行 2「Markdown. This is likely a bug in md_kx. Please create an issue report」、行 3「here: …mdformat/issues」，与 diff 新期望逐字一致（`mdformat` 8 字符→`md_kx` 5 字符，缩短 3 字符使分界右移）。旧期望仅 `mdformat.`/`mdformat` 改 `md_kx.`/`md_kx`，非就地把旧测试预期改成当前实现的输出——分界变化确由字符串长度变化驱动，重算验证成立。
- **实现正确性**：`md_kx.text`/`md_kx.file`/`md_kx._cli` 等引用对应 src 真实符号；`patch("md_kx.renderer._context.get_list_marker_type")` 目标为 `_context.py:24` 导入符号、`patch("md_kx._cli.Path.cwd")` 目标在 `_cli.py:51,383` 使用 `Path`，均存在；`test_for_profiler.py` 断言 `src/md_kx` 存在成立。改名机械替换无逻辑改动，无控制流/错误处理/边界/命名/死代码问题。
- **文件过大**：触达 tests/ 文件均 <600 行（最大 `test_cli.py` 514 行），未达阈值。
- **圈复杂度**：本 diff 全为改名，无新增分支。

## 结论

- 前轮 finding 复核（Round N≥2 才写）：不适用，本轮为 Round 1。
- 本轮新发现：0
- 未进表的提示：文件过大——无；复杂度——无；范围外观察——无。
- 总体判断：改名完整、无残留、wrap 期望重算正确、全量测试通过，无未解决 critical / important，亦无 minor。
- 系统性 follow-up：无

### AC 复验方式

- `re_verified`：AC-001。`grep -rni "mdformat" tests/` 全子树，仅余四类许可例外（第三方插件名 mdformat-gfm/tables/black 与 upstream issue 链接），无 `import mdformat` / `mdformat.` / `.mdformat.toml` 残留。
- `re_verified`：AC-002。实际运行 `uv run --with-requirements tests/requirements.txt pytest tests -q` → `4684 passed, 5 skipped`（≥ spec 要求 4668+）。5 skipped 为 Python 版本条件跳过（`exclude` conf 仅 3.13+），非本改名所致。
- `re_verified`：AC-003。单独运行 `pytest tests/test_table.py tests/test_indent.py tests/test_front_matter.py -q` → `24 passed`。

coverage = 3 / 3

verdict: PASS
