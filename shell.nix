{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.django
    python3Packages.asyncinotify
    nix
  ];

  shellHook = ''
    echo "Run with: python watch.py"
  '';
}
