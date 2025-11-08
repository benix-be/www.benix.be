{ inputs, ... }:
{
  # Import the default make-shell module, required for defining development shells.
  # This module provides the `perSystem.make-shells` attribute.
  imports = [ inputs.make-shell.flakeModules.default ];

  # Define per-system modules.
  # It is a function that takes `pkgs` and many other parameters.
  # The `pkgs` parameter is the package set for the given system architecture.
  perSystem =
    { pkgs, config, ... }:
    {
      # Development shell definition.
      make-shells.default = {
        # List the packages to be available in the shell.
        packages = with pkgs; [
          config.packages.website-watch

          (python3.withPackages (ps: [
            ps.django
            ps.ics
            ps.asyncinotify
          ]))
        ];

        # Optional: Run commands when the shell starts.
        shellHook = ''
          echo ""
          echo ">> Python development environment is ready!"
          echo ""
        '';
      };
    };
}
