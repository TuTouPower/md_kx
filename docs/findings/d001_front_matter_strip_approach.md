# d001 front matter 预处理剥离方案

- 来源：s001
- 结论：mdformat 的 front matter 支持应采用「text() 入口预处理剥离」而非 markdown-it-py 插件。剥离函数识别文档开头闭合 `---` 块（连带其后空行一起剥离），正文走现有渲染管线，重组为 front matter + 渲染结果。markdown-it-py 无内置 front matter 插件，第三方需新依赖。
- 证据：`.scratch/experiment_fm*.py` 实测——现状 front matter 被解析成 thematic break + 标题破坏；剥离重组后逐字节保留，正文正常格式化；无闭合/非开头不剥离（行为不变），空 front matter、`|` 块值、正文含 `---`、前后空行边界均正确。
- 影响：t001 实现按此方案；剥离需兼顾 body 前导空行（连带剥离重组保留原空行）。
- 现状：有效
