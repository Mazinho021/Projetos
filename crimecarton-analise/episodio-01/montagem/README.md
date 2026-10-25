# Zinho — montagem do animatic

Esta ferramenta monta uma prova de ritmo narrada: ilustrações, câmera suave, cartões de TV/celular e legendas. Não sintetiza movimento corporal do personagem. O MP4 e os arquivos de trabalho são gerados a partir da timeline; a pasta `work/` é recriada a cada render e não é versionada.

Requisitos locais: Python com Pillow, FFmpeg com libass, FFprobe. Não usa serviços externos nem geração paga.

## Alinhar a narração

`alinhar_narracao.py` mede o tempo de cada palavra do roteiro na voz gravada e grava `alinhamento-narracao.json`. O reconhecimento de fala (faster-whisper, modelo `medium`, executado localmente) fornece só os tempos; as palavras gravadas são sempre as do roteiro. As bordas das palavras vizinhas a uma pausa são ajustadas às pausas medidas pelo FFmpeg.

```bash
python -m venv .venv && .venv/bin/pip install faster-whisper
.venv/bin/python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py
```

Na primeira execução o modelo é baixado da Hugging Face. Use esse arquivo para posicionar cortes e legendas; refaça o alinhamento se a narração for gerada de novo.

## Executar

A partir da raiz do repositório:

```bash
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --audio crimecarton-analise/episodio-01/narracao-original.wav \
  --timeline crimecarton-analise/episodio-01/montagem/timeline.json \
  --output crimecarton-analise/episodio-01/piloto-zinho-ep01-v1.mp4
```

Sem `--timeline`, o script usa um esboço escalado para a duração da voz, **sem legendas**, com estado `provisional_scaled_to_audio`. Esse modo permite testar o render, mas os cortes devem ser conferidos com a fala antes de apresentar um piloto sincronizado.

`--prepare-only` produz os cartões estáticos e o ASS, sem codificar vídeo. `--workers 2` limita o paralelismo.

## Timeline

Os tempos são segundos absolutos na locução. As cenas devem cobrir de zero até a duração do áudio somada a `tail`, sem espaços ou sobreposições. `tail` mantém o último plano em silêncio depois da voz.

```json
{
  "timing_status": "aligned_to_voice",
  "tail": 1.2,
  "scenes": [
    {"start": 0, "end": 4.88, "kind": "art", "asset": "cena-01-base.png", "zoom": 0.06},
    {"start": 4.88, "end": 8.3, "kind": "art", "asset": "cena-01-base.png", "crop": [0.25, 0.03, 0.85, 0.63]},
    {"start": 8.3, "end": 14.35, "kind": "tv", "asset": "cena-01-base.png"}
  ],
  "captions": [
    {"start": 0.21, "end": 2.42, "text": "O assalto deu certo."},
    {"start": 38.57, "end": 40.07, "text": "“Eu garanto a sua parte”.", "voice": "amigo"}
  ]
}
```

Tipos de cena: `art`, `tv`, `chat`, `comparison`, `audio`. Os cartões usam textos do roteiro. A comparação repete o mesmo retrato ficcional nos dois lugares. O waveform do cartão de áudio é ilustrativo, não uma medição da fala. Os textos de TV e telefone são aplicados por código para manter ortografia e legibilidade.

Campos opcionais das cenas:

- `crop`: enquadramento dentro da ilustração, em frações `[esquerda, topo, direita, base]`. Frações de largura e altura iguais preservam o formato 9:16.
- `zoom` e `direction` (`in` ou `out`): intensidade e sentido do movimento de câmera.
- `status` (`chat`): `sent` mostra a foto como enviada; `seen`, o padrão, mostra “Visualizado” e “Nenhuma resposta.”.
- `play` (`audio`): início e fim absolutos da fala do amigo. O marcador de progresso percorre a barra nesse intervalo e pode ser interrompido pelo corte.

Nas legendas, `"voice": "amigo"` usa itálico âmbar para as falas do amigo, já que a mesma voz narra tudo. As legendas ficam acima da área inferior em que o TikTok e os Reels sobrepõem legenda e nome de usuário, e os cartões são deslocados para cima para deixar espaço a elas. O vídeo não tem selo da série, porque o topo fica coberto pelas duas interfaces; o nome da série e o episódio vão no texto do post.

Ativos esperados na pasta pai: `cena-01-base.png`, `cena-03-roupas.png`, `cena-07-audio.png`, `cena-09-porta.png`. Na ausência de um ativo, o script avisa e usa a primeira cena como fallback provisório. Opcionalmente, `retrato-zinho.png`, um retrato frontal em formato horizontal, substitui o recorte da cena 1 na TV e na comparação de fotos.

## Revisão antes de publicar

- Conferir duração real, cortes nas frases, final completo e legenda legível em tela pequena.
- Verificar que a fotografia só é revelada no momento correto e que o cartão de áudio coincide com a fala do amigo.
- Conferir se todas as imagens finais foram entregues; nenhum fallback deve passar despercebido.
- O arquivo é uma prévia de montagem. A classificação para monetização não é garantida por este tipo de montagem.
