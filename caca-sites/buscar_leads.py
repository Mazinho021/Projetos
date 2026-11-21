#!/usr/bin/env python3
"""Caça empresas sem site no Google (Places API New), dá pontos e põe no funil.

Uso:
  python3 buscar_leads.py "dentista em Campinas" "oficina mecânica em Campinas"
  python3 buscar_leads.py --arquivo exemplos/resposta-exemplo.json   (teste sem a API)

Saídas:
  dados/funil.csv          a planilha do funil (abre no Google Sheets ou Excel)
  dados/leads/<slug>.json  a ficha de cada lead, que a sessão de sites usa na prévia
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

PASTA = Path(__file__).resolve().parent
DADOS = PASTA / "dados"
FUNIL = DADOS / "funil.csv"
FICHAS = DADOS / "leads"

URL = "https://places.googleapis.com/v1/places:searchText"
CAMPOS = ",".join("places." + c for c in [
    "id", "displayName", "formattedAddress", "addressComponents", "location",
    "nationalPhoneNumber", "websiteUri", "rating", "userRatingCount",
    "primaryType", "primaryTypeDisplayName", "types", "googleMapsUri",
    "regularOpeningHours", "businessStatus", "reviews", "editorialSummary",
]) + ",nextPageToken"

# Endereços que não são site de verdade: a empresa é lead mesmo assim.
SITE_FALSO = [
    "instagram.com", "facebook.com", "fb.com", "fb.me", "linktr.ee", "wa.me",
    "whatsapp.com", "beacons.ai", "bio.link", "linkbio", "taplink", "lnk.bio",
    "linkin.bio", "tiktok.com", "ifood.com.br", "business.site", "g.page",
    "sites.google.com", "goo.gl", "bit.ly", "linktree",
]

# Nicho de cada lead, para a sessão de sites escolher o modelo.
# Cada nicho: tipos do Google e palavras do nome da categoria em português.
NICHOS = {
    "odonto": (["dentist", "dental_clinic"], ["dentist", "odonto", "ortodon"]),
    "estetica": (["beauty_salon", "hair_salon", "spa", "skin_care_clinic", "nail_salon", "barber_shop", "beautician", "hair_care"],
                 ["estétic", "estetic", "salão", "salao", "cabelo", "barbear", "unha", "depila", "sobrancelha", "spa"]),
    "saude": (["doctor", "physiotherapist", "medical_clinic", "psychologist", "chiropractor", "medical_lab", "nutritionist"],
              ["clínica", "clinica", "médic", "medic", "fisioter", "psicólog", "psicolog", "nutri", "pilates"]),
    "oficina": (["car_repair", "car_wash", "auto_parts_store", "tire_shop"],
                ["oficina", "mecânic", "mecanic", "auto center", "funilaria", "borracharia", "lava"]),
    "advocacia": (["lawyer", "legal_services"], ["advoga", "advocacia", "jurídic", "juridic"]),
    "pet": (["veterinary_care", "pet_store", "pet_care"], ["veterin", "pet", "banho e tosa"]),
    "contabil": (["accounting"], ["contab", "contador"]),
    "academia": (["gym", "fitness_center"], ["academia", "crossfit", "fitness", "luta"]),
    "imobiliaria": (["real_estate_agency"], ["imobili", "corretor"]),
    "servicos": (["plumber", "electrician", "roofing_contractor", "painter", "locksmith", "moving_company", "general_contractor", "home_improvement_store"],
                 ["encanad", "eletricist", "pintor", "chaveiro", "mudança", "reforma", "marcenar", "serralher", "vidraç", "dedetiz"]),
    "restaurante": (["restaurant", "bakery", "cafe", "meal_takeaway", "pizza_restaurant", "bar"],
                    ["restaurante", "padaria", "pizzaria", "lanchonete", "café", "hamburg", "marmit", "doceria", "confeitaria"]),
}
# Nichos de ticket alto: valem mais pontos.
TICKET_ALTO = {"odonto", "estetica", "saude", "oficina", "advocacia", "pet", "contabil", "imobiliaria", "servicos", "academia"}

COLUNAS = [
    "pontos", "etapa", "nome", "nicho", "categoria", "bairro", "cidade", "telefone",
    "whatsapp", "nota", "avaliacoes", "situacao_site", "site_atual", "concorrente",
    "slug", "link_previa", "data_contato", "ultima_msg", "data_ultima_msg",
    "plano", "valor", "obs", "maps", "place_id", "busca", "coletado_em",
]


def sem_acento(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def fazer_slug(texto):
    return re.sub(r"[^a-z0-9]+", "-", sem_acento(texto).lower()).strip("-")[:60]


def situacao_do_site(url):
    if not url:
        return "sem_site"
    url = url.lower()
    if any(f in url for f in SITE_FALSO):
        return "site_falso"
    return "tem_site"


def descobrir_nicho(lugar):
    tipos = set(lugar.get("types", [])) | {lugar.get("primaryType", "")}
    nome_cat = (lugar.get("primaryTypeDisplayName", {}).get("text", "") + " "
                + lugar.get("displayName", {}).get("text", "")).lower()
    for nicho, (tipos_google, palavras) in NICHOS.items():
        if tipos & set(tipos_google):
            return nicho
    for nicho, (_, palavras) in NICHOS.items():
        if any(p in nome_cat for p in palavras):
            return nicho
    return "generico"


def telefone_e_whatsapp(lugar):
    tel = lugar.get("nationalPhoneNumber", "")
    num = re.sub(r"\D", "", tel).lstrip("0")
    # Celular no Brasil: DDD + 9 dígitos começando com 9.
    whatsapp = "55" + num if len(num) == 11 and num[2] == "9" else ""
    return tel, whatsapp


def parte_do_endereco(lugar, *tipos):
    for comp in lugar.get("addressComponents", []):
        if set(comp.get("types", [])) & set(tipos):
            return comp.get("shortText") if "administrative_area_level_1" in tipos else comp.get("longText", "")
    return ""


def pontuar(lead, tem_concorrente):
    pontos = 0
    if lead["avaliacoes"] >= 20 and lead["nota"] >= 4:
        pontos += 3
    elif lead["avaliacoes"] >= 5 and lead["nota"] >= 4:
        pontos += 1
    if lead["nicho"] in TICKET_ALTO:
        pontos += 3
    if lead["whatsapp"]:
        pontos += 2
    if "instagram.com" in lead["site_atual"].lower():
        pontos += 1
    if tem_concorrente:
        pontos += 1
    return pontos


def buscar_na_api(consulta, paginas):
    chave = os.environ.get("GOOGLE_PLACES_API_KEY", "chave-injetada-pelo-proxy")
    lugares, token = [], None
    for _ in range(paginas):
        corpo = {"textQuery": consulta, "languageCode": "pt-BR", "regionCode": "BR", "pageSize": 20}
        if token:
            corpo["pageToken"] = token
        pedido = urllib.request.Request(URL, data=json.dumps(corpo).encode(), method="POST", headers={
            "Content-Type": "application/json", "X-Goog-Api-Key": chave, "X-Goog-FieldMask": CAMPOS,
        })
        try:
            with urllib.request.urlopen(pedido, timeout=30) as resp:
                dados = json.load(resp)
        except urllib.error.HTTPError as erro:
            sys.exit(f"Erro {erro.code} do Google em \"{consulta}\": {erro.read().decode()[:400]}")
        lugares += dados.get("places", [])
        token = dados.get("nextPageToken")
        if not token:
            break
        time.sleep(2)
    return lugares


def montar_lead(lugar, consulta, concorrente, hoje):
    nome = lugar.get("displayName", {}).get("text", "").strip()
    tel, whatsapp = telefone_e_whatsapp(lugar)
    cidade = parte_do_endereco(lugar, "administrative_area_level_2", "locality")
    avaliacoes_boas = sorted(
        (r for r in lugar.get("reviews", []) if r.get("rating", 0) >= 4 and r.get("text", {}).get("text")),
        key=lambda r: (-r.get("rating", 0), -len(r["text"]["text"])),
    )[:3]
    return {
        "place_id": lugar["id"],
        "nome": nome,
        "nicho": descobrir_nicho(lugar),
        "categoria": lugar.get("primaryTypeDisplayName", {}).get("text", ""),
        "categoria_google": lugar.get("primaryType", ""),
        "telefone": tel,
        "whatsapp": whatsapp,
        "endereco": lugar.get("formattedAddress", ""),
        "bairro": parte_do_endereco(lugar, "sublocality_level_1", "sublocality"),
        "cidade": cidade,
        "uf": parte_do_endereco(lugar, "administrative_area_level_1"),
        "lat": lugar.get("location", {}).get("latitude"),
        "lng": lugar.get("location", {}).get("longitude"),
        "maps": lugar.get("googleMapsUri", ""),
        "nota": lugar.get("rating", 0),
        "avaliacoes": lugar.get("userRatingCount", 0),
        "horario": lugar.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
        "resumo": lugar.get("editorialSummary", {}).get("text", ""),
        "avaliacoes_destaque": [{
            "autor": r.get("authorAttribution", {}).get("displayName", ""),
            "nota": r.get("rating"),
            "texto": r["text"]["text"],
            "quando": r.get("relativePublishTimeDescription", ""),
        } for r in avaliacoes_boas],
        "situacao_site": situacao_do_site(lugar.get("websiteUri")),
        "site_atual": lugar.get("websiteUri", ""),
        "concorrente": concorrente,
        "busca": consulta,
        "coletado_em": hoje,
    }


def ler_funil():
    if not FUNIL.exists():
        return {}
    with FUNIL.open(newline="", encoding="utf-8") as f:
        return {linha["place_id"]: linha for linha in csv.DictReader(f)}


def gravar_funil(funil):
    linhas = sorted(funil.values(), key=lambda l: -int(l.get("pontos") or 0))
    with FUNIL.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUNAS, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(linhas)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("buscas", nargs="*", help='ex.: "dentista em Campinas"')
    ap.add_argument("--arquivo", help="usar uma resposta salva do Google em vez da API (teste)")
    ap.add_argument("--paginas", type=int, default=3, help="páginas de 20 por busca (máx. 3 = 60 empresas)")
    ap.add_argument("--min-pontos", type=int, default=0, help="só põe no funil quem tem esses pontos ou mais")
    args = ap.parse_args()
    if not args.buscas and not args.arquivo:
        ap.error("diga pelo menos uma busca ou --arquivo")

    DADOS.mkdir(exist_ok=True)
    FICHAS.mkdir(exist_ok=True)
    hoje = date.today().isoformat()
    funil = ler_funil()
    slugs_usados = {l["slug"] for l in funil.values()}

    if args.arquivo:
        resposta = json.loads(Path(args.arquivo).read_text(encoding="utf-8"))
        lotes = [(resposta.get("busca", "teste"), resposta.get("places", []))]
    else:
        lotes = [(b, buscar_na_api(b, args.paginas)) for b in args.buscas]

    for consulta, lugares in lotes:
        ativos = [l for l in lugares if l.get("businessStatus", "OPERATIONAL") == "OPERATIONAL"]
        com_site = [l for l in ativos if situacao_do_site(l.get("websiteUri")) == "tem_site"]
        # O concorrente da mensagem 2: quem tem site e mais avaliações na mesma busca.
        melhor = max(com_site, key=lambda l: l.get("userRatingCount", 0), default=None)
        concorrente = melhor.get("displayName", {}).get("text", "") if melhor else ""

        novos = atualizados = 0
        for lugar in ativos:
            if situacao_do_site(lugar.get("websiteUri")) == "tem_site":
                continue
            lead = montar_lead(lugar, consulta, concorrente, hoje)
            lead["pontos"] = pontuar(lead, bool(concorrente))
            if lead["pontos"] < args.min_pontos:
                continue

            antigo = funil.get(lead["place_id"])
            if antigo:
                lead["slug"] = antigo["slug"]
                atualizados += 1
            else:
                base = fazer_slug(f"{lead['nome']} {lead['cidade']}") or fazer_slug(lead["place_id"])
                slug, n = base, 2
                while slug in slugs_usados:
                    slug, n = f"{base}-{n}", n + 1
                lead["slug"] = slug
                slugs_usados.add(slug)
                novos += 1

            (FICHAS / f"{lead['slug']}.json").write_text(
                json.dumps(lead, ensure_ascii=False, indent=2), encoding="utf-8")

            linha = dict(antigo or {"etapa": "novo"})
            for col in COLUNAS:
                if col in lead and col not in ("etapa",):
                    linha[col] = lead[col]
            funil[lead["place_id"]] = linha

        print(f"{consulta}: {len(ativos)} ativas, {len(com_site)} com site, "
              f"{novos} leads novos, {atualizados} atualizados. Concorrente com site: {concorrente or '—'}")

    gravar_funil(funil)
    print(f"\nFunil: {FUNIL.relative_to(PASTA)} ({len(funil)} leads). Fichas em {FICHAS.relative_to(PASTA)}/")


if __name__ == "__main__":
    main()
