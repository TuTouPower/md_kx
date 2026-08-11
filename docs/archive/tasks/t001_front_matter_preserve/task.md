---
tid: "t001"
slug: "front_matter_preserve"
title: "支持 YAML front matter 识别但不格式化"
status: "done"
branch: "t001_front_matter_preserve"
worktree: ""
review_level: "full"
diff_anchor: "2586c5769c2e76c40010c1b6771922611f160b0d"
depends_on: ""
conflicts_with: ""
note: "来自 pending p001；fork 二次开发需求 1"
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

### Round 1 (2026-08-11 22:10 UTC+8)

|finding_id|severity|status|rationale|fix_ref|
|------|------|------|------|------|
|t001_code_f001|important|已修|_strip_front_matter 判定改 `rstrip("\\r\\n")` 兼容 CRLF；CRLF front matter 逐字节保留|src/mdformat/_api.py:22|
|t001_test_f001|important|已修|AC-003 测试改真实断言（分隔线不被误解析成标题），去掉恒真幂等断言|tests/test_front_matter.py:29|
|t001_test_f002|important|已修|新增 CRLF 变体测试覆盖 AC-001/AC-004；判定兼容 CRLF|tests/test_front_matter.py:57|

### Round 2 (2026-08-11 22:30 UTC+8)

|finding_id|severity|status|rationale|fix_ref|
|------|------|------|------|------|
|t001_test_f004|critical|已修|file() 路径 CRLF 写回不损坏：新增 test_file_crlf_end_of_line_keep；LF 归一修复 \r\r\n|src/mdformat/_api.py:32|
|t001_test_f003|important|已修|浅 YAML 判定：front matter 块须含 key: value 行，误吞边界（空块/标题）走基线渲染；新增 test_blank_separator_not_front_matter|src/mdformat/_api.py:30|

## 收尾报告

本 task 的 commit 用 `git log --grep <tid>` 查，不在此逐条记 SHA。

### 验收

- spec：[`spec.md`](spec.md)
- 结果：全部满足
- 证据：handoff.json 的 `ac_evidence` 逐条覆盖 AC-001~004（LF/CRLF front matter 逐字节保留、正文格式化、误吞边界、file() 写回）

### Reviewer verdict

取自对应 review 报告**最后一条** `verdict:`（`full`：`review_code.md` + `review_test.md`；`single`：`review_general.md`；多轮追加时以末轮为准）。按**实际发生**的轮次列出（上限见 `task-work` `max_review_round`）；未开的轮次不写或写 N/A。收尾前最新一轮必须全部 PASS，历史 FAIL 保留。

`full`：

- Round 1 code：FAIL
- Round 1 test：FAIL
- Round 2 code：FAIL
- Round 2 test：FAIL
- Round 3 code：PASS
- Round 3 test：PASS

`single`：

- N/A（review_level=full）

遗留不在此列出——见 `docs/pending/todo/`，本文件处置表的 `fix_ref` 指向对应 `pNNN`。

### 结果摘要

mdformat 现已识别文档开头 YAML front matter（含 `key: value` 键值、LF/CRLF 行尾）并原样保留，正文照常格式化；普通 `---` 分隔线与误吞边界行为不变。

- 一句话；无额外说明可写「见上」
