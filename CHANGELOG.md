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
- The Neovim `<leader>p` which-key menu (`.nvim.lua`) now delegates to
  the `osgeo` dispatcher and gained `:Osgeo` (any subcommand, with
  completion), `:Harvest`, `:CheckLinks` and `:Preview` plus keymaps
  (`<leader>pm` menu, `<leader>pu` prompt, `<leader>ph` harvest,
  `<leader>pK` check-links, `<leader>pw` preview).
