# p001 支持 YAML front matter 不破坏

- 来源：用户提出（fork 二次开发需求）
- 内容：mdformat 默认不识别 YAML front matter，文档开头 `---` 被当分隔线（thematic break），front matter 内 `name:`/`description:` 被误解析成标题，整个 front matter 被破坏。期望：识别 front matter 边界但不格式化，原样保留输出，不触碰内部内容。验收标准：①输入带 YAML front matter 的文档，输出后 front matter 与输入完全一致（逐字节比对）；②无 front matter 的文档行为不变。官方无此能力，需内置实现，不依赖第三方插件。
- 处理：未开
