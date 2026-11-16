#!/usr/bin/env python3
"""Build a 1080x1920 posting video that KEEPS the audio (Flow/Veo narration).

Usage:
    python3 montar_narrado.py config.json

config.json:
{
  "saida": "/path/Agenda diaria/Petisqueira narrada.mp4",
  "partes": [
    {"foto": "/path/04 - foto4_ambiente.jpg", "legenda": "Hook", "dur": 3.2},     # silent photo slide
    {"video": "/path/cena1.mp4", "legenda": "Caption over the clip"},             # clip with its own audio
    {"video": "/path/cena2.mp4", "legenda": "Toque na sacola!", "escuro": true, "ate": 7.9}
  ]
}
Optional "crop": "720:720:0:280" per clip keeps only the real picture (Veo 9:16 clips made from a square
photo come back with a blurred band on top and a dark band below; detection misses it).
Letterboxed Veo clips are cropped and placed over a blurred copy of themselves (same look as montar_video.py).
Photo slides get a silent audio track so the parts concatenate cleanly.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from montar_video import FPS, H, W, caixa_texto, clipe_foto, quadro_foto, run  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

AUDIO = ["-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]


def legenda_png(texto, escuro, destino):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if texto:
        caixa_texto(ImageDraw.Draw(ov), texto, 250, escuro)
    ov.save(destino)


def parte_video(p, destino, tmp, i):
    src = os.path.expanduser(p["video"])
    probe = subprocess.run(["ffmpeg", "-i", src, "-vf", "cropdetect=24:2:0", "-f", "null", "-"],
                           stderr=subprocess.PIPE, text=True).stderr
    crops = [l.split("crop=")[1].split()[0] for l in probe.splitlines() if "crop=" in l]
    c = f"crop={crops[-1]}," if crops else ""
    if p.get("crop"):  # Veo often pads a square start frame with blur on top and dark bars below
        c = f"crop={p['crop']},"
    ov = os.path.join(tmp, f"leg{i}.png")
    legenda_png(p.get("legenda", ""), p.get("escuro", False), ov)
    tem_audio = "audio" in subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
                                           "-of", "csv=p=0", src], stdout=subprocess.PIPE, text=True).stdout
    fc = (f"[0:v]{c}split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40[bg];"
          f"[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps={FPS}[v];[v][1:v]overlay=0:0,format=yuv420p[vo]")
    corte = ["-t", str(p["ate"])] if p.get("ate") else []
    entradas = [*corte, "-i", src, "-i", ov]
    mapa = ["-map", "[vo]"]
    if tem_audio:
        mapa += ["-map", "0:a"]
    else:
        entradas += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        mapa += ["-map", "2:a", "-shortest"]
    run(["ffmpeg", "-y", *entradas, "-filter_complex", fc, *mapa,
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", *AUDIO, destino])


def parte_foto(p, destino, tmp, i):
    img = os.path.join(tmp, f"f{i}.jpg")
    quadro_foto(os.path.expanduser(p["foto"]), p.get("legenda", ""), p.get("escuro", False), img)
    mudo = os.path.join(tmp, f"m{i}.mp4")
    clipe_foto(img, p.get("dur", 3.2), mudo, zoom_in=(i % 2 == 0))
    run(["ffmpeg", "-y", "-i", mudo, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-c:v", "copy", *AUDIO, "-shortest", destino])


def montar(cfg):
    tmp = tempfile.mkdtemp()
    partes = []
    for i, p in enumerate(cfg["partes"]):
        d = os.path.join(tmp, f"p{i}.mp4")
        (parte_video if "video" in p else parte_foto)(p, d, tmp, i)
        partes.append(d)
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as f:
        f.writelines(f"file '{p}'\n" for p in partes)
    saida = os.path.expanduser(cfg["saida"])
    os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c:v", "libx264", "-preset", "medium",
         "-crf", "21", "-pix_fmt", "yuv420p", *AUDIO, "-movflags", "+faststart", saida])
    return saida


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) == 2 else 1)
    print(montar(json.load(open(os.path.expanduser(sys.argv[1])))))
