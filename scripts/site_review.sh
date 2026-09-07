#!/usr/bin/env bash
# osgeo review — interactively review the screenshots captured by
# `osgeo video`, one page at a time, rendered in the terminal with
# chafa (which uses sixel / kitty / iterm graphics when the terminal
# supports them, falling back to unicode blocks otherwise).
#
# For every page: view its frames, then mark it [y] pass or [n] fail.
# Results accumulate in:
#
#   site-video/review-passed.txt   pages confirmed OK
#   site-video/review-failed.txt   pages needing repair (the worklist)
#
# Progress is saved after every answer, so you can quit with [q] and
# resume later — already-reviewed pages are skipped. Options:
#
#   --restart      forget previous answers and review everything again
#   --failed-only  re-review only the pages currently marked failed
#
set -euo pipefail

if [[ -z "${OSGEO_HUGO_ROOT:-}" ]]; then
  if root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    OSGEO_HUGO_ROOT="$root"
  else
    OSGEO_HUGO_ROOT="$PWD"
  fi
fi
cd "$OSGEO_HUGO_ROOT"

FRAMES_DIR="site-video/frames"
MANIFEST="$FRAMES_DIR/manifest.tsv"
PASSED_FILE="site-video/review-passed.txt"
FAILED_FILE="site-video/review-failed.txt"

RESTART=0
FAILED_ONLY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --restart) RESTART=1; shift ;;
    --failed-only) FAILED_ONLY=1; shift ;;
    *) echo "Unknown option: $1 (supported: --restart, --failed-only)" >&2; exit 1 ;;
  esac
done

if [[ ! -f "$MANIFEST" ]]; then
  echo "❌ No captured frames found ($MANIFEST missing)." >&2
  echo "   Run 'osgeo video' first to capture the site." >&2
  exit 1
fi
if ! command -v chafa >/dev/null 2>&1; then
  echo "❌ chafa not found. Run this from 'nix develop' at the repo root." >&2
  exit 1
fi
if [[ ! -t 0 || ! -t 1 ]]; then
  echo "❌ osgeo review is interactive and needs a terminal." >&2
  exit 1
fi

if [[ "$RESTART" -eq 1 ]]; then
  rm -f "$PASSED_FILE" "$FAILED_FILE"
fi
touch "$PASSED_FILE" "$FAILED_FILE"

# Pages in capture order; frames per page looked up from the manifest.
mapfile -t pages < <(awk -F'\t' '!seen[$2]++ {print $2}' "$MANIFEST")

if [[ "$FAILED_ONLY" -eq 1 ]]; then
  mapfile -t pages < <(cat "$FAILED_FILE")
  : > "$FAILED_FILE"
fi

declare -A reviewed
while IFS= read -r line; do reviewed["$line"]=1; done < "$PASSED_FILE"
while IFS= read -r line; do reviewed["$line"]=1; done < "$FAILED_FILE"

summary() {
  local passed failed
  passed="$(wc -l < "$PASSED_FILE")"
  failed="$(wc -l < "$FAILED_FILE")"
  echo ""
  echo "-----------------------------------------------------------------"
  echo "🌈 Review progress: ${passed} passed, ${failed} failed, $(( ${#pages[@]} - passed - failed )) remaining of ${#pages[@]} pages"
  if [[ "$failed" -gt 0 ]]; then
    echo ""
    echo "🪛 Pages needing repair ($FAILED_FILE):"
    sed 's/^/  /' "$FAILED_FILE"
  fi
  echo "-----------------------------------------------------------------"
}

total="${#pages[@]}"
count=0
for page in "${pages[@]}"; do
  count=$(( count + 1 ))
  if [[ -n "${reviewed[$page]:-}" ]]; then
    continue
  fi

  mapfile -t frames < <(awk -F'\t' -v p="$page" '$2 == p {print $1}' "$MANIFEST")
  if [[ "${#frames[@]}" -eq 0 ]]; then
    echo "⚠ No frames for $page, skipping" >&2
    continue
  fi

  idx=0
  while true; do
    rows=$(( $(tput lines) - 4 ))
    cols=$(tput cols)
    clear
    chafa --size "${cols}x${rows}" "${frames[$idx]}"
    printf '%s  —  page %d/%d, frame %d/%d\n' \
      "$page" "$count" "$total" "$(( idx + 1 ))" "${#frames[@]}"
    printf '[y] pass  [n] fail  [f/b] next/prev frame  [o] open in browser  [q] quit+summary : '
    read -rsn1 key
    echo ""
    case "$key" in
      y | Y)
        echo "$page" >> "$PASSED_FILE"
        break
        ;;
      n | N)
        echo "$page" >> "$FAILED_FILE"
        break
        ;;
      f | ' ')
        idx=$(( (idx + 1) % ${#frames[@]} ))
        ;;
      b)
        idx=$(( (idx - 1 + ${#frames[@]}) % ${#frames[@]} ))
        ;;
      o)
        xdg-open "http://localhost:1313${page}" >/dev/null 2>&1 \
          || open "http://localhost:1313${page}" >/dev/null 2>&1 \
          || echo "Could not open a browser (is the dev server running?)"
        ;;
      q | Q)
        summary
        exit 0
        ;;
    esac
  done
done

summary
echo "✅ Review complete."
