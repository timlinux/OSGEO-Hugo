# OSGeo Hugo Website

This is the official website for the Open Source Geospatial Foundation (OSGeo), built with Hugo using the hugo-bulma-blocks-theme.

## About OSGeo

The Open Source Geospatial Foundation (OSGeo) is a not-for-profit organization whose mission is to foster global adoption of open geospatial technology by being an inclusive software foundation devoted to an open philosophy and participatory community-driven development.

## Development

### Prerequisites

- Hugo Extended (v0.139.0 or later)
- Nix (recommended for development environment)

### Using Nix

Enter the development environment:

```bash
nix develop
```

On entry a menu of all project commands is printed. Everything is
driven through the `osgeo` command:

```bash
osgeo serve      # Hugo dev server at http://localhost:1313
osgeo build      # production build
osgeo verify     # verify content against osgeo.org
osgeo            # show the full menu
```

The full command menu (also shown by `osgeo help`):

| Group     | Command                 | Description                                        |
| --------- | ----------------------- | -------------------------------------------------- |
| Serve     | `serve`                 | Run the Hugo dev server (http://localhost:1313)    |
|           | `drafts`                | Dev server with drafts enabled                     |
|           | `preview`               | Serve the nix-built site (http://localhost:8000)   |
|           | `open`                  | Open the dev site in your browser                  |
| Build     | `build`                 | Production build (`public_prod`)                   |
|           | `clean`                 | Remove build artefacts                             |
| Quality   | `format`                | Format md/html/css with Prettier                   |
|           | `format-check`          | Check formatting without changing files            |
|           | `lint`                  | Run all linters                                    |
|           | `lint-md`               | Lint Markdown files                                |
|           | `lint-html`             | Lint built HTML (run a build first)                |
|           | `pre-commit`            | Run pre-commit hooks on all files                  |
|           | `verify`                | Verify content against osgeo.org (args pass through) |
|           | `test`                  | Run the Playwright e2e suite                       |
| Content   | `new-page <path>`       | Create a page, e.g. `osgeo new-page about/contact` |
|           | `new-post "<title>"`    | Create a news post                                 |
|           | `harvest`               | Harvest content from osgeo.org (supports `--dry-run`) |
|           | `check-links`           | Check links on the local dev site                  |
| Utilities | `deploy`                | Deploy the site (pull, backup, rebuild)            |
|           | `revert-deploy`         | Revert to the previous deployment                  |
|           | `help`                  | Show the menu                                      |

You can also run any subcommand without entering the dev shell —
every `osgeo` subcommand is exposed as a flake app:

```bash
nix run .#serve
nix run .#build
nix run .#verify -- --output json
nix run .#osgeo -- help     # the dispatcher itself
```

In Neovim the same commands are available under the `<leader>p`
which-key menu (see `.nvim.lua`): `<leader>ps` serve, `<leader>pm`
osgeo menu, `<leader>pu` run any `osgeo` subcommand, plus bindings
for harvest, verify, tests, linting and more. All of them delegate
to the same `scripts/osgeo` dispatcher.

### Running Locally

Start the development server:

```bash
osgeo serve
```

Or directly, using Hugo or the Makefile (which `osgeo` delegates to):

```bash
hugo server
make hugo-run-dev
```

Visit http://localhost:1313 to see the site.

### Building

Production build (outputs to `public_prod`):

```bash
osgeo build
```

Preview the nix-built site on http://localhost:8000:

```bash
osgeo preview
```

Or directly with Hugo:

```bash
hugo --config config.toml,config/config.prod.toml
```

## Project Structure

```plaintext
OSGEO-hugo/
├── config.toml           # Main Hugo configuration
├── config/               # Environment-specific configs
├── content/              # Markdown content
│   ├── about/           # About OSGeo pages
│   ├── projects/        # OSGeo project listings
│   ├── community/       # Community pages
│   ├── initiatives/     # FOSS4G, Geo for All, etc.
│   ├── resources/       # Documentation and resources
│   ├── membership/      # Membership information
│   ├── local-chapters/  # Local chapter listings
│   ├── donate/          # Donation page
│   └── sponsors/        # Sponsor listings
├── static/              # Static assets
│   └── img/
│       └── osgeo/       # OSGeo logos and branding
├── themes/              # Hugo theme
│   └── hugo-bulma-blocks-theme/
└── data/                # Data files (JSON, YAML)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for more detailed guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Brand Guidelines

This site uses OSGeo's official branding:

- **Primary Color**: Light Green #4DB05B (Pantone 361 U)
- **Secondary Color**: Dark Teal #003A40 (Pantone 330 U)
- **Fonts**: Miriam Libre (headings), Sintony (body text)

For more information about OSGeo branding, see the [OSGeo Branding Materials](https://www.osgeo.org/about/branding-material/).

## Have Questions?

Have questions or feedback? Feel free to open an issue or submit a Pull Request!

---

Based on the QGIS-Hugo website architecture by Tim Sutton (@timlinux).

Made with 💗 by [Kartoza](https://kartoza.com) | [Donate to OSGeo!](https://www.osgeo.org/donate/) | [GitHub](https://github.com/timlinux/OSGEO-Hugo)
