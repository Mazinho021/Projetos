# Parte 3 — O preço

Roteiro em [`roteiro-ep03.txt`](roteiro-ep03.txt), com a voz de cada fala. Na Parte 2, o público escolheu FUGIR, com 10 votos contra 3 (77% e 23%), e deu ao amigo o nome **Renato**.

Este é o terceiro roteiro da Parte 3, de 31/10/2026. O criador recusou os dois primeiros, “A noite”, que seguiam uma fuga pelo bairro, um bar e uma avenida. Ele pediu outro caminho para a história e imagens novas, de mais qualidade. As imagens e as vozes estão pedidas ao Codex em [`pedido-codex-ep03.md`](pedido-codex-ep03.md), com a regra de composição que evita rostos atrás do painel do topo (ver [`../../CLAUDE.md`](../../CLAUDE.md)).

O vídeo tem **2 min 13 s**:
- a vinheta da Parte 1, com 12 s;
- 101 s do narrador, com 254 palavras mais as 16 do pedido do fim;
- 7,2 s do Renato, na voz Algenib;
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

## Mudanças pedidas pelo criador em 31/10/2026

O criador viu a primeira montagem de “O preço” e pediu três mudanças. Elas viraram regra para todas as partes, no [`CLAUDE.md`](../../CLAUDE.md):

1. **A cena 4:** o corpo do Renato saiu cortado pelo muro. O Codex refez a cena, com o Renato inteiro pendurado no muro.
2. **A voz do Renato:** a voz do narrador transformada ficou feia. O Codex gravou as falas em três vozes de teste, e o criador escolheu a **Algenib**, a mais grave.
3. **Uma imagem para cada coisa que a narração conta:** na primeira montagem, 13 desenhos se repetiam com zoom em 37 planos. A nova usa **35 desenhos diferentes em 41 planos**, cada um uma vez só.

O pedido ao Codex está em [`pedido-codex-ep03-cenas-novas.md`](pedido-codex-ep03-cenas-novas.md). Os desenhos chegaram com 941 × 1672 e foram ampliados para 1440 × 2560 por [`montagem/ampliar_cenas.py`](montagem/ampliar_cenas.py). Os originais estão em [`originais/`](originais/).

## Estrutura

| Trecho | Voz | Imagens, em ordem | Na tela |
|---|---|---|---|
| Abertura | Vinheta da Parte 1, aviso e votação | `../episodio-01/cena-01-base.png`, as capas das Partes 1 e 2 lado a lado e fundo escuro | O bloco de sempre, com FUGIR 77% e FICAR 23% |
| O nome | “E deram um nome a ele: Renato.” | `../episodio-02/cena-08-retrato-amigo.png` | “E O NOME DELE” e o carimbo “RENATO” |
| O preço | Narrador | 14, a mochila; 15, a mão no escuro | “FUGIR TEM / UM PREÇO.” e “QUEM PAGA / É ELE.” |
| Os homens | Narrador | 1, o portão | “DOIS HOMENS. / UMA LANTERNA.” |
| Pelos fundos | Renato | 16, Renato puxa o Zinho | “PELOS FUNDOS. / VAI!” |
| O muro | Narrador e Renato | 2, a cozinha; 17, o muro alto; 3, o pé no muro; 18, “Sobe” | “MAIS ALTO DO QUE / VOCÊ LEMBRAVA.”, “ELE TE DÁ PÉ.” e “SOBE. / EU VOU ATRÁS.” |
| O outro lado | Narrador | 19, o beco | — |
| A mão | Narrador e Renato | 4, a mão no muro; 20, o anel na gola; a foto da divisão da Parte 2; 5, Renato grita | “UMA MÃO / POR TRÁS.”, “UM ANEL / DE OURO.”, o carimbo “O MESMO ANEL” e “CORRE, ZINHO! / CORRE!” |
| Sozinho | Narrador | 6, a corrida; 21, sem fôlego; 22, o ônibus de fora; 7, dentro dele; 23, o celular e a chave; 24, o corredor | “CADA PASSO / PESA MAIS.”, “ATÉ O AR / ACABAR.”, “UM ÔNIBUS / ABANDONADO.”, “UMA CASA / SEM VOLTA.” e “VOCÊ ESTÁ / SOZINHO.” |
| A foto | Narrador | 8, a notificação às 01:04; 25, a conversa com a foto; 9, a foto; 26, a sucata; 27, a mão no ombro | “É O NÚMERO / DO RENATO.”, “MAS NÃO É ELE.”, “COM O LÁBIO / CORTADO.”, “MONTES DE / SUCATA.” e “A MÃO / COM O ANEL.” |
| O áudio | Narrador e o cobrador, com voz grave e som de celular | 28, a conversa com o áudio; 10, o Zinho escuta; 29, o cobrador grava; 12, o ferro-velho com a placa; 30, a casa da mãe | “DEPOIS, / UM ÁUDIO.”, “VOCÊ CORREU. / ELE NÃO.”, “VAMOS TROCAR: / VOCÊ POR ELE.”, “3 DA MANHÃ. / SOZINHO.” e “A MÃE DELE / É A PRÓXIMA.” |
| Outra vez | Narrador e o começo do áudio repetido | 31, os olhos do Zinho; 35, o cobrador tranquilo | “CALMA / DEMAIS.” |
| A mãe | Narrador | 11, o almoço, num cartão de foto | “A MESMA QUE TE / DAVA ALMOÇO.” |
| A hora | Narrador | 32, o relógio em 01:12 | “FALTAM MENOS / DE DUAS HORAS.” |
| O preço | Narrador | 33, Renato sozinho no ferro-velho; 34, a lembrança das mãos dele | “AGORA PAGA / POR ELE.” e “MAS ELE / TE DEU PÉ.” |
| Votação | “Trocar ou deixar? Comenta uma palavra só. O que a maioria escolher vira a parte quatro.” | 13, a porta do ônibus, escurecida | “TROCAR / OU DEIXAR?”, os botões e a caixa “PARTE 4” |

Até a votação, o painel do topo mostra “A SUA PARTE R$ 0 · SUSPEITA ★★★★★”. Os quadros de cada plano foram conferidos nas duas versões: nenhum rosto, mão, celular ou anel fica atrás do painel, da etiqueta ou dos botões do TikTok.

## Votação

- **TROCAR:** Zinho vai ao ferro-velho às três da manhã para se entregar no lugar de Renato. É o caminho do confronto: ele fica frente a frente com o homem do anel.
- **DEIXAR:** Zinho não vai. Ele corre para proteger a mãe de Renato, ameaçada no áudio. É o caminho da culpa e da pressa.

Vence a palavra com mais comentários, somando as três redes.

## Aliados e versões

As vagas da Parte 3 fecharam sem aliados, então não há @ no vídeo. Há duas versões:

- [`parte-03-o-preco.mp4`](parte-03-o-preco.mp4), para o Instagram;
- [`parte-03-o-preco-vertical.mp4`](parte-03-o-preco-vertical.mp4), para o TikTok e o Shorts.

A capa é [`../capas/capa-parte-03.png`](../capas/capa-parte-03.png): “O PREÇO / VOCÊ POR ELE?” sobre a foto do Renato preso.
