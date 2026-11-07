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
- **Telas de celular com dedos por cima** (erro que o criador apontou em 06/11/2026): na Parte 4, os dedões da cena 3 saíram pixelados, porque a máscara antiga comia o contorno preto dos dedos e cortava a borda em degraus.
  - Encaixar a tela nova com `encaixar_limpo` (`episodio-04/montagem/compor_cenas.py`), que mantém o contorno e a borda suave de quem está na frente;
  - antes de entregar, conferir os dedos de perto, em tamanho grande.
- **Frases na tela:** ficam entre 65% e 80% da altura (y ≈ 830–1020 de 1280), longe dos rostos.
- **Abertura:** a etiqueta “PARTE N” fica no canto esquerdo (x = 112). No centro, ela cobria a cabeça do Zinho na arte da mochila.
- **Personagem na borda direita do desenho:** na vertical, ele fica atrás dos botões do TikTok. Nesse caso, mostrar o desenho num cartão menor, deslocado para a esquerda, como a lembrança do almoço na Parte 3 (`compor_cenas.py`).

## Cenas (pedido do criador em 31/10/2026, vale para todas as partes)

- **Cada coisa que a narração conta muda a tela**, com uma imagem nova ou com um elemento novo por cima dela: balão, etiqueta, círculo, carimbo ou zoom de investigação. Ver a seção “Ideias do @crimecarton adaptadas à nossa história”.
- **Nunca repetir a mesma imagem só com zoom ou recorte** em planos seguidos: o criador achou a primeira montagem da Parte 3 repetitiva assim.
- **Trocar de imagem** quando muda o lugar, o momento ou o enquadramento.
- **Variar os planos:** plano aberto, close, detalhe, outro ângulo e outro lugar.
- **Movimento de câmera:** dentro de cada plano, só um zoom leve.
- **Exceções:** a abertura padrão e imagens de partes anteriores usadas uma vez como lembrança, como a foto da divisão.
- **No pedido ao Codex:**
  - listar uma imagem por trecho do roteiro;
  - deixar nada importante na borda direita, entre 45% e 80% da altura, onde ficam os botões do TikTok;
  - descrever o corpo inteiro dos personagens e como ele se relaciona com o cenário. Na Parte 3, o corpo do Renato saiu cortado pelo muro.
- **Antes de entregar:** conferir também se o desenho tem corpo cortado ou fundido ao cenário.

## Ideias do @crimecarton adaptadas à nossa história (decisão do criador em 01/11/2026)

O criador mandou a Parte 17 do @crimecarton para ver como ele monta as histórias. A ideia não é copiar o vídeo dele: é **trazer o que faz sentido na nossa história, do nosso jeito**. A análise está em [`crimecarton-analise/analise-crimecarton-parte-17.md`](crimecarton-analise/analise-crimecarton-parte-17.md). Os elementos estão em `episodio-01/montagem/graficos.py`, e um teste com os nossos desenhos está em [`crimecarton-analise/estilo/demo-elementos-novos.mp4`](crimecarton-analise/estilo/demo-elementos-novos.mp4).

- **A tela muda a cada 1 ou 2 s.** As imagens podem ficar mais tempo, desde que entre algo novo por cima a cada fala.
- **Comentários do público, num formato nosso: o recorte de jornal “A VOZ DO BAIRRO”** (`jornal`).
  - Entra logo depois do resultado da votação, com 2 ou 3 comentários reais da parte anterior, impressos como cartas de leitor e assinados só “— leitor”.
  - O jornal é onde o rosto do Zinho saiu, então o bairro opinando no jornal combina com a série.
  - Não usar os balões de comentário do @crimecarton, para não ficar igual.
- **Balões de fala:** a fala de cada personagem aparece num balão perto da cabeça de quem fala (`balloon`), além da voz. O vídeo tem que se entender sem som.
- **Pistas:**
  - etiqueta com linha (`callout`) e círculo (`ring`) apontando para o detalhe;
  - para chegar perto da pista, **um zoom normal**, com um recorte mais fechado.
  - **Nada de moldura de câmera nem “ZOOM 220%”**: o criador achou que não fazia sentido, porque não é uma gravação. Ela só caberia se a imagem fosse mesmo uma gravação ou uma foto vista numa tela.
- **Painel que muda com a história:** as estrelas de suspeita sobem e descem, valores mudam, e etiquetas como “SUSPEITA SUBIU” aparecem quando algo muda.
- **Etiqueta de nome** na primeira aparição de cada personagem (`nametag`), com o nome e quem é.
- **Polaroide de lembrança** de partes anteriores (`polaroid`), como “PARTE 2 · a foto da divisão”.
- **Carimbos e onomatopeias** (`stamp`, `pop`) nos momentos fortes, como “TOC TOC”.
- **Votação ilustrada:** cada opção com a sua cena, o nome em etiqueta (“OPÇÃO 1 · TROCAR”) e prós e contras em verde e vermelho. Depois vêm os botões e a caixa da próxima parte.
- **Um momento leve por parte**, antes da virada, para a tensão pesar mais.
- **Vozes:** o @crimecarton usa uma voz só, e nós mantemos as vozes próprias dos personagens, como o Renato na Algenib, com os balões por cima.

## Abertura (decisões do criador em 01/11 e 06/11/2026, valem da Parte 4 em diante)

- **Primeiro vem a vinheta, o “nosso início de sempre”, igual à do vídeo da Parte 3 (decisão do criador em 06/11/2026):**
  - as três frases fixas na voz da Parte 1: “O assalto deu certo. Seu parceiro ficou com dez milhões. Você ficou com o rosto no jornal.”;
  - nas duas primeiras, a arte da mochila, com “O ASSALTO / DEU CERTO.” e o contador de R$ 10.000.000;
  - na terceira, a tela preta com “VOCÊ FICOU COM / O ROSTO / NO JORNAL.” e as cinco estrelas de suspeita embaixo, que se acendem em “rosto”;
  - são uns 8 s, com a frase na tela desde o primeiro quadro. Os elementos, os tempos e os efeitos são os de `abertura()` da Parte 3, e só muda o número da etiqueta;
  - a voz é igualada ao narrador da parte por `igualar_vozes.py`;
  - a primeira montagem da Parte 4 saiu sem ela, e o criador sentiu falta. Ele pediu que ela viesse antes de tudo e, depois, mandou o vídeo da Parte 3 para ela ficar igual. O roteiro começa por ela.
- **Logo depois, o momento mais forte da própria parte**, com imagem e frase na tela, antes de qualquer resumo (decisão de 01/11/2026).
  - A regra de 01/11 punha esse momento nos 2 primeiros segundos. Na Parte 3, 39,5% passaram o vídeo no começo; na Parte 1, foram 26%. Mais de 90% do público não seguia o perfil, e quem via “PARTE 3” e o resumo da mochila achava que tinha perdido o começo. A história nova só começava aos 17 s.
  - Em 06/11, o criador decidiu que a vinheta vem antes desse momento. Na Parte 4, ele entra aos 8 s, e a história nova começa aos 24 s.
- **Depois vem o resumo, com no máximo 6 a 8 s:** o aviso de que as outras partes estão no perfil, o que aconteceu na parte anterior e o resultado da votação.
- **O tamanho total das partes continua o mesmo.** O criador não quer encurtar.

## Roteiros (o criador recusou dois roteiros da Parte 3 em 30 e 31/10/2026)

- Cada parte precisa de pelo menos uma **reviravolta de verdade** e terminar numa **escolha difícil**, com consequência para a parte seguinte. Tem que ser uma escolha moral ou de risco, não só “para onde ir”.
- Evitar episódio de “correria”, que passa de lugar em lugar sem a história andar.
- O Zinho precisa agir e decidir; ele não pode só seguir os outros.
- Usar as pistas já plantadas (o anel de ouro, o Ferro-Velho São Jorge, a mãe do Renato, a “Cobrança”) para a história avançar.
- **Mostrar o roteiro ao criador e esperar o “ok” antes de pedir as gerações pagas ao Codex.** Imagens e vozes custam créditos, e um roteiro recusado depois de gerado é crédito perdido.

## Site da série (lembrete do criador em 07/11/2026)

- **A cada parte publicada, atualizar o site** (`crimecarton-analise/site/`, no ar em golpecartoon.netlify.app): a capa nova em “Assista do começo”, com o carimbo da votação, o resultado na seção de votação, o fim da parte no topo e o quadro “O caso até aqui”. Em 07/11/2026, o site estava parado na Parte 3.
- **As vagas de aliado estão fechadas** desde 07/11/2026, por decisão do criador. Só abrir quando ele pedir, com o prazo que ele escolher. O passo a passo está em `crimecarton-analise/ideia-site-da-serie.md`.
- Publicar com a ferramenta de deploy do Netlify e conferir no ar a página, o `/api/aliados` e os testes (`node --test crimecarton-analise/site/testes/*.test.mjs`).

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
- **Pedir commit e push logo depois de cada cena pronta.**
  - Em 02/11/2026, a conversa da Parte 4 travou no limite diário antes de fazer push, e nada foi entregue.
  - Em 05/11/2026, o close do Ademir (cena 16) ficou pronto, mas o limite de 5 horas parou a conversa antes do push, que só viria na cena 20.
- **Para gastar menos limite (combinado com o criador em 07/11/2026, vale da Parte 6 em diante):**
  - **tudo numa conversa só**, como até a Parte 5: as vozes e os três lotes de desenhos, em sequência, na mesma aba, com push depois de cada cena;
  - o criador deixa o Codex no **esforço médio**, e não no máximo. As tarefas dele são de seguir o pedido, e o raciocínio já vai pronto nos arquivos;
  - o Codex lê só o `AGENTS.md`, o pedido e o lote, e não o `CLAUDE.md` e o `NOTAS.md` inteiros.
- **Se o limite ainda acabar rápido demais, o plano B é dividir em quatro conversas**, uma para as vozes e uma para cada lote, que podem rodar ao mesmo tempo, em abas separadas:
  - cada conversa faz push numa branch própria, como `codex/ep06-vozes` e `codex/ep06-lote-01`, para uma não recusar nem apagar o push da outra. O Claude junta as branches na dele;
  - os lotes são agrupados por lugar, como todas as cenas do carro num lote só, para cada cenário sair igual sem depender dos desenhos de outro lote;
  - as quatro dividem o mesmo limite de 5 horas e da semana. Se ele acabar, todas param juntas, mas o que já teve push fica salvo.
- **As instruções para o Codex ficam no [`AGENTS.md`](AGENTS.md)**, que ele lê sozinho. Elas mandam ler este arquivo e o `NOTAS.md` antes de cada tarefa.
- **Não propor que o criador gere imagens ou vozes à mão no celular.** Em 03/11/2026, ele achou complicado demais gerar, salvar e mandar tudo, e disse que ocupa muito espaço. Para esse material, o caminho é o Codex, que salva direto no GitHub, ou uma chave de API guardada no ambiente, se o criador quiser.
- **Se o agente não conseguir baixar os áudios do OpusClip,** ele grava os links temporários em `links-temporarios.json`, na pasta da parte, na `codex/crimecarton`. O Claude baixa, confere e salva os WAV antes de os links expirarem, e apaga o arquivo de links. Foi assim com as vozes da Parte 4, em 03/11/2026.
- Depois, `git fetch origin codex/crimecarton` e `git merge --ff-only origin/codex/crimecarton`.
