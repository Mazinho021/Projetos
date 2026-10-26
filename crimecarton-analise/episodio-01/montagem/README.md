# Zinho — montagem do animatic

Esta ferramenta monta o episódio narrado: ilustrações com câmera suave, cartões de TV/celular e uma camada de gráficos animados no estilo do [vídeo de referência da série](../../guia-de-estilo-referencia.md) — frases que entram linha por linha, painel com a parte de Zinho e a suspeita, etiquetas, listas, carimbos e o pedido de comentário no final. Não sintetiza movimento corporal do personagem. O MP4 e os arquivos de trabalho são gerados a partir da timeline; a pasta `work/` é recriada a cada render e não é versionada.

Requisitos locais: Python com Pillow, FFmpeg com libass, FFprobe e a fonte Poppins em `crimecarton-analise/fontes/` (incluída no repositório). Não usa serviços externos nem geração paga.

## Alinhar a narração

`alinhar_narracao.py` mede o tempo de cada palavra do roteiro na voz gravada e grava `alinhamento-narracao.json`. O reconhecimento de fala (faster-whisper, modelo `medium`, executado localmente) fornece só os tempos; as palavras gravadas são sempre as do roteiro. As bordas das palavras vizinhas a uma pausa são ajustadas às pausas medidas pelo FFmpeg.

```bash
python -m venv .venv && .venv/bin/pip install faster-whisper
.venv/bin/python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py
```

Na primeira execução o modelo é baixado da Hugging Face. Use esse arquivo para posicionar cortes e gráficos; refaça o alinhamento se a narração for gerada de novo.

## Montar a timeline

`montar_timeline.py` gera `timeline.json` a partir do alinhamento. Os cortes e os gráficos estão presos aos números das palavras do roteiro, então a edição acompanha a voz se a narração for alinhada de novo. O script também recusa frases mais largas que a área segura. Ajustes de edição podem ser feitos nele, rodando-o em seguida, ou direto no `timeline.json`.

```bash
python crimecarton-analise/episodio-01/montagem/montar_timeline.py
```

## Executar

A partir da raiz do repositório:

```bash
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --audio crimecarton-analise/episodio-01/narracao-original.wav \
  --timeline crimecarton-analise/episodio-01/montagem/timeline.json \
  --output crimecarton-analise/episodio-01/piloto-zinho-ep01-v2.mp4
```

Sem `--timeline`, o script usa um esboço escalado para a duração da voz, sem gráficos nem legendas, com estado `provisional_scaled_to_audio`. Esse modo permite testar o render, mas os cortes devem ser conferidos com a fala antes de apresentar um piloto sincronizado.

`--prepare-only` produz os fundos e cartões estáticos e o ASS, sem codificar vídeo. `--workers 2` limita o paralelismo.

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

Tipos de cena: `art`, `tv`, `chat`, `comparison`, `audio`. Os cartões usam textos do roteiro. A comparação repete o mesmo retrato ficcional nos dois lugares. O waveform do cartão de áudio é ilustrativo, não uma medição da fala. Os textos de TV e telefone são aplicados por código para manter ortografia e legibilidade.

Campos opcionais das cenas:

- `crop`: enquadramento dentro da ilustração, em frações `[esquerda, topo, direita, base]`. Frações de largura e altura iguais preservam o formato 9:16.
- `zoom` e `direction` (`in` ou `out`): intensidade e sentido do movimento de câmera.
- `brightness`: escurece a ilustração (por exemplo, `0.5`) para destacar texto ou cartão.
- `status` (`chat`): `sent` mostra a foto como enviada; `seen`, o padrão, mostra “Visualizado” e “Nenhuma resposta.”.
- `play` (`audio`): início e fim absolutos da fala do amigo. O marcador de progresso percorre a barra nesse intervalo e pode ser interrompido pelo corte.

### Gráficos

Cada item de `graphics` tem `type`, `start` e `end`; os subitens entram nos seus próprios `at`. Cores: `white`, `yellow`, `green`, `red`, `gray`.

- `phrase`: bloco centrado em `y`, com `lines` que entram com “pop” no `at` de cada uma. `size` vale para o bloco e pode ser trocado por linha. Linhas com `"style": "label"` são rótulos pequenos em maiúsculas espaçadas; `"shake": true` treme a linha ao entrar; `count` (`from`, `to`, `start`, `end`, `format`) faz a linha contar um valor em reais.
- `hud`: painel fixo do topo, com `label`, `values` (texto e cor a partir de cada `at`, com `shake` opcional) e `stars` (`count` estrelas de suspeita que enchem a partir de `at`, uma a cada `step` segundos).
- `tag`: etiqueta de capítulo abaixo do painel; `color` `yellow` ou `red`.
- `list`: itens empilhados a partir de `y`, cada um com `left`, `right` e `at`, ligados por uma seta.
- `stamp`: carimbo em `x`, `y`, inclinado em `angle` graus.
- `buttons`: `prompt` e botões (`text`, `at`, `style` `yellow` ou `white`) centrados em `y`.
- `box`: caixa com `title` e `sub`, como “PARTE 2”.

`captions` continua disponível para legendas corridas em ASS, que ficam acima da área inferior em que o TikTok e os Reels sobrepõem legenda e nome de usuário. A referência não usa legenda corrida, então a timeline atual a deixa vazia. O vídeo não tem selo da série no topo, porque essa área fica coberta pelas duas interfaces; o nome da série e o episódio vão no texto do post.

Ativos esperados na pasta pai: `cena-01-base.png`, `cena-03-roupas.png`, `cena-07-audio.png`, `cena-09-porta.png`. Na ausência de um ativo, o script avisa e usa a primeira cena como fallback provisório. Opcionalmente, `retrato-zinho.png`, um retrato frontal em formato horizontal, substitui o recorte da cena 1 na TV e na comparação de fotos.

## Revisão antes de publicar

- Conferir duração real, cortes nas frases, final completo e textos legíveis em tela pequena.
- Verificar que a fotografia só é revelada no momento correto e que o cartão de áudio coincide com a fala do amigo.
- Conferir se todas as imagens finais foram entregues; nenhum fallback deve passar despercebido.
- O arquivo é uma prévia de montagem. A classificação para monetização não é garantida por este tipo de montagem.
