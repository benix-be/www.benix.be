# Builds the static website using the Nix defined context
{
  writeText,
  stdenv,
  python3,
  lib,
  ...
}:

let
  context = import ../../../src/context.nix;
  contextJson = writeText "context.json" (builtins.toJSON context);
in
stdenv.mkDerivation (finalAttrs: {
  name = "www-benix-be";

  src = lib.fileset.toSource {
    root = ../../..;
    fileset = lib.fileset.unions [
      ../../../src
    ];
  };

  buildInputs = [
    (python3.withPackages (ps: [
      ps.django
      ps.ics
      ps.asyncinotify
    ]))
  ];

  sourceRoot = "${finalAttrs.src.name}/src";

  buildPhase = ''
    runHook preBuild

    cp ${contextJson} context.json
    python render.py

    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall

    cp -r dist $out

    runHook postInstall
  '';
})
