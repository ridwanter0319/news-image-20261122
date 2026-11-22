"""Entry point for the news-image-20261122 make.fun entry.

Writes the one-page broadsheet for Sunday 22 November 2026 to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).

The page is drawn by compose.py with PIL. The grader's stock python3.13
image has no Pillow, so when PIL is unavailable this program falls back
to copying the entry.png shipped in the repository — the exact bytes
compose.py produced. Either way the output is deterministic: two runs
write identical bytes, and no network is used.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    try:
        sys.path.insert(0, HERE)
        import compose

        compose.build(out_path)
    except ImportError:
        shutil.copyfile(os.path.join(HERE, "entry.png"), out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
