# Sunday 22 November 2026 — The World in One Day

A one-page broadsheet that sums up the world news of Sunday 22 November 2026
in a single 1024×1024 image: 40 stories across 6 regions, with three
illustrated leads (the capture of "El Chapo Isidro" in Sinaloa, the strikes
on Kyiv's bridges, and the M6.8 Peru quake), ten numbered cards, 27 briefs,
a day-in-numbers strip, and a dotted world map with pins for stories 1–13.

Entry for the make.fun bounty
[news-image-20261122](https://make.fun/bounty/news-image-20261122) on
[make.fun](https://make.fun).

[![Competition](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![Rank](https://make.fun/badge/news-image-20261122/ridwanter0319/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![Reward](https://make.fun/badge/news-image-20261122/ridwanter0319/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

## How it works

- `main.py` is the entrypoint. It draws the page via `compose.py` (PIL)
  when Pillow is available, and otherwise copies the shipped `entry.png`
  (the grader's stock Python image has no Pillow). Output goes to
  `/output/entry.png`, or `$MAKEFUN_OUTPUT_DIR/entry.png` locally.
- `compose.py` renders the whole page deterministically — masthead,
  numbers strip, region bar, lead illustrations, cards, briefs, map and
  date-check footer — with no network and no randomness.
- `entry.png` is the rendered page, exactly 1024×1024.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Licensed under MIT (see `LICENSE`).
