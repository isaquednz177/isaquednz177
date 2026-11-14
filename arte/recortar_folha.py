"""Recorta as peças da folha de artes do Isaque (arte/folha-artes.png) para o README.

- tira o fundo quase preto da folha (vira transparente, com o brilho vermelho preservado);
- deixa os quatro títulos com a mesma largura (estica só as linhas entre os ornamentos);
- corrige o "SOL" do certificado de banco de dados para "SQL";
- apaga os números de exemplo do painel de estatísticas (o estatisticas.py escreve os de verdade).

Uso:  python arte/recortar_folha.py      (grava em arte/pecas/)
Mudou a folha? Suba a VERSAO: o cache do GitHub guarda as imagens pelo nome.
"""
import os

import cv2
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont

VERSAO = 1
PASTA = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(PASTA, "pecas")

PECAS = {  # caixa de cada peça na folha (x0, y0, x1, y1)
    "botao-linkedin": (40, 5, 250, 190), "botao-email": (275, 5, 485, 190), "botao-instagram": (510, 5, 720, 190),
    "titulo-sobre": (12, 195, 812, 293), "titulo-estudos": (828, 195, 1525, 293),
    "titulo-certificados": (12, 300, 832, 395), "titulo-contribuicoes": (855, 300, 1525, 395),
    "certificado-sql": (15, 402, 442, 657), "certificado-claude": (443, 402, 862, 657),
    "painel-estatisticas": (880, 395, 1522, 657), "rodape": (12, 745, 1524, 980),
}
# trechos só de linha reta em cada título (esquerda e direita), medidos na peça já recortada
TRECHOS = {
    "titulo-sobre": ((130, 240), (560, 660)), "titulo-estudos": ((140, 240), (495, 595)),
    "titulo-certificados": ((125, 235), (575, 690)), "titulo-contribuicoes": ((128, 185), (515, 572)),
}
# números de exemplo do painel (na folha): caixa de cada um
NUMEROS_PAINEL = [(1056, 477, 1117, 505), (1340, 476, 1357, 503), (1011, 569, 1030, 596),
                  (1218, 569, 1237, 597), (1402, 569, 1421, 597)]
O_DO_SOL = (218, 466, 233, 484)  # o "O" de "SOL", na primeira linha do título do certificado


def fonte_pil(tam):
    """Cormorant Garamond 500 para o PIL (que não lê woff2)."""
    caminho = os.path.join(SAIDA, "_cormorant.ttf")
    if not os.path.exists(caminho):
        f = TTFont(os.path.join(PASTA, "fontes", "cormorant-garamond-latin.woff2"))
        f = instantiateVariableFont(f, {"wght": 500})
        f.flavor = None
        f.save(caminho)
    return ImageFont.truetype(caminho, tam)


def apagar(arr, caixas, folga=3):
    """Pinta por cima das caixas com o fundo em volta (inpaint)."""
    mascara = np.zeros(arr.shape[:2], np.uint8)
    for x0, y0, x1, y1 in caixas:
        mascara[y0 - folga:y1 + folga + 1, x0 - folga:x1 + folga + 1] = 255
    bgr = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(cv2.inpaint(bgr, mascara, 5, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB).astype(float)


def trocar_o_por_q(arr):
    x0, y0, x1, y1 = O_DO_SOL
    creme = arr[y0:y1, x0:x1]
    cor = tuple(int(v) for v in np.median(creme[creme.max(axis=2) > 170], axis=0))
    arr = apagar(arr, [O_DO_SOL], folga=1)
    k = 4  # desenha grande e reduz, para a borda sair suave
    camada = Image.new("L", ((x1 - x0 + 14) * k, (y1 - y0 + 14) * k), 0)
    fonte = fonte_pil(25 * k)
    d = ImageDraw.Draw(camada)
    l, t, r, b = d.textbbox((0, 0), "O", font=fonte)
    # o Q fica no mesmo lugar do O: mesma esquerda e mesma linha de base
    d.text((-l + 2 * k, -t + 2 * k), "Q", font=fonte, fill=255)
    escala = (y1 - y0) / ((b - t) / k)
    camada = camada.resize((round(camada.width / k * escala), round(camada.height / k * escala)), Image.LANCZOS)
    a = np.asarray(camada).astype(float)[..., None] / 255
    h, w = a.shape[:2]
    oy, ox = y0 - 2, x0 - 2
    a[:, x1 + 1 - ox:] = 0  # a cauda do Q para antes do L
    arr[oy:oy + h, ox:ox + w] = arr[oy:oy + h, ox:ox + w] * (1 - a) + np.array(cor) * a
    return arr


def recortar(arr, bg, nome, box):
    x0, y0, x1, y1 = box
    c = arr[y0:y1, x0:x1]
    diff = np.clip(c - bg, 0, None).max(axis=2)
    if nome == "rodape":
        # silhuetas pretas encostam no fundo: o rodapé é um retângulo até a linha de baixo,
        # com o céu se desfazendo no alto
        forma = np.zeros(diff.shape, np.uint8)
        forma[:972 - y0, 18 - x0:1518 - x0] = 1
        a = np.where(forma > 0, 1.0, np.clip(diff / 38, 0, 1))
        rampa = np.clip(np.arange(diff.shape[0]) / 34, 0, 1)[:, None]
        a = np.maximum(a * rampa, np.clip(diff / 38, 0, 1))
    else:
        escuro = (diff < 9).astype(np.uint8)
        _, lab = cv2.connectedComponents(escuro, connectivity=4)
        borda = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        fundo = np.isin(lab, list(borda)) & (escuro > 0)
        forma = cv2.erode((~fundo).astype(np.uint8), np.ones((5, 5), np.uint8))
        a = np.clip(diff / 38, 0, 1)
        a[forma > 0] = 1
        a = cv2.GaussianBlur(a, (0, 0), .6)
        a[forma > 0] = 1
    cor = bg + (c - bg) / np.maximum(a, 1e-3)[..., None]
    im = Image.fromarray(np.dstack([np.clip(cor, 0, 255), a * 255]).astype(np.uint8), "RGBA")
    bb = Image.fromarray((a > .04).astype(np.uint8) * 255).getbbox()
    return im.crop((max(bb[0] - 2, 0), max(bb[1] - 2, 0), bb[2] + 2, bb[3] + 2))


def esticar(im, trechos, largura):
    """Alarga o título esticando só os dois trechos de linha reta, metade em cada."""
    falta = largura - im.width
    (a0, a1), (b0, b1) = trechos
    ea, eb = falta // 2, falta - falta // 2
    partes = [im.crop((0, 0, a0, im.height)),
              im.crop((a0, 0, a1, im.height)).resize((a1 - a0 + ea, im.height), Image.BICUBIC),
              im.crop((a1, 0, b0, im.height)),
              im.crop((b0, 0, b1, im.height)).resize((b1 - b0 + eb, im.height), Image.BICUBIC),
              im.crop((b1, 0, im.width, im.height))]
    novo = Image.new("RGBA", (largura, im.height))
    x = 0
    for p in partes:
        novo.paste(p, (x, 0))
        x += p.width
    return novo


def main():
    os.makedirs(SAIDA, exist_ok=True)
    arr = np.asarray(Image.open(os.path.join(PASTA, "folha-artes.png")).convert("RGB")).astype(float)
    bg = np.median(np.concatenate([arr[985:1020, 20:1500].reshape(-1, 3), arr[20:60, 760:1500].reshape(-1, 3)]), axis=0)
    arr = trocar_o_por_q(arr)
    arr = apagar(arr, NUMEROS_PAINEL)
    pecas = {nome: recortar(arr, bg, nome, box) for nome, box in PECAS.items()}
    maior = max(pecas[n].width for n in TRECHOS)
    altura = max(pecas[n].height for n in TRECHOS)
    for n, t in TRECHOS.items():
        pecas[n] = esticar(pecas[n], t, maior).resize((maior, altura), Image.LANCZOS)
    for nome, im in pecas.items():
        if nome == "painel-estatisticas":
            # moldura do painel: vai embutida no SVG do estatisticas.py; guarda também a origem dos números
            im.save(os.path.join(SAIDA, f"{nome}.webp"), quality=90, method=6)
        else:
            im.save(os.path.join(SAIDA, f"{nome}-v{VERSAO}.png"), optimize=True)
        print(nome, im.size)
    os.remove(os.path.join(SAIDA, "_cormorant.ttf"))


if __name__ == "__main__":
    main()
