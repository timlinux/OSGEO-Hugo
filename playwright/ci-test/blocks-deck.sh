#!/usr/bin/env bash
#
# Build the shortcode gallery slide deck: regenerate the gallery page,
# build and serve the site, capture each block card, and assemble
# artifacts/blocks-deck.pdf. Invoked as `osgeo blocks --pdf`.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PORT="${SITE_VIDEO_PORT:-1317}"
BASE_URL="http://127.0.0.1:${PORT}"

cd "$HERE"
# shellcheck source=playwright-path.sh
source ./playwright-path.sh

for tool in hugo node ffmpeg python3; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "❌ $tool not found. Run this from 'nix develop' at the repo root." >&2
        exit 1
    fi
done

if [[ -z "${CHROMIUM_PATH:-}" && -z "${PLAYWRIGHT_BROWSERS_PATH:-}" ]]; then
    for candidate in chromium chromium-browser google-chrome-stable google-chrome; do
        if command -v "$candidate" >/dev/null 2>&1; then
            CHROMIUM_PATH="$(command -v "$candidate")"
            export CHROMIUM_PATH
            echo "🧭 Using system browser: $CHROMIUM_PATH"
            break
        fi
    done
fi

echo "🧩 Regenerating the gallery page"
python3 "$ROOT/scripts/generate_blocks_demo.py"

echo "🏗️  Building the site for ${BASE_URL}"
( cd "$ROOT" && rm -f .hugo_build.lock && hugo --gc --config ./config.toml -b "$BASE_URL" --quiet )

server_pid=""
cleanup() {
    if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

echo "🌐 Serving ${ROOT}/public on port ${PORT}"
( cd "$ROOT/public" && exec python3 -m http.server "$PORT" ) >/dev/null 2>&1 &
server_pid=$!

for _ in $(seq 1 30); do
    if curl -sf -o /dev/null "$BASE_URL/dev/blocks/"; then break; fi
    sleep 0.5
done

echo "📸 Capturing block cards"
rm -rf "$ROOT/artifacts/block-cards"
BASE_URL="$BASE_URL" CARDS_DIR="$ROOT/artifacts/block-cards" node ./blocks-deck.mjs

echo "📑 Assembling the deck"
python3 "$ROOT/scripts/make_blocks_deck.py"
