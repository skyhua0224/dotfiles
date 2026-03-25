{
  description = "Shared shell environment for these dotfiles";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        tools = with pkgs; [
          atuin
          bat
          carapace
          delta
          duf
          dust
          eza
          fd
          fzf
          git
          gnugrep
          mise
          procs
          ripgrep
          starship
          tlrc
          zoxide
          zsh
          zsh-autosuggestions
          zsh-completions
          zsh-history-substring-search
          zsh-syntax-highlighting
        ];
      in {
        packages.default = pkgs.buildEnv {
          name = "dotfiles-tools";
          paths = tools;
        };

        devShells.default = pkgs.mkShell {
          packages = tools;
        };

        formatter = pkgs.nixpkgs-fmt;
      });
}
