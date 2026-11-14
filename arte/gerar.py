"""Gera as artes fixas do README (cabeçalho, títulos, botões, certificados, divisor, rodapé).

Uso:  pip install fonttools brotli
      python arte/gerar.py

A faixa de estatísticas é outra: arte/estatisticas.py, rodada pela automação do GitHub.
"""
import math
import os

from base import (GOTICA, MARROM_LINHA, OSSO, PASTA, PRETO_2, SANGUE, SANGUE_CLARO, SANGUE_ESC,
                  SANGUE_VIVO, SERIFA, abrir, brasas, casario, chanfro, defs_comuns, f1, fachada,
                  floreio, morcego, ogiva, placa, quadrifolio, rosacea, rosacea_mini, salvar, textura, torre)


def saida(nome):
    return os.path.join(PASTA, nome)


# ---------------------------------------------------------------- cabeçalho
def cabecalho():
    w, h = 1200, 380
    tv_defs, tv = textura(w, h)
    css_brasas, pontos = brasas(w, h, 24, 3)
    nome = GOTICA.caminho("Isaque Diniz", 104, w / 2, 178)
    apelido = SERIFA.caminho("Billy camomilla", 25, w / 2, 218, espaco=1.5)
    linha = SERIFA.caminho("ESTUDANTE  ·  INTELIGÊNCIA ARTIFICIAL  ·  ENGENHARIA DE SOFTWARE", 15, w / 2, 250, espaco=3)
    cantos = "".join(f'<path d="{quadrifolio(x, y, 9)}" fill="{SANGUE_VIVO}"/>' for x, y in ((w - 12, 12), (12, h - 12)))
    svg = f"""
{abrir(w, h, "Isaque Diniz, Billy camomilla: estudante de inteligência artificial e engenharia de software")}
<defs>{defs_comuns()}{tv_defs}
<linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A0605"/><stop offset=".55" stop-color="#170D09"/><stop offset="1" stop-color="#2A110C"/></linearGradient>
<radialGradient id="brilho" cx=".5" cy=".46" r=".5"><stop offset="0" stop-color="{SANGUE}" stop-opacity=".42"/><stop offset=".6" stop-color="{SANGUE_ESC}" stop-opacity=".15"/><stop offset="1" stop-color="{SANGUE_ESC}" stop-opacity="0"/></radialGradient>
<filter id="sombra" x="-10%" y="-30%" width="120%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#000" flood-opacity=".95"/><feDropShadow dx="0" dy="0" stdDeviation="12" flood-color="{SANGUE}" flood-opacity=".6"/></filter>
<clipPath id="corte"><path d="{chanfro(0, 0, w, h, 26)}"/></clipPath></defs>
{css_brasas}
<g clip-path="url(#corte)">
<rect width="{w}" height="{h}" fill="url(#ceu)"/>
<ellipse cx="{w/2}" cy="175" rx="470" ry="170" fill="url(#brilho)"/>
{rosacea(w/2, 175, 158, SANGUE, largura=1.3, opacidade=.32, petalas=16)}
{morcego(205, 72, .8)}{morcego(250, 108, .5)}{morcego(960, 84, .7)}{morcego(1000, 54, .45)}
<g opacity=".7">{casario(w, h - 10, 11, .62, "#120906", janelas=False)}</g>
{casario(w, h, 4, .55)}
{torre(50, 68, 190, h, 5)}{torre(w - 50 - 68, 68, 190, h, 6)}
{pontos}
<path d="{nome}" fill="url(#sangue)" filter="url(#sombra)"/>
<path d="{apelido}" fill="{OSSO}"/>
{floreio(w/2 - 120, 210, 150, -1)}{floreio(w/2 + 120, 210, 150, 1)}
<path d="{linha}" fill="{OSSO}" opacity=".75"/>
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


# ---------------------------------------------------------------- títulos das seções
def titulo(arquivo, texto, rotulo):
    w, h = 900, 78
    p_defs, p_corpo = placa(w, h)
    larg = GOTICA.largura(texto, 44)
    meio = w / 2
    svg = f"""
{abrir(w, h, rotulo)}
<defs>{defs_comuns()}{p_defs}
<radialGradient id="luz"><stop offset="0" stop-color="{SANGUE}" stop-opacity=".45"/><stop offset="1" stop-color="{SANGUE}" stop-opacity="0"/></radialGradient></defs>
{p_corpo}
<ellipse cx="{meio}" cy="{h}" rx="320" ry="46" fill="url(#luz)"/>
<path d="{GOTICA.caminho(texto, 44, meio, 54)}" fill="url(#sangue)"/>
{floreio(meio - larg/2 - 24, 39, 170, -1)}{floreio(meio + larg/2 + 24, 39, 170, 1)}
</svg>"""
    salvar(saida(arquivo), svg)


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


# ---------------------------------------------------------------- botões dos links
def botao(arquivo, texto, rotulo):
    tam = 17
    larg = SERIFA.largura(texto, tam, 3)
    w, h = int(larg + 68), 42
    svg = f"""
{abrir(w, h, rotulo)}
<defs><linearGradient id="p" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A0A0E"/><stop offset="1" stop-color="#1A0907"/></linearGradient></defs>
<path d="{chanfro(1, 1, w-2, h-2, 8)}" fill="url(#p)" stroke="{SANGUE_VIVO}" stroke-opacity=".75"/>
<path d="M9,1 H{f1(w*.45)}" stroke="{SANGUE_CLARO}" stroke-width="2"/>
<path d="{quadrifolio(17, h/2, 7)}" fill="{SANGUE_CLARO}"/><path d="{quadrifolio(w-17, h/2, 7)}" fill="{SANGUE_CLARO}"/>
<path d="{SERIFA.caminho(texto, tam, w/2, 27, espaco=3)}" fill="{OSSO}"/>
</svg>"""
    salvar(saida(arquivo), svg)


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
    """Lacre de cera cor de sangue com um quadrifólio."""
    pts = " ".join(
        f"{f1(cx + (27 + (2.2 if i % 2 else 0)) * math.cos(i / 36 * 2 * math.pi))},"
        f"{f1(cy + (27 + (2.2 if i % 2 else 0)) * math.sin(i / 36 * 2 * math.pi))}"
        for i in range(36)
    )
    return (
        f'<polygon points="{pts}" fill="#5A0A12"/>'
        f'<circle cx="{cx}" cy="{cy}" r="21" fill="{SANGUE}" stroke="#3A0509"/>'
        f'<circle cx="{cx}" cy="{cy}" r="16" fill="none" stroke="#3A0509" stroke-dasharray="2 2.5"/>'
        f'<path d="{quadrifolio(cx, cy, 12)}" fill="#3A0509"/>'
    )


def certificado(arquivo, categoria, texto, escola, horas, data, rotulo):
    w, h = 460, 250
    p_defs, p_corpo = placa(w, h, 16)
    linhas = quebrar(SERIFA, texto, 25, 330)[:3]
    titulo_d = " ".join(SERIFA.caminho(l, 25, 30, 82 + i * 29, ancora="inicio") for i, l in enumerate(linhas))
    y_escola = 82 + len(linhas) * 29 + 8
    seta = f'<path d="M{w-40},{h-33} l9,-9 M{w-38},{h-42} h7 v7" stroke="{SANGUE_CLARO}" stroke-width="1.4" fill="none"/>'
    svg = f"""
{abrir(w, h, rotulo)}
<defs>{defs_comuns()}{p_defs}
<radialGradient id="luz" cx=".85" cy=".1" r=".6"><stop offset="0" stop-color="{SANGUE}" stop-opacity=".3"/><stop offset="1" stop-color="{SANGUE}" stop-opacity="0"/></radialGradient></defs>
{p_corpo}
<path d="{chanfro(1, 1, w-2, h-2, 16)}" fill="url(#luz)"/>
<path d="{ogiva(w-150, h-64, 60, 112)}" fill="none" stroke="{SANGUE}" stroke-opacity=".25" stroke-width="1.5"/>
<path d="{ogiva(w-142, h-64, 44, 98)}" fill="none" stroke="{SANGUE}" stroke-opacity=".18"/>
<path d="{chanfro(8, 8, w-16, h-16, 11)}" fill="none" stroke="{MARROM_LINHA}" stroke-opacity=".6"/>
<path d="{SERIFA.caminho(categoria.upper(), 12, 30, 44, ancora="inicio", espaco=2.6)}" fill="{SANGUE_CLARO}"/>
{selo(w - 52, 52)}
<path d="{titulo_d}" fill="{OSSO}"/>
<path d="{SERIFA.caminho(escola, 16, 30, y_escola, ancora="inicio", espaco=.4)}" fill="{SANGUE_CLARO}"/>
<rect x="30" y="{h-56}" width="{w-60}" height="1" fill="url(#linhaD)" opacity=".6"/>
<path d="{SERIFA.caminho(f"{horas}  ·  {data}", 15, 30, h-30, ancora="inicio", espaco=1)}" fill="{OSSO}" opacity=".7"/>
<path d="{SERIFA.caminho("VERIFICAR", 12, w-54, h-30, ancora="fim", espaco=2.4)}" fill="{SANGUE_CLARO}"/>
{seta}
</svg>"""
    salvar(saida(arquivo), svg)


# ---------------------------------------------------------------- rodapé
def rodape():
    w, h = 1200, 260
    css_brasas, pontos = brasas(w, h, 14, 9)
    svg = f"""
{abrir(w, h, "")}
<defs>
<linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PRETO_2}" stop-opacity="0"/><stop offset=".45" stop-color="#170D09"/><stop offset="1" stop-color="#2E120C"/></linearGradient>
<radialGradient id="brilho" cx=".5" cy="1" r=".55"><stop offset="0" stop-color="{SANGUE}" stop-opacity=".5"/><stop offset="1" stop-color="{SANGUE}" stop-opacity="0"/></radialGradient></defs>
{css_brasas}
<rect width="{w}" height="{h}" fill="url(#ceu)"/>
<ellipse cx="{w/2}" cy="{h}" rx="420" ry="200" fill="url(#brilho)"/>
{pontos}
<g opacity=".7">{casario(w, h - 8, 21, .62, "#120906", janelas=False)}</g>
{casario(w, h, 8, .7)}
{fachada(w/2, h, .8)}
{morcego(470, 40, .6)}{morcego(760, 58, .45)}
</svg>"""
    salvar(saida("rodape.svg"), svg)


if __name__ == "__main__":
    cabecalho()
    epigrafe()
    divisor()
    rodape()
    titulo("titulo-sobre.svg", "Sobre mim", "Sobre mim")
    titulo("titulo-estudos.svg", "Estudos", "Estudos")
    titulo("titulo-certificados.svg", "Certificados", "Certificados")
    titulo("titulo-contribuicoes.svg", "Contribuições", "Contribuições")
    botao("botao-linkedin.svg", "LINKEDIN", "LinkedIn")
    botao("botao-email.svg", "E-MAIL", "E-mail")
    certificado("certificado-sql.svg", "banco de dados", "Banco de Dados SQL do Zero ao Avançado + Projetos Reais",
                "Udemy · Andre Iacono", "8 horas", "novembro de 2026",
                "Certificado: Banco de Dados SQL do Zero ao Avançado, Udemy")
    certificado("certificado-claude.svg", "inteligência artificial", "Mastering Claude Cowork, Claude Design & AI Agents",
                "Udemy · Ryan Ahmed, Stemplicity", "8,5 horas", "novembro de 2026",
                "Certificado: Mastering Claude Cowork, Claude Design & AI Agents, Udemy")
