#!/bin/bash
# SessionStart フック: セッション開始時に git pull で最新のナレッジを取り込む
# - startup / resume のときだけ実行（compact / clear では何もしない）
# - --ff-only で衝突やマージプロンプトを避ける。失敗してもセッションは止めない
set -uo pipefail

INPUT="$(cat 2>/dev/null || true)"
SOURCE="$(printf '%s' "$INPUT" | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
case "${SOURCE:-startup}" in
  startup|resume) ;;
  *) exit 0 ;;
esac

cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" || exit 0

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"
if [ "$BRANCH" = "HEAD" ] || ! git rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
  echo "[session-start] 追跡ブランチがないため git pull をスキップしました（${BRANCH}）"
  exit 0
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "[session-start] 未コミットの変更があるため git pull をスキップしました"
  exit 0
fi

if OUT="$(GIT_TERMINAL_PROMPT=0 git pull --ff-only 2>&1)"; then
  echo "[session-start] git pull 完了: $(printf '%s' "$OUT" | tail -n 1)"
else
  echo "[session-start] git pull に失敗しました（セッションは続行します）: $(printf '%s' "$OUT" | tail -n 1)"
fi
exit 0
