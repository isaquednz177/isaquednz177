"""Põe a cobrinha dos commits (gerada pelo Platane/snk) dentro da moldura do dragão.

O dragão faz o papel da cobra: segue o caminho da cabeça dela, vira para o lado em que está indo
e bate as asas com os 6 quadros desenhados pelo Isaque (arte/pecas/dragao-voo-1..6.webp, que saem
do arte/preparar_dragao.py). A moldura sai do arte/preparar_cobra.py.

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
DRAGAO_PX = (260, 265)               # tamanho de cada quadro do dragão (saída do preparar_dragao.py)
BOCA_PX = (256.6, 121.1)             # onde fica a boca nos quadros
DRAGAO_LARGURA = 90                  # largura do dragão em unidades do snk (uma célula = 16)
QUADROS = 6
BATIDA = 720                         # ms de uma batida de asa inteira (os 6 quadros)


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


def estilo_do_dragao(pontos, duracao):
    """Cada quadro aparece na sua vez (step-end: troca seca, como num desenho animado)."""
    css = [viradas(pontos), f".vira{{animation:vira {duracao}ms step-end infinite}}"]
    for i in range(QUADROS):
        ini, fim = 100 * i / QUADROS, 100 * (i + 1) / QUADROS
        quadros = f"0%{{opacity:0}}{ini:.3f}%{{opacity:1}}{fim:.3f}%{{opacity:0}}" if i else f"0%{{opacity:1}}{fim:.3f}%{{opacity:0}}"
        css.append(f"@keyframes q{i}{{{quadros}}}.q{i}{{opacity:{1 if i == 0 else 0};animation:q{i} {BATIDA}ms step-end infinite}}")
    css.append("@media (prefers-reduced-motion:reduce){" + ",".join(f".q{i}" for i in range(QUADROS)) + "{animation:none}}")
    return "<style>" + "".join(css) + "</style>"


def desenho_do_dragao():
    w, h = DRAGAO_PX
    return "".join(f'<image class="q{i}" href="{embutir(f"dragao-voo-{i + 1}.webp")}" width="{w}" height="{h}"/>'
                   for i in range(QUADROS))


def montar(snk):
    m = re.search(r"<svg[^>]*>(.*)</svg>\s*$", snk, re.S)
    if not m:
        raise ValueError("o arquivo do snk não parece um SVG")
    miolo = re.sub(r"<desc>.*?</desc>", "", m.group(1), flags=re.S)
    duracao = re.search(r"\.s\{[^}]*?(\d+)ms", miolo).group(1)
    pontos = caminho_da_cabeca(miolo)
    # some com os quadradinhos da cobra: quem anda agora é o dragão
    miolo = re.sub(r'<rect class="s s\d+"[^>]*/>', "", miolo)
    k = DRAGAO_LARGURA / DRAGAO_PX[0]
    # a boca fica um pouco à frente do centro da célula (8, 8), como se mordesse o commit
    dx, dy = 12 - BOCA_PX[0] * k, 8 - BOCA_PX[1] * k
    dragao = (f'<g class="s s0"><g class="vira"><g transform="translate({dx:.2f},{dy:.2f}) scale({k:.5f})">'
              f"{desenho_do_dragao()}</g></g></g>")
    vx, vy, vw, vh = VISTA
    x = GRADE_X - (2 - vx) * K
    y = GRADE_Y - (2 - vy) * K
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="contribuições do último ano, com um dragão comendo os commits">
<image href="{embutir('cobra-moldura.webp')}" width="{W}" height="{H}"/>
<svg x="{x:.1f}" y="{y:.1f}" width="{vw * K:.1f}" height="{vh * K:.1f}" viewBox="{vx} {vy} {vw} {vh}" overflow="visible">{estilo_do_dragao(pontos, duracao)}{miolo}{dragao}</svg>
</svg>
"""


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as f:
        svg = montar(f.read())
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(svg)
    print("ok", sys.argv[2], len(svg) // 1024, "KB")
