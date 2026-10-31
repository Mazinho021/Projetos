# Parte 3 — montagem

Esta pasta monta a Parte 3, **“O preço”**, com as ferramentas de [`episodio-01/montagem/`](../../episodio-01/montagem/README.md) e o molde da [montagem da Parte 2](../../episodio-02/montagem/README.md). O roteiro, com a voz de cada fala, está em [`../roteiro-ep03.txt`](../roteiro-ep03.txt), e o plano em [`../plano-ep03.md`](../plano-ep03.md).

O resultado são dois vídeos:

- [`parte-03-o-preco.mp4`](../parte-03-o-preco.mp4), a versão do Instagram;
- [`parte-03-o-preco-vertical.mp4`](../parte-03-o-preco-vertical.mp4), a do TikTok e do Shorts.

As duas têm 2 min 15 s, com -13,9 LUFS e pico de -0,9 dBFS. Cada plano foi conferido nas duas versões: nenhum rosto, mão, celular, anel ou frase fica atrás do painel, da etiqueta ou da coluna de botões do TikTok.

A versão recusada, “A noite”, continua no histórico do Git, no commit `442918d`.

## Refazer

Os comandos rodam a partir da raiz do repositório e precisam de:

- Pillow, NumPy e FFmpeg;
- faster-whisper e praat-parselmouth;
- onnxruntime, só para ampliar os desenhos.

```bash
A=crimecarton-analise/episodio-03
# 1. Os desenhos do Codex (941 × 1672, em ../originais/) ampliados para 1440 × 2560
python $A/montagem/ampliar_cenas.py
# 2. As vozes, alinhadas ao próprio texto
for v in narrador renato cobranca; do
  python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
    --audio $A/narracao-ep03-$v.wav --script $A/narracao-ep03-$v.txt --output $A/montagem/alinhamento-$v.json
done
# 3. A voz do Renato, a do cobrador e a vinheta igualada a este narrador
python $A/montagem/voz_renato.py
python $A/montagem/voz_cobranca.py
python $A/montagem/igualar_vozes.py
# 4. A conversa no celular do Zinho
python $A/montagem/compor_cenas.py
# 5. A faixa de narração, as duas timelines e os vídeos
python $A/montagem/montar_timeline.py
for v in "" "-vertical"; do
  python crimecarton-analise/episodio-01/montagem/render_animatic.py \
    --timeline $A/montagem/timeline$v.json --output $A/parte-03-o-preco$v.mp4 --workers 4
done
```

## O que cada script faz

- [`ampliar_cenas.py`](ampliar_cenas.py) amplia os desenhos com o Real-ESRGAN anime 6B. O gerador de imagens do Codex entrega no máximo 941 × 1672, menos que os 1080 × 1920 do [`CLAUDE.md`](../../../CLAUDE.md). O script amplia 4 vezes, reduz para 1440 × 2560 e devolve a cor média do original, para a IA só limpar o traço. Assim, os closes da montagem não ampliam a imagem além do tamanho dela. O modelo, de 18 MB, é baixado na primeira vez para `work/modelos/`.
- [`voz_renato.py`](voz_renato.py) passa as falas do Renato, gravadas com a voz do narrador, pela mesma transformação da mensagem de áudio da Parte 1, com tom médio de 112 Hz.
  - Na gravação, o “Zinho” de “Corre, Zinho! Corre!” saiu parecido com “senhor” no reconhecimento de fala sem dica. O Codex cortou a palavra e repetiu o último “Corre!”, como registra [`../narracao-ep03-renato-job.json`](../narracao-ep03-renato-job.json).
  - O roteiro ficou “Corre! Corre!”. O segundo grito sai um pouco mais agudo, para não soar como repetição.
- [`voz_cobranca.py`](voz_cobranca.py) dá ao cobrador uma voz diferente da do narrador. Ela fica mais grave, perto de 78 Hz contra 94 Hz, mais escura e com menos melodia. Também passa por um alto-falante de celular, porque o Zinho escuta a mensagem com o aparelho no ouvido.
  - O script também corta `efeitos/cobranca-eco.wav`, com “Você correu. Ele não.”. A montagem toca esse trecho de novo na pausa depois de “Você escuta outra vez”.
- [`igualar_vozes.py`](igualar_vozes.py) leva a vinheta, cortada da narração da Parte 1, ao tom e ao timbre do narrador desta parte.
- [`compor_cenas.py`](compor_cenas.py) faz em `arte/` duas coisas:
  - o celular da cena 8 aberto na conversa com o número do Renato, no tema escuro. Primeiro chega a foto, às 01:04, e depois o áudio de 0:14, às 01:05;
  - o almoço da cena 11 como lembrança, num cartão de foto sobre uma cópia desfocada do desenho. No desenho inteiro, o Renato menino fica na borda direita, atrás dos botões do TikTok. No cartão da versão vertical, que fica um pouco à esquerda, ele aparece.
- A montagem desenha mais três coisas, a partir do `screen` e do `paint` de `montar_timeline.py`:
  - a tela de bloqueio com a notificação da foto;
  - o relógio em 01:12;
  - a placa “FERRO-VELHO SÃO JORGE”, o nome do calendário da Parte 2.
- [`montar_timeline.py`](montar_timeline.py) segue o da Parte 2. Junta a vinheta, o narrador, o Renato e o cobrador numa faixa, `../narracao-ep03.wav`, com as pausas de `PAUSES`. Cada corte, gráfico e efeito fica preso a uma palavra do roteiro.
  - Os sons do carro, dos passos, do interruptor e do celular vêm de `../../episodio-02/montagem/efeitos/`.
  - Cada enquadramento foi escolhido para deixar rostos, mãos, o celular e o anel fora do quarto de cima, onde ficam o painel e a etiqueta. As frases ficam entre 65% e 80% da altura.

Na conferência das vozes com o faster-whisper `medium` sem dica, a narração saiu com as palavras do roteiro. Houve só variações que não mudam o sentido: “um muro”, “um número do Renato” e “um anel” no lugar de “o”, e “tá sozinho”. O alinhamento acertou 263 de 270 palavras do narrador, as 9 do Renato e 23 de 25 do cobrador.
