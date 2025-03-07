{
  description = "game engine black book development nix flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    flake-utils.url = "github:numtide/flake-utils";

    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-compat, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system: {
      # use nix-shell or nix develop to access this shell
      devShell = with nixpkgs.legacyPackages.${system};
      mkShell {
          buildInputs = [
            nixpkgs-fmt
            python312
            ffmpeg
            yt-dlp
            aria
          ] ++ (with python312Packages; [
            google-auth
            google-auth-oauthlib
            google-auth-httplib2
            google-api-python-client
            pandas
            requests
            openpyxl
          ]);
        };
    });
}
