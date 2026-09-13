#!/usr/bin/env bash
# md_kx 发布与全局命令更新脚本
#
# 场景区分（很重要）：
#   1. 开发测试：用仓库内 .venv（editable 安装，改动即时生效），不要跑本脚本。
#   2. 发布到公网：打 tag 后由 CI（.github/workflows/tests.yaml 的 pypi-publish）
#      经 PyPI Trusted Publishing 自动发布；本地更新只是从 PyPI 重装。
#
# 全局 `md_kx` 由 uv tool 安装（工具名 md-kx），与仓库 .venv 是两个独立环境。
#
# 用法：
#   bash scripts/update_global.sh            # 从 PyPI 安装/升级到最新发布版 + 验证
#   bash scripts/update_global.sh --version 1.2.3
#                                            # 安装指定版本（回退/锁定用）
#
# 发布流程（一次性配置见 docs/blueprint/decisions.md「PyPI 发布」）：
#   1. 提升版本：bump2version patch|minor|major（同时提交并生成 tag）
#   2. 推送：git push origin main --follow-tags
#   3. CI 在 tag push 时构建并发布到 PyPI
#   4. 本地更新：bash scripts/update_global.sh
#
# 说明：不在此处直接 `uv publish`，避免绕过 CI 门禁（linters/tests/allgood）
# 发布未经测试的产物。如需应急手动发布：uv build && uv publish
# （需 PyPI token：UV_PUBLISH_TOKEN 或 --token；推荐改用 Trusted Publishing）。
#
# 脚本自带验证门禁：--table-mode 合法值、默认风格、行为冒烟、
# 已装文件内容检查，任何一项不符即失败退出，不静默通过。

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# 参数解析
TARGET_VERSION=""
WANT_HELP=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      [[ $# -ge 2 ]] || { echo "ERROR: --version 需要参数" >&2; exit 1; }
      TARGET_VERSION="$2"
      shift 2
      ;;
    -h|--help) WANT_HELP=true; shift ;;
    *) echo "ERROR: 未知参数：$1（支持 --version X.Y.Z / -h）" >&2; exit 1 ;;
  esac
done

if "$WANT_HELP"; then
  awk 'NR>=2 { if ($0 ~ /^#/) { sub(/^# ?/, ""); print } else if ($0 ~ /^$/) { print } else { exit } }' "${BASH_SOURCE[0]}"
  exit 0
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: 找不到 uv 命令" >&2
  exit 1
fi

# 1. 确定要安装的版本（默认最新发布版）
SPEC="md-kx"
if [[ -n "$TARGET_VERSION" ]]; then
  SPEC="md-kx==$TARGET_VERSION"
fi
echo "[1/2] 从 PyPI 安装：${SPEC}（uv tool install --reinstall）..."
uv tool install --reinstall "$SPEC"

# 2. 验证
echo "[2/2] 验证..."
if ! command -v md_kx >/dev/null 2>&1; then
  echo "ERROR: 找不到全局 md_kx 命令（~/.local/bin 是否在 PATH？）" >&2
  exit 1
fi

INSTALLED_VERSION="$(md_kx --version)"
INSTALLED_COMMIT="$(md_kx --commit)"
echo "已装：${INSTALLED_VERSION}（PyPI 构建，无源码 commit，build commit=${INSTALLED_COMMIT}）"

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

# 行为冒烟：默认 spaced、compact 零空格（BSD/GNU mktemp 通用写法，不用 --suffix）
TMP="$(mktemp "${TMPDIR:-/tmp}/md_kx_smoke.XXXXXX")"
TMP_MD="$TMP.md"
mv "$TMP" "$TMP_MD"
trap 'rm -f "$TMP_MD"' EXIT
printf '| a | b |\n| --- | --- |\n| 1 | 2 |\n' > "$TMP_MD"
md_kx "$TMP_MD"
grep -q '^| a | b |$' "$TMP_MD" || {
  echo "ERROR: 默认输出非 spaced（表格仍旧行为？）" >&2
  exit 1
}
md_kx --table-mode compact "$TMP_MD"
grep -q '^|a|b|$' "$TMP_MD" || {
  echo "ERROR: compact 输出非零空格（仍是旧 t003 行为？）" >&2
  exit 1
}

# 已装文件内容检查：site-packages 中的实现须含 t008 特征
PKG_DIR="$(uv tool dir)/md-kx/lib/python*/site-packages/md_kx"
if ! grep -rq "_min_marker_width" $PKG_DIR/renderer/_context.py; then
  echo "ERROR: 已装代码不含 t008 特征（_min_marker_width）——仍是旧版" >&2
  exit 1
fi

echo "OK：全局 md_kx 已从 PyPI 更新（${INSTALLED_VERSION}）"
