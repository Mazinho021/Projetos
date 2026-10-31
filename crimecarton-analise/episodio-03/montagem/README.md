# Parte 3 — montagem

Esta pasta monta a Parte 3, “A noite”, com as ferramentas de [`episodio-01/montagem/`](../../episodio-01/montagem/README.md) e o molde da [montagem da Parte 2](../../episodio-02/montagem/README.md). O roteiro, com a voz de cada fala, está em [`../roteiro-ep03.txt`](../roteiro-ep03.txt), e o plano em [`../plano-ep03.md`](../plano-ep03.md). O resultado são [`parte-03-a-noite.mp4`](../parte-03-a-noite.mp4), a versão do Instagram, e [`parte-03-a-noite-vertical.mp4`](../parte-03-a-noite-vertical.mp4), a do TikTok e do Shorts. As duas têm 2 min 25 s, com -13,4 LUFS e pico de -0,8 dBFS.

## Refazer

A partir da raiz do repositório, com Pillow, NumPy, FFmpeg, faster-whisper, praat-parselmouth e onnxruntime (este, só para a máscara do beco):

```bash
A=crimecarton-analise/episodio-03
# 1. As vozes, alinhadas ao próprio texto
python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
  --audio $A/narracao-ep03-narrador.wav --script $A/narracao-ep03-narrador.txt --output $A/montagem/alinhamento-narrador.json
python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
  --audio $A/narracao-ep03-renato.wav --script $A/narracao-ep03-renato.txt --output $A/montagem/alinhamento-renato.json
# 2. A voz do Renato (a do amigo nas Partes 1 e 2) e a vinheta igualada a este narrador
python $A/montagem/voz_renato.py
python $A/montagem/igualar_vozes.py
# 3. As imagens com os @ dos aliados (--buscar lê a lista do site) e a conversa no celular do Renato
python $A/montagem/compor_cenas.py --buscar
# 4. A faixa de narração, as duas timelines e os vídeos
python $A/montagem/montar_timeline.py
for v in "" "-vertical"; do
  python crimecarton-analise/episodio-01/montagem/render_animatic.py \
    --timeline $A/montagem/timeline$v.json --output $A/parte-03-a-noite$v.mp4 --workers 4
done
```

## O que cada script faz

- [`voz_renato.py`](voz_renato.py) passa as falas do Renato, gravadas com a voz do narrador, pela mesma transformação da mensagem de áudio da Parte 1. O tom médio dele fica em 112 Hz, como o do amigo na Parte 2.
- [`igualar_vozes.py`](igualar_vozes.py) leva a vinheta, cortada da narração da Parte 1, ao tom e ao timbre do narrador desta parte.
- [`compor_cenas.py`](compor_cenas.py) faz em `arte/` as imagens que a montagem tira dos desenhos do Codex:
  - **o beco:** os @ pichados no muro, na perspectiva e na luz do muro e atrás dos dois, usando a máscara `arte/beco-pessoas.png`, feita com o isnet-anime;
  - **o plantão:** na TV do bar, com os rostos de Zinho e Renato, “PROCURADOS” e os comentários do público;
  - **o celular do Zinho:** cheio de mensagens;
  - **a conversa do Renato com a “Cobrança”:** de “Tô chegando na casa dele.” às 23:31 até “Cadê vocês?”;
  - **a tela dividida da votação;**
  - **os créditos dos aliados**, quando há algum.

  A lista vem de `aliados-parte-03.json`. As vagas da Parte 3 fecharam sem aliados, então o muro tem só “ZINHO”, e a TV e o celular não têm @.
- [`montar_timeline.py`](montar_timeline.py) segue o da Parte 2: junta a vinheta, o narrador e o Renato numa faixa, `../narracao-ep03.wav`, com as pausas de `PAUSES`. Cada corte, gráfico e efeito fica preso a uma palavra do roteiro. Os sons do carro, dos passos, das portas e do celular vêm de `../../episodio-02/montagem/efeitos/`.

Na gravação do Renato, “Depois eu mudei de lado.” saiu como “depois eu **mandei** de lado”, e o reconhecimento de fala ouve “mandei” com o modelo `medium`. A frase ficou fora da montagem: ele termina em “Antes de ver a tua cara.”.
