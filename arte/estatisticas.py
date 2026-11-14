"""Faixa pequena com as estatísticas do GitHub, no mesmo estilo das outras artes.

Roda na automação (.github/workflows/snake.yml), com o GITHUB_TOKEN que o próprio
GitHub dá a cada execução (só lê dados públicos do perfil).

Uso:  python arte/estatisticas.py dist/estatisticas.svg
      python arte/estatisticas.py previa.svg --exemplo     (números de mentira, para ver o desenho)
"""
import json
import os
import sys
import urllib.request
from datetime import date

from base import (MARROM_LINHA, OSSO, SANGUE, SANGUE_CLARO, SANGUE_VIVO, SERIFA, SERIFA_FORTE,
                  abrir, chanfro, defs_comuns, f1, quadrifolio, salvar, textura)

CONSULTA = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def buscar(login, token):
    corpo = json.dumps({"query": CONSULTA, "variables": {"login": login}}).encode()
    pedido = urllib.request.Request(
        "https://api.github.com/graphql", data=corpo,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "readme-estatisticas"},
    )
    with urllib.request.urlopen(pedido, timeout=30) as r:
        dados = json.load(r)
    if dados.get("errors"):
        raise RuntimeError(dados["errors"][0].get("message", "erro na API do GitHub"))
    return dados["data"]["user"]


def sequencia(dias):
    """Dias seguidos com contribuição até hoje (hoje sem nada ainda não quebra a sequência)."""
    dias = sorted(dias, key=lambda d: d["date"])
    if dias and dias[-1]["contributionCount"] == 0 and dias[-1]["date"] >= date.today().isoformat():
        dias = dias[:-1]
    n = 0
    for d in reversed(dias):
        if d["contributionCount"] == 0:
            break
        n += 1
    return n


def numeros(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    dias = [d for s in cal["weeks"] for d in s["contributionDays"]]
    return {
        "contribuicoes": cal["totalContributions"],
        "sequencia": sequencia(dias),
        "repositorios": u["repositories"]["totalCount"],
        "estrelas": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "seguidores": u["followers"]["totalCount"],
    }


def milhar(n):
    return f"{n:,}".replace(",", ".")


def itens(n):
    def p(v, um, varios):
        return (milhar(v), um if v == 1 else varios)
    return [
        p(n["contribuicoes"], "contribuição no ano", "contribuições no ano"),
        p(n["sequencia"], "dia seguido", "dias seguidos"),
        p(n["repositorios"], "repositório", "repositórios"),
        p(n["estrelas"], "estrela", "estrelas"),
        p(n["seguidores"], "seguidor", "seguidores"),
    ]


def desenhar(n):
    lista = itens(n)
    tn, tl, vao, sep = 18, 13, 7, 34
    larguras = [SERIFA_FORTE.largura(v, tn) + vao + SERIFA.largura(r, tl, .6) for v, r in lista]
    w = int(sum(larguras) + sep * (len(lista) - 1) + 56)
    h = 40
    tv_defs, tv = textura(w, h, "te")
    partes = []
    x = 28
    for i, ((v, r), lg) in enumerate(zip(lista, larguras)):
        partes.append(f'<path d="{SERIFA_FORTE.caminho(v, tn, x, 26, ancora="inicio")}" fill="{SANGUE_CLARO}"/>')
        xr = x + SERIFA_FORTE.largura(v, tn) + vao
        partes.append(f'<path d="{SERIFA.caminho(r, tl, xr, 25.5, ancora="inicio", espaco=.6)}" fill="{OSSO}" opacity=".8"/>')
        x += lg
        if i < len(lista) - 1:
            partes.append(f'<path d="{quadrifolio(x + sep/2, h/2, 6)}" fill="{SANGUE}"/>')
            x += sep
    rotulo = " · ".join(f"{v} {r}" for v, r in lista)
    return f"""
{abrir(w, h, rotulo)}
<defs>{defs_comuns()}{tv_defs}<clipPath id="c"><path d="{chanfro(1, 1, w-2, h-2, 9)}"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#placa)"/>{tv}</g>
<path d="{chanfro(1, 1, w-2, h-2, 9)}" fill="none" stroke="{MARROM_LINHA}"/>
<path d="M10,1 H{f1(w*.3)}" stroke="{SANGUE_VIVO}" stroke-width="2"/>
{"".join(partes)}
</svg>"""


if __name__ == "__main__":
    destino = sys.argv[1]
    if "--exemplo" in sys.argv:
        n = {"contribuicoes": 1234, "sequencia": 6, "repositorios": 8, "estrelas": 3, "seguidores": 1}
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("falta o GITHUB_TOKEN")
        login = os.environ.get("GITHUB_REPOSITORY_OWNER", "isaquednz177")
        n = numeros(buscar(login, token))
    print(n)
    salvar(destino, desenhar(n))
