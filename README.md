# www.benix.be

**Belgium Nix & Guix User Group Website**

This website is build with Nix and Django templates.

Build with: `nix-build`, the build output is in `result/`.

Automatically rebuilds on changes with:
```shell
nix-shell --run "python watch.py"
```

Update the content in Nix in `context.nix`.

---

Happy hacking 👾