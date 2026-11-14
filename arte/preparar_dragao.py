"""Prepara os quadros do dragão voando (arte do Isaque, em arte/dragao-quadros/quadro-1..6.webp).

Os quadros vêm com o dragão em lugares um pouco diferentes: aqui eles são alinhados pelo olho
(o ponto mais vermelho da cabeça), recortados todos do mesmo tamanho e reduzidos para o README.
Saída: arte/pecas/dragao-voo-1..6.webp e, no fim, a posição do olho e da boca para o cobra.py.

Uso:  python arte/preparar_dragao.py
"""
import glob
import os

import numpy as np
from PIL import Image

PASTA = os.path.dirname(os.path.abspath(__file__))
LARGURA = 260  # px de cada quadro final (o dragão aparece com uns 90 px no README; o dobro para telas finas)


def olho(im):
    a = np.asarray(im).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    nota = (r - g - b) * (al > 200)
    nota[:, : im.width * 7 // 10] = 0  # a cabeça fica à direita
    y, x = np.unravel_index(nota.argmax(), nota.shape)
    return x, y


def main():
    arquivos = sorted(glob.glob(os.path.join(PASTA, "dragao-quadros", "quadro-*.webp")))
    quadros = [Image.open(f).convert("RGBA") for f in arquivos]
    olhos = [olho(q) for q in quadros]
    ref = olhos[0]
    folga = max(q.width for q in quadros)
    alinhados = []
    for q, (ox, oy) in zip(quadros, olhos):
        c = Image.new("RGBA", (folga * 2, folga * 2))
        c.paste(q, (folga // 2 + ref[0] - ox, folga // 2 + ref[1] - oy))
        alinhados.append(c)
    caixa = None
    for c in alinhados:
        bb = c.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
        caixa = bb if caixa is None else (min(caixa[0], bb[0]), min(caixa[1], bb[1]), max(caixa[2], bb[2]), max(caixa[3], bb[3]))
    w, h = caixa[2] - caixa[0], caixa[3] - caixa[1]
    k = LARGURA / w
    tam = (LARGURA, round(h * k))
    for i, c in enumerate(alinhados, 1):
        c.crop(caixa).resize(tam, Image.LANCZOS).save(os.path.join(PASTA, "pecas", f"dragao-voo-{i}.webp"), quality=85, method=6)
    ex, ey = (folga // 2 + ref[0] - caixa[0]) * k, (folga // 2 + ref[1] - caixa[1]) * k
    # a boca fica à frente e um pouco abaixo do olho (medido no quadro 1)
    bx, by = ex + 30 * k, ey + 10 * k
    print(f"quadros {tam[0]}x{tam[1]}  olho ({ex:.1f}, {ey:.1f})  boca ({bx:.1f}, {by:.1f})")


if __name__ == "__main__":
    main()
