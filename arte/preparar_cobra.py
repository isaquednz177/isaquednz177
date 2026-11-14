"""Prepara a moldura da cobrinha a partir da arte do Isaque (arte/cobra-arte.png).

Gera em arte/pecas/:
  cobra-moldura.webp  a moldura com a grade de exemplo apagada (a grade de verdade entra por cima)
  cobra-dragao.webp   só o dragão (inteiro)
  dragao-*.webp       o dragão em camadas para a animação: asa, corpo, rabo, ponta do rabo e cabeça
                      (todas do mesmo tamanho; os cortes se sobrepõem uns pixels, para não aparecer emenda)

Uso:  python arte/preparar_cobra.py   (precisa de opencv-python; a automação usa só o arte/cobra.py)
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

PASTA = os.path.dirname(os.path.abspath(__file__))
CORTE = (9, 180, 2164, 527)        # a moldura dentro da arte (o resto é transparente)
DRAGAO = (150, 340, 520, 527)      # caixa do dragão
QUADRADOS_ACESOS = (490, 448, 610, 490)
GRADE = (95, 238, 2080, 500)
LINHA_DE_BAIXO = 497                # a borda vermelha da moldura começa aqui


def dragao(arr):
    x0, y0, x1, y1 = DRAGAO
    c = arr[y0:y1, x0:x1, :3].astype(int)
    r, g = c[..., 0], c[..., 1]
    # o corpo na sombra é bem escuro; as células vazias da grade ficam abaixo de R 52
    forte = ((r > 60) & (r > 2.0 * g)).astype(np.uint8)
    forte[LINHA_DE_BAIXO - y0:] = 0
    qx0, qy0, qx1, qy1 = QUADRADOS_ACESOS
    forte[max(qy0 - y0, 0):qy1 - y0, max(qx0 - x0, 0):qx1 - x0] = 0
    forte = cv2.morphologyEx(forte, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(forte, connectivity=8)
    # asas, corpo e rabo saem em pedaços: fica tudo que é grande (os pontinhos de brilho, não)
    grandes = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > 300]
    m = np.isin(lab, grandes).astype(np.uint8)
    # tapa os buracos (escamas escuras) por dentro do contorno
    cont, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cheio = np.zeros_like(m)
    cv2.drawContours(cheio, cont, -1, 1, -1)
    m = cv2.erode(np.maximum(m, cheio), np.ones((2, 2), np.uint8))
    a = cv2.GaussianBlur(m.astype(float), (0, 0), 1.0)
    out = np.dstack([arr[y0:y1, x0:x1, :3], (a * 255).astype(np.uint8)])
    return Image.fromarray(out, "RGBA"), (m > 0), (x0, y0)


# cortes do dragão (em pixels da arte recortada, 370 x 187)
LINHA_ASA = [(98, 101), (140, 83), (168, 79), (190, 67), (197, 60), (203, 45), (226, 40)]  # a asa fica acima
CORTE_RABO, CORTE_PONTA, CORTE_CABECA = 138, 92, 262  # x de cada corte


def rampa(x, a, b):
    """1 antes de a, 0 depois de b (corte suave)."""
    return np.clip((b - x) / (b - a), 0, 1)


def camadas(drag):
    d = np.asarray(drag).astype(float)
    h, w = d.shape[:2]
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(72, 0), (226, 0)] + LINHA_ASA[::-1] + [(72, 40)], fill=255)
    asa = np.asarray(m).astype(float) / 255
    x = np.arange(w)[None, :].repeat(h, 0).astype(float)
    a = d[..., 3] / 255
    resto = a * (1 - asa)
    alfas = {
        "asa": a * asa,
        "ponta": resto * rampa(x, CORTE_PONTA - 4, CORTE_PONTA + 4),
        "rabo": resto * rampa(x, CORTE_RABO - 4, CORTE_RABO + 4) * (1 - rampa(x, CORTE_PONTA - 8, CORTE_PONTA)),
        "corpo": resto * (1 - rampa(x, CORTE_RABO - 8, CORTE_RABO)) * rampa(x, CORTE_CABECA, CORTE_CABECA + 8),
        "cabeca": a * (1 - rampa(x, CORTE_CABECA - 6, CORTE_CABECA + 2)),
    }
    return {n: Image.fromarray(np.dstack([d[..., :3], np.clip(al, 0, 1) * 255]).astype(np.uint8), "RGBA")
            for n, al in alfas.items()}


def moldura(arr, mascara_dragao, origem):
    x0, y0, x1, y1 = GRADE
    rgb = arr[..., :3].astype(np.uint8).copy()
    r = rgb[..., 0].astype(int)
    m = np.zeros(r.shape, np.uint8)
    m[y0:y1, x0:x1] = (r[y0:y1, x0:x1] > 30).astype(np.uint8)
    qx0, qy0, qx1, qy1 = QUADRADOS_ACESOS
    m[qy0:qy1, qx0:qx1] = 1
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    dx, dy = origem
    h, w = mascara_dragao.shape
    m[dy:dy + h, dx:dx + w] |= cv2.dilate(mascara_dragao.astype(np.uint8), np.ones((9, 9), np.uint8))
    m[:y0] = 0; m[y1:] = 0; m[:, :x0] = 0; m[:, x1:] = 0
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    limpo = cv2.cvtColor(cv2.inpaint(bgr, m * 255, 7, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    return Image.fromarray(np.dstack([limpo, arr[..., 3]]), "RGBA")


def main():
    arr = np.asarray(Image.open(os.path.join(PASTA, "cobra-arte.png")).convert("RGBA"))
    drag, mascara, origem = dragao(arr)
    mold = moldura(arr, mascara, origem)
    saida = os.path.join(PASTA, "pecas")
    mold.crop(CORTE).save(os.path.join(saida, "cobra-moldura.webp"), quality=88, method=6)
    drag.save(os.path.join(saida, "cobra-dragao.webp"), quality=92, method=6)
    for nome, im in camadas(drag).items():
        im.save(os.path.join(saida, f"dragao-{nome}.webp"), quality=92, method=6)
    print("moldura", mold.crop(CORTE).size, "dragão", drag.size, "em", origem)


if __name__ == "__main__":
    main()
