"""
Builds the static website from JSON data using Django templates, and watches for changes.
"""

import asyncio
import json
import shutil
import subprocess
from pathlib import Path

from asyncinotify import Inotify, Mask
from django.conf import settings
from django.template import Engine, Context

TEMPLATE_DIR = Path("template")
OUTPUT_DIR = Path("dist")
CONTEXT_FILE = Path("context.nix")
COPY_DIRS = ["static"]


def load_context():
    out = subprocess.check_output(
        ["nix", "eval", "--json", "--file", str(CONTEXT_FILE)]
    )
    return json.loads(out)


settings.configure()

context = load_context()


# Avoid caching of templates
# engine = Engine(dirs=["template"], auto_reload=True)
def get_engine():
    return Engine(dirs=[str(TEMPLATE_DIR)])


def render_template(src_path: Path):
    rel_path = src_path.relative_to(TEMPLATE_DIR)
    dst_path = OUTPUT_DIR / rel_path
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    template = get_engine().get_template(str(rel_path))
    with open(dst_path, "w") as out:
        out.write(template.render(Context(context)))
    print(f"Rendered: {rel_path} to {dst_path}")


def render_all_html():
    for path in TEMPLATE_DIR.glob("*.html"):
        render_template(path)


def copy_static_dirs():
    for d in COPY_DIRS:
        src = TEMPLATE_DIR / d
        dst = OUTPUT_DIR / d
        if dst.exists():
            shutil.rmtree(dst)
        if src.exists():
            shutil.copytree(src, dst)
            print(f"Copied: {src} → {dst}")


async def watch():
    global context
    inotify = Inotify()

    # inotify.add_watch(str(TEMPLATE_DIR), Mask.MODIFY | Mask.CLOSE_WRITE | Mask.MOVED_TO)
    inotify.add_watch(str(TEMPLATE_DIR), Mask.CLOSE_WRITE)
    # inotify.add_watch(str(CONTEXT_FILE), Mask.MODIFY | Mask.CLOSE_WRITE)
    inotify.add_watch(str(CONTEXT_FILE), Mask.CLOSE_WRITE)

    print("Watching template/ and context.nix...")

    async for event in inotify:
        path = Path(event.name or "")
        full_path = Path(event.watch.path) / path if path else Path(event.watch.path)

        if full_path.resolve() == CONTEXT_FILE.resolve():
            print("Context changed. Reloading and rendering all...")
            context = load_context()
            render_all_html()
        elif full_path.suffix == ".html" and full_path.parent == TEMPLATE_DIR:
            render_template(full_path)


if __name__ == "__main__":
    render_all_html()
    copy_static_dirs()
    asyncio.run(watch())
