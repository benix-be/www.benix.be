{ pkgs ? null }:

let
  system = builtins.currentSystem;
  resolvedPkgs =
    if pkgs != null then pkgs
    else if builtins ? getFlake then
      (builtins.getFlake "nixpkgs/nixos-25.05").legacyPackages.${system}
    else
      import <nixpkgs> { };
in

resolvedPkgs.mkShell {
  buildInputs = with resolvedPkgs; [
    python3
    python3Packages.django
    python3Packages.ics
    python3Packages.asyncinotify
    nix
  ];

  shellHook = ''
    echo "Run with: python watch.py"
  '';
}
