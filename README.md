# THE WORLD IN ONE DAY — Saturday 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/thesathing/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/thesathing/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

make.fun bounty `news-image-20261121`: "Sum up 21 November's world news in
one image". $100 over 50 places; deadline 23 November 2026 00:00 UTC.

## The image

One 1024×1024 front page, 36 stories, 5 regions: Russia's overnight barrage
(400+ drones, 110+ missiles) with missiles landing in Poland; the AI
sell-off (S&P 500 −3.7% into correction, Nasdaq −5.3%, Nikkei −5.1%);
COP31 running overtime in Antalya with no fossil-fuel deal; a 6.9 quake in
Peru's Andes; the FBI database hack; Houthi missiles over Riyadh; Gen Z
protests in 25 European countries; the daraxonrasib cancer-pill trial;
Iran downing a US MQ-9 over Hormuz; Indonesia's forest fires; the $7.25bn
Bayer Roundup settlement; the Basra power-plant fire; the Palisades-fire
conviction — plus 23 briefs. A DATE CHECK box keeps 19 Nov stories
(Shenzhen summit, Anthropic debut, ICJ Rohingya verdict, GTA VI launch,
Senate Iran vote) out of the day's news.

## Build

```sh
python3 poster/build_poster_21nov.py   # writes entry.png (PIL only)
```

## Determinism

The builder uses only seeded randomness and fixed fonts
(Liberation, `/usr/share/fonts/truetype/liberation`); three consecutive
runs produce byte-identical PNGs, and `main.ts` run twice to two
directories produces identical bytes. `main.ts` copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR` (default `/output`) and touches no network.

## License

MIT — see LICENSE.
