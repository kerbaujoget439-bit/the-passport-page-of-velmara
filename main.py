#!/usr/bin/env python3
"""Entry point for "The Passport Page of a Country That Isn't There".

Writes the passport spread of the invented Republic of Velmara to
/output/entry.png. The image itself is rendered by render.py (Pillow)
and shipped beside this file as entry.png; this program only places it,
using nothing but the standard library, so it runs in any sandbox.

The spread it writes: on the right, the data page of Maren Ilse Aurell of
Port Serein, with portrait, ghost image and a machine-readable zone whose
check digits agree with the printed fields; on the left, the visas page
with an endorsement for a Keeper of a Harbour Lantern and the entry and
exit stamps of two journeys to Kordavia and one to the Brannock Isles,
every date after the passport's issue and before its expiry.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
DEST = os.path.join("/output", "entry.png")


def main():
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    shutil.copyfile(SOURCE, DEST)
    print("wrote", DEST, os.path.getsize(DEST), "bytes")


if __name__ == "__main__":
    main()
