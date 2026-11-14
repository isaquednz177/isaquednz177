"""Gera as artes fixas do README (cabeçalho, títulos, botões, certificados, divisor, rodapé).

Uso:  pip install fonttools brotli
      python arte/gerar.py

A faixa de estatísticas é outra: arte/estatisticas.py, rodada pela automação do GitHub.
"""
import base64
import math
import os

from base import (GOTICA, MARROM_LINHA, OSSO, PASTA, PRETO_2, SANGUE, SANGUE_CLARO, SANGUE_ESC,
                  SANGUE_VIVO, SERIFA, abrir, brasas, casario, chanfro, defs_comuns, f1, fachada,
                  floreio, morcego, ogiva, placa, quadrifolio, rosacea, rosacea_mini, salvar, textura, torre)


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


# botões dos links (LinkedIn, E-mail, Instagram): artes prontas do Isaque em arte/botao-*-v1.png


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
    certificado("certificado-sql.svg", "banco de dados", "Banco de Dados SQL do Zero ao Avançado + Projetos Reais",
                "Udemy · Andre Iacono", "8 horas", "novembro de 2026",
                "Certificado: Banco de Dados SQL do Zero ao Avançado, Udemy")
    certificado("certificado-claude.svg", "inteligência artificial", "Mastering Claude Cowork, Claude Design & AI Agents",
                "Udemy · Ryan Ahmed, Stemplicity", "8,5 horas", "novembro de 2026",
                "Certificado: Mastering Claude Cowork, Claude Design & AI Agents, Udemy")
