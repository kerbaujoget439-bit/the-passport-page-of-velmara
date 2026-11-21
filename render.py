#!/usr/bin/env python3
"""Render the passport spread of the Republic of Velmara, a country that
does not exist, as a single 1024x1024 PNG.

Left page: visas and endorsements, with entry/exit stamps that tell one
coherent travel story. Right page: the data page, with portrait, personal
details and a machine-readable zone whose figures agree with the printed
fields (ICAO check digits included).

All lettering is drawn with real fonts through PIL, so every word is clean
and legible. Run:  python3 render.py   -> writes entry.png beside this file.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAGE = 512  # width of one page of the spread

FONTS = "/usr/share/fonts/truetype"
SERIF = f"{FONTS}/liberation/LiberationSerif-Regular.ttf"
SERIF_B = f"{FONTS}/liberation/LiberationSerif-Bold.ttf"
SERIF_I = f"{FONTS}/liberation/LiberationSerif-Italic.ttf"
SANS = f"{FONTS}/liberation/LiberationSans-Regular.ttf"
SANS_B = f"{FONTS}/liberation/LiberationSans-Bold.ttf"
MONO = f"{FONTS}/dejavu/DejaVuSansMono.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- palette
PAPER = (246, 243, 233)
PAPER_SHADE = (238, 233, 218)
NAVY = (27, 48, 92)
NAVY_SOFT = (52, 74, 118)
GOLD = (168, 138, 74)
INK = (38, 38, 40)
LABEL = (96, 96, 100)
RULE = (178, 172, 156)
RED_NUM = (158, 34, 40)
GUARD = (172, 192, 208)  # pale guilloche blue


# ---------------------------------------------------------------- helpers
def text_c(draw, cx, y, s, fnt, fill, spacing=0):
    """Draw text centred on cx at y, with optional letter spacing."""
    if spacing:
        widths = [draw.textlength(ch, font=fnt) for ch in s]
        total = sum(widths) + spacing * (len(s) - 1)
        x = cx - total / 2
        for ch, w in zip(s, widths):
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += w + spacing
        return total
    w = draw.textlength(s, font=fnt)
    draw.text((cx - w / 2, y), s, font=fnt, fill=fill)
    return w


def text_l(draw, x, y, s, fnt, fill, spacing=0):
    if spacing:
        for ch in s:
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += draw.textlength(ch, font=fnt) + spacing
        return x
    draw.text((x, y), s, font=fnt, fill=fill)
    return x + draw.textlength(s, font=fnt)


def field(draw, x, y, label_en, label_vel, value, value_font=None, w=272):
    """One data-page field: bilingual small label over a ruled value line."""
    draw.text((x, y), label_en.upper(), font=font(SANS_B, 12), fill=LABEL)
    lw = draw.textlength(label_en.upper(), font=font(SANS_B, 12))
    draw.text((x + lw + 6, y + 1), "/ " + label_vel, font=font(SERIF_I, 12),
              fill=LABEL)
    draw.text((x, y + 17), value, font=value_font or font(SANS_B, 21), fill=INK)
    draw.line([x, y + 47, x + w, y + 47], fill=RULE, width=1)


def check_digit(s):
    """ICAO 9303 check digit, weights 7-3-1."""
    vals = {c: i for i, c in enumerate("0123456789")}
    vals.update({c: 10 + i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")})
    vals["<"] = 0
    total = sum(vals[c] * w for c, w in zip(s, [7, 3, 1] * 20))
    return str(total % 10)


def mrz_lines():
    doc = "VM4829917"
    dob, expiry = "880314", "310603"
    line1 = ("P<VEL" + "AURELL<<MAREN<ILSE").ljust(44, "<")
    personal = "<" * 14
    core = (doc + check_digit(doc) + "VEL" + dob + check_digit(dob) + "F"
            + expiry + check_digit(expiry) + personal
            + check_digit(personal))
    line2 = core + check_digit(core)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- emblem
def draw_emblem(draw, cx, cy, r, colour=NAVY, lw=3):
    """The arms of Velmara: a harbour lantern above two waves, in a ring."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=colour, width=lw)
    draw.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
                 outline=colour, width=1)
    s = r / 34.0  # scale unit
    # lantern cap and base
    draw.polygon([(cx - 9 * s, cy - 14 * s), (cx + 9 * s, cy - 14 * s),
                  (cx + 4 * s, cy - 19 * s), (cx - 4 * s, cy - 19 * s)],
                 outline=colour, width=max(2, int(2 * s)))
    draw.line([cx, cy - 19 * s, cx, cy - 23 * s], fill=colour, width=max(2, int(2 * s)))
    draw.ellipse([cx - 2.2 * s, cy - 25 * s, cx + 2.2 * s, cy - 21 * s],
                 outline=colour, width=max(1, int(1.6 * s)))
    # lantern body with a lit window
    draw.rectangle([cx - 8 * s, cy - 13 * s, cx + 8 * s, cy + 6 * s],
                   outline=colour, width=max(2, int(2 * s)))
    draw.rectangle([cx - 4.5 * s, cy - 9 * s, cx + 4.5 * s, cy + 2 * s],
                   fill=(233, 183, 76))
    draw.line([cx - 12 * s, cy + 9 * s, cx + 12 * s, cy + 9 * s],
              fill=colour, width=max(2, int(2 * s)))
    # waves
    for k, yy in enumerate((15 * s, 21 * s)):
        pts = []
        for i in range(25):
            px = cx - 14 * s + i * (28 * s / 24)
            py = cy + yy + math.sin(i / 24 * math.pi * 2 + k * 1.4) * 2.2 * s
            pts.append((px, py))
        draw.line(pts, fill=colour, width=max(1, int(1.8 * s)))


# ---------------------------------------------------------------- portrait
def draw_portrait(w=300, h=380):
    """A flat, clean portrait illustration in a passport-photo frame."""
    img = Image.new("RGB", (w, h), (216, 226, 234))
    d = ImageDraw.Draw(img)
    for i in range(h):  # gentle studio backdrop
        t = i / h
        c = tuple(int((216 - 26 * t) + (t) * j) for j in (0, 4, 8))
        d.line([0, i, w, i], fill=(int(216 - 22 * t), int(226 - 18 * t),
                                  int(234 - 12 * t)))
    cx = w // 2
    skin = (232, 190, 148)
    skin_sh = (214, 168, 124)
    hair = (74, 52, 38)
    # shoulders / coat
    d.polygon([(cx - 118, h), (cx - 96, h - 96), (cx - 40, h - 118),
               (cx + 40, h - 118), (cx + 96, h - 96), (cx + 118, h)],
              fill=(52, 74, 84))
    d.polygon([(cx - 30, h), (cx, h - 108), (cx + 30, h)], fill=(240, 238, 232))
    d.polygon([(cx - 8, h), (cx, h - 92), (cx + 8, h)], fill=(120, 44, 48))
    # neck
    d.rectangle([cx - 17, h - 168, cx + 17, h - 104], fill=skin_sh)
    # hair behind the face (bob cut)
    d.ellipse([cx - 74, 34, cx + 74, 268], fill=hair)
    d.rectangle([cx - 74, 150, cx + 74, 262], fill=hair)
    # face
    d.ellipse([cx - 56, 62, cx + 56, 232], fill=skin)
    # fringe
    d.pieslice([cx - 58, 40, cx + 58, 138], 180, 360, fill=hair)
    d.rectangle([cx - 58, 84, cx + 58, 96], fill=hair)
    # brows and eyes
    for sgn in (-1, 1):
        ex = cx + sgn * 27
        d.arc([ex - 13, 128, ex + 13, 142], 190, 340, fill=(70, 50, 36), width=3)
        d.ellipse([ex - 10, 148, ex + 10, 159], fill=(255, 255, 255))
        d.ellipse([ex - 5, 149, ex + 5, 159], fill=(52, 40, 34))
        d.ellipse([ex - 2, 151, ex + 2, 156], fill=(16, 12, 10))
    # nose and mouth
    d.line([cx + 1, 162, cx - 3, 182], fill=skin_sh, width=3)
    d.line([cx - 6, 184, cx + 5, 184], fill=skin_sh, width=3)
    d.arc([cx - 15, 190, cx + 15, 210], 15, 165, fill=(166, 92, 84), width=4)
    # faint laminate lines, as on a real data page
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for yy in range(6, h, 9):
        od.line([0, yy, w, yy], fill=(255, 255, 255, 14))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


# ---------------------------------------------------------------- stamps
def _ink_layer(size, colour, alpha=215):
    lay = Image.new("RGBA", size, (0, 0, 0, 0))
    return lay, ImageDraw.Draw(lay), colour + (alpha,)


def rect_stamp(lines, colour, w=208, h=88):
    """Rectangular border-post stamp; lines = [(text, font, dy), ...]."""
    lay, d, ink = _ink_layer((w + 8, h + 8), colour)
    d.rectangle([3, 3, w + 4, h + 4], outline=ink, width=4)
    d.rectangle([9, 9, w - 2, h - 2], outline=ink, width=1)
    y = 13
    for s, fnt, dy in lines:
        text_c(d, (w + 8) // 2, y, s, fnt, ink)
        y += dy
    return lay


def oval_stamp(lines, colour, w=216, h=118):
    lay, d, ink = _ink_layer((w + 8, h + 8), colour)
    d.ellipse([3, 3, w + 4, h + 4], outline=ink, width=4)
    d.ellipse([10, 10, w - 3, h - 3], outline=ink, width=1)
    y = 20
    for s, fnt, dy in lines:
        text_c(d, (w + 8) // 2, y, s, fnt, ink)
        y += dy
    return lay


def round_stamp(lines, colour, r=64):
    size = 2 * r + 10
    lay, d, ink = _ink_layer((size, size), colour)
    d.ellipse([3, 3, size - 4, size - 4], outline=ink, width=4)
    d.ellipse([10, 10, size - 11, size - 11], outline=ink, width=1)
    y = r - 34
    for s, fnt, dy in lines:
        text_c(d, size // 2, y, s, fnt, ink)
        y += dy
    return lay


def paste_stamp(page, stamp, cx, cy, angle):
    stamp = stamp.rotate(angle, expand=True, resample=Image.BICUBIC)
    page.alpha_composite(stamp, (int(cx - stamp.width / 2),
                                  int(cy - stamp.height / 2)))


BLUE = (39, 66, 148)
PURPLE = (104, 58, 148)
GREEN = (34, 110, 74)

SB = lambda s: font(SANS_B, s)  # stamp bold
SR = lambda s: font(SANS, s)    # stamp regular


def left_page():
    """Visas and endorsements page (the left half of the spread)."""
    pg = Image.new("RGBA", (PAGE, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(pg)
    # faint printed frame and a watermark emblem
    d.rectangle([16, 16, PAGE - 17, H - 17], outline=GUARD + (120,), width=2)
    wm = Image.new("RGBA", (340, 340), (0, 0, 0, 0))
    draw_emblem(ImageDraw.Draw(wm), 170, 170, 150, colour=NAVY + (26,), lw=8)
    pg.alpha_composite(wm, (86, 560))

    text_c(d, PAGE // 2, 44, "VISAS", font(SERIF_B, 27), NAVY, spacing=6)
    text_c(d, PAGE // 2, 82, "VÉLAN · ENDORSEMENTS · OBSERVATIONS",
           font(SANS, 12.5), NAVY_SOFT, spacing=1)
    d.line([56, 112, PAGE - 56, 112], fill=GOLD, width=2)

    # printed endorsement: the one detail that reveals the country
    d.rectangle([44, 132, PAGE - 44, 268], fill=(240, 236, 222, 255),
                outline=NAVY_SOFT, width=1)
    text_l(d, 62, 146, "OBSERVATION", font(SANS_B, 13), NAVY)
    body = [
        "The bearer is a registered Keeper of a Harbour",
        "Lantern and is exempt from the Fog Tax in all",
        "Velmaran ports. Lantern Permit No 2214, issued",
        "at Port Serein, must be carried during the Fog",
        "Season (November to February).",
    ]
    y = 172
    for line in body:
        d.text((62, y), line, font=font(SERIF, 16.5), fill=INK)
        y += 22
    # small green fee stamp overlapping the box corner
    fee = rect_stamp([("FOG TAX", SB(15), 19), ("PAID · 12 SOL", SB(13), 0)],
                     GREEN, w=132, h=52)
    paste_stamp(pg, fee, 392, 268, -7)

    # entry / exit stamps: one coherent travel history
    kord = [("KORDAVIA", SB(17), 21), ("VESK BORDER POST", SR(11), 16)]
    paste_stamp(pg, rect_stamp(kord + [("ARRIVED", SB(14), 18),
                                       ("17 SEP 2022", SB(15), 0)], BLUE),
                150, 356, -4)
    paste_stamp(pg, rect_stamp(kord + [("DEPARTED", SB(14), 18),
                                       ("29 SEP 2022", SB(15), 0)], BLUE),
                368, 348, 3)
    bran = [("BRANNOCK ISLES", SB(15), 20), ("FERRY TERMINAL", SR(11), 17)]
    paste_stamp(pg, oval_stamp(bran + [("ARRIVED", SB(14), 19),
                                       ("04 MAY 2023", SB(15), 0)], PURPLE),
                158, 500, 5)
    paste_stamp(pg, oval_stamp(bran + [("DEPARTED", SB(14), 19),
                                       ("11 MAY 2023", SB(15), 0)], PURPLE),
                362, 512, -6)
    paste_stamp(pg, round_stamp([("VELMARA", SB(14), 18),
                                 ("PORT SEREIN", SR(10.5), 15),
                                 ("DEPARTED", SB(12), 16),
                                 ("21 OCT 2024", SB(12.5), 0)], NAVY),
                138, 668, 8)
    paste_stamp(pg, rect_stamp(kord + [("ARRIVED", SB(14), 18),
                                       ("22 OCT 2024", SB(15), 0)], BLUE),
                356, 664, -2)
    paste_stamp(pg, round_stamp([("VELMARA", SB(14), 18),
                                 ("PORT SEREIN", SR(10.5), 15),
                                 ("ARRIVED", SB(12), 16),
                                 ("03 NOV 2024", SB(12.5), 0)], NAVY),
                250, 822, -5)

    d.text((36, H - 40), "12", font=font(SERIF, 15), fill=LABEL)
    text_c(d, PAGE // 2, H - 40, "REPUBLIC OF VELMARA",
           font(SANS, 10.5), LABEL, spacing=2)
    return pg


# ---------------------------------------------------------------- data page
def right_page():
    pg = Image.new("RGBA", (PAGE, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(pg)
    d.rectangle([16, 16, PAGE - 17, H - 17], outline=GUARD + (120,), width=2)

    MX = 40            # left margin inside the page
    RX = PAGE - 40     # right margin

    draw_emblem(d, PAGE // 2, 84, 44)
    text_c(d, PAGE // 2, 142, "REPUBLIC OF VELMARA", font(SERIF_B, 27), NAVY,
           spacing=2)
    text_c(d, PAGE // 2, 178, "PASSPORT", font(SERIF_B, 23), NAVY, spacing=10)
    text_c(d, PAGE // 2, 210, "VELPÁS · TRAVEL DOCUMENT", font(SANS, 11.5),
           NAVY_SOFT, spacing=2)
    d.line([MX, 240, RX, 240], fill=GOLD, width=2)

    # type / code / number row
    d.text((MX, 254), "TYPE / TIP", font=font(SANS_B, 11), fill=LABEL)
    d.text((MX, 272), "P", font=font(SANS_B, 20), fill=INK)
    d.text((MX + 92, 254), "CODE / CÓD", font=font(SANS_B, 11), fill=LABEL)
    d.text((MX + 92, 272), "VEL", font=font(SANS_B, 20), fill=INK)
    d.text((MX + 196, 254), "PASSPORT No / No VELPÁS",
           font=font(SANS_B, 11), fill=LABEL)
    d.text((MX + 196, 270), "VM 482 9917", font=font(SANS_B, 22), fill=RED_NUM)

    # portrait, with a small ghost image further down the page
    photo = draw_portrait()
    photo = photo.resize((150, 190), Image.LANCZOS)
    pg.paste(photo, (MX, 316))
    d.rectangle([MX, 316, MX + 150, 506], outline=NAVY_SOFT, width=2)
    ghost = draw_portrait().resize((56, 71), Image.LANCZOS).convert("RGBA")
    ghost.putalpha(56)
    pg.alpha_composite(ghost, (RX - 56, 660))

    FX = MX + 172  # fields column, right of the portrait
    FW = RX - FX
    field(d, FX, 312, "Surname", "Atan", "AURELL", w=FW)
    field(d, FX, 372, "Given names", "Vélan", "MAREN ILSE", w=FW)
    field(d, FX, 432, "Nationality", "Nacional", "VELMARAN", w=FW)

    field(d, MX, 528, "Date of birth", "Data násca", "14 MAR 1988", w=196)
    field(d, MX + 224, 528, "Sex", "Ses", "F", w=60)
    field(d, MX + 312, 528, "Personal No", "No pers.", "2214-88", w=120)
    field(d, MX, 592, "Place of birth", "Lógo násca", "PORT SEREIN", w=196)
    field(d, MX + 224, 592, "Height", "Altura", "168 CM", w=88)
    field(d, MX + 340, 592, "Eyes", "Ólos", "GREY", w=92)

    field(d, MX, 656, "Date of issue", "Data émis", "03 JUN 2021", w=196)
    field(d, MX + 224, 656, "Date of expiry", "Data fin", "03 JUN 2031",
          w=208)
    d.text((MX, 720), "AUTHORITY / AUTORIDAD", font=font(SANS_B, 11),
           fill=LABEL)
    d.text((MX, 738), "MINISTRY OF THE INTERIOR — PORT SEREIN",
           font=font(SANS_B, 15.5), fill=INK)
    d.line([MX, 764, RX, 764], fill=RULE, width=1)

    d.text((MX, 780), "HOLDER'S SIGNATURE / FIRMA", font=font(SANS_B, 11),
           fill=LABEL)
    sig = Image.new("RGBA", (240, 56), (0, 0, 0, 0))
    ImageDraw.Draw(sig).text((6, 8), "M. Aurell", font=font(SERIF_I, 34),
                             fill=(24, 34, 84, 235))
    pg.alpha_composite(sig.rotate(2.5, expand=True, resample=Image.BICUBIC),
                       (MX + 6, 796))
    d.line([MX, 856, MX + 220, 856], fill=RULE, width=1)
    d.text((RX - 128, 780), "PAGE 2", font=font(SANS, 11), fill=LABEL)

    # machine-readable zone
    d.rectangle([0, 892, PAGE, H], fill=(240, 238, 228, 255))
    d.line([0, 892, PAGE, 892], fill=RULE, width=1)
    line1, line2 = mrz_lines()
    mf = font(MONO, 16)
    for row, line in enumerate((line1, line2)):
        x = 36.0
        step = (PAGE - 72) / 44
        for ch in line:
            d.text((x, 916 + row * 44), ch, font=mf, fill=(20, 20, 20))
            x += step
    return pg


# ---------------------------------------------------------------- compose
def guilloche(size):
    """Pale interlaced sine curves, the classic passport background print."""
    lay = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    w, h = size
    for base in range(-40, h + 40, 26):
        pts = []
        for x in range(0, w + 8, 8):
            y = base + math.sin(x / 150.0) * 13 + math.sin(x / 47.0) * 4
            pts.append((x, y))
        d.line(pts, fill=GUARD + (44,), width=1)
    for base in range(-40, h + 40, 34):
        pts = []
        for x in range(0, w + 8, 8):
            y = base + math.sin(x / 210.0 + 2.0) * 17
            pts.append((x, y))
        d.line(pts, fill=(196, 178, 150, 30), width=1)
    return lay


def build():
    spread = Image.new("RGBA", (W, H), PAPER + (255,))
    spread.alpha_composite(guilloche((W, H)), (0, 0))
    spread.alpha_composite(left_page(), (0, 0))
    spread.alpha_composite(right_page(), (PAGE, 0))

    # book gutter shadow down the middle, and a soft outer shade
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(26):
        a = int(66 * (1 - i / 26))
        sd.line([PAGE - 26 + i, 0, PAGE - 26 + i, H], fill=(30, 26, 20, a))
        sd.line([PAGE + i, 0, PAGE + i, H], fill=(30, 26, 20, int(a * 0.55)))
    sd.rectangle([0, 0, W - 1, H - 1], outline=(30, 26, 20, 90), width=2)
    spread.alpha_composite(sh)

    img = spread.convert("RGB")
    img.save(OUT, optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
