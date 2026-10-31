# Parte 3 — O preço

Roteiro em [`roteiro-ep03.txt`](roteiro-ep03.txt), com a voz de cada fala. Na Parte 2, o público escolheu FUGIR, com 10 votos contra 3 (77% e 23%), e deu ao amigo o nome **Renato**.

Este é o terceiro roteiro da Parte 3, de 31/10/2026. O criador recusou os dois primeiros, “A noite”, que seguiam uma fuga pelo bairro, um bar e uma avenida. Ele pediu outro caminho para a história e imagens novas, de mais qualidade. As imagens e as vozes estão pedidas ao Codex em [`pedido-codex-ep03.md`](pedido-codex-ep03.md), com a regra de composição que evita rostos atrás do painel do topo (ver [`../../CLAUDE.md`](../../CLAUDE.md)).

O vídeo tem **2 min 15 s**:
- a vinheta da Parte 1, com 12 s;
- 101 s do narrador, com 254 palavras mais as 16 do pedido do fim;
- 7,5 s do Renato;
- 13,7 s do cobrador;
- as pausas de montagem.

## A história

Fugir tem um preço, e quem paga é Renato. Dois homens descem do carro com uma lanterna, e os dois fogem pela cozinha até o muro do quintal. Renato dá pé para Zinho pular. Quando é a vez dele, uma mão com o anel de ouro da foto da divisão puxa a jaqueta dele por trás. Ele grita “Corre! Corre!”, e Zinho corre.

Sozinho, Zinho se esconde num ônibus abandonado no fim da linha. O celular vibra com o número do Renato, mas não é ele. Primeiro vem uma foto: Renato numa cadeira, com o lábio cortado, num ferro-velho, e no ombro dele a mão com o anel. Depois vem um áudio do cobrador, calmo demais: “Você correu. Ele não. Vamos trocar: você por ele. Três da manhã, no ferro-velho. Sozinho. Se chamar a polícia, a mãe dele é a próxima.”

A mãe é a mesma que dava almoço a Zinho quando eles eram moleques. Faltam menos de duas horas. O homem que vendeu o nome de Zinho agora paga por ele, mas foi o mesmo que deu pé a ele no muro. A votação é **TROCAR ou DEIXAR**.

O que muda em relação às versões recusadas:

- **A reviravolta de verdade:** Renato é pego no lugar de Zinho.
- **Uma escolha moral para o público:** trocar a própria liberdade pelo homem que o traiu, ou deixá-lo.
- **As pistas fazem a história andar:** o anel tem dono e está perto, o ferro-velho da foto vira o lugar da troca, e a mãe vira refém da ameaça.

## Estrutura

Os desenhos do Codex chegaram com 941 × 1672 e foram ampliados para 1440 × 2560 por [`montagem/ampliar_cenas.py`](montagem/ampliar_cenas.py). Os originais estão em [`originais/`](originais/).

| Trecho | Voz | Imagem | Na tela |
|---|---|---|---|
| Abertura | Vinheta da Parte 1, aviso e votação | `../episodio-01/cena-01-base.png` e fundo escuro | O bloco de sempre, com FUGIR 77% e FICAR 23% |
| O nome | “E deram um nome a ele: Renato.” | `../episodio-02/cena-08-retrato-amigo.png` | “E O NOME DELE” e o carimbo “RENATO” |
| O preço | Narrador | `cena-01-portao` e um relance de `cena-05-renato-grita`, escuro | “FUGIR TEM / UM PREÇO.” e “QUEM PAGA / É ELE.” |
| Os homens | Narrador | `cena-01-portao`, nos dois homens e na lanterna | “DOIS HOMENS. / UMA LANTERNA.” |
| A fuga | Narrador e Renato (“Pelos fundos. Vai!”, “Sobe. Eu vou atrás.”) | `cena-02-cozinha` e `cena-03-pe-no-muro`, com as mãos dele e o Zinho no alto do muro | “MAIS ALTO DO QUE / VOCÊ LEMBRAVA.” e “ELE TE DÁ PÉ.” |
| A queda | Narrador | Tela preta, com o baque | — |
| A mão | Narrador e Renato (“Corre! Corre!”) | `cena-04-mao-anel`, o anel de perto, o anel da foto da Parte 2 e `cena-05-renato-grita` | “UMA MÃO / POR TRÁS.”, “UM ANEL / DE OURO.” e o carimbo “O MESMO ANEL” |
| Sozinho | Narrador | `cena-06-zinho-corre` e `cena-07-onibus` | “CADA PASSO / PESA MAIS.”, “UM ÔNIBUS / ABANDONADO.” e “VOCÊ ESTÁ / SOZINHO.” |
| A foto | Narrador | `cena-08-celular` com a notificação do número do Renato, a conversa com a foto e `cena-09-foto-refem` | “MAS NÃO É ELE.”, “COM O LÁBIO / CORTADO.” e “A MÃO / COM O ANEL.” |
| O áudio | O cobrador, com voz grave e som de celular | A conversa com o áudio, `cena-10-zinho-escuta` e `cena-12-ferro-velho` com a placa “FERRO-VELHO SÃO JORGE” | “VAMOS TROCAR: / VOCÊ POR ELE.”, “3 DA MANHÃ. / SOZINHO.” e “A MÃE DELE / É A PRÓXIMA.” |
| Outra vez | Narrador e o começo do áudio repetido | `cena-10-zinho-escuta`, escura | “CALMA / DEMAIS.” |
| A mãe | Narrador | `cena-11-almoco` | “A MESMA QUE TE / DAVA ALMOÇO.” |
| A hora | Narrador | `cena-08-celular` com 01:12 na tela de bloqueio | “FALTAM MENOS / DE DUAS HORAS.” |
| O preço | Narrador | `cena-09-foto-refem`, escura, e as mãos do Renato no muro | “AGORA PAGA / POR ELE.” e “MAS ELE / TE DEU PÉ.” |
| Votação | “Trocar ou deixar? Comenta uma palavra só. O que a maioria escolher vira a parte quatro.” | `cena-13-decisao`, escurecida | “TROCAR / OU DEIXAR?”, os botões e a caixa “PARTE 4” |

Até a votação, o painel do topo mostra “A SUA PARTE R$ 0 · SUSPEITA ★★★★★”. Cada enquadramento deixa rostos, mãos, o celular e o anel fora do quarto de cima e da faixa de baixo. Os quadros de cada plano foram conferidos nas duas versões.

## Votação

- **TROCAR:** Zinho vai ao ferro-velho às três da manhã para se entregar no lugar de Renato. É o caminho do confronto: ele fica frente a frente com o homem do anel.
- **DEIXAR:** Zinho não vai. Ele corre para proteger a mãe de Renato, ameaçada no áudio. É o caminho da culpa e da pressa.

Vence a palavra com mais comentários, somando as três redes.

## Aliados e versões

As vagas da Parte 3 fecharam sem aliados, então não há @ no vídeo. Há duas versões:

- [`parte-03-o-preco.mp4`](parte-03-o-preco.mp4), para o Instagram;
- [`parte-03-o-preco-vertical.mp4`](parte-03-o-preco-vertical.mp4), para o TikTok e o Shorts.

A capa é [`../capas/capa-parte-03.png`](../capas/capa-parte-03.png): “O PREÇO / VOCÊ POR ELE?” sobre a foto do Renato preso.
