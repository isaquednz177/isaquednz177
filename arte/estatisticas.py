"""Faixa com as estatísticas do GitHub, escritas sobre a moldura gótica (arte/faixa-estatisticas.webp).

Roda na automação (.github/workflows/snake.yml), com o GITHUB_TOKEN que o próprio
GitHub dá a cada execução (só lê dados públicos do perfil).

Uso:  python arte/estatisticas.py dist/estatisticas-v2.svg
      python arte/estatisticas.py previa.svg --exemplo     (números de mentira, para ver o desenho)
"""
import base64
import json
import os
import sys
import urllib.request
from datetime import date

from base import OSSO, PASTA, SERIFA, SERIFA_FORTE, abrir, quadrifolio, salvar

# moldura da faixa: arte do Isaque, com os números de exemplo apagados (só a placa e as duas ogivas)
MOLDURA = "faixa-estatisticas.webp"
W, H = 2118, 271          # tamanho da arte original; a imagem embutida é menor e escala junto
AREA = (198, 1928)        # entre as duas ogivas
LINHA, CENTRO = 149, 134  # linha de base do texto e altura dos quadrifólios

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
    tn, tl, vao, sep = 73.0, 41.5, 20.0, 93.0
    def larguras(k):
        return [SERIFA_FORTE.largura(v, tn * k) + vao * k + SERIFA.largura(r, tl * k) for v, r in lista]
    total = sum(larguras(1)) + sep * (len(lista) - 1)
    k = min(1.0, (AREA[1] - AREA[0]) / total)  # número grande demais: encolhe tudo junto
    lg = larguras(k)
    x = (AREA[0] + AREA[1]) / 2 - (sum(lg) + sep * k * (len(lista) - 1)) / 2
    partes = []
    for i, ((v, r), l) in enumerate(zip(lista, lg)):
        partes.append(f'<path d="{SERIFA_FORTE.caminho(v, tn * k, x, LINHA, ancora="inicio")}" fill="url(#num)"/>')
        xr = x + SERIFA_FORTE.largura(v, tn * k) + vao * k
        partes.append(f'<path d="{SERIFA.caminho(r, tl * k, xr, LINHA, ancora="inicio")}" fill="{OSSO}"/>')
        x += l
        if i < len(lista) - 1:
            partes.append(f'<path d="{quadrifolio(x + sep * k / 2, CENTRO, 16 * k)}" fill="url(#num)"/>')
            x += sep * k
    with open(os.path.join(PASTA, MOLDURA), "rb") as f:
        moldura = base64.b64encode(f.read()).decode()
    rotulo = " · ".join(f"{v} {r}" for v, r in lista)
    return f"""
{abrir(W, H, rotulo)}
<defs>
<linearGradient id="num" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F0525B"/><stop offset=".55" stop-color="#C8141F"/><stop offset="1" stop-color="#8E0A13"/></linearGradient>
<filter id="sombra" x="-5%" y="-30%" width="110%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#000" flood-opacity=".85"/></filter>
</defs>
<image href="data:image/webp;base64,{moldura}" width="{W}" height="{H}"/>
<g filter="url(#sombra)">{"".join(partes)}</g>
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
