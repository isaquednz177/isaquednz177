"""Põe a cobrinha dos commits (gerada pelo Platane/snk) dentro da moldura do dragão.

O dragão (arte/pecas/cobra-dragao.webp) faz o papel da cobra: segue o caminho da cabeça dela,
vira para o lado em que está indo e bate as asas (sobe e desce de leve) enquanto voa.
A moldura (arte/pecas/cobra-moldura.webp) e o dragão saem do arte/preparar_cobra.py.

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
VISTA = (-8, -8, 860, 124)           # pedaço do snk em que a grade se encaixa (a barra de progresso fica de fora)
DRAGAO_PX = (370, 187)               # tamanho da arte do dragão
BOCA_PX = (352, 104)                 # onde fica a boca na arte
DRAGAO_LARGURA = 96                  # largura do dragão em unidades do snk (uma célula = 16)


def embutir(nome):
    with open(os.path.join(PASTA, "pecas", nome), "rb") as f:
        return "data:image/webp;base64," + base64.b64encode(f.read()).decode()


def caminho_da_cabeca(estilo):
    """[(porcentagem, x, y)] da cabeça da cobra, em ordem."""
    m = re.search(r"@keyframes s0\{(.*?\})\}", estilo, re.S)
    if not m:
        raise ValueError("não achei o caminho da cobra (@keyframes s0) no SVG do snk")
    pontos = []
    for pcts, x, y in re.findall(r"([\d.,%]+)\{transform:translate\((-?[\d.]+)px,(-?[\d.]+)px\)\}", m.group(1)):
        for p in pcts.split(","):
            pontos.append((float(p.rstrip("%")), float(x), float(y)))
    return sorted(pontos)


def viradas(pontos):
    """Keyframes que espelham o dragão quando ele vai para a esquerda (e desvira para a direita)."""
    lado, quadros = 1, []
    for (p, x, _), (_, x2, _) in zip(pontos, pontos[1:]):
        if x2 != x:
            lado = 1 if x2 > x else -1
        # espelha em volta do centro da célula (x = 8)
        quadros.append(f"{p:g}%{{transform:{'none' if lado == 1 else 'matrix(-1,0,0,1,16,0)'}}}")
    return "@keyframes vira{" + "".join(quadros) + "}"


def montar(snk):
    m = re.search(r"<svg[^>]*>(.*)</svg>\s*$", snk, re.S)
    if not m:
        raise ValueError("o arquivo do snk não parece um SVG")
    miolo = re.sub(r"<desc>.*?</desc>", "", m.group(1), flags=re.S)
    duracao = re.search(r"\.s\{[^}]*?(\d+)ms", miolo).group(1)
    pontos = caminho_da_cabeca(miolo)
    # some com os quadradinhos da cobra: quem anda agora é o dragão
    miolo = re.sub(r'<rect class="s s\d+"[^>]*/>', "", miolo)
    dw = DRAGAO_LARGURA
    dh = dw * DRAGAO_PX[1] / DRAGAO_PX[0]
    bx, by = BOCA_PX[0] * dw / DRAGAO_PX[0], BOCA_PX[1] * dh / DRAGAO_PX[1]
    estilo = (f"<style>{viradas(pontos)}"
              f".vira{{animation:vira {duracao}ms step-end infinite}}"
              "@keyframes voo{0%,100%{transform:translateY(-1.3px)}50%{transform:translateY(1.3px)}}"
              ".voo{animation:voo 900ms ease-in-out infinite}"
              "@media (prefers-reduced-motion:reduce){.voo{animation:none}}</style>")
    # a boca fica um pouco à frente do centro da célula (8, 8), como se mordesse o commit
    dragao = (f'<g class="s s0"><g class="vira"><g class="voo">'
              f'<image href="{embutir("cobra-dragao.webp")}" x="{12 - bx:.1f}" y="{8 - by:.1f}" width="{dw}" height="{dh:.1f}"/>'
              f"</g></g></g>")
    vx, vy, vw, vh = VISTA
    x = GRADE_X - (2 - vx) * K
    y = GRADE_Y - (2 - vy) * K
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="contribuições do último ano, com um dragão comendo os commits">
<image href="{embutir('cobra-moldura.webp')}" width="{W}" height="{H}"/>
<svg x="{x:.1f}" y="{y:.1f}" width="{vw * K:.1f}" height="{vh * K:.1f}" viewBox="{vx} {vy} {vw} {vh}" overflow="visible">{estilo}{miolo}{dragao}</svg>
</svg>
"""


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        svg = montar(f.read())
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(svg)
    print("ok", sys.argv[2], len(svg) // 1024, "KB")
