# 决策记录（ADR）

只记录已经确认、影响后续工作的非显然决策。追加新条目，不重写历史；决策被替代时，新条目通过“替代”字段引用旧编号。

每条结构：`## NNN 标题（YYYY-MM-DD）`，下接 `- 背景` / `- 选项` / `- 结论` / `- 替代` 四项；替代填旧编号，无则写「无」。

## 001 fork 改名 md_kx，插件协议随包名同步（2026-08-12）

- 背景：本仓库 fork 自 hukkin/mdformat，需改名为 md_kx（包名、CLI 命令、配置文件名均改，避免与 PyPI 官方 mdformat 冲突）。改名触及插件发现协议：entry_points group 原为 `mdformat.codeformatter` / `mdformat.parser_extension`。
- 选项：a) 保留 `mdformat.*` group，兼容既有 mdformat-* 第三方插件（mdformat-gfm 等）；b) 随包名改为 `md_kx.*` group，彻底改名但既有插件需重注册。
- 结论：b。用户明确要求"全都改"。fork 破坏性升级优先于兼容包袱；第三方插件如需适配，改其 entry_points group 注册到 `md_kx.*`。配置文件亦改为 `.md_kx.toml`。
- 替代：无

## 002 经 PyPI 发布，本地从 PyPI 更新（2026-09-14）

- 背景：仓库原在 WSL 开发，`scripts/update_global.sh` 直接 `uv tool install .` 本地打包安装，并带 `--win` 分支经 WSL 互操作更新 Windows 全局。迁到 macOS 后该脚本依赖 `wslpath` / `/mnt/c` 不可用，且本地打包安装绕过 CI 门禁、产物无法在其它机器复用。
- 选项：a) 保持本地构建 + 安装，按平台分叉（macOS/WSL/Windows）；b) 发布到 PyPI，本地 `uv tool install md-kx --reinstall` 从公网更新；c) GitHub Release 附件安装（`uv tool install <release-url>`）。
- 结论：b。包名 `md-kx`（PyPI 可用，`md_kx` 为无效发行名）。CI（`.github/workflows/tests.yaml` 的 `pypi-publish`）在 tag push 时构建并发布，linters/tests/allgood 全绿才发；认证用仓库 secret `PYPI_TOKEN`（PyPI API token，最低权限 `upload`）。本地 `scripts/update_global.sh` 简化为从 PyPI 安装，带 `--version` 回退。`_build_meta.py` 的 commit 注入只用于本地开发构建；PyPI 构建报告 `--commit=unknown`，改用 `--version` 校验。另加 `.github/workflows/build.yaml` 在 GitHub Release 时附带 wheel/sdist 作为镜像渠道。
- 替代：无
