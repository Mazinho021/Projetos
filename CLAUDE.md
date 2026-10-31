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

## Roteiros (o criador recusou dois roteiros da Parte 3 em 30 e 31/10/2026)

- Cada parte precisa de pelo menos uma **reviravolta de verdade** e terminar numa **escolha difícil**, com consequência para a parte seguinte. Tem que ser uma escolha moral ou de risco, não só “para onde ir”.
- Evitar episódio de “correria”, que passa de lugar em lugar sem a história andar.
- O Zinho precisa agir e decidir; ele não pode só seguir os outros.
- Usar as pistas já plantadas (o anel de ouro, o Ferro-Velho São Jorge, a mãe do Renato, a “Cobrança”) para a história avançar.
- **Mostrar o roteiro ao criador e esperar o “ok” antes de pedir as gerações pagas ao Codex.** Imagens e vozes custam créditos, e um roteiro recusado depois de gerado é crédito perdido.

## Vozes

- Todas as vozes são geradas com a voz Charon, no OpusClip, pelo Codex.
- **Renato** passa pela transformação de `voz_amigo.py`, com tom médio de cerca de 112 Hz.
- **A vinheta** é igualada ao narrador de cada parte por `igualar_vozes.py`.
- **Conferir cada gravação com o faster-whisper `medium` sem dar o texto como dica.** O TTS troca palavras: na Parte 3, “depois eu mudei de lado” saiu como “mandei de lado”. Se uma palavra sair errada, cortar a frase ou gerar a fala de novo.

## Codex

- Pedidos em `.md` com os parâmetros em `.json`. Mostrar o custo antes de executar.
- **O commit e o push têm que ser feitos na mesma conversa do Codex que gerou os arquivos.** Uma conversa nova não enxerga os arquivos da outra, como aconteceu em 30/10/2026.
- Depois, `git fetch origin codex/crimecarton` e `git merge --ff-only origin/codex/crimecarton`.
