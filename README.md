# THE WORLD IN ONE DAY — Saturday 21 November 2026 in one image

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/thesathing/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/thesathing/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A one-page newspaper front page that sums up Saturday 21 November 2026 in
a single image: 36 stories across 7 regions, drawn as original vector art
with Pillow. No network access, no clock, no unseeded randomness — every
run writes identical bytes.

## What is on the page

- **Leads:** COP31 runs overtime in Antalya · Houthis fire on Riyadh,
  three intercepted · 6.7 quake shakes Peru's Andes (USGS magnitude 6.7).
- **Features:** Kryvyi Rih double-tap (2 killed, 42 hurt) · FBI database
  reportedly hacked · Air Niugini 767 emergency landing at Davao, all 146
  safe · Gen Z protests in 25 European countries · cancer pill trial ·
  Iran downs a US MQ-9 · Indonesia forest fires · Bayer $7.25bn deal ·
  Malawi fuel crisis · Cyclone Xavier.
- **23 more stories** in the briefs column, plus a world map with 13 pins
  and a DATE CHECK box that names the big stories that are *not* 21 Nov
  news (Thursday 19 Nov items, and Friday 20 Nov items such as Wall
  Street's fall into correction, the Kyiv bridge barrage and the Poland
  missile).

## Region tally (36 stories)

Pictured 13 — EUROPE 4 (COP31, Kryvyi Rih, Berlin, London), AMERICAS 3
(Peru, Washington, United States), MIDEAST 2 (Riyadh, Hormuz),
ASIA-PACIFIC 2 (Davao, Indonesia), AFRICA 1 (Malawi), OCEANIA 1 (Xavier).
Briefs 23 — EUROPE 5 (Madrid, Copenhagen, Kerch, Brussels, Turin),
AMERICAS 5 (Port-au-Prince, Washington ×2, Caracas, Cleveland),
ASIA-PACIFIC 3 (India, Pyongyang, Dhaka), MIDEAST 3 (Hormuz, Gaza,
Baghdad), AFRICA 2 (Johannesburg, Blantyre), OCEANIA 2 (Cook Islands,
Melbourne), WORLD 3 (Riemann hypothesis, Las Vegas GP, Kyiv fertiliser
plant). Totals: EUROPE 9, AMERICAS 8, ASIA-PACIFIC 5, MIDEAST 5,
AFRICA 3, OCEANIA 3, WORLD 3 = 36.

## Build

```sh
python3 poster/build_poster_v4.py   # writes entry.png (1024x1024, <=1 MiB)
```

Then run `main.ts` to copy `entry.png` into `$MAKEFUN_OUTPUT_DIR`.

## License

MIT — see LICENSE.
