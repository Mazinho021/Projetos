# Zinho — montagem do animatic

Esta ferramenta monta o episódio narrado: ilustrações com câmera suave, cartões de TV/celular e uma camada de gráficos animados no estilo do [vídeo de referência da série](../../guia-de-estilo-referencia.md) — frases que entram linha por linha, painel com a parte de Zinho e a suspeita, etiquetas, listas, carimbos e o pedido de comentário no final. Não sintetiza movimento corporal do personagem. O MP4 e os arquivos de trabalho são gerados a partir da timeline; a pasta `work/` é recriada a cada render e não é versionada.

Requisitos locais: Python com Pillow, FFmpeg com libass, FFprobe e a fonte Poppins em `crimecarton-analise/fontes/` (incluída no repositório). Não usa serviços externos nem geração paga.

O renderizador, a camada de gráficos e o alinhador desta pasta servem todas as partes. Cada parte tem a própria pasta `montagem/`, com o script que gera as timelines dela, como [`episodio-02/montagem/`](../../episodio-02/montagem/README.md). Os ativos de uma timeline são procurados na pasta do episódio dela, e os arquivos de trabalho e relatórios ficam ao lado dela.

## Alinhar a narração

`alinhar_narracao.py` mede o tempo de cada palavra do roteiro na voz gravada e grava `alinhamento-narracao.json`. O reconhecimento de fala (faster-whisper, modelo `medium`, executado localmente) fornece só os tempos; as palavras gravadas são sempre as do roteiro. As bordas das palavras vizinhas a uma pausa são ajustadas às pausas medidas pelo FFmpeg.

```bash
python -m venv .venv && .venv/bin/pip install faster-whisper
.venv/bin/python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py
```

Na primeira execução o modelo é baixado da Hugging Face. Use esse arquivo para posicionar cortes e gráficos; refaça o alinhamento se a narração for gerada de novo.

## Dar voz ao amigo

Na narração, o áudio que o amigo manda (“Eu estava devendo … no meu lugar.”) foi lido pela mesma voz grave do narrador, e a repetição soava como o narrador outra vez. `voz_amigo.py` recorta essa fala de `narracao-original.wav` e a passa para outra voz com a função “Change gender” do Praat: tom médio de 112 Hz, contra uns 85 Hz do narrador, e formantes 8% mais altos, como os de um trato vocal menor. Depois ela ganha o som de um alto-falante de celular. O resultado, `efeitos/audio-amigo.wav`, tem exatamente a duração da fala original. `montar_timeline.py` o põe no lugar da leitura do narrador, e `gerar_efeitos.py` recorta dele a repetição, sem mudar a sincronização.

```bash
.venv/bin/pip install praat-parselmouth
.venv/bin/python crimecarton-analise/episodio-01/montagem/voz_amigo.py
python crimecarton-analise/episodio-01/montagem/gerar_efeitos.py
```

Se a narração for gerada ou alinhada de novo, rode os dois antes de `montar_timeline.py`.

## Montar a timeline

`montar_timeline.py` gera `timeline.json` a partir dos alinhamentos da narração e do pedido de comentário. Os cortes, os gráficos e os efeitos estão presos aos números das palavras, então a edição acompanha a voz se a narração for alinhada de novo. O script também monta o áudio do episódio em `narracao-ep01-com-cta.wav`: põe o áudio do amigo na voz dele, abre uma pausa depois de “Você escuta outra vez.”, onde a frase principal do amigo toca de novo e Zinho reage, e junta no fim o pedido de comentário gravado à parte, igualando o volume. Tudo o que vem depois da pausa é deslocado automaticamente. O script ainda recusa frases mais largas que a área segura. Ajustes de edição podem ser feitos nele, rodando-o em seguida, ou direto no `timeline.json`.

O pedido de comentário foi alinhado com o mesmo script de alinhamento:

```bash
.venv/bin/python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py \
  --audio crimecarton-analise/episodio-01/narracao-cta-ep01.wav \
  --script crimecarton-analise/narracao-cta-ep01.txt \
  --output crimecarton-analise/episodio-01/montagem/alinhamento-cta.json
```

```bash
python crimecarton-analise/episodio-01/montagem/montar_timeline.py
```

## Executar

A partir da raiz do repositório:

```bash
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --timeline crimecarton-analise/episodio-01/montagem/timeline.json \
  --output crimecarton-analise/episodio-01/piloto-zinho-ep01-v8.mp4
```

Sem `--audio`, o script usa o áudio indicado em `audio` na timeline, ao lado do episódio. Sem `--timeline`, usa `narracao-original.wav` e um esboço escalado para a duração da voz, sem gráficos nem legendas, com estado `provisional_scaled_to_audio`. Esse modo permite testar o render, mas os cortes devem ser conferidos com a fala antes de apresentar um piloto sincronizado.

`--prepare-only` produz os fundos e cartões estáticos e o ASS, sem codificar vídeo. `--workers 2` limita o paralelismo.

### Versão do TikTok e do YouTube Shorts

Cada episódio sai em duas versões: `timeline.json` para o Instagram e `timeline-tiktok.json` para o TikTok e o YouTube Shorts, ambas geradas por `montar_timeline.py`. As margens publicadas para o Shorts são 12,5% em cima, 19,8% embaixo e 17,8% à direita, e a versão do TikTok já fica dentro delas. Nas versões verticais, os elementos devem ficar à esquerda de x = 590 px, por causa da coluna de botões. A do TikTok difere em dois pontos:

- **Abertura:** começa com 3,3 s de flash-forward. Zinho aparece assustado, com borda vermelha, enquanto toca a frase do amigo com voz de celular. O texto “SEU AMIGO / TE VENDEU.” já está na tela no primeiro quadro. No TikTok, a maioria dos espectadores da primeira versão saiu no primeiro segundo. O episódio vem em seguida, igual, e o áudio `narracao-ep01-com-cta-tiktok.wav` é a narração com esses 3,3 s de silêncio no início.
- **Topo:** a barra de busca do TikTok cobre os 11,4% de cima da tela. Por isso, o painel desce 67 px, as etiquetas passam para `y` 297, os cartões começam em 334 e o carimbo vai para 629.

```bash
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --timeline crimecarton-analise/episodio-01/montagem/timeline-tiktok.json \
  --output crimecarton-analise/episodio-01/piloto-zinho-ep01-v8-tiktok.mp4
```

Cada versão grava o próprio registro: `timeline-used.json` e `render-report.json` para a do Instagram, `timeline-tiktok-used.json` e `render-report-tiktok.json` para a do TikTok.

### Trechos para o TikTok

`montar_cortes.py` corta a versão do TikTok em três trechos de 26 a 29 s. Cada um vai até uma virada da história, e juntos eles cobrem o episódio inteiro, sem o pedido de comentário:

1. Do começo até “Nada.”.
2. Da ligação sem resposta até a foto no jornal.
3. Do áudio do amigo até “Você deixa ele entrar?”.

Cada trecho tem texto na tela desde o primeiro quadro e um impacto no início. No trecho 1 é a frase de abertura; nos outros, “QUEM VAZOU / A SUA FOTO?” e “O ÁUDIO QUE / ENTREGOU TUDO.”. O final é um cartão de 2,2 s com “PARTE 1 COMPLETA / NO PERFIL” sobre o último plano escurecido. O script grava `timeline-corte-N.json` e `narracao-ep01-corte-N.wav`. Ele lê `timeline-tiktok.json`, então deve rodar depois de `montar_timeline.py`.

```bash
python crimecarton-analise/episodio-01/montagem/montar_cortes.py
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --timeline crimecarton-analise/episodio-01/montagem/timeline-corte-1.json \
  --output crimecarton-analise/episodio-01/cortes-tiktok/corte-1-a-mochila.mp4
```

### Resultado da votação

`montar_resultado.py` monta um vídeo de 13,7 s para os stories que anuncia o resultado da votação, no estilo do episódio e com narração própria, na mesma voz: `narracao-resultado-ep01.wav`, gerada no Codex conforme [`pedido-codex-resultado.md`](../../pedido-codex-resultado.md) e alinhada em `alinhamento-resultado.json`. O texto é “A maioria decidiu: abrir. Na parte dois, a porta se abre, e o homem que vendeu seu nome vai ter que se explicar. Mas dá para acreditar nele?”.

As cenas acompanham as palavras: a porta com “A MAIORIA DECIDIU:” e “ABRIR”, o quarto inteiro com “A PORTA SE ABRE.”, o amigo na janela com “VENDEU SEU NOME.” e “VAI TER QUE SE EXPLICAR.”, e Zinho desconfiado, com borda vermelha, com a pergunta e a caixa “PARTE 2 · em breve”. O vídeo não mostra números de votos.

```bash
.venv/bin/python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py \
  --audio crimecarton-analise/episodio-01/narracao-resultado-ep01.wav \
  --script crimecarton-analise/narracao-resultado-ep01.txt \
  --output crimecarton-analise/episodio-01/montagem/alinhamento-resultado.json
python crimecarton-analise/episodio-01/montagem/montar_resultado.py
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --timeline crimecarton-analise/episodio-01/montagem/timeline-resultado.json \
  --output crimecarton-analise/episodio-01/resultado-votacao.mp4
```

## Timeline

Os tempos são segundos absolutos na locução. As cenas devem cobrir de zero até a duração do áudio somada a `tail`, sem espaços ou sobreposições. `tail` mantém o último plano em silêncio depois da voz.

```json
{
  "timing_status": "aligned_to_voice",
  "tail": 3.0,
  "scenes": [
    {"start": 0, "end": 4.88, "kind": "art", "asset": "cena-01-base.png", "zoom": 0.06},
    {"start": 4.88, "end": 8.3, "kind": "art", "asset": "cena-01-base.png", "crop": [0.25, 0.03, 0.85, 0.63]},
    {"start": 8.3, "end": 14.35, "kind": "tv", "asset": "cena-01-base.png"}
  ],
  "graphics": [
    {"type": "phrase", "start": 0.2, "end": 2.4, "y": 700, "size": 78, "lines": [
      {"text": "O ASSALTO", "at": 0.26},
      {"text": "DEU CERTO.", "at": 1.08, "color": "yellow"}]}
  ],
  "captions": []
}
```

Tipos de cena: `art`, `tv`, `chat`, `comparison`, `audio` e, a partir da Parte 2, `black` (a tela preta da abertura), `photo` (uma foto aberta num celular), `call` (uma ligação) e `notification` (uma mensagem que acende a tela, sobre a ilustração). Os cartões usam textos do roteiro. A comparação repete o mesmo retrato ficcional nos dois lugares. O waveform do cartão de áudio é ilustrativo, não uma medição da fala. Os textos de TV e telefone são aplicados por código para manter ortografia e legibilidade.

Campos opcionais das cenas:

- `crop`: enquadramento dentro da ilustração, em frações `[esquerda, topo, direita, base]`. Frações de largura e altura iguais preservam o formato 9:16.
- `zoom` e `direction` (`in` ou `out`): intensidade e sentido do movimento de câmera.
- `brightness`: escurece a ilustração (por exemplo, `0.5`) para destacar texto ou cartão.
- `status` (`chat`): `sent` mostra a foto como enviada; `seen`, o padrão, mostra “Visualizado” e “Nenhuma resposta.”.
- `card_top` (cartões): altura do topo do cartão, 300 por padrão; a versão do TikTok usa 334.
- `card_dx` e `card_scale` (cartões): deslocam o cartão na horizontal e o reduzem a partir do centro do topo, para as versões verticais o manterem longe da coluna de botões.
- `photo` e `photo_crop` (`photo`): a ilustração que aparece na tela do celular e o enquadramento dela.
- `status` e `number` (`call`): `calling`, `answered` (com o tempo em `clock`) ou `ended`, e o número exibido.
- `sender`, `message` e `when` (`notification`): remetente, texto e horário da mensagem.
- `paint`: textos aplicados sobre uma superfície em branco da ilustração, como um calendário na parede, e que acompanham a câmera. Cada item tem `text` (aceita `\n`), `box` em frações da ilustração inteira, e opcionalmente `color`, `weight`, `angle`, `opacity` e `blur`.
- `play` (`audio`): início e fim absolutos da fala do amigo. O marcador de progresso percorre a barra nesse intervalo e pode ser interrompido pelo corte.

### Gráficos

Cada item de `graphics` tem `type`, `start` e `end`; os subitens entram nos seus próprios `at`. Cores: `white`, `yellow`, `green`, `red`, `gray`.

- `phrase`: bloco centrado em `y`, com `lines` que entram com “pop” no `at` de cada uma. `size` vale para o bloco e pode ser trocado por linha. Linhas com `"style": "label"` são rótulos pequenos em maiúsculas espaçadas; `"shake": true` treme a linha ao entrar; `count` (`from`, `to`, `start`, `end`, `format`) faz a linha contar um valor em reais.
- `hud`: painel fixo do topo, com `label`, `values` (texto e cor a partir de cada `at`, com `shake` opcional) e `stars` (`count` estrelas de suspeita que enchem a partir de `at`, uma a cada `step` segundos). `dy` desce o painel inteiro, como na versão do TikTok.
- `tag`: etiqueta de capítulo abaixo do painel; `color` `yellow` ou `red`; `size` aumenta a etiqueta, como na “PARTE N” da abertura.
- `list`: itens empilhados a partir de `y`, cada um com `left`, `right` e `at`, ligados por uma seta.
- `stamp`: carimbo em `x`, `y`, inclinado em `angle` graus; com `"filled": true`, todo pintado na cor, como o da opção vencedora.
- `buttons`: `prompt` e botões (`text`, `at`, `style` `yellow` ou `white`) centrados em `y`.
- `box`: caixa com `title` e `sub`, como “PARTE 2”.
- `vignette`: bordas da tela tingidas com `color` (por padrão o vermelho de alerta), com intensidade `strength`, para momentos de choque, como na referência.
- `stars`: as cinco estrelas de suspeita em tamanho grande, na tela preta da abertura; enchem a partir de `at`, uma a cada `step` segundos.
- `pointer`: o @ do perfil numa pílula branca, com uma seta que desce em direção ao nome de usuário que os apps mostram embaixo do vídeo.
- `bars`: o resultado da votação anterior, com `title` e `items` (`label`, `pct`, `at`, `winner`); cada barra enche até a porcentagem real.
- `input`: a caixa de comentário vazia, com cursor piscando, de uma votação livre como a do nome do amigo; `placeholder` e `width`.

Todos os elementos centrados aceitam `x`; as versões verticais centram os da metade de baixo em x = 330.

### Efeitos sonoros

`sfx` lista os efeitos do episódio, cada um com `sound` (arquivo na pasta `efeitos/` ao lado da timeline ou, se não estiver lá, na desta pasta; `effects` na timeline acrescenta outras pastas), `at` (início em segundos) e `gain` (dB). Eles são somados por baixo da narração já normalizada, nas pausas da voz, como na referência: whoosh nas trocas de capítulo, tique enquanto o dinheiro conta, impactos nas perdas e no carimbo, toque de chamada, notificação, o trecho do áudio do amigo repetido e as batidas na porta. Um limitador só segura picos sobrepostos.

`gerar_efeitos.py` sintetiza `whoosh.wav`, `tique.wav`, `notificacao.wav` e `chamada.wav` e recorta `replay-amigo.wav` de `audio-amigo.wav`, a fala do amigo na voz dele, criada por `voz_amigo.py`. `batida-1.wav`, `batida-2.wav`, `impacto.wav`, `impacto-suave.wav` e `pop.wav` são gravações do pacote Impact Sounds de Kenney, em domínio público (CC0, ver `efeitos/LICENCA-kenney-impact-sounds.txt`).

`captions` continua disponível para legendas corridas em ASS, que ficam acima da área inferior em que o TikTok e os Reels sobrepõem legenda e nome de usuário. A referência não usa legenda corrida, então a timeline atual a deixa vazia. O vídeo não tem selo da série no topo, porque essa área fica coberta pelas duas interfaces; o nome da série e o episódio vão no texto do post.

Ativos esperados na pasta pai: `cena-01-base.png`, `cena-03-roupas.png`, `cena-07-audio.png`, `cena-09-porta.png`. Na ausência de um ativo, o script avisa e usa a primeira cena como fallback provisório. Opcionalmente, `retrato-zinho.png`, um retrato frontal em formato horizontal, substitui o recorte da cena 1 na TV e na comparação de fotos.

## Revisão antes de publicar

- Conferir duração real, cortes nas frases, final completo e textos legíveis em tela pequena.
- Verificar que a fotografia só é revelada no momento correto e que o cartão de áudio coincide com a fala do amigo.
- Conferir se todas as imagens finais foram entregues; nenhum fallback deve passar despercebido.
- O arquivo é uma prévia de montagem. A classificação para monetização não é garantida por este tipo de montagem.
