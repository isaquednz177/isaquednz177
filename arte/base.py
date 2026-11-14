"""Peças comuns das artes do README: paleta, texto em desenho e ornamentos góticos.

O GitHub não deixa usar fonte própria no README, então o texto vira caminho SVG
aqui mesmo (as fontes ficam em arte/fontes, licença OFL).
"""
import math
import os
import random
from html import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

PASTA = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(PASTA, "fontes")

# paleta: vermelho-sangue, marrom-escuro e preto
PRETO = "#060404"
PRETO_2 = "#0D0806"
MARROM = "#1E120C"
MARROM_2 = "#2B1A11"
MARROM_LINHA = "#5A3A28"
SANGUE_ESC = "#4A060B"
SANGUE = "#8B0A14"
SANGUE_VIVO = "#B3121E"
SANGUE_CLARO = "#D64550"
OSSO = "#D8C6B2"  # texto pequeno: marrom bem claro, para ler sobre o escuro
SILHUETA = "#030202"
VITRAL = "#C41E2A"


class Fonte:
    def __init__(self, arquivo, peso=None, algarismos=None):
        """algarismos="lf": números alinhados (todos da mesma altura) em vez dos antigos."""
        f = TTFont(os.path.join(FONTES, arquivo))
        if peso and "fvar" in f:
            f = instantiateVariableFont(f, {"wght": peso})
        self.upm = f["head"].unitsPerEm
        self.cmap = f.getBestCmap()
        self.glifos = f.getGlyphSet()
        self.avanco = f["hmtx"].metrics
        if algarismos:
            for c in "0123456789":
                alt = f"{self.cmap[ord(c)]}.{algarismos}"
                if alt in self.avanco:
                    self.cmap[ord(c)] = alt

    def largura(self, texto, tam, espaco=0):
        s = tam / self.upm
        return sum(self.avanco[self.cmap[ord(c)]][0] * s + espaco for c in texto) - espaco

    def caminho(self, texto, tam, x, y, ancora="meio", espaco=0):
        """Texto como o 'd' de um <path>. x é o centro (ancora='meio'), o início ou o fim."""
        s = tam / self.upm
        if ancora == "meio":
            x -= self.largura(texto, tam, espaco) / 2
        elif ancora == "fim":
            x -= self.largura(texto, tam, espaco)
        pen = SVGPathPen(self.glifos, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
        for c in texto:
            nome = self.cmap[ord(c)]
            self.glifos[nome].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
            x += self.avanco[nome][0] * s + espaco
        return pen.getCommands()


GOTICA = Fonte("unifrakturcook-latin.woff2")
SERIFA = Fonte("cormorant-garamond-latin.woff2", peso=600)
SERIFA_FORTE = Fonte("cormorant-garamond-latin.woff2", peso=700)
NUMEROS = Fonte("cormorant-garamond-latin.woff2", peso=600, algarismos="lf")


def salvar(caminho, svg):
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg.strip() + "\n")
    print("ok", os.path.basename(caminho), len(svg) // 1024, "KB")


def abrir(w, h, rotulo):
    rot = escape(rotulo)
    papel = f'role="img" aria-label="{rot}"' if rotulo else 'aria-hidden="true"'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" {papel}>'


# ---------------------------------------------------------------- formas
def f1(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def chanfro(x, y, w, h, c):
    """Retângulo com o canto de cima à esquerda e o de baixo à direita cortados."""
    return f"M{f1(x+c)},{f1(y)} H{f1(x+w)} V{f1(y+h-c)} L{f1(x+w-c)},{f1(y+h)} H{f1(x)} V{f1(y+c)} Z"


def ogiva(x, base, w, h):
    """Janela em arco ogival (pontudo), com a base em y=base."""
    o = base - h + w * 0.9
    return (f"M{f1(x)},{f1(base)} V{f1(o)} Q{f1(x)},{f1(base-h+w*.25)} {f1(x+w/2)},{f1(base-h)} "
            f"Q{f1(x+w)},{f1(base-h+w*.25)} {f1(x+w)},{f1(o)} V{f1(base)} Z")


def quadrifolio(cx, cy, r):
    """Quatro lóbulos, o ornamento de pedra das catedrais."""
    a = r * 0.5
    return "".join(
        f"M{f1(cx+dx-a)},{f1(cy+dy)} a{f1(a)},{f1(a)} 0 1,0 {f1(2*a)},0 a{f1(a)},{f1(a)} 0 1,0 {f1(-2*a)},0 Z"
        for dx, dy in ((0, -a), (a, 0), (0, a), (-a, 0))
    )


def rosacea(cx, cy, r, cor, largura=1.0, opacidade=1.0, petalas=12):
    """Rosácea (vitral redondo) só em traço."""
    p = [f'<g fill="none" stroke="{cor}" stroke-width="{largura}" opacity="{opacidade}">',
         f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}"/>',
         f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r*.93)}"/>',
         f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r*.24)}"/>',
         f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r*.12)}"/>']
    for i in range(petalas):
        a = i / petalas * 2 * math.pi
        b = a + math.pi / petalas
        p.append(f'<circle cx="{f1(cx+r*.56*math.cos(a))}" cy="{f1(cy+r*.56*math.sin(a))}" r="{f1(r*.3)}"/>')
        p.append(f'<circle cx="{f1(cx+r*.82*math.cos(b))}" cy="{f1(cy+r*.82*math.sin(b))}" r="{f1(r*.09)}"/>')
        p.append(f'<path d="M{f1(cx+r*.24*math.cos(a))},{f1(cy+r*.24*math.sin(a))} L{f1(cx+r*.93*math.cos(a))},{f1(cy+r*.93*math.sin(a))}"/>')
    p.append("</g>")
    return "".join(p)


def rosacea_mini(cx, cy, r, cor):
    """Rosácea pequena, cheia, para os enfeites dos títulos."""
    furos = "".join(
        f'<circle cx="{f1(cx+r*.55*math.cos(i*math.pi/4))}" cy="{f1(cy+r*.55*math.sin(i*math.pi/4))}" r="{f1(r*.17)}"/>'
        for i in range(8)
    )
    return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{cor}"/>'
            f'<g fill="{PRETO}">{furos}<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r*.2)}"/></g>')


def defs_comuns():
    return (
        f'<linearGradient id="linhaD" x1="0" x2="1"><stop offset="0" stop-color="{SANGUE_VIVO}"/><stop offset="1" stop-color="{SANGUE_VIVO}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="linhaE" x1="1" x2="0"><stop offset="0" stop-color="{SANGUE_VIVO}"/><stop offset="1" stop-color="{SANGUE_VIVO}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="sangue" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E5474F"/><stop offset=".5" stop-color="{SANGUE_VIVO}"/><stop offset="1" stop-color="#6A0910"/></linearGradient>'
        f'<linearGradient id="placa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MARROM_2}"/><stop offset="1" stop-color="{PRETO_2}"/></linearGradient>'
    )


def floreio(cx, cy, comp, lado):
    """Linha que some aos poucos, com uma rosácea perto do texto e um quadrifólio na ponta."""
    x2 = cx + lado * comp
    return (
        f'<rect x="{f1(min(cx, x2))}" y="{f1(cy-.6)}" width="{f1(comp)}" height="1.2" fill="url(#linha{"D" if lado > 0 else "E"})"/>'
        + rosacea_mini(cx + lado * 2, cy, 7, SANGUE_VIVO)
        + f'<path d="{quadrifolio(x2 + lado * 8, cy, 7)}" fill="{SANGUE}"/>'
    )


def textura(w, h, id_="tv"):
    """Linhas de TV de tubo e grão, parados (nada pisca)."""
    defs = (
        f'<pattern id="{id_}" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>'
        f'<filter id="g{id_}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/>'
        f'<feColorMatrix values="0 0 0 0 .8  0 0 0 0 .6  0 0 0 0 .5  0 0 0 .07 0"/></filter>'
    )
    return defs, f'<rect width="{w}" height="{h}" fill="url(#{id_})"/><rect width="{w}" height="{h}" filter="url(#g{id_})"/>'


def placa(w, h, c=14, id_="cp"):
    """Fundo marrom-escuro chanfrado com filete vermelho em cima."""
    tv_defs, tv = textura(w, h, "t" + id_)
    defs = tv_defs + f'<clipPath id="{id_}"><path d="{chanfro(1, 1, w-2, h-2, c)}"/></clipPath>'
    corpo = (
        f'<g clip-path="url(#{id_})"><rect width="{w}" height="{h}" fill="url(#placa)"/>{tv}</g>'
        f'<path d="{chanfro(1, 1, w-2, h-2, c)}" fill="none" stroke="{MARROM_LINHA}" stroke-width="1.2"/>'
        f'<path d="M{c+2},1 H{f1(w*.4)}" stroke="{SANGUE_VIVO}" stroke-width="2"/>'
    )
    return defs, corpo


# ---------------------------------------------------------------- arquitetura
def torre(x, w, topo, base, semente=0):
    """Torre de catedral: corpo com contrafortes, janelas ogivais acesas, rosácea e flecha."""
    rnd = random.Random(semente)
    s, luz = [], []
    s.append(f"M{f1(x)},{f1(base)} V{f1(topo)} H{f1(x+w)} V{f1(base)} Z")
    # contrafortes dos dois lados, cada um com um pináculo
    for bx in (x - 8, x + w):
        yy = topo + (base - topo) * .22
        s.append(f"M{f1(bx)},{f1(base)} V{f1(yy+6)} L{f1(bx+4)},{f1(yy)} L{f1(bx+8)},{f1(yy+6)} V{f1(base)} Z")
        s.append(f"M{f1(bx+1)},{f1(yy+1)} L{f1(bx+4)},{f1(yy-16)} L{f1(bx+7)},{f1(yy+1)} Z")
    # ameias e pináculos no topo do corpo
    for px in (x - 2, x + w + 2):
        s.append(f"M{f1(px-4)},{f1(topo)} L{f1(px)},{f1(topo-26)} L{f1(px+4)},{f1(topo)} Z")
    # flecha com crochês
    meio = x + w / 2
    alt_flecha = w * 1.9
    s.append(f"M{f1(x+w*.12)},{f1(topo)} L{f1(meio)},{f1(topo-alt_flecha)} L{f1(x+w*.88)},{f1(topo)} Z")
    for k in range(1, 6):
        yy = topo - alt_flecha * k / 6.5
        meia = (w * .38) * (1 - k / 6.5)
        for lado in (-1, 1):
            bx = meio + lado * meia
            s.append(f"M{f1(bx)},{f1(yy)} l{f1(lado*4)},-2 l{f1(-lado*2)},4 Z")
    s.append(f"M{f1(meio-1)},{f1(topo-alt_flecha)} V{f1(topo-alt_flecha-12)} H{f1(meio+1)} V{f1(topo-alt_flecha)} Z")
    # janelas: duas fileiras de ogivas e uma rosácea no meio
    jw = w * .22
    for fila, yb in enumerate((topo + (base - topo) * .38, base - 14)):
        for col in (x + w * .17, x + w * .61):
            h = (base - topo) * (.22 if fila == 0 else .26)
            luz.append(f'<path d="{ogiva(col, yb, jw, h)}" fill="{VITRAL}" opacity="{rnd.uniform(.35, .6):.2f}"/>')
    ry = topo + (base - topo) * .56
    luz.append(f'<circle cx="{f1(meio)}" cy="{f1(ry)}" r="{f1(w*.2)}" fill="{VITRAL}" opacity=".55"/>')
    luz.append(rosacea(meio, ry, w * .2, SILHUETA, largura=1.4, petalas=8))
    return f'<path d="{" ".join(s)}" fill="{SILHUETA}"/>' + "".join(luz)


def fachada(cx, base, escala=1.0):
    """Fachada de catedral: duas torres, nave com frontão, rosácea grande e portal."""
    e = escala
    tw = 64 * e
    vao = 120 * e
    tx_e = cx - vao / 2 - tw
    tx_d = cx + vao / 2
    topo_t = base - 190 * e
    partes = [torre(tx_e, tw, topo_t, base, 1), torre(tx_d, tw, topo_t, base, 2)]
    # nave e frontão
    topo_n = base - 150 * e
    nave = (f"M{f1(cx-vao/2)},{f1(base)} V{f1(topo_n)} L{f1(cx)},{f1(topo_n-58*e)} "
            f"L{f1(cx+vao/2)},{f1(topo_n)} V{f1(base)} Z")
    partes.insert(0, f'<path d="{nave}" fill="{SILHUETA}"/>')
    # galeria de arcos acima do portal
    for i in range(5):
        partes.append(f'<path d="{ogiva(cx - vao/2 + 10*e + i*20.5*e, topo_n + 26*e, 12*e, 18*e)}" fill="{VITRAL}" opacity=".4"/>')
    ry = topo_n + 62 * e
    partes.append(f'<circle cx="{f1(cx)}" cy="{f1(ry)}" r="{f1(34*e)}" fill="{VITRAL}" opacity=".7"/>')
    partes.append(rosacea(cx, ry, 34 * e, SILHUETA, largura=1.6 * e))
    partes.append(f'<path d="{ogiva(cx - 17*e, base, 34*e, 52*e)}" fill="{VITRAL}" opacity=".35"/>')
    partes.append(f'<path d="{ogiva(cx - 12*e, base, 24*e, 42*e)}" fill="{SILHUETA}"/>')
    return "".join(partes)


def casario(w, base, semente, escala=1.0, cor=SILHUETA, janelas=True):
    """Linha de torres e telhados góticos ao longo da largura."""
    rnd = random.Random(semente)
    partes = []
    x = -10
    while x < w + 10:
        larg = rnd.uniform(24, 54) * escala
        alt = rnd.uniform(36, 90) * escala
        topo = base - alt
        partes.append(f"M{f1(x)},{f1(base)} V{f1(topo)} H{f1(x+larg)} V{f1(base)} Z")
        if rnd.random() < 0.6:
            meio = x + larg / 2
            flecha = rnd.uniform(30, 75) * escala
            partes.append(f"M{f1(x+larg*.15)},{f1(topo)} L{f1(meio)},{f1(topo-flecha)} L{f1(x+larg*.85)},{f1(topo)} Z")
            for px in (x + 2, x + larg - 2):
                partes.append(f"M{f1(px-3)},{f1(topo)} L{f1(px)},{f1(topo-13*escala)} L{f1(px+3)},{f1(topo)} Z")
        else:
            # telhado de duas águas bem inclinado
            partes.append(f"M{f1(x-2)},{f1(topo)} L{f1(x+larg/2)},{f1(topo-larg*.8)} L{f1(x+larg+2)},{f1(topo)} Z")
        x += larg + rnd.uniform(-4, 8)
    out = f'<path d="{" ".join(partes)}" fill="{cor}"/>'
    if janelas:
        rnd2 = random.Random(semente + 1)
        for _ in range(int(w / 120)):
            jx = rnd2.uniform(20, w - 20)
            jy = base - rnd2.uniform(8, 30) * escala
            out += f'<path d="{ogiva(jx, jy, 5, 10)}" fill="{VITRAL}" opacity="{rnd2.uniform(.3, .6):.2f}"/>'
    return out


def morcego(x, y, t):
    return (
        f'<path transform="translate({f1(x)},{f1(y)}) scale({t})" fill="{SILHUETA}" '
        f'd="M0,0 c-4,-5 -10,-6 -16,-3 c3,1 4,3 4,5 c-3,-2 -6,-1 -8,1 c4,0 6,2 7,4 c3,-3 8,-4 13,-3 '
        f'c1,-2 2,-3 3,-3 c1,0 2,1 3,3 c5,-1 10,0 13,3 c1,-2 3,-4 7,-4 c-2,-2 -5,-3 -8,-1 c0,-2 1,-4 4,-5 c-6,-3 -12,-2 -16,3 Z"/>'
    )


def brasas(w, h, n, semente):
    """Brasas subindo devagar (só transform e opacity; param com movimento reduzido)."""
    rnd = random.Random(semente)
    estilo, pontos = [], []
    for i in range(n):
        dur = rnd.uniform(9, 15)
        atraso = -rnd.uniform(0, dur)
        dx = rnd.uniform(-40, 40)
        sobe = rnd.uniform(h * .4, h * .75)
        estilo.append(
            f"@keyframes b{i}{{0%{{transform:translate(0,0);opacity:0}}15%{{opacity:.8}}"
            f"100%{{transform:translate({dx:.0f}px,-{sobe:.0f}px);opacity:0}}}}"
            f".b{i}{{animation:b{i} {dur:.1f}s linear {atraso:.1f}s infinite}}"
        )
        cor = rnd.choice([SANGUE_CLARO, VITRAL, "#E2603A"])
        pontos.append(f'<circle class="b{i}" cx="{rnd.uniform(30, w-30):.0f}" cy="{h - rnd.uniform(5, 40):.0f}" r="{rnd.uniform(1, 2.3):.1f}" fill="{cor}"/>')
    css = "@media (prefers-reduced-motion:reduce){circle[class]{animation:none!important;opacity:0}}"
    return "<style>" + "".join(estilo) + css + "</style>", "".join(pontos)
