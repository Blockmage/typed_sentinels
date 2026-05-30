{
  lib,
  pkgs,
  ...
}: let
  wspRoot = ".";
  cfgDir = "_meta/config";
in {
  git-hooks = {
    enable = true;
    install.enable = true;
    package = pkgs.prek;

    default_stages = [
      "pre-commit"
      "pre-push"
      "commit-msg"
    ];

    excludes = [
      ".*-lock\..*"
      ".*\.lock$"
      ".*example.*"
      "cspell\.txt"
    ];

    hooks = {
      # -------------------------------- Hooks ---------------------------------
      treefmt.enable = true;

      pyright.enable = true;
      pytest.enable = true;

      actionlint.enable = true;

      cspell-msg.enable = true;
      cspell-wsp.enable = true;

      trufflehog.enable = true;

      check-added-large-files.enable = true;
      check-case-conflicts.enable = true;
      check-merge-conflicts.enable = true;
      check-symlinks.enable = true;

      end-of-file-fixer.enable = true;
      mixed-line-endings.enable = true;
      trim-trailing-whitespace.enable = true;

      # ------------------------------- Options --------------------------------
      treefmt.settings.fail-on-change = false;
      treefmt.settings.no-cache = false;

      check-added-large-files.args = ["--maxkb=8192"];
      mixed-line-endings.args = ["--fix=auto"];

      trufflehog = {
        stages = ["pre-commit" "pre-push"];
        args = [
          "git"
          "\"file://${wspRoot}\""
          "--since-commit"
          "HEAD"
          "--results=verified"
          "--fail"
          "--exclude-paths=\"${cfgDir}/trufflehog_exclude.txt\""
          "--detector-timeout=15s"
        ];
      };

      cspell-wsp = {
        name = "check spelling: workspace files";
        entry = "${pkgs.cspell}/bin/cspell";
        language = "system";
        stages = ["pre-commit" "pre-push"];
        args = [
          "--config"
          "${wspRoot}/cspell.config.jsonc"
          "--no-summary"
          "--no-progress"
          "--no-must-find-files"
        ];
      };

      cspell-msg = {
        name = "check spelling: commit message";
        always_run = true;
        entry = "${pkgs.cspell}/bin/cspell";
        language = "system";
        stages = ["commit-msg"];
        args = [
          "--config"
          "${wspRoot}/cspell.config.jsonc"
          "--no-must-find-files"
          "--no-progress"
          "--no-summary"
          "--files"
          ".git/COMMIT_EDITMSG"
        ];
      };

      pyright = {
        stages = ["pre-push"];
        types = ["python"];
        args = ["--project" "${wspRoot}"];
      };

      pytest = {
        name = "pytest";
        always_run = true;
        language = "system";
        pass_filenames = false;
        stages = ["pre-push"];
        types = ["python"];
        entry = ''
          sh -c '"${wspRoot}/.devenv/state/venv/bin/pytest"'
        '';
      };
    };
  };
}
