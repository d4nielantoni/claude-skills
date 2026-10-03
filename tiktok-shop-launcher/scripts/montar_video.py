#!/usr/bin/env python3
"""Build the final TikTok posting video (1080x1920, 30 fps, no audio):
[optional Flow clip] + photo slides with captions, each over a blurred copy of itself.

Usage:
    python3 montar_video.py config.json

config.json:
{
  "saida": "/path/Para postar - versao final/15 - Gato articulado.mp4",
  "video": "/path/Flow - mao mostrando/15 - Gato articulado (mao).mp4",   # optional, null for photo-only
  "video_ate": 2.5,                       # optional: keep only the first N seconds of the clip
  "slides": [
    [null, "Hook caption shown over the clip", false, 0],            # first item = clip caption when "video" is set
    ["/path/01 - foto1_principal.jpg", "Benefit caption", false, 3.0],
    ["/path/04 - foto4_ambiente.jpg", "", false, 3.0],
    ["/path/07 - foto7_presente.jpg", "Presente geek certeiro", true, 3.0],   # true = dark caption box
    ["/path/02 - foto2_angulo.jpg", "Toque na sacola laranja e garanta o seu", false, 3.0]
  ]
}
Without "video", the first slide is a normal photo slide (use the hook caption on it).
Aim for 16–22 s total: TikTok's Start-Up mission only counts shoppable videos longer than 15 s.
Veo clips from square photos come letterboxed; black bars are detected, cropped and replaced by blur.
"""
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
FONTES = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
          "/Library/Fonts/Arial Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FONT = next((f for f in FONTES if os.path.exists(f)), None)
LEGENDA_Y = 250  # caption top; photos start at (1920-1000)/2 = 460, so captions never cover them


def fonte(tam):
    return ImageFont.truetype(FONT, tam) if FONT else ImageFont.load_default()


def quebrar(draw, texto, font, largura_max):
    linhas, atual = [], ""
    for p in texto.split():
        teste = (atual + " " + p).strip()
        if draw.textlength(teste, font=font) <= largura_max or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    linhas.append(atual)
    return linhas


def caixa_texto(draw, texto, y, escuro=False, tam=58, largura_max=900):
    font = fonte(tam)
    linhas = quebrar(draw, texto, font, largura_max)
    if len(linhas) > 1:
        # balance the lines so no single word is left alone on the last line
        alvo = draw.textlength(texto, font=font) / len(linhas) + 40
        while alvo < largura_max and len(quebrar(draw, texto, font, alvo)) > len(linhas):
            alvo += 20
        linhas = quebrar(draw, texto, font, alvo)
    alt_linha = tam + 14
    fundo, cor = ((20, 20, 20), (255, 255, 255)) if escuro else ((255, 255, 255), (0, 0, 0))
    for i, ln in enumerate(linhas):
        w = draw.textlength(ln, font=font)
        x0, yy = (W - w) / 2, y + i * alt_linha
        draw.rounded_rectangle([x0 - 22, yy - 8, x0 + w + 22, yy + tam + 8], radius=14, fill=fundo)
        draw.text((x0, yy - 2), ln, font=font, fill=cor)


def fundo_desfocado(img):
    bg = img.copy().convert("RGB")
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1))
    x, y = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(40))
    return Image.blend(bg, Image.new("RGB", (W, H), (0, 0, 0)), 0.15)


def quadro_foto(foto, legenda, escuro, destino):
    img = Image.open(foto).convert("RGB")
    tela = fundo_desfocado(img)
    lado = 1000
    im = img.resize((lado, int(img.height * lado / img.width)))
    tela.paste(im, ((W - lado) // 2, (H - im.height) // 2))
    if legenda:
        caixa_texto(ImageDraw.Draw(tela), legenda, LEGENDA_Y, escuro)
    tela.save(destino, quality=95)


def sobreposicao_legenda(legenda, destino):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if legenda:
        caixa_texto(ImageDraw.Draw(ov), legenda, LEGENDA_Y, False)
    ov.save(destino)


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        raise SystemExit(f"ffmpeg falhou:\n{r.stderr[-1500:]}")


def clipe_foto(img, dur, destino, zoom_in=True):
    n = int(dur * FPS)
    z = f"1+0.06*on/{n}" if zoom_in else f"1.06-0.06*on/{n}"
    run(["ffmpeg", "-y", "-loop", "1", "-i", img, "-vf",
         f"scale={W*2}:{H*2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p",
         "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "20", destino])


def clipe_video(mp4, legenda, destino, tmp, ate=None):
    probe = subprocess.run(["ffmpeg", "-i", mp4, "-vf", "cropdetect=24:2:0", "-f", "null", "-"],
                           stderr=subprocess.PIPE, text=True).stderr
    crops = [l.split("crop=")[1].split()[0] for l in probe.splitlines() if "crop=" in l]
    c = f"crop={crops[-1]}," if crops else ""
    ov = os.path.join(tmp, "leg.png")
    sobreposicao_legenda(legenda, ov)
    fc = (f"[0:v]{c}split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40[bg];"
          f"[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps={FPS}[v];[v][1:v]overlay=0:0,format=yuv420p")
    corte = ["-t", str(ate)] if ate else []
    run(["ffmpeg", "-y", *corte, "-i", mp4, "-i", ov, "-filter_complex", fc, "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", destino])


def montar(cfg):
    tmp = tempfile.mkdtemp()
    partes = []
    slides = cfg["slides"]
    if cfg.get("video"):
        p = os.path.join(tmp, "v.mp4")
        clipe_video(os.path.expanduser(cfg["video"]), slides[0][1], p, tmp, cfg.get("video_ate"))
        partes.append(p)
        slides = slides[1:]
    for i, (foto, leg, escuro, dur) in enumerate(slides):
        img = os.path.join(tmp, f"s{i}.jpg")
        quadro_foto(os.path.expanduser(foto), leg, escuro, img)
        p = os.path.join(tmp, f"s{i}.mp4")
        clipe_foto(img, dur, p, zoom_in=(i % 2 == 0))
        partes.append(p)
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as f:
        f.writelines(f"file '{p}'\n" for p in partes)
    saida = os.path.expanduser(cfg["saida"])
    os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c:v", "libx264", "-preset", "medium",
         "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", saida])
    return saida


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) == 2 else 1)
    print(montar(json.load(open(os.path.expanduser(sys.argv[1])))))
