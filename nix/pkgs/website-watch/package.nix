# Builds the static website using the Nix defined context
{
  writeShellApplication,
  python3,
  ...
}:

writeShellApplication {
  name = "website-watch";

  runtimeInputs = [
    (python3.withPackages (ps: [
      ps.django
      ps.ics
      ps.asyncinotify
    ]))
  ];

  text = ''
    pushd src
    python watch.py
    popd
  '';
}
