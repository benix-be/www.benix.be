# Builds the static website using the Nix defined context
{
  pkgs ? import <nixpkgs> { },
}:

let
  context = import ./context.nix;
  contextJson = pkgs.writeText "context.json" (builtins.toJSON context);
in
pkgs.stdenv.mkDerivation {
  name = "www-benix-be";
  src = ./.;

  buildInputs = [
    pkgs.python3
    pkgs.python3Packages.django
    pkgs.python3Packages.ics
  ];

  installPhase = ''
    cp ${contextJson} context.json
    python render.py
    mkdir -p $out
    cp -r dist/* $out/
  '';
}
