#!/usr/bin/env bash
#
# Record a validation video of the whole site: build with Hugo, serve it
# statically, screenshot every page in the sitemap (scroll-through, with
# the URL path burned into each frame), then stitch the frames into an
# mp4 with ffmpeg. Invoked as `osgeo video`.
#
#   ./site-video.sh                 # whole site, full pages top to bottom
#   ./site-video.sh --limit 10      # only the first 10 pages (quick check)
#   ./site-video.sh --fps 4         # faster playback
#   ./site-video.sh --max-steps 3   # cap scroll frames per page (0 = full page)
#
# Output: site-video/site.mp4 plus site-video/frames/ (with manifest.tsv
# mapping each frame back to its page path).
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PORT="${SITE_VIDEO_PORT:-1316}"
BASE_URL="http://127.0.0.1:${PORT}"
OUT_DIR="$ROOT/site-video"
FRAMES_DIR="$OUT_DIR/frames"
FPS="${VIDEO_FPS:-2}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --limit) export VIDEO_LIMIT="$2"; shift 2 ;;
        --fps) FPS="$2"; shift 2 ;;
        --max-steps) export VIDEO_MAX_STEPS="$2"; shift 2 ;;
        *) echo "Unknown option: $1 (supported: --limit N, --fps N, --max-steps N)" >&2; exit 1 ;;
    esac
done

cd "$HERE"
# shellcheck source=playwright-path.sh
source ./playwright-path.sh

for tool in hugo node ffmpeg; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "❌ $tool not found. Run this from 'nix develop' at the repo root." >&2
        exit 1
    fi
done

echo "🏗️  Building the site for ${BASE_URL}"
( cd "$ROOT" && rm -f .hugo_build.lock && hugo --gc --config ./config.toml -b "$BASE_URL" --quiet )

server_pid=""
cleanup() {
    if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
        echo "🧹 Stopping server (pid ${server_pid})"
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

echo "🌐 Serving ${ROOT}/public on port ${PORT}"
( cd "$ROOT/public" && exec python3 -m http.server "$PORT" ) >/dev/null 2>&1 &
server_pid=$!

for _ in $(seq 1 30); do
    if curl -sf -o /dev/null "$BASE_URL/"; then break; fi
    sleep 0.5
done
if ! curl -sf -o /dev/null "$BASE_URL/"; then
    echo "❌ Server did not come up on ${BASE_URL}" >&2
    exit 1
fi

echo "📸 Capturing page screenshots"
rm -rf "$FRAMES_DIR"
mkdir -p "$FRAMES_DIR"
BASE_URL="$BASE_URL" FRAMES_DIR="$FRAMES_DIR" node ./capture-site.mjs

echo "🎬 Stitching frames into ${OUT_DIR}/site.mp4 (${FPS} fps)"
ffmpeg -y -loglevel error \
    -framerate "$FPS" \
    -i "$FRAMES_DIR/frame_%06d.png" \
    -c:v libx264 -pix_fmt yuv420p \
    "$OUT_DIR/site.mp4"

echo ""
echo "✅ Done: ${OUT_DIR}/site.mp4"
echo "   Frame → page map: ${FRAMES_DIR}/manifest.tsv"
