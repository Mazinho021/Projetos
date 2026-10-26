# Guia de estilo — vídeo de referência da série

O criador definiu como base da série o vídeo **“Design sem nome.mp4”** (exportado do Canva; 89,9 s, 720 × 1280, 30 fps), enviado na sessão de 25/10/2026. O arquivo não está versionado; este guia registra o que foi medido nele. A referência acompanha o parceiro que ficou com os dez milhões. O episódio 1 de Zinho mostra o outro lado do mesmo assalto e por isso abre com a mesma frase: “O assalto deu certo.”

## Estrutura narrativa

| Trecho | Referência | Episódio 1 de Zinho |
|---|---|---|
| Gancho (0–5 s) | “O ASSALTO / DEU CERTO.” e contador “A SUA PARTE R$ 10.000.000 EM DINHEIRO VIVO” | Mesma frase; o contador mostra o que ficou com o parceiro |
| Painel fixo | “DINHEIRO VIVO” e “SUSPEITA” com 5 estrelas que enchem ao longo do vídeo | “A SUA PARTE” (R$ ? → R$ 0 em vermelho) e “SUSPEITA” cheia já no “primeiro suspeito identificado” |
| Capítulos | Etiquetas amarelas “PROBLEMA 1 · O PESO”, “PROBLEMA 2 · O PAÍS DO PIX”, “PROBLEMA 3 · O BANCO” | “PISTA 1 · A MOCHILA”, “PISTA 2 · O SILÊNCIO”, “PISTA 3 · A FOTO”, “PISTA 4 · O ÁUDIO” |
| Desenvolvimento | Cartões de dados, listas com seta (“CONCESSIONÁRIA → COAF”), carimbos (“AUTOMÁTICO”, “MALHA FINA”) | Lista “BOLSOS → VAZIOS”, carimbo “A MESMA FOTO”, cartões de TV, celular e áudio |
| Virada | Tela escura com “TODO REAL / DEIXA RASTRO.” | “VENDEU / SEU NOME.” sobre o amigo |
| Final | “E AGORA?”, “COMENTA UMA PALAVRA”, botões “ARRISCAR / DESISTIR”, “PARTE 2 · a maioria decide o próximo passo” | “VOCÊ DEIXA / ELE ENTRAR?”, mesmo bloco com “ABRIR / NÃO ABRIR” |

A narração da referência fala em segunda pessoa, com cerca de 160 palavras por minuto, e não tem trilha de fundo: as pausas da voz ficam em silêncio.

## Texto na tela

- **Não há legenda corrida.** Só frases-chave grandes, centralizadas, que entram linha por linha no momento em que são faladas.
- Animação “pop”: cada linha cresce de cerca de 60–70 % até 100 % em 0,15–0,2 s, com um leve exagero antes de assentar.
- Primeira linha em branco, segunda (a revelação) em amarelo. Poppins Bold, ~78 px num quadro de 720 px de largura, centro do bloco em ~48 % da altura.
- Rótulos pequenos em maiúsculas espaçadas (“A SUA PARTE”, “EM DINHEIRO VIVO”), ~22 px.
- Valores em dinheiro em verde; perdas e alertas em vermelho.

## Paleta (amostrada da referência)

| Uso | Cor |
|---|---|
| Amarelo de destaque, etiquetas, estrelas, botão principal | `#FDB822` |
| Branco quente de texto e botão secundário | `#F6F0E2` |
| Verde de dinheiro | `#34C077` |
| Vermelho de texto de alerta (“→ COAF”, carimbos) | `#EB584C` |
| Vermelho de etiqueta (“SINALIZADO”) | `#B63424` |
| Rótulo cinza do painel | `#B1B3AE` |
| Painel escuro translúcido | preto quente com ~85 % de opacidade |
| Fundo dos infográficos | verde quase preto `#0B1913` com grade sutil |

## Layout

- Painel fixo de 42 a 678 px na largura e de 87 a 193 px na altura, cantos de 16 px; etiqueta de capítulo centralizada logo abaixo (y ≈ 230).
- Conteúdo principal entre ~300 px e ~980 px, fora das áreas cobertas pelo TikTok e pelos Reels (topo e faixa inferior com nome, texto do post e áudio).
- Cenas em cartoon 2D com aproximação lenta da câmera; cortes secos e, raramente, escurecimento rápido para tela preta.

## Onde está implementado

Os elementos ficam em [`episodio-01/montagem/graficos.py`](episodio-01/montagem/graficos.py) e são posicionados na timeline (`graphics`). A fonte Poppins está em [`fontes/`](fontes/) (licença OFL).
