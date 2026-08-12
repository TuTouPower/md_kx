---
tid: "t007"
slug: "fix_list_table_lazy_continuation"
title: "修复列表项后 0 缩进表格行 validate 失败"
status: "done"
branch: "t007_fix_list_table_lazy_continuation"
worktree: ""
review_level: "full"
diff_anchor: "b3e6991001d6b136b35e9a6b4c2b584130abde64"
depends_on: ""
conflicts_with: ""
note: "来自 p006；enable table 后 lazy continuation 解析不一致"
---

# Task 过程总账

**front matter 是状态权威**，只经 `scripts/repo_template/task.py` 修改；`docs/tasks_index.json` 由它派生。reviewer 只写 `review_code.md` / `review_test.md` / `review_general.md`，不改本文件。

## 实施笔记

执行期边做边写：实际步骤、踩坑、中途决策、偏离 spec、关键验证、blocked 原因与用户放行的新轮次上限。

创建期不预测实施步骤——那时尚未读代码，预测必然失准。只记有追溯价值的内容，不写命令流水账。无事项时写：无

- 根因定位（2026-08-12）：p006 复现确认 validate 失败根因在 renderer 对 lazy 表格行缩进 + enable table 二次解析变 table，非 indent-width 特有。
- 修复方案迭代：初始尝试 list_item 层 `|` 开头守卫（误伤嵌套表格/代码块）→ 移到 paragraph 子块标记（首行泄漏 + 独立段落误伤）→ softbreak 全局标记（非列表泄漏）→ softbreak 加 _in_block(list_item)（列表内块引用仍泄漏）→ 精化 `node.parent.parent.parent.type == "list_item"`（九场景全过）。最终方案在 softbreak 层识别 lazy 续行加 `\x00` 标记，列表 renderer 续行循环剥标记不缩进。
- 关键坑：`\x00` 标记必须跟随 softbreak 行尾，消费循环按「上一行行尾标记 → 当前行不缩进」处理；blockquote 等中间层会破坏标记，故标记条件严格限定 paragraph 直接父为 list_item。

## Review 处置

本小节 = 处置表唯一落点。review 结束后在此追加轮次小节与表格；不写进 `review_code.md` / `review_test.md` / `review_general.md`，也不另建文件。

逐条对应当前 `review_level` 的 review finding（`full`：code/test；`single`：general）。`status` 只许：`已修` / `遗留` / `撤回`（全处理，不静默丢 finding）。

- `已修`：本 task 内已按 finding 改完
- `遗留`：本 task 不处理。**内容登记到 `docs/pending/todo/`**：用 `scripts/repo_template/pending.py new --slug <主题>` 建条目并填写，`fix_ref` 填该 `pNNN`（已有 follow-up task 则填 tid）；本表只留引用与一句话 rationale。critical / important 遗留仍阻断，minor 遗留不阻断。
- `撤回`：误报；须原 reviewer 在对应 `review_*.md` 末尾追加撤回记录后，再在本表标 `撤回`

本 task 目录会随 `finish` 归档，遗留正文留在这里等于丢失——`fix_ref` 为空的 `遗留` 行不算处置完成。

reviewer 标注为 spec 过时的 finding（实现合理但与 spec 描述不符），处置为改 spec 上下文区，不计 FAIL。

### Round 1 场景说明

- **无 finding**：写「Round 1 零 finding，未进处置表。」
- **仅有 minor（无 critical / important）**：仍建表，逐条处置 minor。
- **有 critical / important**：建表，逐条填 status（不得留空）。

### Round 1 (2026-08-12 14:50 UTC+8)

|finding_id|severity|status|rationale|fix_ref|
|------|------|------|------|------|
|t007_code_f001|important|已修|守卫改在 paragraph 子块标记 lazy 表格行（\x00），续行循环识别不缩进；嵌套表格/代码块行不受影响|src/md_kx/renderer/_context.py:483|
|t007_code_f002|minor|已修|守卫逻辑收敛到 list_item render_child + 续行循环统一处理|src/md_kx/renderer/_context.py:483|
|t007_code_f003|minor|已修|补列表内嵌套表格与代码块管道行测试|tests/test_list_table.py:56|
|t007_test_f001|critical|已修|嵌套表格回归修复 + 测试（test_nested_table_in_list_kept）|tests/test_list_table.py:56|
|t007_test_f002|critical|已修|代码块管道行回归修复 + 测试（test_pipe_line_in_list_code_block_kept）|tests/test_list_table.py:66|

### Round 2 (2026-08-12 15:10 UTC+8)

|finding_id|severity|status|rationale|fix_ref|
|------|------|------|------|------|
|t007_code_f004|important|已修|首行 \x00 标记剥除（first_line rstrip）；续行循环改行尾状态判断|src/md_kx/renderer/_context.py:516,577|
|t007_code_f005|important|已修|守卫移入 softbreak 层（仅 lazy 续行标记），独立缩进段落不受影响|src/md_kx/renderer/_context.py:108|
|t007_test_f003|important|已修|补首行管道与独立缩进段落测试|tests/test_list_table.py:70|

### Round 3 (2026-08-12 15:30 UTC+8)

|finding_id|severity|status|rationale|fix_ref|
|------|------|------|------|------|
|t007_code_f006|important|已修|softbreak 标记加 _in_block(list_item) 条件，非列表上下文不标记|src/md_kx/renderer/_context.py:114|
|t007_code_f007|minor|已修|续行消费逻辑两处重复（list renderer 内，属既定结构）|src/md_kx/renderer/_context.py:522,618|
|t007_test_f004|critical|已修|补非列表上下文管道续行测试（独立段落/引用块）|tests/test_list_table.py:78|

### Round 4 (2026-08-12 15:45 UTC+8)

|finding_id|severity|status|rationale|fix_ref|
|------|------|------|------|------|
|t007_code_f008|important|已修|softbreak 标记条件精化为 paragraph 父= list_item（排除 blockquote 中间层）|src/md_kx/renderer/_context.py:114|
|t007_test_f005|critical|已修|补列表内块引用管道行测试|tests/test_list_table.py:85|

## 收尾报告

本 task 的 commit 用 `git log --grep <tid>` 查，不在此逐条记 SHA。

### 验收

- spec：[`spec.md`](spec.md)
- 结果：全部满足
- 证据：handoff.json 的 `ac_evidence` 逐条覆盖 AC-001~005（validate 通过、HTML 不变、转义保留、三态不变、多行项不变）

### Reviewer verdict

取自对应 review 报告**最后一条** `verdict:`（`full`：`review_code.md` + `review_test.md`；`single`：`review_general.md`；多轮追加时以末轮为准）。按**实际发生**的轮次列出（上限见 `task-work` `max_review_round`）；未开的轮次不写或写 N/A。收尾前最新一轮必须全部 PASS，历史 FAIL 保留。

`full`：

- Round 1 code：FAIL
- Round 1 test：FAIL
- Round 2 code：FAIL
- Round 2 test：FAIL
- Round 3 code：FAIL
- Round 3 test：FAIL
- Round 4 code：FAIL
- Round 4 test：FAIL
- Round 5 code：PASS
- Round 5 test：PASS

`single`：

- N/A（review_level=full）

遗留不在此列出——见 `docs/pending/todo/`，本文件处置表的 `fix_ref` 指向对应 `pNNN`。

### 结果摘要

修复列表项 lazy 表格行 validate 失败：softbreak 层识别「paragraph 直接位于 list_item 内 + 续行 `|` 开头」的 lazy 表格行，加 `\x00` 标记，列表 renderer 续行循环剥标记不缩进。嵌套表格、代码块、独立段落、非列表上下文、列表内块引用均不受影响（11 测试覆盖）。
