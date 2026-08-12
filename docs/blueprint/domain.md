# 领域模型

> 初稿：2026-08-11 按 mdformat 1.0.0 领域概念填写，任务完结时同步更新。

## 概念 / 术语表（中英对照，命名以此为准）

|英文|中文|说明|
|------|------|------|
|Markdown|Markdown|轻量标记语言，md_kx 处理的目标文本格式|
|CommonMark|CommonMark|Markdown 的标准规范；md_kx 基于其实现解析与渲染|
|token|token|markdown-it-py 解析产物，构成中间表示（AST）|
|renderer|渲染器|把 token 流按样式规则重排为 Markdown 文本的组件|
|wrap|换行|`--wrap` 选项控制段落文本折行宽度（keep 或 0–999）|
|number|列表编号|`--number` 选项让有序列表连续编号|
|quote|引用|`--quote` 选项格式化段落引用样式|
|plugin|插件|第三方扩展包（`md_kx-*`），通过 `md_kx.plugins` 注册|
|pre-commit hook|pre-commit 钩子|md_kx 以 pre-commit 插件形式集成进代码检查流程|

## 领域规则

- 格式化目标：输入已合规的 Markdown 输出保持稳定（幂等）。
- 解析与渲染分离：md_kx 不修改 markdown-it-py，只消费其 token 流。
