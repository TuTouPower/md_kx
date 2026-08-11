# Task spec

## 背景

mdformat 默认不识别 YAML front matter。文档开头的 `---` 被当作分隔线（thematic break），front matter 内 `name:`/`description:` 被误解析成标题，整个 front matter 被破坏。仓库内 12 个带 front matter 的 skill 文档全部受损。用户提出二次开发需求：识别 front matter 边界但不格式化，原样保留。

## 契约区

### 范围

- 内置 front matter 识别（不依赖第三方插件），识别文档开头的 YAML front matter 块
- front matter 内容原样输出，不进入格式化管线

### 非范围

- 不解析/校验 front matter 内部 YAML 语义
- 不提供 front matter 的配置开关（本 task 固定识别并保留）

### 验收标准

<!-- 规范（门禁必留，不得删除） -->
只写用户或调用方可观察行为，每条可独立验证。普通版本号、底层库和目录结构不作为验收标准；需要长期约束后续工作的技术选择写入 `docs/blueprint/decisions.md`。
<!-- /规范 -->

<!-- 规范（门禁必留，不得删除） -->
需真实部署或人工环境才能验证的条目加 `[deploy]` 前缀，标明 agent 无法自证。
<!-- /规范 -->

<!-- 规范（门禁必留，不得删除） -->
每条 AC 条目带稳定编号 `AC-NNN`（三位十进制、task 内从 001 顺序编号、唯一、删除不复用）；收尾时 `handoff.json` 的 `ac_evidence` 须精确覆盖本区全部编号。编号约定见 `docs/blueprint/conventions.md`。
<!-- /规范 -->

- [ ] AC-001：文档开头为 YAML front matter（`---` 包裹，含 `name:`/`description:` 等键值）时，mdformat 输出后 front matter 与输入完全一致（逐字节比对）。
- [ ] AC-002：带 front matter 文档中，front matter 之后的正文内容照常按现有规则格式化。
- [ ] AC-003：无 front matter 的文档（普通 `---` 分隔线、纯正文）行为与格式化结果不变。
- [ ] AC-004：front matter 内部内容（含未格式化代码样式的键值、特殊字符）不被格式化或改写。

### 可测试性声明

<!-- 规范（门禁必留，不得删除） -->
逐条说明哪些 AC 不可自动测试及原因；全部可测则写「全部 AC 可自动测试」。
<!-- /规范 -->

- 全部 AC 可自动测试。

## 上下文区

- 来源：p001（核实日期 2026-08-11；源码 `src/mdformat/` 无 front matter/yaml 处理，确认未实现；pending 条目含用户确认的验收标准）

### 有意不测

<!-- 规范（门禁必留，不得删除） -->
已判定不写测试的分支与原因。reviewer 不得据此出 blocking finding。无则写「无」。
<!-- /规范 -->

- 无。

### 测试策略

<!-- 规范（门禁必留，不得删除） -->
mock 边界、fixture 来源、断言目标。无特殊约定写「按项目默认」。
<!-- /规范 -->

- 按项目默认：`tests/` 下新增测试，构造带 front matter 的输入字符串，`mdformat.text()` 输出后逐字节比对 front matter 部分，断言正文格式化生效。

### 未知契约清单

<!-- 规范（门禁必留，不得删除） -->
尚未核实的外部 endpoint、API 形态、数据结构、第三方行为须分类标记；核实后删除标记，改为结论并注明验证方式。无则写「无」。
<!-- /规范 -->

- front matter 识别实现方式：已验证（s001，2026-08-11）。采用 `text()` 入口预处理剥离方案（剥离文档开头闭合 `---` 块连带其后空行，正文走管线，重组）；markdown-it-py 无内置插件，插件方案需新依赖故弃。详见 `docs/findings/d001`。

### 风险与回退

- 风险：front matter 识别与普通 `---` 分隔线歧义；识别逻辑误吞正文开头分隔线导致格式化跳过正文。
- 回退：AC-003 保证无 front matter 文档行为不变；识别失败场景由该 AC 测试覆盖，失败则回退改动重新设计判定条件。

### 依赖与约束

- 无前置依赖；不引入新依赖；不破坏现有 CommonMark 合规性。

### Finalization 时更新的 blueprint

- `docs/blueprint/domain.md`：如有新领域概念（front matter 识别边界）补充术语表。
