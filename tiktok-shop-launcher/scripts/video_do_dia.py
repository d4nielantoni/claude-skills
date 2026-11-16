#!/usr/bin/env python3
"""Daily posting flow: build the video + caption file for one day of the posting agenda.

Usage:
    python3 video_do_dia.py AGENDA.json            # today's entry
    python3 video_do_dia.py AGENDA.json 2026-11-20 # a given day
    python3 video_do_dia.py AGENDA.json --todos    # every entry that has no video yet

AGENDA.json:
{
  "raiz": "~/Downloads/Fotos Anuncios TikTok",      # relative paths below start here
  "saida": "Videos para postar/Agenda diaria",        # where videos + txt are written
  "produtos": {
    "globo": {"anuncio": "Globo de Neve ...", "nome_curto": "Globo Castelo Luminoso",
              "fotos": "NOVOS/n23-globo - .../2 - fotos para o anuncio"}
  },
  "dias": [
    {"data": "2026-11-14", "produto": "globo", "video": "Videos para postar/Flow - mao mostrando/14 - ....mp4",
     "video_ate": 5, "slides": [[null, "Hook"], ["04 - foto4_ambiente.jpg", "Texto"], ["07 - foto7_presente.jpg", "CTA", true]],
     "legenda": "Post caption", "hashtags": "#natal #..."}
  ]
}
Slide photos are file names inside the product's "fotos" folder (or a path relative to "raiz").
Each photo slide lasts 3.2 s; keep the total above 10 s (TikTok missions count videos > 10 s).
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from montar_video import montar  # noqa: E402

DUR = 3.2


def caminho(raiz, base, nome):
    if nome is None:
        return None
    for c in (os.path.join(raiz, base or "", nome), os.path.join(raiz, nome)):
        if os.path.exists(c):
            return c
    raise SystemExit(f"Arquivo não encontrado: {nome}")


def nome_arquivo(dia, prod):
    d = datetime.date.fromisoformat(dia["data"])
    return f"{d:%m-%d} - {prod['nome_curto']}"


def gerar(ag, dia):
    raiz = os.path.expanduser(ag["raiz"])
    prod = ag["produtos"][dia["produto"]]
    pasta = os.path.join(raiz, ag["saida"])
    base = os.path.join(pasta, nome_arquivo(dia, prod))
    slides = []
    for s in dia["slides"]:
        foto, leg = s[0], s[1]
        escuro = s[2] if len(s) > 2 else False
        slides.append([caminho(raiz, prod["fotos"], foto), leg, escuro, 0 if foto is None else DUR])
    cfg = {"saida": base + ".mp4", "slides": slides}
    if dia.get("video"):
        cfg["video"] = caminho(raiz, None, dia["video"])
        cfg["video_ate"] = dia.get("video_ate", 5)
    montar(cfg)
    texto = (
        f"DATA: {dia['data']} (postar entre 18h e 21h)\n\n"
        f"PRODUTO PARA VINCULAR\n{prod['anuncio']}\n\n"
        f"NOME CURTO (máx. 30 letras)\n{prod['nome_curto']}\n\n"
        f"LEGENDA (Descrição)\n{dia['legenda']}\n\n"
        f"HASHTAGS\n{dia['hashtags']}\n\n"
        f"CONTEÚDO GERADO POR IA: {'ligar' if dia.get('ia', True) else 'não precisa'}\n"
    )
    with open(base + ".txt", "w") as f:
        f.write(texto)
    return base + ".mp4"


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) > 1 else 1)
    ag = json.load(open(os.path.expanduser(sys.argv[1])))
    alvo = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
    raiz = os.path.expanduser(ag["raiz"])
    if alvo == "--todos":
        for dia in ag["dias"]:
            mp4 = os.path.join(raiz, ag["saida"], nome_arquivo(dia, ag["produtos"][dia["produto"]]) + ".mp4")
            if not os.path.exists(mp4):
                print(gerar(ag, dia))
        return
    dias = [d for d in ag["dias"] if d["data"] == alvo]
    if not dias:
        raise SystemExit(f"Nenhum vídeo na agenda para {alvo}")
    for dia in dias:
        print(gerar(ag, dia))


if __name__ == "__main__":
    main()
