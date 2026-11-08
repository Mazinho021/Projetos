# Parte 5 — montagem

Esta pasta monta a Parte 5, **“A divisão”**, com as ferramentas de [`episodio-01/montagem/`](../../episodio-01/montagem/) e o molde da [montagem da Parte 4](../../episodio-04/montagem/README.md). O roteiro está em [`../roteiro-ep05-cancelar.txt`](../roteiro-ep05-cancelar.txt), o plano cena por cena em [`../plano-ep05.md`](../plano-ep05.md) e o pedido ao Codex em [`../pedido-codex-ep05.md`](../pedido-codex-ep05.md).

**Situação em 08/11/2026:** a Parte 5 está pronta, nas duas versões: [`../parte-05-a-divisao.mp4`](../parte-05-a-divisao.mp4), para o Instagram, e [`../parte-05-a-divisao-vertical.mp4`](../parte-05-a-divisao-vertical.mp4), para o TikTok e o Shorts, com 2 min 11,8 s. Os 19 desenhos e as 4 vozes vieram do Codex, e a vinheta vem da Parte 1. Os balões, as setas e as etiquetas foram postos em cada desenho, e cada plano foi conferido nas duas versões.

## Refazer

Os comandos rodam a partir da raiz do repositório e precisam de:

- Pillow, NumPy e FFmpeg;
- faster-whisper e praat-parselmouth;
- onnxruntime, só para ampliar os desenhos.

```bash
A=crimecarton-analise/episodio-05
# 1. Os desenhos do Codex (941 × 1672, em ../originais/) ampliados para 1440 × 2560
python crimecarton-analise/episodio-03/montagem/ampliar_cenas.py --episodio $A
# 2. As vozes, alinhadas ao próprio texto (a do Ademir na gravação original). No alinhamento do
#    Renato, o “Cheguei.” foi acertado à mão (0,17–0,74 s): o Whisper o pôs na respiração seguinte,
#    e a montagem cortava a palavra. Ao alinhar de novo, conferir o começo de cada voz.
for v in narrador ademir renato toninho; do
  python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
    --audio $A/narracao-ep05-$v.wav --script $A/narracao-ep05-$v.txt --output $A/montagem/alinhamento-$v.json
done
# 3. A voz do Ademir (a do cobrador da Parte 3, ao vivo) e a vinheta igualada a este narrador
python crimecarton-analise/episodio-04/montagem/voz_ademir.py \
  --fonte $A/narracao-ep05-ademir.wav --saida $A/montagem/vozes/ademir.wav
python $A/montagem/igualar_vozes.py
# 4. As telas dos celulares, a grade do perfil, as lembranças da Parte 4 e as opções
python $A/montagem/compor_cenas.py
# 5. A faixa de narração, as duas timelines e os vídeos
python $A/montagem/montar_timeline.py
for v in "" "-vertical"; do
  python crimecarton-analise/episodio-01/montagem/render_animatic.py \
    --timeline $A/montagem/timeline$v.json --output $A/parte-05-a-divisao$v.mp4 --workers 4
done
```

## O que cada script faz

- [`igualar_vozes.py`](igualar_vozes.py) leva a vinheta, cortada da narração da Parte 1, ao tom e ao timbre do narrador desta parte, como nas Partes 3 e 4.
- [`compor_cenas.py`](compor_cenas.py) faz em `arte/`:
  - **a grade do perfil,** com as capas das Partes 1 a 4;
  - **as duas lembranças da Parte 4,** desfocadas e escuras, atrás das polaroides: o aperto de mão (“o acordo”) e o parceiro com as duas bolsas (“as bolsas”);
  - **as quatro telas de celular,** encaixadas com `encaixar_limpo`, da Parte 4, que mantém o contorno dos dedos:
    - na cena 2, a conversa com o jornal às 03:14, com a foto da divisão agendada e o botão de cancelar sob o polegar;
    - na cena 6, “Apagados recentemente”, com a foto da divisão e os 30 dias;
    - na cena 9, a conversa com o Renato, com o áudio de 0:07;
    - na cena 14, o gravador ligado no bolso, com 00:03;
  - **as duas opções lado a lado,** para a pergunta final.
- [`montar_timeline.py`](montar_timeline.py) junta o narrador, o Ademir, o Renato e o Toninho numa faixa, `../narracao-ep05.wav`, com as pausas de `PAUSES`, e monta as duas timelines seguindo o plano.
  - **Abertura:** a vinheta, igual à da Parte 3; logo depois, aos 8 s, as mãos enchendo a mochila de roupa velha, com “Hoje você descobre quem encheu a sua mochila de roupa velha.”; depois, o resumo, com o perfil, o acordo com o Ademir, o CANCELAR por 5 a 0 e o jornal “A VOZ DO BAIRRO”. A história nova começa aos 23 s.
  - **O painel muda com a história:** “A SUA PARTE R$ 0”, “A FOTO: NA LIXEIRA”, “QUEM TE ROUBOU: ADEMIR”, em vermelho e tremendo, e “A SUA PARTE: R$ 5 MI?”.
  - **Os elementos:** balões das falas do Ademir, do Renato e do Toninho; as falas do Toninho sobre a noite da divisão, quando ele não aparece, entre aspas; as etiquetas de nome do Toninho e da Dona Célia; os círculos no botão de cancelar, na foto da lixeira e no gravador; os carimbos “NÃO SAI”, “SÓCIOS” e “APAGADA”; a polaroide da mochila da Parte 1; o áudio do Renato e o bolo de fubá como momento leve; e as opções TOPAR e CONTAR com prós e contras.
  - **As posições** de balões, círculos e etiquetas foram medidas em cada desenho, e as frases ficam entre 830 e 1020 px de altura.
