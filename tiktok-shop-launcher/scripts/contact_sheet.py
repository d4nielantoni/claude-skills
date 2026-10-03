#!/usr/bin/env python3
"""Collect downloaded images into a folder and build one labelled contact sheet to review them at once.

Usage:
    python3 contact_sheet.py --dir WORK/n24 --collect "~/Downloads/flow_n24_*.jpeg"
    python3 contact_sheet.py --dir WORK/ref            # just build the sheet

--collect moves the matching files into --dir first (Flow downloads land in ~/Downloads).
The sheet is written next to the folder as <dir>_sheet.jpg (or --out) and the path is printed,
so it can be opened with the Read tool. Labels are the file names, used later by save_photos.py.
"""
import argparse
import glob
import os
import shutil

from PIL import Image, ImageDraw

EXTS = (".jpg", ".jpeg", ".png", ".webp")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True, help="folder with the images (created if missing)")
    ap.add_argument("--collect", help="glob of files to move into --dir first, e.g. ~/Downloads/flow_n24_*.jpeg")
    ap.add_argument("--out", help="sheet path (default: <dir>_sheet.jpg)")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--thumb", type=int, default=400, help="thumbnail size in px")
    a = ap.parse_args()

    pasta = os.path.expanduser(a.dir).rstrip("/")
    os.makedirs(pasta, exist_ok=True)
    if a.collect:
        for f in glob.glob(os.path.expanduser(a.collect)):
            shutil.move(f, os.path.join(pasta, os.path.basename(f)))

    fs = sorted(f for f in glob.glob(os.path.join(pasta, "*")) if f.lower().endswith(EXTS))
    if not fs:
        raise SystemExit(f"nenhuma imagem em {pasta}")
    th, cols = a.thumb, a.cols
    rows = (len(fs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * th, rows * (th + 20)), "white")
    d = ImageDraw.Draw(sheet)
    for k, f in enumerate(fs):
        im = Image.open(f).convert("RGB")
        im.thumbnail((th, th))
        x, y = (k % cols) * th, (k // cols) * (th + 20)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + th + 4), os.path.basename(f), fill="black")
    out = os.path.expanduser(a.out) if a.out else pasta + "_sheet.jpg"
    sheet.save(out, quality=80)
    print(len(fs), out)


if __name__ == "__main__":
    main()
