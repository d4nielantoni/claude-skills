#!/usr/bin/env python3
"""Save the 7 chosen Flow images into the product folder with the shop's numbering,
and (optionally) copy them to the upload folder as <code>_0N.jpg.

Usage:
    python3 save_photos.py --src WORK/n24 \
        --product "~/Downloads/Fotos Anuncios TikTok/NOVOS/n24-gato - Gato articulado" \
        --picks flow_n24_4 flow_n24_r_1 flow_n24_3 flow_n24_r_0 flow_n24_0 flow_n24_1 flow_n24_5 \
        [--code n24-gato --upload "~/Downloads/Fotos Anuncios TikTok/NOVOS/_upload_central_midia"]

--picks are 7 file names (with or without extension) from --src, in slot order:
1 principal, 2 ângulo, 3 detalhe, 4 ambiente, 5 medidas, 6 escala, 7 presente. Use "-" to leave a slot
untouched (e.g. when redoing only one photo).
"""
import argparse
import glob
import os
import shutil

SLOTS = ["01 - foto1_principal", "02 - foto2_angulo", "03 - foto3_detalhe", "04 - foto4_ambiente",
         "05 - foto5_medidas", "06 - foto6_escala", "07 - foto7_presente"]


def achar(src, nome):
    p = os.path.join(src, nome)
    if os.path.isfile(p):
        return p
    c = glob.glob(p + ".*")
    if len(c) != 1:
        raise SystemExit(f"não achei (ou ambíguo) {nome} em {src}: {c}")
    return c[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True)
    ap.add_argument("--product", required=True, help="product folder (nXX-code - Nome)")
    ap.add_argument("--picks", nargs=7, required=True)
    ap.add_argument("--code", help="product code, e.g. n24-gato (needed with --upload)")
    ap.add_argument("--upload", help="upload folder; copies <code>_0N.jpg there")
    a = ap.parse_args()

    src = os.path.expanduser(a.src)
    destino = os.path.join(os.path.expanduser(a.product), "2 - fotos para o anuncio")
    os.makedirs(destino, exist_ok=True)
    for slot, pick in zip(SLOTS, a.picks):
        if pick == "-":
            continue
        shutil.copy(achar(src, pick), os.path.join(destino, slot + ".jpg"))
    print(sorted(os.listdir(destino)))

    if a.upload:
        if not a.code:
            raise SystemExit("--upload precisa de --code")
        up = os.path.expanduser(a.upload)
        os.makedirs(up, exist_ok=True)
        for i, slot in enumerate(SLOTS, 1):
            f = os.path.join(destino, slot + ".jpg")
            if os.path.exists(f):
                shutil.copy(f, os.path.join(up, f"{a.code}_0{i}.jpg"))
        print("upload:", sorted(x for x in os.listdir(up) if x.startswith(a.code + "_")))


if __name__ == "__main__":
    main()
