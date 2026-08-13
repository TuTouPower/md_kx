---
tid: "t008"
slug: "table_three_output_styles"
title: "表格三种输出风格重定义"
status: "done"
branch: "t008_table_three_output_styles"
worktree: ""
review_level: "full"
diff_anchor: "d00127287022ce001bcacb946562d71a6c2dca45"
depends_on: ""
conflicts_with: ""
note: ""
---

# Task 过程总账

**front matter 是状态权威**，只经 `scripts/repo_template/task.py` 修改；`docs/tasks_index.json` 由它派生。reviewer 只写 `review_code.md` / `review_test.md` / `review_general.md`，不改本文件。

## 实施笔记

执行期边做边写：实际步骤、踩坑、中途决策、偏离 spec、关键验证、blocked 原因与用户放行的新轮次上限。

创建期不预测实施步骤——那时尚未读代码，预测必然失准。只记有追溯价值的内容，不写命令流水账。无事项时写：无

无

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

### Round 1 (2026-08-13 22:55 UTC+8)

|finding_id|severity|status|rationale|fix_ref|
|------|------|------|------|------|
|t008_code_f001|important|已修|pad 分隔行改为按列宽拉长（_separator_row 传 widths，_align_marker 全宽生成），冒号贴边不错位|src/md_kx/renderer/_context.py:759-775|
|t008_test_f001|important|已修|补宽列 pad 测试锚定 AC-004/005（拉长 + 冒号位置 + center 超 5）|tests/test_table.py::test_pad_wide_column_separator_stretches / test_pad_center_marker_stretches|
|t008_test_f002|minor|已修|转义竖线测试补「不拆列」行数断言与幂等断言|tests/test_table.py::test_escaped_pipe_preserved|
|t008_test_f003|minor|已修|test_table.py 顶部注释写明整体删除重写理由|tests/test_table.py:1-4|
|t008_test_f004|minor|已修|转义竖线测试改整行精确断言（列结构不变），废除行数断言|tests/test_table.py::test_escaped_pipe_preserved|
|t008_test_f005|minor|已修|补 right/纯文本宽列分隔段断言与宽列 pad 幂等断言|tests/test_table.py::test_pad_right_marker_stretches / test_pad_plain_wide_column / test_pad_wide_column_idempotent|

## 收尾报告

本 task 的 commit 用 `git log --grep <tid>` 查，不在此逐条记 SHA。

### 验收

- spec：[`spec.md`](spec.md)
- 结果：全部满足
- 证据：AC-001~012 全部经 `tests/test_table.py`（20 用例）与 CLI/配置用例验证，全量 4723 passed；`handoff.json` 的 `ac_evidence` 精确覆盖全部编号

### Reviewer verdict

取自对应 review 报告**最后一条** `verdict:`（`full`：`review_code.md` + `review_test.md`；`single`：`review_general.md`；多轮追加时以末轮为准）。按**实际发生**的轮次列出（上限见 `task-work` `max_review_round`）；未开的轮次不写或写 N/A。收尾前最新一轮必须全部 PASS，历史 FAIL 保留。

`full`：

- Round 1 code：FAIL（t008_code_f001 important：pad 分隔行未按列宽拉长，已修）
- Round 1 test：FAIL（t008_test_f001~f003：AC-004/005 无锚定、转义断言弱、删除理由缺失，已修）
- Round 2 code：PASS
- Round 2 test：PASS（披露 f004/f005 两条 minor，Round 3 修复闭环）
- Round 3 code：PASS
- Round 3 test：PASS

遗留不在此列出——见 `docs/pending/todo/`，本文件处置表的 `fix_ref` 指向对应 `pNNN`。

### 结果摘要

table_mode 重定义为 compact/spaced/pad 三风格（默认 spaced），删除 none；渲染器、CLI choices、配置校验、spec、guides、README 与测试同步更新；全量 4723 passed，黑盒 `md_kx --check README.md` 通过。
