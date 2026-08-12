# Task review t004（reviewer_focus: 测试）

- task：`t004_rename_package_md_kx`
- spec：`docs/tasks/t004_rename_package_md_kx/spec.md`
- diff_anchor：`5e1fbc147a53203f8e632af02d20cb44953d2adc`
- target：`git diff 5e1fbc147a53203f8e632af02d20cb44953d2adc`
- round：1
- reviewed_at：2026-08-12 14:35 UTC+8

## Findings

无（0 findings）。diff 无任何测试文件改动（`tests/` 非范围，t005 负责），无测试可审；全部 AC 由 reviewer 独立黑盒复验通过。

## 结论

- 前轮 finding 复核：Round 1，无前轮。
- 改测方向复核：无（diff 未改动任何既有测试；`tests/` 目录零改动）。
- 本轮新发现：0 条。
- 未进表的提示：
  1. `src/md_kx/plugins.py` 将 entry point group 由 `mdformat.codeformatter` / `mdformat.parser_extension` 改为 `md_kx.*`。属超范围语义变更（spec 范围未列 entry point group），但符合 fork 改名破坏性升级取向；后果是上游按 `mdformat.*` 注册的插件（如 mdformat-gfm）不再被本包加载。属架构/代码评审关注点，非测试问题，不进 finding。
  2. 内部 option key `mdit.options["mdformat"]` → `md_kx`（`src/md_kx/_util.py`、`src/md_kx/renderer/_context.py`）与配置文件 `.mdformat.toml` → `.md_kx.toml`（`src/md_kx/_conf.py`、`src/md_kx/_cli.py` 报错文案）均已读写两侧一致改名。与基线提交对比验证无行为变化；第三方插件读取旧 key 会失效，属 fork 改名预期。
  3. 可测试性声明「全部 AC 可自动测试」：本 task 实际无提交的自动化测试，但上下文区「测试策略」已明确批准黑盒验证（改名后 pytest 因 tests 引用旧名按设计失败，由 t005 跟进）。所有 AC 均有黑盒验证命令且 reviewer 已独立复验，不构成覆盖缺口。
- 总体判断：改名重构干净无回归，三态表格功能与基线一致，全部 AC 复验通过，无 blocking/minor finding，PASS。
- 系统性 follow-up：无。

## AC 复验披露

- AC-001 `re_verified`：`uv run --with-requirements tests/requirements.txt python -c "import md_kx; print(md_kx.__version__)"` 输出 `1.0.0`；`src/md_kx/` 存在、`src/mdformat/` 不存在（ls 确认）。
- AC-002 `re_verified`：`grep -rnE '^\s*(import mdformat|from mdformat)'` 全仓扫描，命中全部位于 `tests/`（非范围，t005）；`src/md_kx/` 内唯一 `mdformat` 字符串为 `_cli.py:173` GitHub issue 链接（非 import）。
- AC-003 `re_verified`：`pyproject.toml` 逐项核对——`name = "md_kx"`（L7）、entry point `md_kx = "md_kx.__main__:run"`、coverage `source = ["md_kx"]`（L153）、isort `known_first_party = ["md_kx", "tests"]`（L47）。
- AC-004 `re_verified`：`uv run --with-requirements tests/requirements.txt python -m md_kx --version` 输出 `md_kx 1.0.0`；另以 `printf '# Hello\n\nx  y\n' | python -m md_kx -` 验证 CLI stdin 端到端格式化，输出 `x y`（双空格归一化生效）。

coverage = 4 / 4

reviewed_scope: 1e6bc7a87c3781fa

verdict: PASS
