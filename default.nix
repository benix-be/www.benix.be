# Builds the static website using the Nix defined context
{ pkgs ? null }:

let
  system = builtins.currentSystem;
  resolvedPkgs =
    if pkgs != null then pkgs
    else if builtins ? getFlake then
      (builtins.getFlake "nixpkgs/nixos-24.05").legacyPackages.${system}
    else
      import <nixpkgs> { };
  context = import ./context.nix;
  contextJson = resolvedPkgs.writeText "context.json" (builtins.toJSON context);
in
resolvedPkgs.stdenv.mkDerivation {
  name = "www-benix-be";
  src = ./.;

  buildInputs = [
    resolvedPkgs.python3
    resolvedPkgs.python3Packages.django
    resolvedPkgs.python3Packages.ics
  ];

  installPhase = ''
    cp ${contextJson} context.json
    python render.py
    mkdir -p $out
    cp -r dist/* $out/
  '';
}
