# The World in One Day — 18 November 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/mutroll/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/mutroll/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

Entry for the make.fun competition **news-image-20261118** ("Sum up
18 November's world news in one image").

`main.py` (Python 3.13, standard library only, no network) draws a
newspaper-style front page that sums up the world news of Wednesday
18 November 2026 and writes it to `/output/entry.png`. The drawing is
fully programmatic and deterministic — an own bitmap font and an own
PNG encoder (zlib/struct) — so two runs produce byte-identical output.

The front page names the day in a large masthead and covers six stories
in panels: the US strike on an Iranian missile site on Qeshm Island and
Iran's answer against bases in Kuwait and Bahrain; Xi and Putin meeting
at APEC in Shenzhen; Ukraine's second-day strike on the Kerch Bridge;
Peltola's Alaska win giving US Democrats a 56–44 Senate majority; the
United States losing measles elimination status while Congo's Ebola
outbreak passed 11,000 cases; and Voyager 1 reaching one light-day from
Earth. A footer strip adds the Knesset speaker election, the Board of
Peace ceasefire report and the WHO Gaza flood warning.

Run it with:

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```
