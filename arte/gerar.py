"""Gera as artes desenhadas em código do README: cabeçalho, epígrafe e divisor.

Uso:  pip install fonttools brotli
      python arte/gerar.py

As outras peças vêm da folha de artes (arte/recortar_folha.py), e as estatísticas
do arte/estatisticas.py, rodado pela automação do GitHub.
"""
import base64
import os

from base import (GOTICA, MARROM_LINHA, OSSO, PASTA, SANGUE, SANGUE_VIVO, SERIFA, abrir, brasas,
                  chanfro, defs_comuns, floreio, quadrifolio, rosacea_mini, salvar, textura)


# O servidor de imagens do GitHub guarda cada arquivo pelo NOME (ignora ?v=) por um tempo.
# Mudou alguma arte? Suba a VERSAO: os arquivos ganham nome novo e o README precisa
# apontar para eles (troque "-v4.svg" pelo número novo no README.md).
VERSAO = 4


def saida(nome):
    return os.path.join(PASTA, nome.replace(".svg", f"-v{VERSAO}.svg"))


# ---------------------------------------------------------------- cabeçalho
def cabecalho():
    """A pintura da catedral (arte/capa.jpg) no alto; a névoa desce e o nome fica sobre ela."""
    w, h = 1200, 510
    ih = 400  # altura da pintura (1800 x 600 reduzida para 1200 x 400)
    with open(os.path.join(PASTA, "capa.jpg"), "rb") as f:
        capa = base64.b64encode(f.read()).decode()
    tv_defs, tv = textura(w, h)
    css_brasas, pontos = brasas(w, h, 18, 3)
    nome = GOTICA.caminho("Isaque Diniz", 96, w / 2, 414)
    apelido = SERIFA.caminho("Billy camomilla", 24, w / 2, 452, espaco=1.5)
    linha = SERIFA.caminho("ESTUDANTE  ·  INTELIGÊNCIA ARTIFICIAL  ·  ENGENHARIA DE SOFTWARE", 14, w / 2, 482, espaco=3)
    cantos = "".join(f'<path d="{quadrifolio(x, y, 9)}" fill="{SANGUE_VIVO}"/>' for x, y in ((w - 12, 12), (12, h - 12)))
    svg = f"""
{abrir(w, h, "Isaque Diniz, Billy camomilla: estudante de inteligência artificial e engenharia de software")}
<defs>{defs_comuns()}{tv_defs}
<linearGradient id="nevoa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A1B1D" stop-opacity="0"/><stop offset=".38" stop-color="#1A1B1D"/><stop offset="1" stop-color="#100C0B"/></linearGradient>
<radialGradient id="vinheta" cx=".5" cy=".42" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".7"/></radialGradient>
<radialGradient id="brilho" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{SANGUE}" stop-opacity=".28"/><stop offset="1" stop-color="{SANGUE}" stop-opacity="0"/></radialGradient>
<filter id="sombra" x="-10%" y="-30%" width="120%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#000" flood-opacity=".95"/><feDropShadow dx="0" dy="0" stdDeviation="12" flood-color="{SANGUE}" flood-opacity=".55"/></filter>
<clipPath id="corte"><path d="{chanfro(0, 0, w, h, 26)}"/></clipPath></defs>
{css_brasas}
<g clip-path="url(#corte)">
<rect width="{w}" height="{h}" fill="#100C0B"/>
<image href="data:image/jpeg;base64,{capa}" x="0" y="0" width="{w}" height="{ih}" preserveAspectRatio="xMidYMid slice"/>
<rect y="{ih - 140}" width="{w}" height="{h - ih + 140}" fill="url(#nevoa)"/>
<ellipse cx="{w/2}" cy="{h - 70}" rx="430" ry="90" fill="url(#brilho)"/>
<rect width="{w}" height="{h}" fill="url(#vinheta)"/>
{pontos}
<path d="{nome}" fill="url(#sangue)" filter="url(#sombra)"/>
<path d="{apelido}" fill="{OSSO}"/>
{floreio(w/2 - 112, 444, 150, -1)}{floreio(w/2 + 112, 444, 150, 1)}
<path d="{linha}" fill="{OSSO}" opacity=".7"/>
{tv}
<path d="{chanfro(12, 12, w-24, h-24, 18)}" fill="none" stroke="{MARROM_LINHA}" stroke-width="1.5"/>
<path d="{chanfro(18, 18, w-36, h-36, 14)}" fill="none" stroke="{SANGUE}" stroke-opacity=".55"/>
{cantos}
</g>
</svg>"""
    salvar(saida("cabecalho.svg"), svg)


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
        f'<path class="f f{i}" style="animation-delay:{i*passo - passo*.3:.2f}s" d="{SERIFA.caminho(t, 27, w/2, 37, espaco=.6)}" fill="{OSSO}"/>'
        for i, t in enumerate(frases)
    )
    svg = f"""
{abrir(w, h, " · ".join(frases))}
<style>{css}</style>
{caminhos}
<rect x="{w/2-300}" y="{h-3}" width="600" height="1" fill="{SANGUE_VIVO}" opacity=".5"/>
</svg>"""
    salvar(saida("epigrafe.svg"), svg)


# ---------------------------------------------------------------- divisor
def divisor():
    w, h = 900, 34
    m = w / 2
    svg = f"""
{abrir(w, h, "")}
<defs>{defs_comuns()}</defs>
{floreio(m - 22, 17, 330, -1)}{floreio(m + 22, 17, 330, 1)}
{rosacea_mini(m, 17, 13, SANGUE_VIVO)}
</svg>"""
    salvar(saida("divisor.svg"), svg)


# títulos, botões, certificados, painel de estatísticas e rodapé: peças da folha de artes do Isaque,
# recortadas por arte/recortar_folha.py (em arte/pecas/)


if __name__ == "__main__":
    cabecalho()
    epigrafe()
    divisor()
