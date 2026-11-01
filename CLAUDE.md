# Memória do projeto — A parte que faltou (Zinho)

Regras combinadas com o criador. Valem para toda sessão nova. O estado detalhado do projeto está em [`NOTAS.md`](NOTAS.md), o arco da série em [`crimecarton-analise/producao-zinho.md`](crimecarton-analise/producao-zinho.md) e o estilo em [`crimecarton-analise/guia-de-estilo-referencia.md`](crimecarton-analise/guia-de-estilo-referencia.md).

## Conversa

- Responder sempre em português do Brasil, em tom simples e direto. O criador escreve por voz, então “usina” e “usinho” querem dizer Zinho.
- Commits em português, com as linhas de atribuição pedidas no sistema.
- Push com `git push -u origin claude/ecstatic-brown-xb2qxd`, sempre depois de `git pull --rebase`.

## Composição das imagens (erro que o criador apontou em 31/10/2026)

O painel “A SUA PARTE · SUSPEITA” cobre o topo de todo episódio, e a etiqueta da parte fica logo abaixo dele:

- **Instagram:** num quadro de 1280 px de altura, o painel vai de y = 87 a 193, e a etiqueta fica em y ≈ 230.
- **Versão vertical:** os dois descem 67 px.

Na Parte 3, rostos e cabeças ficaram escondidos atrás do painel. Por isso:

- **Nos pedidos de imagem ao Codex:**
  - os **25% de cima** ficam só com fundo calmo (céu, teto, parede, escuro), sem rosto, mão, celular ou objeto importante;
  - **rostos e a ação principal ficam entre 30% e 60% da altura**, no meio da largura;
  - os 20% de baixo ficam com chão ou fundo, porque ali entram as legendas e os botões dos apps.
- **Resolução:** imagens verticais 9:16 com **1080 × 1920 ou mais**.
  - O gerador do Codex entrega no máximo 941 × 1672, mesmo quando o pedido diz outra coisa. Isso aconteceu duas vezes na Parte 3.
  - Por isso, os desenhos são ampliados para 1440 × 2560 com `episodio-03/montagem/ampliar_cenas.py` (Real-ESRGAN anime). Os originais ficam em `originais/`.
- **Na montagem:** os recortes (`crop`) e os zooms também seguem a regra. Um recorte da metade de baixo de uma imagem sobe o conteúdo dela, então é preciso conferir.
- **Antes de entregar:** tirar um quadro de cada plano **nas duas versões** e conferir que nenhum rosto, mão, celular, anel ou frase fica atrás do painel, da etiqueta ou da coluna de botões (à direita de x = 590 na vertical).
- **Frases na tela:** ficam entre 65% e 80% da altura (y ≈ 830–1020 de 1280), longe dos rostos.
- **Abertura:** a etiqueta “PARTE N” fica no canto esquerdo (x = 112). No centro, ela cobria a cabeça do Zinho na arte da mochila.
- **Personagem na borda direita do desenho:** na vertical, ele fica atrás dos botões do TikTok. Nesse caso, mostrar o desenho num cartão menor, deslocado para a esquerda, como a lembrança do almoço na Parte 3 (`compor_cenas.py`).

## Cenas (pedido do criador em 31/10/2026, vale para todas as partes)

- **Cada coisa que a narração conta tem uma imagem própria.** Não repetir a mesma imagem só com zoom ou recorte em planos seguidos: o criador achou a Parte 3 repetitiva assim.
- **Variar os planos:** plano aberto, close, detalhe, outro ângulo e outro lugar.
- **Movimento de câmera:** dentro de cada plano, só um zoom leve.
- **Exceções:** a abertura padrão e imagens de partes anteriores usadas uma vez como lembrança, como a foto da divisão.
- **No pedido ao Codex:**
  - listar uma imagem por trecho do roteiro;
  - deixar nada importante na borda direita, entre 45% e 80% da altura, onde ficam os botões do TikTok;
  - descrever o corpo inteiro dos personagens e como ele se relaciona com o cenário. Na Parte 3, o corpo do Renato saiu cortado pelo muro.
- **Antes de entregar:** conferir também se o desenho tem corpo cortado ou fundido ao cenário.

## Abertura (decisão do criador em 01/11/2026, vale da Parte 4 em diante)

- **Os 2 primeiros segundos mostram o momento mais forte da própria parte**, com imagem e frase na tela, antes de qualquer resumo. O roteiro já começa por essa frase.
  - Na Parte 3, 39,5% passaram o vídeo no começo; na Parte 1, foram 26%.
  - Mais de 90% do público não seguia o perfil: quem via “PARTE 3” e o resumo da mochila achava que tinha perdido o começo.
  - A história nova só começava aos 17 s.
- **Depois vem o resumo, com no máximo 6 a 8 s:** o que aconteceu antes, o aviso de que as outras partes estão no perfil e o resultado da votação. A vinheta de 12 s da Parte 1 não cabe inteira nesse tempo.
- **O tamanho total das partes continua o mesmo.** O criador não quer encurtar.

## Roteiros (o criador recusou dois roteiros da Parte 3 em 30 e 31/10/2026)

- Cada parte precisa de pelo menos uma **reviravolta de verdade** e terminar numa **escolha difícil**, com consequência para a parte seguinte. Tem que ser uma escolha moral ou de risco, não só “para onde ir”.
- Evitar episódio de “correria”, que passa de lugar em lugar sem a história andar.
- O Zinho precisa agir e decidir; ele não pode só seguir os outros.
- Usar as pistas já plantadas (o anel de ouro, o Ferro-Velho São Jorge, a mãe do Renato, a “Cobrança”) para a história avançar.
- **Mostrar o roteiro ao criador e esperar o “ok” antes de pedir as gerações pagas ao Codex.** Imagens e vozes custam créditos, e um roteiro recusado depois de gerado é crédito perdido.

## Vozes

- O narrador, a vinheta e o cobrador usam a voz Charon, gerada no OpusClip pelo Codex.
- **Renato** tem voz própria, de homem adulto e natural, desde a Parte 3. Até ali, ele era a voz do narrador transformada por `voz_amigo.py`, e o criador achou essa voz feia (31/10/2026).
  - O Codex gera as falas dele com outra voz do TTS, sem transformação.
  - **A voz do Renato é a Algenib**, escolhida pelo criador em 31/10/2026 entre três testes (Orus, Achird e Algenib). É a mais grave das três, um pouco rouca. Vale para todas as próximas partes.
  - O pedido de voz do Renato ao Codex usa `"voice": "Algenib"` e o estilo de [`episodio-03/pedido-narracao-renato-ep03-algenib.json`](crimecarton-analise/episodio-03/pedido-narracao-renato-ep03-algenib.json).
- **A vinheta** é igualada ao narrador de cada parte por `igualar_vozes.py`.
- **Conferir cada gravação com o faster-whisper `medium` sem dar o texto como dica.** O TTS troca palavras: na Parte 3, “depois eu mudei de lado” saiu como “mandei de lado”. Se uma palavra sair errada, cortar a frase ou gerar a fala de novo.

## Codex

- Pedidos em `.md` com os parâmetros em `.json`. Mostrar o custo antes de executar.
- **O commit e o push têm que ser feitos na mesma conversa do Codex que gerou os arquivos.** Uma conversa nova não enxerga os arquivos da outra, como aconteceu em 30/10/2026.
- Depois, `git fetch origin codex/crimecarton` e `git merge --ff-only origin/codex/crimecarton`.
