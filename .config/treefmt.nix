{
  lib,
  pkgs,
  ...
}: let
  # 'configsDir' must be a path relative to the root of the repository
  configsDir = ".config";

  excludes = {
    js = [];
    json = [];
    md = [];
    py = [];
    sh = [];
    toml = [];
    yaml = [];
  };

  includes = {
    js = ["*.js" "*.jsx" "*.ts" "*.tsx"];
    json = ["*.json" "*.jsonc" "*.sublime-keymap" "*.sublime-settings"];
    md = ["*.md"];
    py = ["*.py" "*.pyi" "*.ipynb"];
    sh = ["*.sh" "*.zsh" "zsh*" ".zsh*" "*.bash" "bash*" ".bash*" "profile" ".profile"];
    toml = ["*.toml"];
    yaml = ["*.yml" "*.yaml"];
  };
in {
  enable = true;
  config = {
    programs = {
      alejandra = {
        enable = true;
        excludes = [];
        includes = ["*.nix"];
        package = pkgs.alejandra;
      };
    };

    settings = {
      formatter = {
        # --------- Shell Scripts
        sh_shfmt = {
          priority = 0;
          command = "${lib.getExe pkgs.shfmt}";
          excludes = excludes.sh;
          includes = includes.sh;
          options = ["-s" "-ci" "-i" "2" "--write"];
        };
        #sh_shellharden = {
        #  priority = 1;
        #  command = "${lib.getExe pkgs.shellharden}";
        #  excludes = excludes.sh ++ [".envrc"];
        #  includes = includes.sh;
        #  # WARNING: '--replace' will break scripts that depend on word splitting!
        #  options = ["--replace"];
        #};

        # --------- Python
        py_ruff_check = {
          priority = 0;
          command = "${lib.getExe pkgs.ruff}";
          excludes = excludes.py;
          includes = includes.py;
          options = ["--config" "${configsDir}/ruff.toml" "check" "--fix"];
        };
        py_docformatter = {
          priority = 1;
          command = "${lib.getExe pkgs.python313Packages.docformatter}";
          excludes = excludes.py;
          includes = lib.lists.filter (i: i != "*.ipynb") includes.py;
          options = ["--in-place" "--style" "numpy" "--wrap-descriptions" "120" "--wrap-summaries" "120"];
        };
        py_ruff_format = {
          priority = 2;
          command = "${lib.getExe pkgs.ruff}";
          excludes = excludes.py;
          includes = includes.py;
          options = ["--config" "${configsDir}/ruff.toml" "format"];
        };

        # --------- Markdown
        md_prettier = {
          priority = 0;
          command = "${lib.getExe pkgs.prettier}";
          excludes = excludes.md;
          includes = includes.md;
          options = ["--config" "${configsDir}/.prettierrc.yml" "--write"];
        };
        md_markdownlint = {
          priority = 1;
          command = "${lib.getExe pkgs.markdownlint-cli2}";
          excludes = excludes.md;
          includes = includes.md;
          options = ["--config" "${configsDir}/.markdownlint.yml" "--fix"];
        };

        # --------- TOML
        toml_taplo = {
          priority = 0;
          command = "${lib.getExe pkgs.taplo}";
          excludes = excludes.toml;
          includes = includes.toml;
          options = ["format" "--config" "${configsDir}/taplo.toml"];
        };

        # --------- YAML
        yaml_yamlfmt = {
          priority = 0;
          command = "${lib.getExe pkgs.yamlfmt}";
          excludes = excludes.yaml;
          includes = includes.yaml;
          options = ["-conf" "${configsDir}/yamlfmt.yml" "format"];
        };

        # --------- JavaScript / TypeScript
        js_biome = {
          priority = 0;
          command = "${lib.getExe pkgs.biome}";
          excludes = excludes.js;
          includes = includes.js;
          options = ["format" "--config-path" "${configsDir}/biome.jsonc" "--write"];
        };

        # --------- JSON
        json_biome = {
          priority = 0;
          command = "${lib.getExe pkgs.biome}";
          excludes = excludes.json;
          includes = includes.json;
          options = ["format" "--config-path" "${configsDir}/biome.jsonc" "--write"];
        };
      };
    };
  };
}
