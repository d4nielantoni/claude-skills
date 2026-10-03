#!/usr/bin/env python3
"""Measure the real size of every object on a 3MF build plate (Bambu Studio / MakerWorld) or in an STL.

Usage:
    python3 bbox3mf.py model.3mf [part.stl ...]

Prints, per build item, the bounding box in cm (X, Y, Z) with the object name stored by Bambu Studio.
Z is the printed height. Components and their transforms are resolved, so assembled parts report
their real size. numpy may print "divide by zero / overflow in matmul" warnings on macOS — they are
harmless (Accelerate false positives) and are silenced here.
"""
import argparse
import re
import sys
import warnings
import xml.etree.ElementTree as ET
import zipfile

import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)

NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
PNS = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}"


def matriz(s):
    """3MF transform string -> 4x4 matrix (row-vector convention: p' = p @ m)."""
    if not s:
        return np.eye(4)
    v = [float(x) for x in s.split()]
    m = np.eye(4)
    m[:3, :3] = np.array(v[:9]).reshape(3, 3)
    m[3, :3] = v[9:12]
    return m


def medir(caminho):
    z = zipfile.ZipFile(caminho)
    cache = {}

    def carregar(path):
        path = path.lstrip("/")
        if path not in cache:
            root = ET.fromstring(z.read(path))
            cache[path] = (root, {o.get("id"): o for o in root.iter(NS + "object")})
        return cache[path]

    def vertices(path, oid, M):
        _, objs = carregar(path)
        o = objs[oid]
        pts = []
        mesh = o.find(NS + "mesh")
        if mesh is not None:
            v = np.array([[float(x.get("x")), float(x.get("y")), float(x.get("z")), 1.0]
                          for x in mesh.find(NS + "vertices")])
            pts.append((v @ M)[:, :3])
        comps = o.find(NS + "components")
        if comps is not None:
            for c in comps:
                p = c.get(PNS + "path") or path
                pts.extend(vertices(p, c.get("objectid"), matriz(c.get("transform")) @ M))
        return pts

    root, objs = carregar("3D/3dmodel.model")
    nomes = {oid: (o.get("name") or "") for oid, o in objs.items()}
    try:  # Bambu keeps the friendly names here
        cfg = z.read("Metadata/model_settings.config").decode()
        for m in re.finditer(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]*)"', cfg):
            nomes[m.group(1)] = m.group(2)
    except KeyError:
        pass

    resultado = []
    for it in root.find(NS + "build"):
        oid = it.get("objectid")
        P = np.vstack(vertices("3D/3dmodel.model", oid, matriz(it.get("transform"))))
        d = (P.max(0) - P.min(0)) / 10
        resultado.append((oid, nomes.get(oid, ""), d))
    return resultado


def medir_stl(caminho):
    """Binary or ASCII STL -> one bounding box (Printables files often come as STL)."""
    import struct
    dados = open(caminho, "rb").read()
    n = struct.unpack("<I", dados[80:84])[0] if len(dados) >= 84 else 0
    if len(dados) == 84 + n * 50 and n:
        tri = np.frombuffer(dados[84:], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n)
        P = tri["v"].reshape(-1, 3)
    else:
        P = np.array([[float(x) for x in l.split()[1:4]] for l in dados.decode(errors="ignore").splitlines()
                      if l.strip().startswith("vertex")])
    return [("stl", "", (P.max(0) - P.min(0)) / 10)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arquivos", nargs="+", help=".3mf or .stl files")
    a = ap.parse_args()
    for f in a.arquivos:
        print(f"== {f}")
        try:
            for oid, nome, d in (medir_stl(f) if f.lower().endswith(".stl") else medir(f)):
                print(f"obj {oid:>4} {nome[:40]:40s} X={d[0]:.1f} Y={d[1]:.1f} Z={d[2]:.1f} cm")
        except Exception as e:  # keep going with the other files
            print(f"   erro: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
