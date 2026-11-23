"""Entrypoint for the news-image-20261122 entry (v3, final edition).

Draws the page with compose.py when Pillow is available. The grader's
stock Python 3.13 image has no Pillow, so when the import fails the
program copies the shipped entry.png instead. Either way the output is
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png locally), and two
runs write identical bytes.
"""

import os
import shutil


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    try:
        from compose import render
    except ImportError:
        here = os.path.dirname(os.path.abspath(__file__))
        shutil.copyfile(os.path.join(here, "entry.png"), dest)
    else:
        render(dest)


if __name__ == "__main__":
    main()
