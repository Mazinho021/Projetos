#!/usr/bin/env python3
"""Anda com o funil: fila do dia, mensagens prontas e o resumo dos números.

Comandos:
  python3 funil.py fila                       gera dados/fila.html com o que fazer hoje
  python3 funil.py previa <slug> <link>       a prévia ficou pronta (vai para a fila da mensagem 1)
  python3 funil.py enviei <slug>              mandei a próxima mensagem da sequência
  python3 funil.py respondeu <slug> [obs]     a empresa respondeu (sai da sequência automática)
  python3 funil.py proposta <slug> <plano> <valor>
  python3 funil.py fechou <slug> [plano] [valor]
  python3 funil.py perdeu <slug> [motivo]
  python3 funil.py parar <slug>               pediu para não receber mais (nunca mais aparece)
  python3 funil.py resumo                     quantos em cada etapa e as taxas
"""
import csv
import html
import json
import sys
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

PASTA = Path(__file__).resolve().parent
FUNIL = PASTA / "dados" / "funil.csv"
FILA = PASTA / "dados" / "fila.html"
CONFIG = json.loads((PASTA / "config.json").read_text(encoding="utf-8"))

ETAPAS = ["novo", "previa_pronta", "msg1", "msg2", "msg3", "msg4",
          "respondeu", "proposta", "fechou", "perdeu", "nao_quer", "sem_resposta"]
SEQUENCIA = {"previa_pronta": "1", "msg1": "2", "msg2": "3", "msg3": "4"}


def ler():
    with FUNIL.open(newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        return leitor.fieldnames, list(leitor)


def gravar(colunas, linhas):
    with FUNIL.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(linhas)


def achar(linhas, slug):
    for linha in linhas:
        if linha["slug"] == slug:
            return linha
    sys.exit(f"Não achei o lead '{slug}' no funil.")


def mensagem(lead, numero):
    chave = "2_sem_concorrente" if numero == "2" and not lead.get("concorrente") else numero
    categoria = (lead.get("categoria") or "empresa").lower()
    return CONFIG["mensagens"][chave].format(
        vendedor=CONFIG["vendedor"]["nome"],
        cidade=lead.get("cidade") or CONFIG["vendedor"]["cidade"],
        empresa=lead["nome"],
        avaliacoes=lead.get("avaliacoes", ""),
        link=lead.get("link_previa", ""),
        concorrente=lead.get("concorrente", ""),
        categoria=categoria,
        bairro=lead.get("bairro", ""),
    )


def vence_em(lead):
    """Data em que a próxima mensagem deve sair."""
    numero = SEQUENCIA.get(lead["etapa"])
    if not numero:
        return None
    if numero == "1":
        return date.today()
    dias = CONFIG["dias_entre_mensagens"]
    inicio = date.fromisoformat(lead["data_contato"])
    return inicio + timedelta(days=dias[int(numero) - 1])


def fila():
    _, linhas = ler()
    hoje = date.today()
    cartoes, sem_previa = [], []
    for lead in linhas:
        if lead["etapa"] == "novo":
            sem_previa.append(lead)
            continue
        quando = vence_em(lead)
        if quando and quando <= hoje:
            numero = SEQUENCIA[lead["etapa"]]
            texto = mensagem(lead, numero)
            wa = ""
            if lead.get("whatsapp"):
                wa = f"https://wa.me/{lead['whatsapp']}?text={urllib.parse.quote(texto)}"
            cartoes.append((lead, numero, texto, wa))

    cartoes.sort(key=lambda c: (c[1], -int(c[0]["pontos"] or 0)))
    sem_previa.sort(key=lambda l: -int(l["pontos"] or 0))
    e = html.escape

    blocos = []
    for lead, numero, texto, wa in cartoes:
        botao = (f'<a class="botao" href="{e(wa)}" target="_blank" rel="noopener">Abrir no WhatsApp</a>'
                 if wa else f'<span class="aviso">Sem celular. Ligar: {e(lead["telefone"] or "—")}</span>')
        blocos.append(f"""
<article>
  <header><span class="msg">Mensagem {numero}</span><strong>{e(lead['nome'])}</strong>
  <span class="meta">{e(lead['categoria'])} · {e(lead['bairro'] or lead['cidade'])} · {lead['pontos']} pontos</span></header>
  <p>{e(texto).replace(chr(10), '<br>')}</p>
  <footer>{botao}<code>python3 funil.py enviei {e(lead['slug'])}</code></footer>
</article>""")

    lista_previa = "".join(
        f"<li><strong>{e(l['nome'])}</strong> · {e(l['categoria'])} · {l['pontos']} pontos "
        f"<code>dados/leads/{e(l['slug'])}.json</code></li>" for l in sem_previa[:20])

    FILA.write_text(f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fila do dia</title>
<style>
:root {{ --fundo:#f6f5f2; --cartao:#fff; --texto:#1d1d1b; --fraco:#6b6a66; --verde:#1f8a4c; --borda:#e3e1dc; }}
@media (prefers-color-scheme: dark) {{ :root {{ --fundo:#141413; --cartao:#1f1f1d; --texto:#f0efe9; --fraco:#a3a29c; --verde:#3fbf72; --borda:#333230; }} }}
body {{ margin:0; padding:16px; background:var(--fundo); color:var(--texto); font:16px/1.5 system-ui, sans-serif; }}
main {{ max-width:680px; margin:0 auto; }}
h1 {{ font-size:22px; margin:8px 0 4px; }} h2 {{ font-size:17px; margin:28px 0 8px; }}
.sub {{ color:var(--fraco); margin:0 0 16px; }}
article {{ background:var(--cartao); border:1px solid var(--borda); border-radius:12px; padding:14px 16px; margin:12px 0; }}
header {{ display:flex; flex-wrap:wrap; gap:4px 10px; align-items:baseline; }}
.msg {{ font-size:12px; font-weight:600; color:var(--verde); text-transform:uppercase; letter-spacing:.04em; }}
.meta {{ color:var(--fraco); font-size:14px; width:100%; }}
footer {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; }}
.botao {{ background:var(--verde); color:#fff; padding:9px 14px; border-radius:8px; text-decoration:none; font-weight:600; }}
.aviso {{ color:var(--fraco); }}
code {{ font-size:12px; color:var(--fraco); overflow-wrap:anywhere; }}
li {{ margin:6px 0; }}
</style></head><body><main>
<h1>Fila do dia · {hoje.strftime('%d/%m/%Y')}</h1>
<p class="sub">{len(cartoes)} mensagens para mandar. Confira o texto, toque no botão, envie no WhatsApp e marque como enviada.</p>
{''.join(blocos) or '<p>Nada para mandar hoje.</p>'}
<h2>Esperando prévia ({len(sem_previa)})</h2>
<p class="sub">Os 20 com mais pontos. Mande as fichas para a sessão de sites.</p>
<ol>{lista_previa}</ol>
</main></body></html>
""", encoding="utf-8")
    print(f"{len(cartoes)} mensagens na fila, {len(sem_previa)} leads esperando prévia → {FILA.relative_to(PASTA)}")


def resumo():
    _, linhas = ler()
    conta = {etapa: 0 for etapa in ETAPAS}
    for linha in linhas:
        conta[linha["etapa"]] = conta.get(linha["etapa"], 0) + 1
    for etapa, n in conta.items():
        if n:
            print(f"{etapa:15} {n}")
    contatados = sum(conta[e] for e in ETAPAS[2:])
    responderam = sum(conta[e] for e in ("respondeu", "proposta", "fechou", "perdeu"))
    if contatados:
        print(f"\nContatados: {contatados}")
        print(f"Responderam: {responderam} ({responderam / contatados:.0%})")
        print(f"Propostas: {conta['proposta'] + conta['fechou'] + conta['perdeu']}")
        print(f"Fechados: {conta['fechou']} ({conta['fechou'] / contatados:.0%} dos contatados)")
        mensal = sum(float(l["valor"] or 0) for l in linhas if l["etapa"] == "fechou")
        print(f"Valor fechado (soma da coluna valor): R$ {mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "ajuda"):
        print(__doc__)
        return
    comando, resto = sys.argv[1], sys.argv[2:]
    if comando == "fila":
        return fila()
    if comando == "resumo":
        return resumo()

    colunas, linhas = ler()
    if not resto:
        sys.exit("Diga o slug do lead.")
    lead = achar(linhas, resto[0])
    hoje = date.today().isoformat()

    if comando == "previa":
        if len(resto) < 2:
            sys.exit("Uso: funil.py previa <slug> <link>")
        lead["link_previa"] = resto[1]
        if lead["etapa"] == "novo":
            lead["etapa"] = "previa_pronta"
    elif comando == "enviei":
        numero = SEQUENCIA.get(lead["etapa"])
        if not numero:
            sys.exit(f"O lead está na etapa '{lead['etapa']}', fora da sequência de mensagens.")
        if numero == "1":
            lead["data_contato"] = hoje
        lead["etapa"] = f"msg{numero}"
        lead["ultima_msg"] = numero
        lead["data_ultima_msg"] = hoje
        if numero == "4":
            lead["obs"] = (lead["obs"] + " | " if lead["obs"] else "") + "sequência completa"
    elif comando == "respondeu":
        lead["etapa"] = "respondeu"
    elif comando == "proposta":
        lead["etapa"] = "proposta"
        lead["plano"], lead["valor"] = (resto[1:3] + ["", ""])[:2]
    elif comando == "fechou":
        lead["etapa"] = "fechou"
        if len(resto) > 1:
            lead["plano"], lead["valor"] = (resto[1:3] + [""])[:2]
    elif comando in ("perdeu", "parar"):
        lead["etapa"] = "perdeu" if comando == "perdeu" else "nao_quer"
    else:
        sys.exit(f"Comando desconhecido: {comando}. Veja: python3 funil.py ajuda")

    extra = " ".join(resto[1:]) if comando in ("respondeu", "perdeu") else ""
    if extra:
        lead["obs"] = (lead["obs"] + " | " if lead["obs"] else "") + extra
    gravar(colunas, linhas)
    print(f"{lead['nome']}: etapa {lead['etapa']}")


if __name__ == "__main__":
    main()
