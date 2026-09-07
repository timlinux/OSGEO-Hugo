{
  description = "OSGeo Website";

  # nixConfig = {
  #   extra-substituters = [ "https://example.cachix.org" ];
  #   extra-trusted-public-keys = [ "example.cachix.org-1:xxxx=" ];
  # };

  inputs = {
    nixpkgs-version.url = "github:QGIS/qgis-nixpkgs-version";
    # Stable channel supplies the bulk of the toolchain (python, make).
    nixpkgs.follows = "nixpkgs-version/nixpkgs-26-05";
    # Hugo moves fast and stable lags a few releases behind, so the site
    # generator itself is taken from unstable to track the current release.
    nixpkgs-unstable.follows = "nixpkgs-version/nixpkgs-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
      nixpkgs-unstable,
      ...
    }:

    let
      # Flake system
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      nixpkgsFor = forAllSystems (
        system:
        import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        }
      );
      # Only used to pull the latest Hugo; everything else comes from stable.
      unstableFor = forAllSystems (
        system:
        import nixpkgs-unstable {
          inherit system;
          config.allowUnfree = true;
        }
      );
      hugoFor = forAllSystems (system: unstableFor.${system}.hugo);

      # Python env for the content scripts (verifier, harvester) with all
      # required libraries provisioned from nixpkgs (no pip/npm).
      scriptsPythonFor = forAllSystems (
        system:
        nixpkgsFor.${system}.python3.withPackages (ps: [
          ps.requests
          ps.beautifulsoup4
          ps.lxml
          ps.html2text
          ps.rich
        ])
      );

      # Thin launcher for the project command dispatcher. All command
      # logic lives in scripts/osgeo (no code embedded in nix); this
      # wrapper only locates the repo root and puts the tools the
      # subcommands rely on (make, hugo, python, git) on PATH so
      # `nix run .#osgeo` also works outside the dev shell.
      osgeoFor = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
        in
        pkgs.writeShellApplication {
          name = "osgeo";
          runtimeInputs = [
            pkgs.git
            pkgs.gnumake
            hugoFor.${system}
            scriptsPythonFor.${system}
          ];
          text = ''
            if [[ -z "''${OSGEO_HUGO_ROOT:-}" ]]; then
              if root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
                export OSGEO_HUGO_ROOT="$root"
              else
                export OSGEO_HUGO_ROOT="$PWD"
              fi
            fi
            exec "$OSGEO_HUGO_ROOT/scripts/osgeo" "$@"
          '';
        }
      );

    in
    {
      #
      ### PACKAGES
      #

      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
        in
        rec {
          website = pkgs.callPackage ./nix/package.nix { hugo = hugoFor.${system}; };
          default = website;
        }
      );

      #
      ### APPS
      #

      apps = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
          inherit (nixpkgs) lib;

          # Every osgeo subcommand is also exposed as its own flake app so
          # `nix run .#serve` (etc.) works without entering the dev shell.
          # Keep this list in step with the dispatch table in scripts/osgeo.
          osgeoCommands = [
            # Serve
            "serve"
            "drafts"
            "preview"
            "open"
            # Build
            "build"
            "clean"
            # Quality
            "format"
            "format-check"
            "lint"
            "lint-md"
            "lint-html"
            "pre-commit"
            "verify"
            "test"
            # Content
            "new-page"
            "new-post"
            "harvest"
            "check-links"
            # Utilities
            "deploy"
            "revert-deploy"
          ];

          # Thin per-subcommand launcher: exec the dispatcher with the
          # subcommand baked in, passing any extra args through.
          osgeoApp =
            cmd:
            let
              launcher = pkgs.writeShellApplication {
                name = "osgeo-${cmd}";
                text = ''
                  exec ${osgeoFor.${system}}/bin/osgeo ${cmd} "$@"
                '';
              };
            in
            {
              type = "app";
              program = "${launcher}/bin/osgeo-${cmd}";
            };

          wwwLauncher = pkgs.writeShellApplication {
            name = "website";
            runtimeInputs = [ pkgs.python3 ];
            text = ''
              exec ${lib.getExe pkgs.python3} \
                -m http.server 8000 \
                -d ${self.packages.${system}.website}/public_www/
            '';
          };

          # Shared python env for the content scripts (see top-level let).
          verifyPython = scriptsPythonFor.${system};

          verifyLauncher = pkgs.writeShellApplication {
            name = "verify-content";
            runtimeInputs = [ verifyPython pkgs.git ];
            text = ''
              # Locate the project root so the script works from any
              # subdirectory. Honour an explicit override first.
              if [[ -z "''${OSGEO_HUGO_ROOT:-}" ]]; then
                if root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
                  export OSGEO_HUGO_ROOT="$root"
                else
                  export OSGEO_HUGO_ROOT="$PWD"
                fi
              fi
              exec ${verifyPython}/bin/python3 \
                "$OSGEO_HUGO_ROOT/scripts/verify_content.py" "$@"
            '';
          };
        in
        lib.genAttrs osgeoCommands osgeoApp
        // rec {
          website = {
            type = "app";
            program = "${wwwLauncher}/bin/website";
          };
          verify-content = {
            type = "app";
            program = "${verifyLauncher}/bin/verify-content";
          };
          osgeo = {
            type = "app";
            program = "${osgeoFor.${system}}/bin/osgeo";
          };
          default = website;
        }
      );

      #
      ### SHELLS
      #

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgsFor.${system};
        in
        {
          # Development environment
          default = pkgs.mkShell {
            packages = [
              hugoFor.${system} # Hugo (latest release, from nixpkgs-unstable)
              # One interpreter carrying every library the scripts in
              # scripts/ import, so `python3 scripts/<name>.py` works
              # directly in the dev shell. Keep in step with
              # REQUIREMENTS.txt.
              #
              # NOTE: atoma (used by fetch_feeds.py) is not packaged in
              # nixpkgs, so that one script still needs the pipenv
              # environment until we add a derivation for it.
              (pkgs.python3.withPackages (ps: [
                ps.beautifulsoup4 # HTML parsing for harvesters
                ps.boto3 # S3 download listings
                ps.html2text # HTML to markdown conversion
                ps.icalendar # Release schedule .ics generation
                ps.lxml # Fast HTML/XML parser backend
                ps.pillow # Logo/image resizing
                ps.python-dateutil # Feed date parsing
                ps.requests # HTTP client
                ps.rich # Pretty terminal tables
                ps.stripe # Donation sync
                ps.pytest # Test runner
              ]))
            ]
            ++ (with pkgs; [
              gnumake # GNU Make for build automation
            ])
            ++ [
              osgeoFor.${system} # `osgeo` project command dispatcher
            ];
            shellHook = ''
              export DIRENV_LOG_FORMAT=
              echo ""
              echo "🌈 Your Hugo Dev Environment is ready."
              echo "It provides hugo, python and the osgeo command for the"
              echo "OSGeo Website Project."
              echo ""
              echo "🪛 Editor: this project is set up for Neovim; see .nvim.lua"
              echo "for project-local configuration."
              echo ""
              osgeo help
            '';
          };
        }
      );
    };
}
