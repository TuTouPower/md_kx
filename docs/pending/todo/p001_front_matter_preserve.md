# p001 支持 YAML front matter 不破坏

- 来源：用户提出（fork 二次开发需求 1）
- 内容：mdformat 默认不识别 YAML front matter，文档开头 `---` 被当分隔线，front matter 内 `name:`/`description:` 被误解析成标题致内容破坏。期望：文档开头 YAML front matter 原样保留，不格式化、不破坏、不变更。官方无此能力，需内置实现，不依赖第三方插件。
- 处理：未开
