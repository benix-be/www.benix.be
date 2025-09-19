"""
Builds the static website from JSON data using Django templates
"""
import json
import shutil
from pathlib import Path

from django.conf import settings
from django.template import Context, Engine

settings.configure()
template_root = Path("template")
output_root = Path("dist")
engine = Engine(dirs=[str(template_root)])

with open("context.json") as f:
    context = json.load(f)

for src_path in template_root.rglob("*"):
    rel_path = src_path.relative_to(template_root)
    dst_path = output_root / rel_path

    if src_path.is_dir():
        continue

    dst_path.parent.mkdir(parents=True, exist_ok=True)

    if src_path.suffix == ".html":
        template = engine.get_template(str(rel_path))
        with open(dst_path, "w") as out:
            out.write(template.render(Context(context)))
    else:
        shutil.copy2(src_path, dst_path)
