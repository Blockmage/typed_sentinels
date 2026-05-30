{
  pkgs,
  lib,
  inputs,
  config,
  ...
}: {
  scripts = {
    git = {
      description = ''Alias for `git` that forces the use of UTC timestamps for commits'';
      exec = ''
        UTC_TIMESTAMP="$(date '+%s')+0000"
        export TZ="UTC" GIT_AUTHOR_DATE="$UTC_TIMESTAMP" GIT_COMMITTER_DATE="$UTC_TIMESTAMP"
        "${lib.getExe pkgs.git}" "$@"
      '';
    };

    _link_binaries_to_workspace = {
      description = lib.concatStrings [
        ''Symlink the binaries for `treefmt`, `biome`, and Go development tools to the workspace so that they can be ''
        ''used by the VS Code run-on-save and Go extensions. This runs automatically when entering the shell.''
      ];
      exec = ''
        set -eu

        wspRoot="''${WORKSPACE_ROOT:-"''${DEVENV_ROOT:-"."}"}"

        treefmtBin="${lib.getExe pkgs.treefmt}"
        treefmtCfg="${config.treefmt.config.build.configFile}"
        biomeBin="${lib.getExe pkgs.biome}"

        if mkdir -p "$wspRoot/_meta/bin"; then
          [ -f "$treefmtBin" ] && ln -sf "$treefmtBin" "$wspRoot/_meta/bin/treefmt"
          [ -f "$treefmtCfg" ] && ln -sf "$treefmtCfg" "$wspRoot/_meta/config/treefmt.toml"
          [ -f "$biomeBin" ]   && ln -sf "$biomeBin"   "$wspRoot/_meta/bin/biome"
        fi
      '';
    };
  };
}
