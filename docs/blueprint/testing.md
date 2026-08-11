# 测试

mdformat 门禁命令：

- doctor：环境前置检查 → `python3 -m pytest tests -q --collect-only`（依赖可导入即视为就绪）
- test：日常测试（红/绿）→ `python3 -m pytest tests -q`
- blackbox：黑盒验证 → `python3 -m mdformat --check README.md && python3 -m mdformat --check docs/index.md`

## Schema / codegen 验证

无。mdformat 无 schema、migration 或 codegen 流程。

普通 merge 不自动执行生产 migration、部署或数据操作；此类动作遵循项目发布流程。

## 门禁类别清单

|类别|必须覆盖|常见盲区|
|------|------|------|
|单元测试|`python3 -m pytest tests -q` 通过|mock 掉被测逻辑、断言过弱（假绿）|
|生产代码类型检查|`mypy src/ tests/` 通过（tox -e mypy 同款）|类型错误被测试框架转译忽略|
|测试代码类型检查|`mypy src/ tests/` 覆盖（pyproject 对 `tests.*` 放宽 untyped）|测试 mock 类型不匹配、长期积累无人修|
|lint|`pre-commit run -a` 通过（black / isort / flake8 / docformatter）|只查改动文件、存量无限积累|
|生产构建|`python -m build` 通过（CI pypi-publish 步骤同款）|codegen 与 schema 不同步、RSC 边界、server-only 导入|
