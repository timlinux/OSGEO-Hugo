# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `osgeo` command dispatcher (`scripts/osgeo`): a single entry point for
  all project commands (`osgeo serve`, `osgeo build`, `osgeo verify`,
  `osgeo harvest`, …) that delegates to the existing Makefile targets
  and scripts. Available on `PATH` inside `nix develop` and standalone
  via `nix run .#osgeo -- <command>`.
- The `nix develop` shell now prints the full grouped `osgeo` command
  menu on entry.
- Every `osgeo` subcommand is also exposed as its own flake app, so
  `nix run .#serve`, `nix run .#build`, `nix run .#verify -- <args>`
  etc. work without entering the dev shell.
- `osgeo video`: records a scroll-through validation video of every
  page in the sitemap (Playwright screenshots stitched with ffmpeg,
  URL path burned into each frame). Also `nix run .#video` and
  `:SiteVideo` / `<leader>py` in Neovim. Node.js and ffmpeg are now
  provided by the flake dev shell.
- `osgeo video --theme <name>`: capture screenshots in any brand-pack
  theme; defaults to the `current` theme regardless of any theme
  previously persisted by the site's theme switcher.
- Shortcode gallery: `data/shortcodes.json` registry (71 blocks) drives
  the generated `/dev/blocks/` demo page (`osgeo blocks`), the Neovim
  `:InsertBlock` / `<leader>pa` snippet picker, and a lockstep drift
  check (`osgeo blocks --check`).
- `osgeo review`: interactive terminal review of the screenshots from
  `osgeo video`, rendered with chafa (sixel/kitty capable). Yes/no
  verdict per page with resume support; verdicts accumulate in
  `site-video/review-passed.txt` and `review-failed.txt` (the repair
  worklist), with `--restart` and `--failed-only` modes.
- The Neovim `<leader>p` which-key menu (`.nvim.lua`) now delegates to
  the `osgeo` dispatcher and gained `:Osgeo` (any subcommand, with
  completion), `:Harvest`, `:CheckLinks` and `:Preview` plus keymaps
  (`<leader>pm` menu, `<leader>pu` prompt, `<leader>ph` harvest,
  `<leader>pK` check-links, `<leader>pw` preview).
