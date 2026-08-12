# Task review t006（reviewer_focus: 通用）

- task：`t006_rename_cli_docs_md_kx`
- spec：`docs/tasks/t006_rename_cli_docs_md_kx/spec.md`
- diff_anchor：`f2c50f7622f39621383e766e6294d868146ed594`
- target：`git diff f2c50f7622f39621383e766e6294d868146ed594`
- round：1
- reviewed_at：2026-08-12 13:20 UTC+8

reviewed_scope: cff8e0443a4c3261

## Findings

### t006_gen_f001 - README CLI usage 快照缩进未随 prog 改名更新，与实际 `md_kx --help` 输出不一致

- 严重度：important
- 锚点：AC-004（README 的 CLI usage 快照应与实际 `md_kx --help` 输出一致）
- 位置：`README.md:78-83`
- 问题：README usage 摘要块 continuation 行首缩进为 16 空格，但实际 `md_kx --help` 输出为 13 空格。原因：该缩进继承自上游 `mdformat`（prog 8 字符，`usage: mdformat ` 前缀 16 字符 → 16 空格续行），改名 `md_kx`（5 字符）后 argparse 续行缩进应为 13 空格。已在 3.12 真实运行 `.venv/bin/python` 以 argv[0]=md_kx 捕获输出（13 空格），并模拟 3.13+ parser（补 `--exclude`）得到相同 13 空格——缩进错位与 Python 版本无关。README 快照仅改了首行 prog 名，续行缩进未同步。注：快照含 `[--exclude PATTERN]`，与实际 CI linters 环境（Python 3.13）一致，且 README 已注明 "--exclude option is only available on Python 3.13+"，此部分可接受；Python <3.13 本地环境输出无 `--exclude`，比对时需按 3.13 口径。字节级比对（`/tmp/md_kx_help.txt` vs README 块）`MATCH == False`。
- 建议：在 Python 3.13+ 环境重新生成 usage 快照（`md_kx --help`）替换 README 78-83 行，修正续行缩进为 13 空格。

### t006_gen_f002 - README 品牌描述残留 6 处「Mdformat」产品名，AC-001 未完全落实

- 严重度：important
- 锚点：AC-001（README/docs/blueprint/docs/specs 产品名与命令引用改 md_kx，除 "fork 自上游 mdformat" 历史指代）
- 位置：`README.md:15`、`README.md:17`、`README.md:127`、`README.md:132`、`README.md:149`、`README.md:175`
- 问题：下列句子用旧品牌「Mdformat」描述当前产品，非 upstream/fork 历史指代，属改漏（spec 风险节明列的"品牌改漏"项）。大小写敏感替换 `mdformat`→`md_kx` 漏掉大写形式：
  - `README.md:15` "Mdformat is an opinionated Markdown formatter"
  - `README.md:17` "Mdformat is a Unix-style command-line tool as well as a Python library."
  - `README.md:127` "Mdformat is a CommonMark formatter."
  - `README.md:132` "Mdformat often resorts to backslash escaping..."
  - `README.md:149` "Mdformat is pure Python code!"
  - `README.md:175` "Mdformat's parser extension plugin API allows..."
  同段 FAQ 标题已改 `md_kx`（README.md:125），正文却保留 `Mdformat`（README.md:127），段内自相矛盾，佐证漏改。docs/blueprint 与 docs/specs 无此问题（仅剩两处「初稿按 mdformat 1.0.0 填写」历史来源注记，属合法指代）。
- 建议：将上述 6 处 `Mdformat`/`Mdformat's` 统一改为 `md_kx`/`md_kx's`，与 README 其余品牌用法一致。

## 结论

- 前轮 finding 复核（Round 1 无）
- 本轮新发现：2 条（t006_gen_f001、t006_gen_f002）
- 未进表的提示：
  - 范围外改动：diff 含 `src/md_kx/_cli.py:84-102` 与 `tests/test_api.py:149-150`、`tests/test_performance.py:7-8` 的纯格式重排（长行折叠），spec 非范围明示 src/tests 由 t004/t005 已改，本 task 不应触碰。疑似实现期误跑格式化器（`md_kx`）对源文件生效所致。无害但属偏航，建议提交前剔除，勿并入 t006 执行 commit。
  - `pre-commit` 二进制本机不可用，未直接跑 `pre-commit validate-manifest`；改由直接核对 `.pre-commit-hooks.yaml`（7 行、YAML 合法、必需字段 id/name/entry/language 齐全，entry=`md_kx` 与 pyproject `[project.scripts]` 一致）。
- 总体判断：CLI 命令与 docs 品牌改名主体正确、`.md_kx.toml` 与 `context.options["md_kx"]` 与代码一致、AC-002/AC-003 通过；但 AC-004 快照缩进错位、AC-001 残留 6 处品牌名，两条 important 未解决，FAIL。
- 系统性 follow-up：无

### AC 复验方式

- AC-001：`re_verified`。大小写不敏感 grep 全量扫描 README/docs/blueprint/docs/specs，发现 6 处残留（见 f002）；代码侧 `.md_kx.toml`（`src/md_kx/_conf.py:39`）与 `options["md_kx"]`（`src/md_kx/renderer/_context.py:395`）与 docs 改动一致。
- AC-002：`re_verified`。直接核对 `.pre-commit-hooks.yaml`：YAML 合法，必需字段（id/name/entry/language）齐全且值正确，entry 与 pyproject 脚本入口匹配。因本机无 pre-commit 二进制，未重跑 `validate-manifest` 命令本身；已核对其实际检查对象（文件结构与必需键）。
- AC-003：`re_verified`。重跑 `.venv/bin/python -m md_kx --check README.md`，exit 0；CI linters 跑 Python 3.13，`md_kx --check README.md` 与 `pre-commit try-repo . md_kx` 均与改名后 hook id/入口一致。
- AC-004：`re_verified`。捕获真实 `md_kx --help`（3.12 实跑 + 模拟 3.13+ parser）与 README 78-83 块做字节比对，`MATCH == False`：continuation 缩进 16 vs 13 空格（版本无关）；见 f001。

coverage = 4 / 4

verdict: FAIL

## Round 2 (2026-08-12 12:57 UTC+8)

reviewed_scope: 5ac538d26391dbf6

## Findings

### t006_gen_f003 - README「Install with GFM support」指引与插件 group 改名决策矛盾，注入 mdformat-gfm 不会被发现

- 严重度：important
- 锚点：行为缺陷（用户按 README 操作得到静默失效安装）+ 契约区非范围决策矛盾。契约区非范围当前版本记录「fork 改名后插件 group 为 md_kx.*，mdformat-gfm 不再适用」；`docs/blueprint/decisions.md:10` 记录选 option b（`md_kx.*` group，既有插件需重注册）。
- 位置：`README.md:35`（GFM 安装块 30-37）
- 问题：README 仍宣称 `pipx inject md_kx mdformat-gfm` 即可获得 GFM 支持。但 md_kx 插件发现只读 `md_kx.parser_extension` / `md_kx.codeformatter` group（`src/md_kx/plugins.py:89,99`），全 src grep 无 `mdformat.*` group 回退。上游 mdformat-gfm 注册在 `mdformat.parser_extension` group，注入后 md_kx 不会发现该插件，GFM 功能实际不生效——README 指引与已选决策矛盾，且是用户可观察的失败（装了插件但无 GFM）。
- 建议：删除该 GFM 安装小节，或改写为「GFM 需 fork 后重注册为 md_kx.* group 的插件」，移除 `pipx inject md_kx mdformat-gfm`（与 decisions.md option b 一致）。

## 结论

- 前轮 finding 复核（Round 2）：
  - t006_gen_f001（important，AC-004）：**修不彻底，仍存在**。实测当前 `README.md:79-83` 续行缩进 15 空格；真实 `md_kx --help`（console script，prog=`md_kx`，Python 3.12 实测）续行缩进 13 空格。argparse 续行缩进 = `len("usage: " + prog + " ")` = 13，与 Python 版本无关。16→15 仍 ≠ 13，README 快照与实际输出字节比对仍 MATCH==False，AC-004 未满足。task.md 处置表自称「已修 16→13」，与实际 diff（15）不符，采信 diff 不采信自述。
  - t006_gen_f002（important，AC-001）：**已消除**。大小写敏感 grep 确认 README/docs/blueprint/docs/specs 无大写 `Mdformat` 残留；6 处已改 `Md_kx`（句首大写，沿用上游句首品牌惯例）。剩余 `mdformat` 引用均为上游链接/来源注记/决策背景（README:3-7,140,141,176；domain/architecture.md:3；decisions.md:9-10），属合法指代。
- 本轮新发现：1 条（t006_gen_f003）
- 未进表的提示：
  - 范围外改动仍在：`src/md_kx/_cli.py:84-102`、`tests/test_api.py:149-150`、`tests/test_performance.py:7-8` 纯格式重排（长行折叠），spec 非范围声明 src/tests 归 t004/t005，本 task 不应触碰；无害但偏航，建议勿并入 t006 执行 commit。
  - `tests/test_plugins.py:405,414` 用 `"mdformat-gfm"` 作 mock dist 名，仅为字符串 fixture，非真实依赖，非本 task 范围问题。
  - pre-commit 二进制本机不可用，未重跑 `validate-manifest` 命令本身；.pre-commit-hooks.yaml 结构核对同 Round 1。
- 总体判断：f001 未真正修复（README usage 续行缩进 15≠13），f003 新增 README GFM 指引与插件 group 决策矛盾；两条 important 未解决，FAIL。
- 系统性 follow-up：无

### AC 复验披露（Round 2）

- AC-001：`re_verified`。大小写敏感 grep 全量扫描 README/docs/blueprint/docs/specs，无 `Mdformat` 残留；剩余 `mdformat` 均为上游链接/来源注记/决策背景。README:35 `mdformat-gfm` 注入指令与决策矛盾，见 f003。
- AC-002：`re_verified`（结构核对）。`.pre-commit-hooks.yaml` id/name/entry 均 `md_kx`，必需字段齐全；本机无 pre-commit 二进制，未跑 `validate-manifest` 命令本身，依赖结构核对与 hook 定义检查。
- AC-003：`re_verified`。`.venv/bin/python -m md_kx --check README.md` exit 0；`tests.yaml` linter 命令 `md_kx --check README.md`、`pre-commit try-repo . md_kx` 与改名后 hook id/入口一致；`test-gfm-plugin` job 已完整删除，CI/tests/src 无悬空引用。
- AC-004：`re_verified`（不通过）。捕获真实 `md_kx --help`（console script，prog=`md_kx`）与 README 78-115 块比对：唯一差异为 usage 续行缩进，README 15 空格 vs 实际 13 空格；`--exclude` 位置与 options/positional 各行与 Python 3.13+ 口径一致。AC-004 未满足，f001 未闭合。

coverage = 4 / 4

verdict: FAIL

## Round 3 (2026-08-12 13:04 UTC+8)

reviewed_scope: ca94a718eaec675d

## Findings

本轮无新 finding。

## 结论

- 前轮 finding 复核（Round 3，以 git diff 与实跑为准）：
  - t006_gen_f001（important，AC-004，usage 缩进）：**已修**。README 71-107 行（```console 块正文，剔 70 行 `foo@bar` 提示行）与模拟 3.13+ `md_kx --help` 完整输出**字节级一致**（模拟方式：复用 `md_kx._cli.make_arg_parser` 真实代码路径，`sys.version_info` 补丁为 (3,13,0)，prog=`md_kx`；`diff` 无输出）。续行缩进 13 空格（`sed -n 71,76p | cat -A` 确认 `usage: md_kx ` 前缀 13 字符）。`--exclude` 位于 `--table-mode` 与 `--extensions` 之间，与 `_cli.py:252-259` 3.13+ 门控注册顺序一致。本地 3.12 实跑 `md_kx --help` 与 README 唯一差异为缺 `--exclude` 行——该选项 3.13+ 门控（`_cli.py:252`），README 注明 "--exclude option is only available on Python 3.13+"，CI linters 跑 Python 3.13，口径一致。AC-004 满足。
  - t006_gen_f002（important，AC-001，大写 Mdformat）：**已修**（Round 2 已消除，本轮复核仍成立）。大小写敏感 grep README/docs/blueprint/docs/specs 无 `Mdformat` 残留，句首统一 `Md_kx`；README 现存 `mdformat` 仅上游 badge/链接/GitHub topic/插件 URL（README:3-5,7,133-134,169），属 AC-001 允许的 fork 历史指代。
  - t006_gen_f003（important，README GFM 安装段）：**已修**。README diff 显示 GFM 安装段整体删除，现仅剩 CommonMark 安装 `pipx install md_kx`；grep 确认 README 无 gfm/GitHub Flavored 残留（唯 `docs/blueprint/decisions.md:10` 在决策背景提及 `mdformat-gfm`，属合法决策记录）。`.github/workflows/tests.yaml` `test-gfm-plugin` job 完整删除。与 decisions.md option b（`md_kx.*` group）及 spec 非范围一致，不再有「注入 mdformat-gfm 但不生效」的用户可观察失效。
- 本轮新发现：0 条
- 未进表的提示：
  - 范围外改动仍在 diff：`src/md_kx/_cli.py:84-89,100-103`、`tests/test_api.py:149-150`、`tests/test_performance.py:7-8` 纯格式重排（长行折叠），spec 非范围声明 src/tests 归 t004/t005；无害、非 blocking，建议勿并入 t006 执行 commit（与 Round 1/2 同）。
  - pre-commit 二进制本机不可用，未重跑 `validate-manifest` 命令本身；`.pre-commit-hooks.yaml` 结构核对同前（id/name/entry 均 `md_kx`，必需字段齐全，entry 与 `pyproject [project.scripts]` 一致）。
  - pyproject.toml 相对 anchor 无 diff（t004 已改），tox env 描述与 `[project.scripts]` 均 `md_kx`，Homepage 指向上游 mdformat URL，合法。
- 总体判断：三条前轮 important（f001/f002/f003）均以 diff/字节比对/实跑核实消除，本轮无新 blocking；AC-001/AC-003/AC-004 复核通过，AC-002 结构核对通过。PASS。
- 系统性 follow-up：无

### AC 复验披露（Round 3）

- AC-001：`re_verified`。大小写敏感 grep 全量扫描 README/docs/blueprint/docs/specs，无 `Mdformat` 残留；剩余 `mdformat` 均为上游链接/来源注记/决策背景。
- AC-002：`re_verified`（结构核对）。`.pre-commit-hooks.yaml` id/name/entry 均 `md_kx`，必需字段齐全；本机无 pre-commit 二进制，未跑 `validate-manifest` 命令本身，依赖结构核对与 hook 定义检查。
- AC-003：`re_verified`。`.venv/bin/md_kx --check README.md` 实跑 exit 0；`tests.yaml` linter 命令 `md_kx --check README.md`、`pre-commit try-repo . md_kx` 与改名后 hook id/入口一致；`test-gfm-plugin` job 已完整删除，无悬空引用。
- AC-004：`re_verified`（通过）。README 71-107 行与模拟 3.13+ `md_kx --help` 完整输出字节级一致（make_arg_parser 真实路径 + version_info 3.13 模拟，`diff` 无输出）；续行缩进 13 空格；`--exclude` 位置与 3.13 门控注册顺序一致。

coverage = 4 / 4

verdict: PASS
