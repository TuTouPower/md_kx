# Spike report

## 问题

front matter 识别应如何接入 mdformat：markdown-it-py 插件 vs 预处理剥离？需不引入新依赖。

## 成功判据

- 找到不引新依赖、能逐字节保留 front matter、正文正常格式化的最简接入路径
- 边界情况（无闭合、非开头、空 front matter、正文含 `---`、前后空行）行为明确

## 尝试

- 方案 A：markdown-it-py front matter 插件。确认 markdown-it-py 无内置 front matter 插件，需第三方 `markdown-it-front-matter`（新依赖），违反「不引入新依赖」约束，弃。
- 方案 B：预处理剥离。在 `mdformat._api.text()` 入口检测文档开头闭合 `---` 块，剥离 front matter（连带其后空行），正文走现有管线，重组。实测：
  - 现状：front matter 被解析成 thematic break + `## name: x description: y` 标题，完全破坏
  - 剥离后：front matter 逐字节保留，正文正常格式化，重组成功
  - 边界：无闭合/非开头不剥离（行为不变）；空 front matter、含 `|` 块值、正文含 `---` 均正确处理；fm 后空行连带剥离后重组保留原空行

## 证据

- 实验脚本与输出见 `.scratch/experiment_fm*.py`（验证：现状破坏、剥离重组、边界、空行保留）

## 结论

采用预处理剥离方案。`text()` 入口剥离，仅识别文档开头闭合 `---` 块，连带其后空行剥离；正文走管线；重组 fm + 渲染结果。不引新依赖，逐字节保留 front matter，正文正常格式化。

## 是否采纳

- 决定：是
- 理由：最简、无新依赖、边界行为已验证
- 后续 task：t001
