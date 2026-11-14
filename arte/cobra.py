"""Põe a cobrinha dos commits (gerada pelo Platane/snk) dentro da moldura do dragão.

Camadas: moldura (arte/pecas/cobra-moldura.webp) → grade e cobrinha de verdade → dragão por cima
(arte/pecas/cobra-dragao.webp). As duas artes saem do arte/preparar_cobra.py.

Uso:  python arte/cobra.py dist/snake-sangue.svg dist/cobra-v1.svg
"""
import base64
import os
import re
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
W, H = 2155, 347                     # tamanho da moldura
K = 1951 / 844                       # escala: a grade do snk (844 de largura) no lugar da grade da arte
GRADE_X, GRADE_Y = 102, 60           # onde fica a 1ª célula (que no snk está em x=2, y=2)
VISTA = (-8, -8, 860, 124)           # pedaço do snk que aparece: a grade e uma folga para a cobra (sem a barra de baixo)
DRAGAO = (141, 160, 370, 187)        # x, y, largura, altura


def embutir(nome):
    with open(os.path.join(PASTA, "pecas", nome), "rb") as f:
        return "data:image/webp;base64," + base64.b64encode(f.read()).decode()


def montar(snk):
    m = re.search(r"<svg[^>]*>(.*)</svg>\s*$", snk, re.S)
    if not m:
        raise ValueError("o arquivo do snk não parece um SVG")
    miolo = re.sub(r"<desc>.*?</desc>", "", m.group(1), flags=re.S)
    vx, vy, vw, vh = VISTA
    x = GRADE_X - (2 - vx) * K
    y = GRADE_Y - (2 - vy) * K
    dx, dy, dw, dh = DRAGAO
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="contribuições do último ano, com a cobrinha comendo os commits">
<image href="{embutir('cobra-moldura.webp')}" width="{W}" height="{H}"/>
<svg x="{x:.1f}" y="{y:.1f}" width="{vw * K:.1f}" height="{vh * K:.1f}" viewBox="{vx} {vy} {vw} {vh}" overflow="hidden">{miolo}</svg>
<image href="{embutir('cobra-dragao.webp')}" x="{dx}" y="{dy}" width="{dw}" height="{dh}"/>
</svg>
"""


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        svg = montar(f.read())
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(svg)
    print("ok", sys.argv[2], len(svg) // 1024, "KB")
