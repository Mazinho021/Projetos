# Caça de empresas sem site

Acha empresas sem site no Google, dá pontos a elas, prepara as mensagens e acompanha o funil até a venda. A prévia de cada site é feita na sessão de sites, com o prompt em [`PROMPT-SESSAO-SITES.md`](PROMPT-SESSAO-SITES.md).

## O caminho de cada lead

```
buscar_leads.py ──► ficha JSON ──► sessão de sites ──► link da prévia
                                                          │
         funil.py previa <slug> <link> ◄──────────────────┘
                     │
   fila do dia: mensagem 1 (dia 0) → 2 (dia 2) → 3 (dia 5) → 4 (dia 10)
                     │
   respondeu → proposta → fechou / perdeu
```

## Antes do primeiro uso

1. **Chave do Google Places.** No Google Cloud, crie um projeto, ative a **Places API (New)**, cadastre o cartão (o Google dá uma cota grátis por mês) e crie uma chave restrita a essa API. A chave é guardada no ambiente pelo formulário seguro do Claude Code, e nunca no chat nem no código.
   - Cada busca é uma chamada de até 20 empresas, e o script faz no máximo 3 por busca (60 empresas). O preço do Google muda; confira na página de preços da Places API antes de rodar muitas buscas.
2. **Os seus dados.** Em `config.json`, troque "SEU NOME", o WhatsApp e a cidade. As mensagens e os planos também estão lá, para editar à vontade.

## Comandos

```bash
# Caçar (uma busca por nicho e cidade)
python3 buscar_leads.py "dentista em Campinas" "clínica de estética em Campinas" --min-pontos 6

# Quando a sessão de sites devolver o link da prévia
python3 funil.py previa <slug> <link>

# Todo dia: gera dados/fila.html com as mensagens prontas e o botão do WhatsApp
python3 funil.py fila
python3 funil.py enviei <slug>          # depois de mandar cada mensagem

# Andando no funil
python3 funil.py respondeu <slug> "quer saber o preço"
python3 funil.py proposta <slug> Profissional 497
python3 funil.py fechou <slug> Profissional 497
python3 funil.py perdeu <slug> "achou caro"
python3 funil.py parar <slug>            # pediu para não receber mais
python3 funil.py resumo                  # números e taxas
```

Os pontos de cada lead:

| Critério | Pontos |
|---|---|
| 20 avaliações ou mais e nota 4 ou mais (de 5 a 19 avaliações valem 1) | +3 |
| Nicho de ticket alto (odonto, estética, saúde, oficina, advocacia, pet, contábil, imobiliária, serviços, academia) | +3 |
| Tem celular, que quase sempre é WhatsApp | +2 |
| O "site" é o Instagram | +1 |
| Um concorrente da mesma busca tem site | +1 |

## Regras para não ter problema

- **Um a um, nunca em massa.** A fila abre o WhatsApp com o texto pronto, e você envia. Disparo em massa pelo número pessoal leva a bloqueio.
- **No máximo umas 20 a 30 primeiras mensagens por dia** no começo, e com o número já em uso há algum tempo.
- **Quem pede para parar sai na hora** (`funil.py parar`). A mensagem 1 já oferece essa saída.
- **LGPD:** só dados públicos da empresa e contato comercial. Nada de comprar listas.
- **A prévia é demonstração,** com `noindex` e a faixa avisando que não é o site oficial. Se a empresa não quiser, ela sai do ar no fim da sequência.

## Respostas prontas para as objeções

**"Quanto custa?"**
> Tem três opções, e a mais escolhida é a de R$ 497 + R$ 99/mês, com domínio, hospedagem e o Google Meu Negócio arrumado. Te mando a proposta com as três: {link da proposta}

**"Tá caro."**
> Entendo. Tem o Essencial, que é sem entrada, só R$ 79/mês, e dá para subir de plano depois. Um cliente novo por mês já paga o site.

**"Já tenho Instagram."**
> O Instagram é ótimo para quem já te segue. O site é para quem ainda não te conhece e procura "{categoria} em {cidade}" no Google. Hoje esse cliente cai no {concorrente}.

**"Vou pensar."**
> Claro! Para eu não te encher: o que falta para decidir, o preço ou ver alguma coisa mudada na prévia? Mudo o que você quiser sem custo.

**"Meu sobrinho faz."**
> Show, se ele fizer, ótimo! A prévia fica no ar até sexta se quiser comparar. E o meu inclui a hospedagem e o suporte: se der problema, é comigo.

**"Manda por e-mail."**
> Mando sim! Qual e-mail? Envio a proposta e a prévia. E posso te ligar 5 minutinhos amanhã para tirar dúvida?

## Para fechar

1. Mande a proposta e combine o plano.
2. Cobre o sinal da entrada por Pix ou link de pagamento e marque como `fechou`.
3. Peça o logo, as fotos e o texto de "quem somos", e coloque o site no ar em até 48 h.
4. Depois de 30 dias, ofereça o próximo passo: o Google Meu Negócio, anúncios ou um cardápio digital.
