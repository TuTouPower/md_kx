# Task review t005（reviewer_focus: 测试）

- task：`t005_rename_tests_md_kx`
- spec：`docs/tasks/t005_rename_tests_md_kx/spec.md`
- diff_anchor：`71a49c1457fd53f26442fd49a58130b1c257b97b`
- target：`git diff 71a49c1457fd53f26442fd49a58130b1c257b97b`
- round：1
- reviewed_at：2026-08-12 12:38 UTC+8

## Findings

无 finding。

改动性质：纯改名 task。diff 覆盖 tests/ 全部 15 个 .py（14 测试文件 + tests/utils.py），116 insertions / 116 deletions 完全平衡，无测试函数/文件删除（逐条扫描 diff 无 `-def` 行）。已逐条核对：所有 import、`mdformat.text()`/`mdformat._cli` 等模块方法引用、`mdformat.renderer.*`/`mdformat._util`/`mdformat.plugins` 路径、patch 目标、`.mdformat.toml` 配置文件名、`opts["mdformat"]` 命名空间全部改为 `md_kx`，与生产代码（`src/md_kx/`）一致。

### 重点核实项

**test_wrap_paragraphs 期望更新（合理，非迁就实现）**：`tests/test_cli.py:156-168`。错误文案中 `mdformat`（8 字符）→ `md_kx`（5 字符），短 3 字符。wrap 宽度被 mock 钉在 72（`patch("shutil.get_terminal_size", return_value=(72, 24))`，生产 `wrap_paragraphs` 对 0<w<80 取 terminal_width=72）。独立用 `textwrap.fill(width=72)` 重算两个字符串：
- 旧 `mdformat.`（9 字符）：第 2 行 66 字符后 `report`（+7=73>72）折行 → 旧期望 `...Please create an issue\nreport here: ...` 吻合
- 新 `md_kx.`（5 字符）：第 2 行 70 字符后 `here:`（+6=76>72）折行 → 新期望 `...Please create an issue report\nhere: ...` 吻合

wrap 边界移动完全由字符串长度差驱动，期望值经确定性计算逐字吻合。文案中保留的 `https://github.com/hukkin/mdformat/issues` 为上游 issue tracker URL，与生产 `src/md_kx/_cli.py:173` 一致。

**test_load_entrypoints 分组改名（合理）**：`tests/test_plugins.py:397-400`。entry_points.txt 分组 `[mdformat.parser_extension]` → `[md_kx.parser_extension]`，`ext1/ext2=md_kx.plugins`，断言值 `md_kx.plugins`——与生产 `src/md_kx/plugins.py` 的 `group="md_kx.parser_extension"` 一致。

**残余 "mdformat" 字符串（允许）**：grep 确认 tests/ 仅 `test_plugins.py`（dist-info 目录名 `mdformat_gfm-0.3.6.dist-info`、METADATA `Name: mdformat-gfm`、dict key 断言）与 `test_cli.py`（`mdformat-black`/`mdformat-tables` fixture dist 名、上游 URL）含字面 "mdformat"。均为任意 fixture 数据或外部 URL，非 import 或 `mdformat.` 模块引用，且 spec 风险节明确「mdformat-gfm 插件测试依赖官方包名」。AC-001 的精确 grep（import / `mdformat.` 引用 / `.mdformat.toml`）三项全为 NONE。

### 危险模式扫描

逐条未命中：无恒真断言、无删/反转 expect、无注释掉断言、无弱化断言、无测试删除、无 `.skip`/`.only` 新增、无静默错误（test_api.py 唯一 `# noqa: F401` 为原行随改名保留，属 import-ability 测试的合法 noqa，非抑制错误）、无阈值改动、无 mock 误用（patch 目标全部对应生产真实模块路径）。

## 结论

- 前轮 finding 复核（Round N≥2 才写）：不适用（本轮 round 1）
- 改测方向复核：无「迁就实现」的改测。test_wrap_paragraphs 期望更新已证明由改名引起的确定性 wrap 边界变化；test_load_entrypoints / 配置文件名 / opts 命名空间改动均对齐生产代码
- 本轮新发现：0 条
- 未进表的提示：无
- 总体判断：改名完整、测试全量通过、无危险模式、无迁就实现的改测；0 finding
- 系统性 follow-up：无

### AC 复验方式

- AC-001（无残留 mdformat import / `mdformat.` 引用）：`re_verified`。grep 三项独立复验：import / 模块引用 / `.mdformat.toml` 全为 NONE；仅存 fixture dist 名与上游 URL
- AC-002（全量 pytest 4668+ passed）：`re_verified`。重跑 `uv run --with-requirements tests/requirements.txt pytest tests -q` 得 **4684 passed, 5 skipped**（4684 ≥ 4668）
- AC-003（test_table/test_indent/test_front_matter 仍通过）：`re_verified`。三文件与 test_cli 单独重跑 62 passed, 1 skipped；全量跑亦含全部通过

coverage = 3 / 3

reviewed_scope: a9404b54543ba19d

verdict: PASS
