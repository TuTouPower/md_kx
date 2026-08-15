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
#   bash scripts/update_global.sh            # 重新构建 + 更新 WSL 全局 + 验证
#   bash scripts/update_global.sh --no-build # 跳过构建，仅重装 WSL 全局
#   bash scripts/update_global.sh --win      # 更新 Windows 全局（无 Windows uv 时自动安装）
#   bash scripts/update_global.sh --win --no-build
#
# Windows 全局说明：Windows 侧由 uv tool 管理（命令 md_kx.exe），从 WSL 经
# 互操作调用 %USERPROFILE%\.local\bin\uv.exe，直接安装 dist/ 下已构建的
# py3-none-any wheel（UNC 路径 \\wsl.localhost\...），Windows 侧无需再构建。
# 若 Windows 未装 uv，脚本自动执行 install.ps1（装到 %USERPROFILE%\.local\bin）。
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

# 参数解析
NO_BUILD=false
TARGET=linux
for arg in "$@"; do
  case "$arg" in
    --no-build) NO_BUILD=true ;;
    --win) TARGET=win ;;
    *) echo "ERROR: 未知参数：$arg（支持 --no-build / --win）" >&2; exit 1 ;;
  esac
done

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: 找不到 uv 命令" >&2
  exit 1
fi

# 1. 注入构建 commit（写进 src/md_kx/_build_meta.py，gitignore；打包时随源码进包）
COMMIT="$(git rev-parse HEAD)"
echo "[1/4] 注入构建 commit id：$COMMIT"
printf '"""构建时生成，勿手改。"""\nBUILD_COMMIT = "%s"\n' "$COMMIT" > src/md_kx/_build_meta.py

# 2. 重新打包（sdist + wheel 到 dist/）
if ! "$NO_BUILD"; then
  echo "[2/4] 构建发行包（uv build → dist/）..."
  uv build
else
  echo "[2/4] 跳过构建（--no-build）"
fi

update_linux() {
  # 3. 更新全局命令
  echo "[3/4] 更新全局 md_kx（uv tool install . --reinstall）..."
  uv tool install . --reinstall

  # 4. 验证（防旧代码装回来）
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

  echo "OK：WSL 全局 md_kx 已更新为当前仓库代码（commit $COMMIT）"
}

update_win() {
  echo "[3/4] 目标：Windows 全局（uv tool，命令 md_kx.exe）"
  local ps="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
  local win_home win_uv_win win_uv win_md win_bin_win

  [[ -x "$ps" ]] || { echo "ERROR: 找不到 Windows PowerShell（互操作不可用？）" >&2; exit 1; }

  win_home="$("$ps" -NoProfile -Command '$env:USERPROFILE' | tr -d '\r')"
  [[ -n "$win_home" ]] || { echo "ERROR: 取不到 Windows 用户目录" >&2; exit 1; }
  win_uv_win="$win_home\\.local\\bin\\uv.exe"
  win_uv="$(wslpath -u "$win_uv_win")"
  win_md="$(wslpath -u "$win_home\\.local\\bin\\md_kx.exe")"
  win_bin_win="$win_home\\.local\\bin"

  # 3a. 确保 Windows uv 存在，否则自动安装
  #     不用 install.ps1：本机 PowerShell 加载不了 Microsoft.PowerShell.Security
  #     模块（Get-ExecutionPolicy 不可用）。改为直接下载 GitHub release zip。
  if [[ ! -x "$win_uv" ]]; then
    echo "[win] 未发现 Windows uv（$win_uv_win），自动安装（下载 GitHub release zip）..."
    local uv_zip
    uv_zip="$(mktemp --suffix=.zip)"
    curl -fsSL --retry 2 -o "$uv_zip" \
      "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip" \
      || { echo "ERROR: 下载 uv 失败" >&2; exit 1; }
    unzip -o -q "$uv_zip" -d "$win_bin" \
      || { echo "ERROR: 解压 uv 失败（需要 unzip）" >&2; exit 1; }
    rm -f "$uv_zip"
    [[ -x "$win_uv" ]] || { echo "ERROR: Windows uv 安装失败" >&2; exit 1; }
    echo "[win] uv 已装（$win_uv_win）。若新终端仍敲不了 uv，确认 Windows 用户 PATH 含 $win_bin_win"
  fi

  # 3b. 用 Windows uv 安装 dist/ 下 wheel（py3-none-any 跨平台，Windows 侧无需构建）
  local wheel wheel_win
  wheel="$(ls -t dist/md_kx-*.whl 2>/dev/null | head -1)"
  [[ -n "$wheel" ]] || { echo "ERROR: dist/ 无 wheel（去掉 --no-build 先构建）" >&2; exit 1; }
  wheel_win="$(wslpath -w "$REPO_ROOT/$wheel")"
  echo "[win] 安装：uv tool install $wheel_win --reinstall"
  "$win_uv" tool install "$wheel_win" --reinstall

  # 4. 验证（防旧代码装回来）
  echo "[4/4] 验证（Windows）..."
  [[ -x "$win_md" ]] || { echo "ERROR: Windows 无 md_kx.exe（$win_md）" >&2; exit 1; }
  echo -n "[win] "; "$win_md" --version | tr -d '\r'

  # commit id 校验
  local installed_commit
  installed_commit="$("$win_md" --commit | tr -d '\r')"
  if [[ "$installed_commit" != "$COMMIT" ]]; then
    echo "ERROR: Windows 安装 commit（$installed_commit）≠ 仓库 HEAD（$COMMIT）" >&2
    exit 1
  fi
  echo "commit id 校验通过：$installed_commit"

  # 行为冒烟：默认 spaced（Windows exe 输出为 CRLF，先归一）
  TMP="$(mktemp --suffix=.md)"
  trap 'rm -f "$TMP"' EXIT
  printf '| a | b |\n| --- | --- |\n| 1 | 2 |\n' > "$TMP"
  "$win_md" "$(wslpath -w "$TMP")"
  if ! tr -d '\r' < "$TMP" | grep -q '^| a | b |$'; then
    echo "ERROR: Windows 默认输出非 spaced" >&2
    exit 1
  fi

  # 已装文件内容检查：Windows uv 工具目录在 %APPDATA%\uv\tools（非 Linux 的 ~/.local/share）
  local win_appdata pkg_dir
  win_appdata="$("$ps" -NoProfile -Command '$env:APPDATA' | tr -d '\r')"
  pkg_dir="$(wslpath -u "$win_appdata\\uv\\tools\\md-kx\\Lib\\site-packages\\md_kx")"
  if ! grep -rq "_min_marker_width" "$pkg_dir/renderer/_context.py"; then
    echo "ERROR: Windows 已装代码不含 t008 特征（_min_marker_width）——仍是旧版" >&2
    exit 1
  fi

  # 让新 PowerShell/CMD 会话能直接敲 uv / md_kx（最佳努力，失败仅提示）
  if "$win_uv" tool update-shell >/dev/null 2>&1; then
    echo "[win] 已更新 shell PATH（新终端生效）"
  else
    echo "[win] 提示：Windows PATH 未含 $win_bin_win，新终端手动添加或执行 uv tool update-shell"
  fi

  echo "OK：Windows 全局 md_kx 已更新为当前仓库代码（commit $COMMIT）"
}

if [[ "$TARGET" == "win" ]]; then
  update_win
else
  update_linux
fi

