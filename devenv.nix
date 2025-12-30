{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = [
    pkgs.git
    pkgs.nil
    pkgs.pyright
    pkgs.nodejs_24
  ];

  treefmt = import ./.config/treefmt.nix {inherit pkgs lib;};

  languages = {
    shell.enable = true;

    nix.enable = true;
    nix.lsp.package = pkgs.nixd;

    python.enable = true;
    python.version = "3.13";
    python.venv.enable = true;
    python.uv.enable = true;
    python.uv.sync.enable = true;
    python.uv.sync.allGroups = true;
  };

  tasks = {
    "local:syncTreefmt" = {
      description = "Sync the treefmt binary and configuration file from the Nix store to the workspace";
      exec = ''
        mkdir -p "${config.git.root}"/.{config,bin} && {
          ln -sf "${lib.getExe pkgs.treefmt}"                 "${config.git.root}/.bin/treefmt"
          ln -sf "${config.treefmt.config.build.configFile}"  "${config.git.root}/.config/treefmt.toml"
        }
      '';
    };
  };
}
