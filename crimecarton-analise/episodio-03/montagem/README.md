# Parte 3 — montagem

Esta pasta monta a Parte 3, **“O preço”**, com as ferramentas de [`episodio-01/montagem/`](../../episodio-01/montagem/README.md) e o molde da [montagem da Parte 2](../../episodio-02/montagem/README.md). O roteiro, com a voz de cada fala, está em [`../roteiro-ep03.txt`](../roteiro-ep03.txt), e o plano em [`../plano-ep03.md`](../plano-ep03.md).

O resultado são dois vídeos:

- [`parte-03-o-preco.mp4`](../parte-03-o-preco.mp4), a versão do Instagram;
- [`parte-03-o-preco-vertical.mp4`](../parte-03-o-preco-vertical.mp4), a do TikTok e do Shorts.

Esta é a segunda montagem de “O preço”. A primeira usava 13 desenhos repetidos com zoom em 37 planos, e o criador pediu uma imagem para cada coisa que a narração conta. Esta usa **35 desenhos diferentes em 41 planos**, cada um uma vez só. Se um desenho se repetir, `montar_timeline.py` para com erro. A primeira montagem e a versão recusada, “A noite”, continuam no histórico do Git.

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
python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
  --audio $A/narracao-ep03-narrador.wav --script $A/narracao-ep03-narrador.txt --output $A/montagem/alinhamento-narrador.json
python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
  --audio $A/narracao-ep03-cobranca.wav --script $A/narracao-ep03-cobranca.txt --output $A/montagem/alinhamento-cobranca.json
python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
  --audio $A/narracao-ep03-renato-algenib.wav --script $A/narracao-ep03-renato.txt \
  --output $A/montagem/alinhamento-renato-algenib.json
# 3. A voz do cobrador e a vinheta igualada a este narrador
python $A/montagem/voz_cobranca.py
python $A/montagem/igualar_vozes.py
# 4. As telas dos celulares, a lembrança do almoço e as capas da abertura
python $A/montagem/compor_cenas.py
# 5. A faixa de narração, as duas timelines e os vídeos
python $A/montagem/montar_timeline.py
for v in "" "-vertical"; do
  python crimecarton-analise/episodio-01/montagem/render_animatic.py \
    --timeline $A/montagem/timeline$v.json --output $A/parte-03-o-preco$v.mp4 --workers 4
done
```

## O que cada script faz

- [`ampliar_cenas.py`](ampliar_cenas.py) amplia os desenhos com o Real-ESRGAN anime 6B.
  - O gerador de imagens do Codex entrega no máximo 941 × 1672, menos que os 1080 × 1920 do [`CLAUDE.md`](../../../CLAUDE.md).
  - O script amplia 4 vezes, reduz para 1440 × 2560 e devolve a cor média do original, para a IA só limpar o traço.
  - O modelo, de 18 MB, é baixado na primeira vez para `work/modelos/`.
- **A voz do Renato** é a **Algenib**, que o criador escolheu entre três testes (Orus, Achird e Algenib). A gravação entra como veio, sem transformação. As outras duas ficam em `../` como registro.
  - Até a primeira montagem desta parte, o Renato era a voz do narrador transformada, que o criador achou feia.
  - A fala “Corre, Zinho! Corre!” passou na conferência sem dica: o reconhecimento de fala ouve “Correzinho, corre!”, com o “Zinho” no lugar.
- [`voz_cobranca.py`](voz_cobranca.py) dá ao cobrador uma voz diferente da do narrador. Ela fica mais grave, perto de 78 Hz contra 94 Hz, mais escura e com menos melodia. Também passa por um alto-falante de celular, porque o Zinho escuta a mensagem com o aparelho no ouvido.
  - O script também corta `efeitos/cobranca-eco.wav`, com “Você correu. Ele não.”. A montagem toca esse trecho de novo na pausa depois de “Você escuta outra vez”.
- [`igualar_vozes.py`](igualar_vozes.py) leva a vinheta, cortada da narração da Parte 1, ao tom e ao timbre do narrador desta parte.
- [`compor_cenas.py`](compor_cenas.py) faz em `arte/`:
  - **As telas dos quatro celulares.** O script acha sozinho a tela em branco de cada desenho e encaixa nela:
    - na cena 8, a notificação da foto às 01:04;
    - na cena 25, a conversa com a foto;
    - na cena 28, a conversa com a foto e o áudio de 0:14;
    - na cena 32, o relógio em 01:12.

    A cena 25 é espelhada antes, porque o celular estava na borda direita, atrás dos botões do TikTok.
  - **O almoço da cena 11 como lembrança**, num cartão de foto. No desenho inteiro, o Renato menino fica atrás dos botões do TikTok. No cartão da versão vertical, que fica um pouco à esquerda, ele aparece.
  - **As capas das Partes 1 e 2 lado a lado**, como a grade do perfil mostra. Elas entram em “As partes um e dois estão no perfil”, no lugar da arte da mochila repetida.
- A placa “FERRO-VELHO SÃO JORGE”, o nome do calendário da Parte 2, é pintada pela montagem, a partir do `paint` de `montar_timeline.py`.
- [`montar_timeline.py`](montar_timeline.py) segue o da Parte 2. Junta a vinheta, o narrador, o Renato e o cobrador numa faixa, `../narracao-ep03.wav`, com as pausas de `PAUSES`. Cada corte, gráfico e efeito fica preso a uma palavra do roteiro.
  - Os sons do carro, dos passos, do interruptor e do celular vêm de `../../episodio-02/montagem/efeitos/`.
  - Cada enquadramento deixa rostos, mãos, o celular e o anel fora do quarto de cima, onde ficam o painel e a etiqueta. As frases ficam entre 65% e 80% da altura.

Na conferência das vozes com o faster-whisper `medium` sem dica, a narração saiu com as palavras do roteiro. Houve só variações que não mudam o sentido: “um muro”, “um número do Renato” e “um anel” no lugar de “o”, e “tá sozinho”. O alinhamento acertou:

- 263 de 270 palavras do narrador;
- 23 de 25 do cobrador;
- 8 de 10 do Renato, porque “Corre, Zinho” vira uma palavra só no reconhecimento.
