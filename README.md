# THE WORLD IN ONE DAY — Saturday 21 November 2026 in one image

[![competition](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/thesathing/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/thesathing/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

One program that draws a single 1024×1024 newspaper front page summing up
Saturday 21 November 2026: three leads, ten pictured features, a world map
with 13 pins, and 23 briefs — 36 stories across 7 regions, all of them
verified as Saturday 21 November news (a DATE CHECK box lists the Thursday
19 November and Friday 20 November stories that were deliberately left
out). Everything is drawn with Pillow from hand-written vector shapes; no
network access, no clock, no unseeded randomness, so two runs write
identical bytes.

## v6 — the red banners

v6 is v5 plus one thing only: a consistent red banner on all 13 pictured
cards — a 16px crimson strip across the bottom edge of each art box, white
bold sans text, same red, same height, same position on every card
(COP31: DEADLOCK, RIYADH: 3 DOWNED, PERU: QUAKE 6.7, KRYVYI RIH: 2 DEAD,
WASHINGTON: HACKED, DAVAO: 146 SAFE, BERLIN: 25 COUNTRIES, LONDON: 1 IN 12,
HORMUZ: DRONE DOWN, INDONESIA: FIRES, BAYER: $7.25BN, MALAWI: FUEL QUEUES,
XAVIER: CAT 5). It is the one structural element every top-10 entry has
and ours lacked: at 300px thumbnail scale the eye catches the date, then
the row of red banners, then the number strip. The trust chips from v5
(CONFIRMED / OFFICIAL / REPORTED / CLAIM on every pictured card, plus the
HOW WE CHECKED legend) are unchanged, as is every headline, body, number,
region count, pin, brief and the DATE CHECK box.

## Story tally (36 total)

Pictured 13: EUROPE 4, AMERICAS 3, MIDEAST 2, ASIA-PACIFIC 2, AFRICA 1,
OCEANIA 1. Briefs 23: EUROPE 5, AMERICAS 5, ASIA-PACIFIC 3, MIDEAST 3,
AFRICA 2, OCEANIA 2, WORLD 3. Totals: EUROPE 9, AMERICAS 8,
ASIA-PACIFIC 5, MIDEAST 5, AFRICA 3, OCEANIA 3, WORLD 3.

## Run

```
python3 poster/build_poster_v6.py   # writes entry.png
```

`main.ts` copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.

## License

MIT — see LICENSE.
