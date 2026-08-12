# Task review t004（reviewer_focus: 代码）

- task：`t004_rename_package_md_kx`
- spec：`docs/tasks/t004_rename_package_md_kx/spec.md`
- diff_anchor：`5e1fbc147a53203f8e632af02d20cb44953d2adc`
- target：`git diff 5e1fbc147a53203f8e632af02d20cb44953d2adc`
- round：1
- reviewed_at：2026-08-12 12:30 UTC+8

reviewed_scope: 1e6bc7a87c3781fa

## Findings

### t004_code_f001 - entry point 组名（`mdformat.*` → `md_kx.*`）超出 spec 范围，破坏上游插件发现契约

- 严重度：minor
- 锚点：无对应 AC；违反 spec 范围枚举（范围仅列 src 目录、包内 import、pyproject name/entry point/isort/coverage、bumpversion 路径、其他 Python 文件 import），且与「非范围：上游 mdformat-gfm 插件的测试（CI 中保留）」存在张力
- 位置：`src/md_kx/plugins.py:89`、`src/md_kx/plugins.py:99`（`__getattr__` 内 `importlib.metadata.entry_points(group=...)`）
- 问题：spec 范围内只要求改「Python 文件对 mdformat 包的 import」。entry point 组名（`mdformat.parser_extension` / `mdformat.codeformatter`）不是 import，是插件发现协议字符串。此处改为 `md_kx.*` 属范围外自由发挥，且后果可观测：上游 mdformat-gfm / mdformat-black 等插件按 `mdformat.*` 组注册，改名后本包无法发现任何既有插件，与「非范围：上游 mdformat-gfm 插件测试 CI 保留」冲突。gfm CI job 的适配（含 `import mdformat` 深层不兼容）整体在 t006，故非本 task 阻断；但该组名变更应由 spec 或 `docs/blueprint/decisions.md` 显式记录为「fork 自持插件生态」决策，否则后续维护者无据可依。
- 建议：在 `docs/blueprint/decisions.md` 记录 entry point 组随包名改 `md_kx.*`（fork 自持插件生态）；或如需保持上游插件兼容，将两处 `md_kx.*` 组名改回 `mdformat.*`。二选一并补文档，留作实施侧处置。

## 结论

- 前轮 finding 复核：Round 1，无。
- 本轮新发现：1 条（f001，minor）。
- 未进表的提示：
  - **配置文件名 `.mdformat.toml` → `.md_kx.toml`**（`src/md_kx/_conf.py:39` 及 `_cli.py:75` 错误文案）：包内一致、低风险，属 fork 改名自然延伸；但为既有用户可见契约变更，建议一并记入 `decisions.md`。
  - **pyproject tox `hook` env**（`pyproject.toml` `["pre-commit", "try-repo", ".", "md_kx", ...]`）：`md_kx` 是 CLI 命令名，当前 `.pre-commit-hooks.yaml` 仍注册 `id/name/entry: mdformat`，该 env 此刻不可跑。属 t006 范围（`.pre-commit-hooks.yaml` hook id 改名），链式跟进后闭合，非本 task 缺陷。
  - **本地 venv 残留**：`.venv` 内仍有 `mdformat-1.0.0.dist-info` 与 `__editable__.mdformat-1.0.0.pth`（旧包安装未清理），导致该环境同时存在 `mdformat` 与 `md_kx` 两个 console script；pyproject 只声明 `md_kx`，新装环境不会复现，非代码缺陷。
  - **文件过大**：`src/md_kx/renderer/_context.py` 787 行、`_cli.py` 500 行，`_unicode_punctuation.py` 8636 行为生成 Unicode 数据（排除）。本 task 对 src 全为等量改名、净增 0 行，未触发阈值条件。
  - **复杂度**：`_cli.run`（C901）与 `renderer/_context.paragraph`（C901）高复杂度为既有，本 task 仅改名未增分支。
  - **范围外观察**：`.github/workflows/tests.yaml` 与 `.pre-commit-hooks.yaml` 中 `mdformat` 命令引用、`.github/ISSUE_TEMPLATE/` 文案均属 t006 范围；`_cli.py:173` 错误信息里 `https://github.com/hukkin/mdformat/issues` 是上游 URL（fork 归因），非残留 import，不构成问题。
- 总体判断：包改名完整（src 无残留 import、entry point/isort/coverage/bumpversion 一致、fuzzer 已改），三态功能黑盒复验通过；仅 1 条 minor，无未解决 critical / important。
- 系统性 follow-up：无（entry point 组名与配置文件名决策建议写入 `docs/blueprint/decisions.md`，不另立 task）。

### AC 复验方式

- AC-001 `re_verified`：`uv run python -c "import md_kx"` 输出 OK、`__version__==1.0.0`；`src/mdformat` 不存在，`src/md_kx` 存在。
- AC-002 `re_verified`：`grep -rn "import mdformat\|from mdformat" src/md_kx/` 无匹配；全库非 tests 非 docs 的 .py（src、fuzzer、scripts）亦无 `import mdformat`，仅 `_cli.py:173` 一条上游 URL。
- AC-003 `re_verified`：pyproject `name = "md_kx"`（:7）、`md_kx = "md_kx.__main__:run"`（:37）、`known_first_party = ["md_kx", "tests"]`（:47）、`source = ["md_kx"]`（:153）；`.bumpversion.cfg:11` 指向 `src/md_kx/__init__.py`。
- AC-004 `re_verified`：`uv run --with-requirements tests/requirements.txt python -m md_kx --version` 输出 `md_kx 1.0.0`；另 `uv run python -m md_kx --version` 同。

coverage = 4 / 4

verdict: PASS
