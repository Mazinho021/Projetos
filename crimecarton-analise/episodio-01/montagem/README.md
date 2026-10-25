# Zinho — montagem do animatic

Esta ferramenta monta uma prova de ritmo narrada: ilustrações, câmera suave, cartões de TV/celular e legendas. Não sintetiza movimento corporal do personagem. Os arquivos de trabalho e o MP4 ficam nesta pasta.

Requisitos locais: Python com Pillow, FFmpeg com libass, FFprobe. Não usa serviços externos nem geração paga.

## Executar

```bash
python /workspace/crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --audio /workspace/crimecarton-analise/episodio-01/narracao-original.wav \
  --timeline /workspace/crimecarton-analise/episodio-01/montagem/timeline.json
```

Sem `--timeline`, o script usa um esboço escalado para a duração da voz, **sem legendas**, com estado `provisional_scaled_to_audio`. Esse modo permite testar o render, mas os cortes devem ser conferidos com a fala antes de apresentar um piloto sincronizado.

`--prepare-only` produz os cartões estáticos e o ASS, sem codificar vídeo. `--workers 2` limita o paralelismo. `--clean` remove a indicação de prévia no marcador da série.

## Timeline

Os tempos são segundos absolutos na locução. As cenas devem cobrir de zero até a duração do áudio, sem espaços ou sobreposições.

```json
{
  "timing_status": "manually_aligned",
  "scenes": [
    {"start": 0, "end": 8, "kind": "art", "asset": "cena-01-base.png"},
    {"start": 8, "end": 14, "kind": "tv", "asset": "cena-01-base.png"}
  ],
  "captions": [
    {"start": 0.15, "end": 1.8, "text": "O assalto deu certo."},
    {"start": 2.1, "end": 4.6, "text": "Seu parceiro ficou\ncom dez milhões."}
  ]
}
```

Tipos de cena: `art`, `tv`, `chat`, `comparison`, `audio`. Os cartões usam textos do roteiro. A comparação repete o mesmo retrato ficcional nos dois lugares. O waveform do cartão de áudio é ilustrativo, não uma medição da fala. Os textos de TV e telefone são aplicados por código para manter ortografia e legibilidade.

Ativos esperados na pasta pai: `cena-01-base.png`, `cena-03-roupas.png`, `cena-07-audio.png`, `cena-09-porta.png`. Na ausência de um ativo, o script avisa e usa a primeira cena como fallback provisório.

## Revisão antes de publicar

- Conferir duração real, cortes nas frases, final completo e legenda legível em tela pequena.
- Verificar que a fotografia só é revelada no momento correto e que o cartão de áudio coincide com a fala do amigo.
- Conferir se todas as imagens finais foram entregues; nenhum fallback deve passar despercebido.
- O arquivo é uma prévia de montagem. A classificação para monetização não é garantida por este tipo de montagem.

O script e a timeline podem ser continuados por outro editor ou agente de código, inclusive Claude Code quando houver uma instalação disponível.
