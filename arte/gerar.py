"""Gera as artes góticas do README (cabeçalho, títulos, botões, divisor, rodapé).

Uso:  python arte/gerar.py CAMINHO_DAS_FONTES
      (as fontes são as do MFG: unifrakturcook-latin.woff2 e cormorant-garamond-latin.woff2)

O GitHub não deixa usar fonte própria no README, então o texto vira desenho
(caminho SVG) aqui mesmo: o resultado não depende de nenhuma fonte instalada.
"""
import math
from html import escape
import os
import random
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTES = sys.argv[1] if len(sys.argv) > 1 else "."
SAIDA = os.path.dirname(os.path.abspath(__file__))

# paleta do MFG (camada gótica)
FUNDO = "#0B0709"
FUNDO_2 = "#140A0E"
VINHO = "#8A3F50"
VINHO_ESC = "#3A1119"
OURO = "#D9B36C"
OURO_ESC = "#8C6A35"
MARFIM = "#E8E2D6"


class Fonte:
    def __init__(self, arquivo, peso=None):
        f = TTFont(os.path.join(FONTES, arquivo))
        if peso and "fvar" in f:
            f = instantiateVariableFont(f, {"wght": peso})
        self.upm = f["head"].unitsPerEm
        self.cmap = f.getBestCmap()
        self.glifos = f.getGlyphSet()
        self.avanco = f["hmtx"].metrics

    def largura(self, texto, tam, espaco=0):
        s = tam / self.upm
        return sum(self.avanco[self.cmap[ord(c)]][0] * s + espaco for c in texto) - espaco

    def caminho(self, texto, tam, x, y, ancora="meio", espaco=0):
        """Texto como um 'd' de <path>. x é o centro (ancora='meio') ou o início."""
        s = tam / self.upm
        if ancora == "meio":
            x -= self.largura(texto, tam, espaco) / 2
        pen = SVGPathPen(self.glifos, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
        for c in texto:
            nome = self.cmap[ord(c)]
            self.glifos[nome].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
            x += self.avanco[nome][0] * s + espaco
        return pen.getCommands()


GOTICA = Fonte("unifrakturcook-latin.woff2")
SERIFA = Fonte("cormorant-garamond-latin.woff2", peso=600)


def salvar(nome, svg):
    with open(os.path.join(SAIDA, nome), "w", encoding="utf-8", newline="\n") as f:
        f.write(svg.strip() + "\n")
    print("ok", nome, len(svg) // 1024, "KB")


def chanfro(x, y, w, h, c):
    """Retângulo com o canto de cima à esquerda e o de baixo à direita cortados (como no MFG)."""
    return f"M{x+c},{y} H{x+w} V{y+h-c} L{x+w-c},{y+h} H{x} V{y+c} Z"


def losango(cx, cy, r):
    return f"M{cx},{cy-r} L{cx+r},{cy} L{cx},{cy+r} L{cx-r},{cy} Z"


def floreio(cx, cy, comp, lado):
    """Linha com losango na ponta e um arco pequeno, para os lados de um título."""
    d = lado
    x2 = cx + d * comp
    return (
        f'<rect x="{min(cx, x2)}" y="{cy - .6}" width="{comp}" height="1.2" fill="url(#linha{"D" if d > 0 else "E"})"/>'
        f'<path d="{losango(x2 + d * 7, cy, 4.5)}" fill="{OURO}"/>'
        f'<path d="{losango(cx + d * 14, cy, 3)}" fill="{VINHO}"/>'
        f'<path d="M{cx + d * 26},{cy - 6} q{d * 8},6 0,12" fill="none" stroke="{OURO_ESC}" stroke-width="1"/>'
    )


def defs_linhas():
    return (
        f'<linearGradient id="linhaD" x1="0" x2="1"><stop offset="0" stop-color="{OURO}"/><stop offset="1" stop-color="{OURO}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="linhaE" x1="1" x2="0"><stop offset="0" stop-color="{OURO}"/><stop offset="1" stop-color="{OURO}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="ouro" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3DDA6"/><stop offset=".55" stop-color="{OURO}"/><stop offset="1" stop-color="#9C7438"/></linearGradient>'
    )


def textura(w, h, id_="tv"):
    """Linhas de TV de tubo e grão parados (nada pisca)."""
    return (
        f'<pattern id="{id_}" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>'
        f'<filter id="grao{id_}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/>'
        f'<feColorMatrix values="0 0 0 0 .9  0 0 0 0 .85  0 0 0 0 .8  0 0 0 .07 0"/></filter>'
    ), (
        f'<rect width="{w}" height="{h}" fill="url(#{id_})"/>'
        f'<rect width="{w}" height="{h}" filter="url(#grao{id_})"/>'
    )


def catedral(w, base, semente, escala=1.0, cor="#050304"):
    """Silhueta de torres góticas ao longo da largura."""
    rnd = random.Random(semente)
    partes = []
    x = -10
    while x < w + 10:
        larg = rnd.uniform(26, 58) * escala
        alt = rnd.uniform(40, 95) * escala
        topo = base - alt
        partes.append(f"M{x:.1f},{base} V{topo:.1f} H{x + larg:.1f} V{base} Z")
        # torre com flecha
        if rnd.random() < 0.55:
            meio = x + larg / 2
            flecha = rnd.uniform(35, 80) * escala
            partes.append(f"M{x + larg * .18:.1f},{topo:.1f} L{meio:.1f},{topo - flecha:.1f} L{x + larg * .82:.1f},{topo:.1f} Z")
            partes.append(f"M{meio - .8:.1f},{topo - flecha:.1f} V{topo - flecha - 9 * escala:.1f} H{meio + .8:.1f} V{topo - flecha:.1f} Z")
            # pináculos
            for px in (x + 2, x + larg - 2):
                partes.append(f"M{px - 3:.1f},{topo:.1f} L{px:.1f},{topo - 14 * escala:.1f} L{px + 3:.1f},{topo:.1f} Z")
        else:
            # ameias
            n = max(2, int(larg // 9))
            for i in range(n):
                ax = x + i * larg / n
                partes.append(f"M{ax:.1f},{topo:.1f} v-6 h{larg / n * .55:.1f} v6 Z")
        x += larg + rnd.uniform(-4, 10)
    janelas = []
    rnd2 = random.Random(semente + 1)
    for _ in range(int(w / 140)):
        jx = rnd2.uniform(20, w - 20)
        jy = base - rnd2.uniform(10, 35) * escala
        janelas.append(f'<path d="M{jx:.1f},{jy:.1f} v-7 q2.5,-5 5,0 v7 Z" fill="#E8A050" opacity="{rnd2.uniform(.25, .6):.2f}"/>')
    return f'<path d="{" ".join(partes)}" fill="{cor}"/>' + "".join(janelas)


def morcego(x, y, t):
    return (
        f'<path transform="translate({x},{y}) scale({t})" fill="#050304" '
        f'd="M0,0 c-4,-5 -10,-6 -16,-3 c3,1 4,3 4,5 c-3,-2 -6,-1 -8,1 c4,0 6,2 7,4 c3,-3 8,-4 13,-3 '
        f'c1,-2 2,-3 3,-3 c1,0 2,1 3,3 c5,-1 10,0 13,3 c1,-2 3,-4 7,-4 c-2,-2 -5,-3 -8,-1 c0,-2 1,-4 4,-5 c-6,-3 -12,-2 -16,3 Z"/>'
    )


def brasas(w, h, n, semente):
    rnd = random.Random(semente)
    estilo = []
    pontos = []
    for i in range(n):
        dur = rnd.uniform(8, 14)
        atraso = -rnd.uniform(0, dur)
        dx = rnd.uniform(-40, 40)
        sobe = rnd.uniform(h * .45, h * .8)
        estilo.append(
            f"@keyframes b{i}{{0%{{transform:translate(0,0);opacity:0}}15%{{opacity:.85}}"
            f"100%{{transform:translate({dx:.0f}px,-{sobe:.0f}px);opacity:0}}}}"
            f".b{i}{{animation:b{i} {dur:.1f}s linear {atraso:.1f}s infinite}}"
        )
        cx = rnd.uniform(30, w - 30)
        cy = h - rnd.uniform(5, 40)
        r = rnd.uniform(1, 2.4)
        cor = rnd.choice(["#F0A04B", "#E07A3C", OURO])
        pontos.append(f'<circle class="b{i}" cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.1f}" fill="{cor}"/>')
    css = "@media (prefers-reduced-motion:reduce){circle{animation:none!important;opacity:0}}"
    return "<style>" + "".join(estilo) + css + "</style>", "".join(pontos)


def moldura(w, h, m=12, c=18):
    """Duas linhas douradas com os cantos chanfrados e losangos nos cantos."""
    return (
        f'<path d="{chanfro(m, m, w - 2 * m, h - 2 * m, c)}" fill="none" stroke="{OURO}" stroke-opacity=".55" stroke-width="1.5"/>'
        f'<path d="{chanfro(m + 6, m + 6, w - 2 * m - 12, h - 2 * m - 12, c - 4)}" fill="none" stroke="{OURO_ESC}" stroke-opacity=".5" stroke-width="1"/>'
        + "".join(f'<path d="{losango(x, y, 5)}" fill="{OURO}"/>' for x, y in ((w - m, m), (m, h - m)))
    )


# ---------------------------------------------------------------- cabeçalho
def cabecalho():
    w, h = 1200, 360
    tv_defs, tv = textura(w, h)
    css_brasas, pontos = brasas(w, h, 26, 3)
    nome = GOTICA.caminho("Isaque Diniz", 104, w / 2, 178)
    apelido = SERIFA.caminho("— Billy camomilla —", 25, w / 2, 222, espaco=1.5)
    linha = SERIFA.caminho("ESTUDANTE  ·  INTELIGÊNCIA ARTIFICIAL  ·  ENGENHARIA DE SOFTWARE", 15, w / 2, 256, espaco=3)
    lua = (
        f'<circle cx="1030" cy="86" r="90" fill="url(#halo)"/>'
        f'<circle cx="1030" cy="86" r="36" fill="#EDE3CC"/>'
        f'<circle cx="1046" cy="76" r="33" fill="url(#ceu)"/>'
    )
    morcegos = morcego(940, 70, .9) + morcego(985, 118, .6) + morcego(170, 92, .75) + morcego(215, 62, .5)
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Isaque Diniz — Billy camomilla">
<defs>
{defs_linhas()}
<linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{FUNDO}"/><stop offset=".6" stop-color="{FUNDO_2}"/><stop offset="1" stop-color="#2B0D15"/></linearGradient>
<radialGradient id="halo"><stop offset="0" stop-color="#E9D7AE" stop-opacity=".35"/><stop offset=".45" stop-color="{VINHO}" stop-opacity=".12"/><stop offset="1" stop-color="{VINHO}" stop-opacity="0"/></radialGradient>
<radialGradient id="brilho" cx=".5" cy=".55" r=".5"><stop offset="0" stop-color="{VINHO}" stop-opacity=".35"/><stop offset="1" stop-color="{VINHO}" stop-opacity="0"/></radialGradient>
<filter id="sombra" x="-10%" y="-30%" width="120%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000" flood-opacity=".9"/><feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="{VINHO}" flood-opacity=".55"/></filter>
<clipPath id="corte"><path d="{chanfro(0, 0, w, h, 26)}"/></clipPath>
{tv_defs}
</defs>
{css_brasas}
<g clip-path="url(#corte)">
<rect width="{w}" height="{h}" fill="url(#ceu)"/>
<ellipse cx="{w/2}" cy="190" rx="520" ry="150" fill="url(#brilho)"/>
{lua}
{morcegos}
<g opacity=".55">{catedral(w, h - 8, 11, .85, "#160A0E")}</g>
{catedral(w, h, 4)}
{pontos}
<path d="{nome}" fill="url(#ouro)" filter="url(#sombra)"/>
<path d="{apelido}" fill="{MARFIM}" opacity=".92"/>
{floreio(w/2 - 150, 214, 150, -1)}{floreio(w/2 + 150, 214, 150, 1)}
<path d="{linha}" fill="{OURO}" opacity=".85"/>
{tv}
{moldura(w, h)}
</g>
</svg>"""
    salvar("cabecalho.svg", svg)


# ---------------------------------------------------------------- frases que se revezam
def epigrafe():
    w, h = 900, 56
    frases = [
        "bem-vindo ao meu perfil",
        "sou o Isaque, mais conhecido como Billy",
        "estudante de IA e engenharia de software",
        "construindo pequenos projetos pra aprender",
    ]
    passo = 4.5
    total = passo * len(frases)
    fim = 100 / len(frases)
    css = (
        f"@keyframes f{{0%{{opacity:0}}{fim*.18:.1f}%{{opacity:1}}{fim*.82:.1f}%{{opacity:1}}{fim:.1f}%{{opacity:0}}100%{{opacity:0}}}}"
        f".f{{opacity:0;animation:f {total}s ease-in-out infinite}}"
        "@media (prefers-reduced-motion:reduce){.f{animation:none}.f0{opacity:1}}"
    )
    caminhos = "".join(
        f'<path class="f f{i}" style="animation-delay:{i*passo - passo*.3:.2f}s" d="{SERIFA.caminho(t, 27, w/2, 37, espaco=.6)}" fill="{MARFIM}"/>'
        for i, t in enumerate(frases)
    )
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{' · '.join(frases)}">
<style>{css}</style>
<defs>{defs_linhas()}</defs>
{caminhos}
<rect x="{w/2-300}" y="{h-3}" width="600" height="1" fill="{OURO}" opacity=".35"/>
</svg>"""
    salvar("epigrafe.svg", svg)


# ---------------------------------------------------------------- títulos das seções
def titulo(arquivo, texto, rotulo):
    w, h = 900, 78
    tv_defs, tv = textura(w, h, "tvt")
    larg = GOTICA.largura(texto, 44)
    meio = w / 2
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{rotulo}">
<defs>{defs_linhas()}{tv_defs}
<linearGradient id="placa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{FUNDO_2}"/><stop offset="1" stop-color="{FUNDO}"/></linearGradient>
<radialGradient id="luz"><stop offset="0" stop-color="{VINHO}" stop-opacity=".4"/><stop offset="1" stop-color="{VINHO}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><path d="{chanfro(1, 1, w - 2, h - 2, 14)}"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#placa)"/>
<ellipse cx="{meio}" cy="{h}" rx="320" ry="46" fill="url(#luz)"/>{tv}</g>
<path d="{chanfro(1, 1, w - 2, h - 2, 14)}" fill="none" stroke="{OURO}" stroke-opacity=".5" stroke-width="1.2"/>
<path d="M14,1 H{w*.35}" stroke="{OURO}" stroke-width="2"/>
<path d="{GOTICA.caminho(texto, 44, meio, 54)}" fill="url(#ouro)"/>
{floreio(meio - larg/2 - 22, 39, 170, -1)}{floreio(meio + larg/2 + 22, 39, 170, 1)}
</svg>"""
    salvar(arquivo, svg)


# ---------------------------------------------------------------- divisor
def divisor():
    w, h = 900, 34
    m = w / 2
    lua = f'<circle cx="{m}" cy="17" r="8" fill="{OURO}"/><circle cx="{m+4}" cy="14" r="7.5" fill="{FUNDO}"/>'
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="">
<defs>{defs_linhas()}</defs>
<path d="{losango(m, 17, 15)}" fill="{FUNDO}" stroke="{OURO}" stroke-opacity=".6"/>
{lua}
{floreio(m - 24, 17, 330, -1)}{floreio(m + 24, 17, 330, 1)}
</svg>"""
    salvar("divisor.svg", svg)


# ---------------------------------------------------------------- botões dos links
def botao(arquivo, texto, rotulo):
    tam = 17
    larg = SERIFA.largura(texto, tam, 3)
    w, h = int(larg + 64), 42
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{rotulo}">
<defs><linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4A1822"/><stop offset="1" stop-color="#2A0C13"/></linearGradient></defs>
<path d="{chanfro(1, 1, w - 2, h - 2, 8)}" fill="url(#p)" stroke="{OURO}" stroke-opacity=".7"/>
<path d="M9,1 H{w*.45}" stroke="{OURO}" stroke-width="2"/>
<path d="{losango(16, h/2, 3.5)}" fill="{OURO}"/><path d="{losango(w - 16, h/2, 3.5)}" fill="{OURO}"/>
<path d="{SERIFA.caminho(texto, tam, w/2, 27, espaco=3)}" fill="{MARFIM}"/>
</svg>"""
    salvar(arquivo, svg)


# ---------------------------------------------------------------- rodapé
def rodape():
    w, h = 1200, 190
    css_brasas, pontos = brasas(w, h, 14, 9)
    frase = SERIFA.caminho("que a curiosidade te guie pela escuridão", 22, w / 2, 58, espaco=1)
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="que a curiosidade te guie pela escuridão">
<defs>{defs_linhas()}
<linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{FUNDO}" stop-opacity="0"/><stop offset=".5" stop-color="{FUNDO_2}"/><stop offset="1" stop-color="#2B0D15"/></linearGradient></defs>
{css_brasas}
<rect width="{w}" height="{h}" fill="url(#ceu)"/>
<path d="{frase}" fill="{OURO}" opacity=".9"/>
{floreio(w/2 - 225, 51, 120, -1)}{floreio(w/2 + 225, 51, 120, 1)}
{pontos}
<g opacity=".6">{catedral(w, h - 6, 21, .7, "#160A0E")}</g>
{catedral(w, h, 8, .8)}
</svg>"""
    salvar("rodape.svg", svg)


# ---------------------------------------------------------------- certificados
def quebrar(fonte, texto, tam, largura):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if atual and fonte.largura(teste, tam) > largura:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    return linhas + [atual]


def selo(cx, cy):
    """Selo de lacre vinho com borda irregular e uma lua crescente dourada."""
    pts = []
    for i in range(36):
        a = i / 36 * 2 * math.pi
        r = 27 + (2.2 if i % 2 else 0)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return (
        f'<polygon points="{" ".join(pts)}" fill="#5E1A28"/>'
        f'<circle cx="{cx}" cy="{cy}" r="21" fill="#7A2434" stroke="{OURO}" stroke-opacity=".6"/>'
        f'<circle cx="{cx}" cy="{cy}" r="16" fill="none" stroke="#4A1420" stroke-dasharray="2 2.5"/>'
        f'<circle cx="{cx}" cy="{cy}" r="8.5" fill="{OURO}"/><circle cx="{cx + 4}" cy="{cy - 3}" r="8" fill="#7A2434"/>'
    )


def certificado(arquivo, categoria, texto, escola, horas, data, rotulo):
    w, h = 460, 250
    tv_defs, tv = textura(w, h, "tvc")
    linhas = quebrar(SERIFA, texto, 25, 330)[:3]
    titulo_d = " ".join(SERIFA.caminho(l, 25, 30, 82 + i * 29, ancora="inicio") for i, l in enumerate(linhas))
    y_escola = 82 + len(linhas) * 29 + 8
    seta = f'<path d="M{w-40},{h-33} l9,-9 M{w-38},{h-42} h7 v7" stroke="{OURO}" stroke-width="1.4" fill="none"/>'
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(rotulo)}">
<defs>{defs_linhas()}{tv_defs}
<linearGradient id="placa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A0D12"/><stop offset="1" stop-color="{FUNDO}"/></linearGradient>
<radialGradient id="luz" cx=".85" cy=".1" r=".6"><stop offset="0" stop-color="{VINHO}" stop-opacity=".3"/><stop offset="1" stop-color="{VINHO}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><path d="{chanfro(1, 1, w - 2, h - 2, 16)}"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#placa)"/><rect width="{w}" height="{h}" fill="url(#luz)"/>{tv}</g>
<path d="{chanfro(1, 1, w - 2, h - 2, 16)}" fill="none" stroke="{OURO}" stroke-opacity=".55" stroke-width="1.2"/>
<path d="{chanfro(8, 8, w - 16, h - 16, 11)}" fill="none" stroke="{OURO_ESC}" stroke-opacity=".35"/>
<path d="M16,1 H{w*.4}" stroke="{OURO}" stroke-width="2"/>
<path d="{SERIFA.caminho(categoria.upper(), 12, 30, 44, ancora="inicio", espaco=2.6)}" fill="{OURO}" opacity=".8"/>
{selo(w - 52, 52)}
<path d="{titulo_d}" fill="{MARFIM}"/>
<path d="{SERIFA.caminho(escola, 16, 30, y_escola, ancora="inicio", espaco=.4)}" fill="{OURO}"/>
<rect x="30" y="{h-56}" width="{w-60}" height="1" fill="url(#linhaD)" opacity=".5"/>
<path d="{SERIFA.caminho(f"{horas}  ·  {data}", 15, 30, h-30, ancora="inicio", espaco=1)}" fill="{MARFIM}" opacity=".7"/>
<path d="{SERIFA.caminho("VERIFICAR", 12, w - 54 - SERIFA.largura("VERIFICAR", 12, 2.4), h-30, ancora="inicio", espaco=2.4)}" fill="{OURO}"/>
{seta}
</svg>"""
    salvar(arquivo, svg)


cabecalho()
epigrafe()
divisor()
rodape()
titulo("titulo-sobre.svg", "Sobre mim", "Sobre mim")
titulo("titulo-grimorio.svg", "Grimório", "Grimório: o que estou aprendendo")
titulo("titulo-serpente.svg", "A serpente dos commits", "A serpente comendo meus commits")
botao("botao-linkedin.svg", "LINKEDIN", "LinkedIn")
botao("botao-email.svg", "E-MAIL", "E-mail")
titulo("titulo-certificados.svg", "Certificados", "Certificados")
certificado("certificado-sql.svg", "banco de dados", "Banco de Dados SQL do Zero ao Avançado + Projetos Reais",
            "Udemy · Andre Iacono", "8 horas", "novembro de 2026", "Certificado: Banco de Dados SQL do Zero ao Avançado, Udemy")
certificado("certificado-claude.svg", "inteligência artificial", "Mastering Claude Cowork, Claude Design & AI Agents",
            "Udemy · Ryan Ahmed, Stemplicity", "8,5 horas", "novembro de 2026", "Certificado: Mastering Claude Cowork, Claude Design & AI Agents, Udemy")
