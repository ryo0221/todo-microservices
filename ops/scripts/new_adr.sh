#!/usr/bin/env bash
set -euo pipefail

# 実行場所に依らず常にリポジトリルートを起点にする
cd "$(dirname "$0")/../.."

if [ $# -lt 1 ]; then
  echo "Usage: $0 <kebab-title or free text>"
  exit 1
fi

TITLE="$*"

# 拡張子 .md を剥がす（付けてもOK）
TITLE="${TITLE%.md}"

# ゆるい正規化：アンダースコア等→スペース
TITLE="${TITLE//_/ }"

# kebab化：英字小文字化 → 非英数はハイフン → 連続/先頭末尾ハイフン除去
KEBAB="$(
  echo "$TITLE" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'
)"

if [ -z "$KEBAB" ]; then
  echo "Error: slug becomes empty. Please provide a meaningful title."
  exit 1
fi

DIR="docs/adr"
mkdir -p "$DIR"

# ---------- ★ 重複判定は「番号抜き + kebab だけ」で行う ----------
# 例：docs/adr/0007-foo-bar.md が存在すれば重複とみなす
if ls "$DIR"/[0-9][0-9][0-9][0-9]-"$KEBAB".md >/dev/null 2>&1; then
  case "${ADR_DUPLICATE_STRATEGY:-error}" in
    error)
      echo "Duplicate ADR slug detected: '$KEBAB'. File already exists:"
      ls -1 "$DIR"/[0-9][0-9][0-9][0-9]-"$KEBAB".md
      echo "If you intend a follow-up, either choose a different title or set ADR_DUPLICATE_STRATEGY=version to append -vN."
      exit 2
      ;;
    version)
      # 既存の -vN を探索して次番号を採番（-v2, -v3 ...）
      base="$KEBAB"
      n=2
      while ls "$DIR"/[0-9][0-9][0-9][0-9]-"$base"-v$n.md >/dev/null 2>&1; do
        n=$((n+1))
      done
      KEBAB="$base-v$n"
      ;;
    *)
      echo "Unknown ADR_DUPLICATE_STRATEGY='${ADR_DUPLICATE_STRATEGY}'. Use 'error' or 'version'."
      exit 3
      ;;
  esac
fi

# 次の連番（0001 から）
LAST="$(ls "$DIR" | grep -E '^[0-9]{4}-' | sort | tail -n1 || true)"
if [ -z "$LAST" ]; then
  N=1
else
  N=$((10#$(echo "$LAST" | cut -d- -f1) + 1))
fi
NNNN=$(printf "%04d" "$N")

DATE=$(date +%F)
F="$DIR/$NNNN-$KEBAB.md"
TEMPLATE="$DIR/_template.md"

if [ -f "$F" ]; then
  echo "Unexpected: target file already exists: $F" >&2
  exit 4
fi

if [ -f "$TEMPLATE" ]; then
  sed -e "s/ADR-NNNN/ADR-$NNNN/g" \
      -e "s/<YYYY-MM-DD>/$DATE/g" \
      -e "s/<短いタイトル>/$TITLE/g" \
      "$TEMPLATE" > "$F"
else
  cat > "$F" <<EOF
# ADR-$NNNN: $TITLE

- **Status**: Draft
- **Date**: $DATE

## Context
## Decision
## Consequences
## Alternatives Considered
## Implementation notes (optional)
## Links
EOF
fi

echo "Created $F"
