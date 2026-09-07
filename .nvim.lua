-- OSGeo Hugo Website nvim project configuration
-- Auto-sourced by nvim when exrc is enabled, or source manually with:
--   :source .nvim.lua
--
-- All project commands delegate to the `osgeo` dispatcher
-- (scripts/osgeo) so nvim, the CLI, `nix run .#<cmd>` and the
-- `nix develop` menu all share one implementation.
--
-- Workflow:
--   1. Start Hugo dev server: <leader>ps (or :HugoServer → osgeo serve)
--   2. Open browser: <leader>po
--   3. Edit content, preview changes
--   4. Format files: <leader>pf
--   5. Build for production: <leader>pb
--   6. Verify content vs osgeo.org: <leader>pv (or :VerifyContent)
--   7. Run Playwright e2e tests: <leader>pt (or :E2eTest)
--   Any subcommand: <leader>pu (or :Osgeo <command>), menu: <leader>pm

-- Guard against re-sourcing
if vim.g.osgeo_hugo_loaded then
  return
end
vim.g.osgeo_hugo_loaded = true

-- ============================================================================
-- osgeo dispatcher helpers
-- ============================================================================

-- Build an `osgeo <args>` command line. Falls back to the flake app when
-- nvim was not started from inside `nix develop`.
local function osgeo_cmd(args)
  if vim.fn.executable('osgeo') == 1 then
    return 'osgeo ' .. args
  end
  return 'nix run .#osgeo -- ' .. args
end

-- Run an osgeo subcommand in a terminal buffer (for long-running tasks).
local function osgeo_term(args)
  vim.cmd('terminal ' .. osgeo_cmd(args))
end

-- Run an osgeo subcommand as a one-shot shell command.
local function osgeo_shell(args)
  vim.cmd('!' .. osgeo_cmd(args))
end

-- Subcommand list for :Osgeo completion. Keep in step with scripts/osgeo.
local osgeo_commands = {
  'serve', 'drafts', 'preview', 'open',
  'build', 'clean',
  'format', 'format-check', 'lint', 'lint-md', 'lint-html',
  'pre-commit', 'verify', 'test', 'video', 'review',
  'new-page', 'new-post', 'harvest', 'check-links',
  'deploy', 'revert-deploy', 'help',
}

-- ============================================================================
-- User Commands
-- ============================================================================

-- Generic dispatcher: :Osgeo <subcommand> [args], with completion.
vim.api.nvim_create_user_command('Osgeo', function(opts)
  local args = opts.args ~= '' and opts.args or 'help'
  osgeo_term(args)
end, {
  nargs = '*',
  complete = function(arglead)
    return vim.tbl_filter(function(c)
      return vim.startswith(c, arglead)
    end, osgeo_commands)
  end,
  desc = 'Run an osgeo project command',
})

-- Hugo commands
vim.api.nvim_create_user_command('HugoServer', function()
  osgeo_term('serve')
end, { desc = 'Start Hugo development server (osgeo serve)' })

vim.api.nvim_create_user_command('HugoServerDrafts', function()
  osgeo_term('drafts')
end, { desc = 'Start Hugo server with drafts (osgeo drafts)' })

vim.api.nvim_create_user_command('HugoBuild', function()
  -- Dev build has no osgeo subcommand (osgeo build is production).
  vim.cmd('!hugo --config config.toml,config/config.dev.toml')
end, { desc = 'Build site (development)' })

vim.api.nvim_create_user_command('HugoBuildProd', function()
  osgeo_shell('build')
end, { desc = 'Build site (production, osgeo build)' })

vim.api.nvim_create_user_command('HugoNew', function(opts)
  if opts.args ~= '' then
    vim.cmd('!hugo new ' .. opts.args)
  else
    vim.notify('Usage: :HugoNew <path/to/content.md>', vim.log.levels.WARN)
  end
end, { nargs = '?', desc = 'Create new content' })

vim.api.nvim_create_user_command('Preview', function()
  osgeo_term('preview')
end, { desc = 'Serve the nix-built site on :8000 (osgeo preview)' })

-- Formatting commands
vim.api.nvim_create_user_command('PrettierFormat', function()
  -- Single-file formatting stays direct; osgeo format runs the full tree.
  local file = vim.fn.expand('%')
  vim.cmd('!npx prettier --write ' .. file)
  vim.cmd('edit!')
end, { desc = 'Format current file with Prettier' })

vim.api.nvim_create_user_command('PrettierFormatAll', function()
  osgeo_shell('format')
end, { desc = 'Format all content and theme files (osgeo format)' })

vim.api.nvim_create_user_command('PrettierCheck', function()
  osgeo_shell('format-check')
end, { desc = 'Check formatting with Prettier (osgeo format-check)' })

-- Linting commands
vim.api.nvim_create_user_command('MarkdownLint', function()
  osgeo_shell('lint-md')
end, { desc = 'Lint Markdown files (osgeo lint-md)' })

vim.api.nvim_create_user_command('HtmlHint', function()
  osgeo_shell('lint-html')
end, { desc = 'Lint HTML output (osgeo lint-html)' })

-- Git/Pre-commit commands
vim.api.nvim_create_user_command('PreCommit', function()
  osgeo_shell('pre-commit')
end, { desc = 'Run pre-commit hooks (osgeo pre-commit)' })

vim.api.nvim_create_user_command('GitStatus', function()
  vim.cmd('!git status')
end, { desc = 'Show git status' })

vim.api.nvim_create_user_command('GitDiff', function()
  vim.cmd('terminal git diff')
end, { desc = 'Show git diff' })

-- Make commands (low-level escape hatch; osgeo is the front door)
vim.api.nvim_create_user_command('Make', function(opts)
  if opts.args ~= '' then
    vim.cmd('!make ' .. opts.args)
  else
    vim.cmd('!make help')
  end
end, { nargs = '?', desc = 'Run make command' })

vim.api.nvim_create_user_command('MakeBuild', function()
  vim.cmd('!make build')
end, { desc = 'Run make build' })

vim.api.nvim_create_user_command('MakeDev', function()
  vim.cmd('terminal make hugo-run-dev')
end, { desc = 'Run make hugo-run-dev' })

-- Testing
vim.api.nvim_create_user_command('E2eTest', function(opts)
  local args = opts.args ~= '' and (' ' .. opts.args) or ''
  osgeo_term('test' .. args)
end, { nargs = '*', desc = 'Run the Playwright end-to-end suite (osgeo test)' })

vim.api.nvim_create_user_command('E2eTestUI', function()
  osgeo_term('test --ui')
end, { desc = 'Run the Playwright suite in UI mode' })

vim.api.nvim_create_user_command('SiteVideo', function(opts)
  local args = opts.args ~= '' and (' ' .. opts.args) or ''
  osgeo_term('video' .. args)
end, { nargs = '*', desc = 'Record a validation video of every page (osgeo video)' })

vim.api.nvim_create_user_command('SiteReview', function(opts)
  local args = opts.args ~= '' and (' ' .. opts.args) or ''
  osgeo_term('review' .. args)
end, { nargs = '*', desc = 'Review captured screenshots interactively (osgeo review)' })

-- Content verification (cross-check local Hugo content against upstream
-- osgeo.org and optionally emit an nginx redirect map).
vim.api.nvim_create_user_command('VerifyContent', function(opts)
  local args = opts.args ~= '' and (' ' .. opts.args) or ''
  osgeo_term('verify' .. args)
end, { nargs = '*', desc = 'Verify content against upstream osgeo.org (osgeo verify)' })

vim.api.nvim_create_user_command('VerifyContentReport', function()
  osgeo_term('verify --output markdown --save VERIFICATION-REPORT.md')
end, { desc = 'Verify content and save markdown report' })

vim.api.nvim_create_user_command('VerifyContentNginx', function()
  osgeo_term('verify --nginx-config osgeo-redirects.conf')
end, { desc = 'Verify content and emit nginx redirect snippet' })

vim.api.nvim_create_user_command('VerifyContentLinks', function()
  osgeo_term('verify --output markdown --save VERIFICATION-REPORT.md --verbose')
end, { desc = 'Verify content + walk every hyperlink, flag broken' })

vim.api.nvim_create_user_command('VerifyContentRemap', function()
  -- Destructive: rewrites internal absolute URLs in content/**/*.md.
  -- Run --skip-links first so the rewrite isn't gated on slow HTTP checks.
  local choice = vim.fn.confirm(
    'Rewrite all https://www.osgeo.org/* links in content/ to Hugo-relative form?',
    '&Yes\n&No', 2)
  if choice == 1 then
    osgeo_term('verify --remap-internal --skip-links --verbose')
  end
end, { desc = 'Rewrite internal osgeo.org links to Hugo-relative (DESTRUCTIVE)' })

-- Content harvesting
vim.api.nvim_create_user_command('Harvest', function(opts)
  local args = opts.args ~= '' and (' ' .. opts.args) or ''
  osgeo_term('harvest' .. args)
end, { nargs = '*', desc = 'Harvest content from osgeo.org (osgeo harvest)' })

vim.api.nvim_create_user_command('CheckLinks', function()
  osgeo_term('check-links')
end, { desc = 'Check links on the local dev site (osgeo check-links)' })

-- Utility commands
vim.api.nvim_create_user_command('OpenBrowser', function()
  osgeo_shell('open')
end, { desc = 'Open site in browser (osgeo open)' })

vim.api.nvim_create_user_command('NixDevelop', function()
  vim.cmd('terminal nix develop')
end, { desc = 'Enter Nix development shell' })

vim.api.nvim_create_user_command('CleanPublic', function()
  osgeo_shell('clean')
end, { desc = 'Clean build output directories (osgeo clean)' })

-- Content helpers (keep the direct hugo call so the new file opens
-- in the editor straight away)
vim.api.nvim_create_user_command('NewPage', function(opts)
  if opts.args ~= '' then
    vim.cmd('!hugo new ' .. opts.args .. '/_index.md')
    vim.cmd('edit content/' .. opts.args .. '/_index.md')
  else
    vim.notify('Usage: :NewPage <section/path>', vim.log.levels.WARN)
  end
end, { nargs = '?', desc = 'Create new section page' })

vim.api.nvim_create_user_command('NewPost', function(opts)
  local title = opts.args ~= '' and opts.args or 'new-post'
  local slug = title:lower():gsub('%s+', '-'):gsub('[^%w%-]', '')
  local path = 'news/' .. os.date('%Y-%m-%d') .. '-' .. slug .. '.md'
  vim.cmd('!hugo new ' .. path)
  vim.cmd('edit content/' .. path)
end, { nargs = '?', desc = 'Create new news post' })

-- ============================================================================
-- Which-Key Registration
-- ============================================================================

local wk_ok, wk = pcall(require, 'which-key')
if wk_ok then
  wk.add({
    -- Project group
    { '<leader>p', group = 'Project (OSGeo Hugo)' },

    -- Hugo server & build
    { '<leader>ps', '<cmd>HugoServer<cr>', desc = 'Start Hugo server (osgeo serve)' },
    { '<leader>pS', '<cmd>HugoServerDrafts<cr>', desc = 'Hugo server with drafts (osgeo drafts)' },
    { '<leader>pb', '<cmd>HugoBuild<cr>', desc = 'Build site (dev)' },
    { '<leader>pB', '<cmd>HugoBuildProd<cr>', desc = 'Build site (prod, osgeo build)' },
    { '<leader>po', '<cmd>OpenBrowser<cr>', desc = 'Open in browser (osgeo open)' },
    { '<leader>pw', '<cmd>Preview<cr>', desc = 'Preview nix-built site (osgeo preview)' },

    -- Formatting
    { '<leader>pf', '<cmd>PrettierFormat<cr>', desc = 'Format current file' },
    { '<leader>pF', '<cmd>PrettierFormatAll<cr>', desc = 'Format all files (osgeo format)' },

    -- Linting
    { '<leader>pl', '<cmd>MarkdownLint<cr>', desc = 'Lint Markdown (osgeo lint-md)' },
    { '<leader>pL', '<cmd>HtmlHint<cr>', desc = 'Lint HTML output (osgeo lint-html)' },
    { '<leader>pc', '<cmd>PrettierCheck<cr>', desc = 'Check formatting (osgeo format-check)' },

    -- Testing
    { '<leader>pt', '<cmd>E2eTest<cr>', desc = 'Run Playwright e2e tests (osgeo test)' },
    { '<leader>pT', '<cmd>E2eTestUI<cr>', desc = 'Playwright e2e tests (UI mode)' },
    { '<leader>py', '<cmd>SiteVideo<cr>', desc = 'Record site validation video (osgeo video)' },
    { '<leader>pi', '<cmd>SiteReview<cr>', desc = 'Review site screenshots (osgeo review)' },

    -- Pre-commit / Git
    { '<leader>pp', '<cmd>PreCommit<cr>', desc = 'Run pre-commit (osgeo pre-commit)' },
    { '<leader>pg', '<cmd>GitStatus<cr>', desc = 'Git status' },
    { '<leader>pd', '<cmd>GitDiff<cr>', desc = 'Git diff' },

    -- osgeo dispatcher
    { '<leader>pm', '<cmd>Osgeo<cr>', desc = 'osgeo command menu' },
    { '<leader>pu', ':Osgeo ', desc = 'osgeo <command>…', silent = false },
    { '<leader>pM', '<cmd>Make<cr>', desc = 'Make (show help)' },

    -- Content creation & sync
    { '<leader>pn', '<cmd>NewPost<cr>', desc = 'New news post' },
    { '<leader>pN', '<cmd>NewPage<cr>', desc = 'New section page' },
    { '<leader>ph', '<cmd>Harvest<cr>', desc = 'Harvest content (osgeo harvest)' },
    { '<leader>pK', '<cmd>CheckLinks<cr>', desc = 'Check links (osgeo check-links)' },

    -- Verification (content cross-check + link integrity + nginx redirect map)
    { '<leader>pv', '<cmd>VerifyContent<cr>', desc = 'Verify content vs osgeo.org (osgeo verify)' },
    { '<leader>pV', '<cmd>VerifyContentReport<cr>', desc = 'Verify + save markdown report' },
    { '<leader>pr', '<cmd>VerifyContentNginx<cr>', desc = 'Verify + emit nginx redirects' },
    { '<leader>pk', '<cmd>VerifyContentLinks<cr>', desc = 'Verify + walk all hyperlinks' },
    { '<leader>pR', '<cmd>VerifyContentRemap<cr>', desc = 'Rewrite internal links (DESTRUCTIVE)' },

    -- Utilities
    { '<leader>px', '<cmd>NixDevelop<cr>', desc = 'Nix develop shell' },
    { '<leader>pC', '<cmd>CleanPublic<cr>', desc = 'Clean build dirs (osgeo clean)' },
  })
else
  -- Fallback keymaps if which-key not available
  local opts = { noremap = true, silent = true }

  -- Hugo
  vim.keymap.set('n', '<leader>ps', '<cmd>HugoServer<cr>', vim.tbl_extend('force', opts, { desc = 'Start Hugo server' }))
  vim.keymap.set('n', '<leader>pb', '<cmd>HugoBuild<cr>', vim.tbl_extend('force', opts, { desc = 'Build site' }))
  vim.keymap.set('n', '<leader>po', '<cmd>OpenBrowser<cr>', vim.tbl_extend('force', opts, { desc = 'Open in browser' }))

  -- osgeo dispatcher
  vim.keymap.set('n', '<leader>pm', '<cmd>Osgeo<cr>', vim.tbl_extend('force', opts, { desc = 'osgeo command menu' }))

  -- Formatting
  vim.keymap.set('n', '<leader>pf', '<cmd>PrettierFormat<cr>', vim.tbl_extend('force', opts, { desc = 'Format file' }))

  -- Linting
  vim.keymap.set('n', '<leader>pl', '<cmd>MarkdownLint<cr>', vim.tbl_extend('force', opts, { desc = 'Lint Markdown' }))

  -- Pre-commit
  vim.keymap.set('n', '<leader>pp', '<cmd>PreCommit<cr>', vim.tbl_extend('force', opts, { desc = 'Pre-commit' }))

  -- Verification
  vim.keymap.set('n', '<leader>pv', '<cmd>VerifyContent<cr>', vim.tbl_extend('force', opts, { desc = 'Verify content' }))
end

-- ============================================================================
-- Auto-commands
-- ============================================================================

-- Auto-format Markdown on save (optional, uncomment to enable)
-- vim.api.nvim_create_autocmd('BufWritePre', {
--   pattern = '*.md',
--   callback = function()
--     vim.cmd('silent! PrettierFormat')
--   end,
-- })

-- Set filetypes for Hugo templates
vim.api.nvim_create_autocmd({ 'BufRead', 'BufNewFile' }, {
  pattern = { '*.html' },
  callback = function()
    -- Check if we're in a Hugo project
    if vim.fn.filereadable('config.toml') == 1 then
      vim.bo.filetype = 'gohtmltmpl'
    end
  end,
})

-- ============================================================================
-- Notification
-- ============================================================================

vim.notify("OSGeo Hugo: Project config loaded. Use <leader>p for commands.", vim.log.levels.INFO)
