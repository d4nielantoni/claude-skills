#!/usr/bin/env python3
"""Write the listing text (anuncio.txt, in each product folder) and the posting text
(<num> - <video>.txt, next to the final video) for a batch of products.

Usage:
    python3 gerar_textos.py produtos.json \
        --novos "~/Downloads/Fotos Anuncios TikTok/NOVOS" \
        --videos "~/Downloads/Fotos Anuncios TikTok/Videos para postar/Para postar - versao final"

produtos.json is a list of objects (see references/tiktok-shop.md for a full example):
  code, pasta, num, video, titulo, nome_curto (<=30 chars), desc (intro + "• " bullets),
  criador (or credito to override the whole credit line), site (default "MakerWorld"),
  preco, peso (g), cx [comprimento, largura, altura] (cm), legenda, tags, extras, atencao (optional)

The made-to-order footer below is the shop's current wording. The user asked to keep
"impresso em 3D" out of IMAGE/VIDEO PROMPTS; listing text still uses it. To drop it from listings
too, edit RODAPE here and the "Material:" bullet in each product's desc.
"""
import argparse
import json
import os

RODAPE = ("Peça produzida sob encomenda em impressora 3D: pequenas marcas de camada fazem parte do processo. "
          "Não indicado para menores de 3 anos (contém partes pequenas).")


def credito(p):
    if p.get("credito"):
        return p["credito"]
    criador = p.get("criador", "")
    site = p.get("site", "MakerWorld")
    # Seller Center strips non-Latin characters (e.g. Chinese names), so fall back to a generic credit
    if not criador or not criador.isascii():
        return f"Modelo 3D de designer da {site}, com licença comercial."
    return f"Modelo 3D por {criador} ({site}), licença comercial."


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("produtos")
    ap.add_argument("--novos", required=True)
    ap.add_argument("--videos", required=True)
    a = ap.parse_args()
    novos, videos = os.path.expanduser(a.novos), os.path.expanduser(a.videos)
    os.makedirs(videos, exist_ok=True)

    for p in json.load(open(os.path.expanduser(a.produtos))):
        assert len(p["nome_curto"]) <= 30, f"nome_curto > 30: {p['nome_curto']}"
        desc = p["desc"] + "\n\n" + RODAPE + "\n\n" + credito(p)
        c, l, h = p["cx"]
        preco = f"{p['preco']:.2f}".replace(".", ",")
        atencao = f"\n{p['atencao']}\n" if p.get("atencao") else ""
        anuncio = (f"TÍTULO DO ANÚNCIO\n{p['titulo']}\n\nDESCRIÇÃO\n{desc}\n\n"
                   f"PREÇO SUGERIDO: R$ {preco}\nPESO COM EMBALAGEM (estimado): {p['peso']} g\n"
                   f"CAIXA (estimada): {c} x {l} x {h} cm\n"
                   f"FOTOS: pasta \"2 - fotos para o anuncio\" (7 fotos, na ordem)\n{atencao}")
        with open(os.path.join(novos, p["pasta"], "anuncio.txt"), "w") as f:
            f.write(anuncio)
        post = (f"PRODUTO PARA VINCULAR NO VÍDEO\n{p['titulo']}\n\nNOME CURTO (máx. 30 letras)\n{p['nome_curto']}\n\n"
                f"LEGENDA DO VÍDEO (copie e cole na Descrição)\n{p['legenda']}\n\n"
                f"HASHTAGS SUGERIDAS (copie e cole no campo Hashtags)\n{p['tags']}\n\n"
                f"HASHTAGS EXTRAS (opcional, troque alguma das de cima se quiser)\n{p['extras']}\n\n"
                f"DESCRIÇÃO DO PRODUTO (a mesma do anúncio, para consulta)\n{desc}\n{atencao}")
        with open(os.path.join(videos, f"{p['num']} - {p['video']}.txt"), "w") as f:
            f.write(post)
        print("ok", p["code"])


if __name__ == "__main__":
    main()
