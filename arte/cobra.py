"""Põe a cobrinha dos commits (gerada pelo Platane/snk) dentro da moldura do dragão.

O dragão faz o papel da cobra: segue o caminho da cabeça dela e vira para o lado em que está indo.
Ele é montado em camadas (arte/pecas/dragao-*.webp) para a animação: as duas asas batem, o corpo
sobe a cada batida, o rabo ondula, a cabeça balança, o olho pulsa e sai uma chama da boca.
A moldura e as camadas saem do arte/preparar_cobra.py.

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


# pontos do dragão, em pixels da arte (370 x 187)
RAIZ_ASA = 82                        # linha em que a asa encosta no corpo
PIVO_RABO, PIVO_PONTA, PIVO_CABECA = (138, 110), (92, 128), (262, 58)
OLHO = (328, 84)
BATIDA = 640                         # ms de uma batida de asa (o corpo sobe junto)


def girar(nome, pivo, graus, ms, atraso=0):
    x, y = pivo
    t = lambda g: f"transform:translate({x}px,{y}px) rotate({g}deg) translate({-x}px,{-y}px)"
    return (f"@keyframes {nome}{{0%,100%{{{t(-graus)}}}50%{{{t(graus)}}}}}"
            f".{nome}{{animation:{nome} {ms}ms ease-in-out {atraso}ms infinite}}")


def estilo_do_dragao(pontos, duracao):
    asa = lambda sy: f"transform:translate(0,{RAIZ_ASA}px) scale(1,{sy}) translate(0,{-RAIZ_ASA}px)"
    bx, by = BOCA_PX
    chama = lambda sx, sy: f"transform:translate({bx}px,{by}px) scale({sx},{sy}) translate({-bx}px,{-by}px)"
    return ("<style>" + viradas(pontos)
            + f".vira{{animation:vira {duracao}ms step-end infinite}}"
            + "@keyframes voo{0%,100%{transform:translateY(1.4px)}50%{transform:translateY(-1.4px)}}"
            + f".voo{{animation:voo {BATIDA}ms ease-in-out infinite}}"
            + f"@keyframes bate{{0%,100%{{{asa(1)}}}50%{{{asa(-.5)}}}}}"
            + f".asa{{animation:bate {BATIDA}ms ease-in-out infinite}}"
            + f".asa2{{animation:bate {BATIDA}ms ease-in-out -90ms infinite}}"
            + girar("rabo", PIVO_RABO, 5, BATIDA * 2)
            + girar("ponta", PIVO_PONTA, 9, BATIDA * 2, -BATIDA // 2)
            + girar("cabeca", PIVO_CABECA, 3, BATIDA * 2, -BATIDA // 3)
            + "@keyframes olho{0%,100%{opacity:.35}50%{opacity:1}}.olho{animation:olho 1400ms ease-in-out infinite}"
            + f"@keyframes chama{{0%{{{chama(.55, .8)};opacity:.7}}50%{{{chama(1.1, 1)};opacity:1}}100%{{{chama(.7, .9)};opacity:.8}}}}"
            + ".chama{animation:chama 220ms linear infinite alternate}"
            + "@media (prefers-reduced-motion:reduce){.voo,.asa,.asa2,.rabo,.ponta,.cabeca,.olho,.chama{animation:none}}"
            + "</style>")


def desenho_do_dragao():
    """As camadas, de trás para a frente, em pixels da arte."""
    w, h = DRAGAO_PX
    img = lambda nome, extra="": f'<image href="{embutir(f"dragao-{nome}.webp")}" width="{w}" height="{h}"{extra}/>'
    bx, by = BOCA_PX
    ox, oy = OLHO
    return (
        '<defs><filter id="sombra-asa"><feColorMatrix type="matrix" values=".62 0 0 0 0 0 .5 0 0 0 0 0 .5 0 0 0 0 0 1 0"/></filter>'
        '<radialGradient id="fogo"><stop offset="0" stop-color="#FFE7A3"/><stop offset=".35" stop-color="#FF8A2B"/>'
        '<stop offset=".7" stop-color="#E8333A" stop-opacity=".8"/><stop offset="1" stop-color="#E8333A" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="brilho"><stop offset="0" stop-color="#FFD9C9"/><stop offset=".3" stop-color="#FF3B3B"/>'
        '<stop offset="1" stop-color="#FF3B3B" stop-opacity="0"/></radialGradient></defs>'
        f'<g transform="translate(14,-9)" filter="url(#sombra-asa)"><g class="asa2">{img("asa")}</g></g>'
        f'<g class="rabo">{img("rabo")}<g class="ponta">{img("ponta")}</g></g>'
        f'{img("corpo")}'
        f'<g class="cabeca">{img("cabeca")}<circle class="olho" cx="{ox}" cy="{oy}" r="7" fill="url(#brilho)"/>'
        f'<ellipse class="chama" cx="{bx + 16}" cy="{by + 1}" rx="18" ry="7" fill="url(#fogo)"/></g>'
        f'<g class="asa">{img("asa")}</g>'
    )


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
    dragao = (f'<g class="s s0"><g class="vira"><g class="voo"><g transform="translate({dx:.2f},{dy:.2f}) scale({k:.5f})">'
              f"{desenho_do_dragao()}</g></g></g></g>")
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
