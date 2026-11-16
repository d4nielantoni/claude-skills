#!/usr/bin/env python3
"""Status board for the photo → publish pipeline (see references/subagents.md).

Usage:
    python3 fila.py --novos "~/Downloads/Fotos Anuncios TikTok/NOVOS" n50-cupulaespiral n51-elyra ...
    python3 fila.py --novos "<NOVOS>" --desde n50      # every product from n50 up

For each product prints: base photo, Flow prompt, listing text, 7 upload photos, TikTok ID,
and the next step (fotografo / publicador / pronto).
"""
import argparse
import glob
import os
import re


def pasta_de(novos, code):
    c = glob.glob(os.path.join(novos, code + " - *"))
    return c[0] if c else None


def estado(novos, code):
    p = pasta_de(novos, code)
    if not p:
        return dict(code=code, erro="pasta não encontrada")
    up = os.path.join(novos, "_upload_central_midia")
    fotos = sum(os.path.exists(os.path.join(up, f"{code}_0{i}.jpg")) for i in range(1, 8))
    anuncio = os.path.join(p, "anuncio.txt")
    txt = open(anuncio).read() if os.path.exists(anuncio) else ""
    m = re.search(r"ID do produto:\s*(\d+)", txt)
    st = re.findall(r"Status em [^:]+:\s*(.+)", txt)
    e = dict(code=code,
             base=os.path.exists(os.path.join(p, f"base_{code}.jpg")),
             prompt=os.path.exists(os.path.join(p, "prompt_flow.txt")),
             textos="TÍTULO DO ANÚNCIO" in txt,
             fotos=fotos,
             id=m.group(1) if m else "",
             status=st[-1].strip() if st else "")
    if e["id"]:
        e["proximo"] = "pronto"
    elif fotos == 7 and e["textos"]:
        e["proximo"] = "publicador"
    elif e["base"] and e["prompt"]:
        e["proximo"] = "fotografo"
    else:
        e["proximo"] = "orquestrador (fase 1/5)"
    return e


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--novos", required=True)
    ap.add_argument("--desde", help="include every nXX folder with number >= this (e.g. n50)")
    ap.add_argument("codes", nargs="*")
    a = ap.parse_args()
    novos = os.path.expanduser(a.novos)
    codes = list(a.codes)
    if a.desde:
        lim = int(a.desde.lstrip("n"))
        for d in sorted(os.listdir(novos)):
            m = re.match(r"(n(\d+)-[^ ]+) - ", d)
            if m and int(m.group(2)) >= lim and m.group(1) not in codes:
                codes.append(m.group(1))
    print(f"{'produto':24} base prompt textos fotos  id                   próximo")
    for c in codes:
        e = estado(novos, c)
        if "erro" in e:
            print(f"{c:24} {e['erro']}")
            continue
        sim = lambda b: " ok " if b else " -- "
        print(f"{c:24}{sim(e['base'])} {sim(e['prompt'])}  {sim(e['textos'])}  {e['fotos']}/7  "
              f"{(e['id'] or '-'):20} {e['proximo']}{(' (' + e['status'] + ')') if e['status'] else ''}")


if __name__ == "__main__":
    main()
