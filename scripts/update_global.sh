#!/usr/bin/env bash
# md_kx 全局命令更新脚本
#
# 场景区分（很重要）：
#   1. 开发测试：用仓库内 .venv（editable 安装，改动即时生效），不要跑本脚本。
#   2. 开发完成 → 全局更新：跑本脚本，重新打包并更新全局 `md_kx` 命令。
#
# 全局 `md_kx` 由 uv tool 安装（~/.local/bin/md_kx，工具名 md-kx），
# 与仓库 .venv 是两个独立环境。改完代码必须重装全局才会生效。
#
# 用法：
#   bash scripts/update_global.sh            # 重新构建 + 更新全局 + 验证
#   bash scripts/update_global.sh --no-build # 跳过构建，仅重装全局
#
# 关键坑（项目文档已记录）：必须用 `uv tool install . --reinstall`
# （implies --refresh）。`--force` 会命中 uv 构建缓存装入旧代码——
# 现象是版本号不变但改动不生效。
#
# 脚本自带验证门禁：--table-mode 合法值、默认风格、行为冒烟、
# 已装文件内容检查，任何一项不符即失败退出，不静默通过。

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: 找不到 uv 命令" >&2
  exit 1
fi

# 1. 注入构建 commit（写进 src/md_kx/_build_meta.py，gitignore；打包时随源码进包）
COMMIT="$(git rev-parse HEAD)"
echo "[1/4] 注入构建 commit id：$COMMIT"
printf '"""构建时生成，勿手改。"""\nBUILD_COMMIT = "%s"\n' "$COMMIT" > src/md_kx/_build_meta.py

# 2. 重新打包（sdist + wheel 到 dist/）
if [[ "${1:-}" != "--no-build" ]]; then
  echo "[2/4] 构建发行包（uv build → dist/）..."
  uv build
else
  echo "[2/4] 跳过构建（--no-build）"
fi

# 3. 更新全局命令
echo "[3/4] 更新全局 md_kx（uv tool install . --reinstall）..."
uv tool install . --reinstall

# 3. 验证（防旧代码装回来）
echo "[4/4] 验证..."
if ! command -v md_kx >/dev/null 2>&1; then
  echo "ERROR: 找不到全局 md_kx 命令（~/.local/bin 是否在 PATH？）" >&2
  exit 1
fi

md_kx --version

HELP="$(md_kx --help)"
HELP_ONE="$(printf '%s' "$HELP" | tr '\n' ' ')"
if ! grep -q -- '{compact,spaced,pad}' <<<"$HELP"; then
  echo "ERROR: --table-mode 合法值不正确（应含 {compact,spaced,pad}）" >&2
  exit 1
fi
if grep -q '{none' <<<"$HELP"; then
  echo "ERROR: --table-mode 仍列 none（t008 后应删除）" >&2
  exit 1
fi
if ! grep -qE 'default:[[:space:]]+spaced' <<<"$HELP_ONE"; then
  echo "ERROR: --table-mode 默认值不是 spaced" >&2
  exit 1
fi

# 行为冒烟：默认 spaced、compact 零空格
TMP="$(mktemp --suffix=.md)"
trap 'rm -f "$TMP"' EXIT
printf '| a | b |\n| --- | --- |\n| 1 | 2 |\n' > "$TMP"
md_kx "$TMP"
grep -q '^| a | b |$' "$TMP" || {
  echo "ERROR: 默认输出非 spaced（表格仍旧行为？）" >&2
  exit 1
}
md_kx --table-mode compact "$TMP"
grep -q '^|a|b|$' "$TMP" || {
  echo "ERROR: compact 输出非零空格（仍是旧 t003 行为？）" >&2
  exit 1
}

# 已装文件内容检查：site-packages 中的实现须含 t008 特征
PKG_DIR="$HOME/.local/share/uv/tools/md-kx/lib/python*/site-packages/md_kx"
if ! grep -rq "_min_marker_width" $PKG_DIR/renderer/_context.py; then
  echo "ERROR: 已装代码不含 t008 特征（_min_marker_width）——仍是旧版" >&2
  exit 1
fi

# commit id 校验：安装包内注入的 commit 必须等于仓库当前 HEAD
INSTALLED_COMMIT="$(md_kx --commit)"
if [[ "$INSTALLED_COMMIT" != "$COMMIT" ]]; then
  echo "ERROR: 安装包 commit（$INSTALLED_COMMIT）≠ 仓库 HEAD（$COMMIT）" >&2
  exit 1
fi
echo "commit id 校验通过：$INSTALLED_COMMIT"

echo "OK：全局 md_kx 已更新为当前仓库代码（commit $COMMIT）"
