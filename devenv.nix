{
  config,
  inputs,
  lib,
  pkgs,
  ...
}: {
  imports = [
    ./_meta/nix/git-hooks.nix
    ./_meta/nix/scripts.nix
    ./_meta/nix/treefmt.nix
  ];

  dotenv = {
    enable = false;
    disableHint = true;
  };

  packages = [
    pkgs.alejandra
    pkgs.biome
    pkgs.cspell
    pkgs.findutils
    pkgs.gawk
    pkgs.git
    pkgs.gnugrep
    pkgs.gnused
    pkgs.nixd
    pkgs.nodejs_24
    pkgs.pyright
    pkgs.uv
  ];

  env = {
    NODE_OPTIONS = "--max-old-space-size=4096";
    NPM_CONFIG_AUDIT = "true";
    NPM_CONFIG_FUND = "false";
    NPM_CONFIG_IGNORE_SCRIPTS = "true";
    NPM_CONFIG_MINIMUM_RELEASE_AGE = "1440";
    NPM_CONFIG_SAVE_EXACT = "true";
    NPM_CONFIG_UPDATE_NOTIFIER = "false";
  };

  enterShell = ''
    _link_binaries_to_workspace
  '';

  languages = {
    python.enable = true;
    shell.enable = true;
    nix.enable = true;

    python = {
      version = "3.13";
      venv.enable = true;
      uv = {
        enable = true;
        sync.enable = true;
        sync.allExtras = true;
        sync.allGroups = true;
        sync.allPackages = false;
      };
    };
  };
}
