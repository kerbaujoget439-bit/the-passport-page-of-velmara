[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/kerbaujoget439-bit/the-passport-page-of-velmara/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/kerbaujoget439-bit/the-passport-page-of-velmara/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

An entry for the make.fun bounty of the same name. `main.py` writes one
image to `/output/entry.png`: an open passport spread of the **Republic of
Velmara**, a small fog-bound harbour country that does not exist.

- **Right — the data page.** Portrait and ghost image of Maren Ilse Aurell
  of Port Serein, bilingual Velmaran/English field labels, and a
  machine-readable zone whose ICAO check digits agree with the printed
  dates and document number.
- **Left — visas and endorsements.** A printed observation records that the
  bearer is a Keeper of a Harbour Lantern, exempt from the Fog Tax, and the
  stamps tell one consistent story: Kordavia in September 2022, the
  Brannock Isles in May 2023, and out of Port Serein again in October 2024 —
  no stamp before the passport was issued, none after it expires.

`render.py` draws the spread with Pillow (real fonts throughout, so every
word is legible) and produces the shipped `entry.png`; `main.py` itself
needs only the standard library. Velmara, Kordavia and the Brannock Isles
are invented; any resemblance to a real document is the point of the
exercise, and none of them will get you through a border.
