{ pkgs, lib, config, inputs, ... }:

let
  pkgs-unstable = import inputs.nixpkgs-unstable { system = pkgs.stdenv.system; };
in

{
  # disable cachix cache management to suppress errors
  cachix.enable = false;

  # disable devenv's dotenv processing as it doesn't support features we need;
  # we will source it via direnv instead.
  dotenv.disableHint = true; # we'll source this using direnv

  # https://devenv.sh/packages/
  packages = [
    pkgs.git
    pkgs.just
    pkgs.openconnect
  ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    package = pkgs-unstable.python313;

    uv = {
      enable = true;
      package = pkgs-unstable.uv;
      sync = {
        enable = true;
        allExtras = true;
      };

    };
  };

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;
  pre-commit.excludes = [ "^data/" ];
  pre-commit.hooks = {
    trim-trailing-whitespace.enable = true;
    end-of-file-fixer.enable = true;
    check-yaml.enable = true;
    check-added-large-files.enable = true;
    ruff.enable = true;
    ruff-format.enable = true;
  };

  enterShell = ''
    source "''${UV_PROJECT_ENVIRONMENT}/bin/activate"
  '';

  # See full reference at https://devenv.sh/reference/options/
}
