# Parte 4 — montagem

Esta pasta monta a Parte 4, **“O dono do anel”**, com as ferramentas de [`episodio-01/montagem/`](../../episodio-01/montagem/) e o molde da [montagem da Parte 3](../../episodio-03/montagem/README.md). O roteiro está em [`../roteiro-ep04-trocar.txt`](../roteiro-ep04-trocar.txt), o plano cena por cena em [`../plano-ep04.md`](../plano-ep04.md) e o pedido ao Codex em [`../pedido-codex-ep04.md`](../pedido-codex-ep04.md).

**Situação em 03/11/2026:** os desenhos e as vozes ainda não chegaram do Codex. A montagem já está pronta para recebê-los. Enquanto isso, ela gera um rascunho, com tempos estimados e um cartão provisório no lugar de cada desenho.

## Refazer

Os comandos rodam a partir da raiz do repositório e precisam de:

- Pillow, NumPy e FFmpeg;
- faster-whisper e praat-parselmouth;
- onnxruntime, só para ampliar os desenhos.

```bash
A=crimecarton-analise/episodio-04
# 1. Os desenhos do Codex (941 × 1672, em ../originais/) ampliados para 1440 × 2560
python crimecarton-analise/episodio-03/montagem/ampliar_cenas.py --episodio $A
# 2. As vozes, alinhadas ao próprio texto (a do Ademir na gravação original)
for v in narrador renato ademir; do
  python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
    --audio $A/narracao-ep04-$v.wav --script $A/narracao-ep04-$v.txt --output $A/montagem/alinhamento-$v.json
done
# 3. A voz do Ademir: a do cobrador da Parte 3, sem o som de celular
python $A/montagem/voz_ademir.py
# 4. As telas dos celulares, a grade do perfil, a lembrança da Parte 3 e as opções
python $A/montagem/compor_cenas.py
# 5. A faixa de narração, as duas timelines e os vídeos
python $A/montagem/montar_timeline.py
for v in "" "-vertical"; do
  python crimecarton-analise/episodio-01/montagem/render_animatic.py \
    --timeline $A/montagem/timeline$v.json --output $A/parte-04-o-dono-do-anel$v.mp4 --workers 4
done
```

**O rascunho,** antes do material, sai assim:

```bash
python $A/montagem/compor_cenas.py --rascunho
python $A/montagem/montar_timeline.py --estimar /tmp/rascunho-ep04
```

## O que cada script faz

- [`voz_ademir.py`](voz_ademir.py) dá ao Ademir a voz do cobrador da Parte 3. É a mesma troca de voz de `voz_cobranca.py`, mais grave, escura e com menos melodia, mas sem o alto-falante de celular, porque agora ele fala ao vivo. Quem ouviu o áudio da Parte 3 reconhece o homem.
- [`compor_cenas.py`](compor_cenas.py) faz em `arte/`:
  - **a grade do perfil,** com as capas das Partes 1, 2 e 3;
  - **a lembrança da Parte 3:** a cena da mão com o anel no muro, desfocada, atrás da polaroide dela;
  - **as duas telas de celular:**
    - na cena 3, a conversa com o jornal, com a foto da divisão agendada para 03:15 e o botão de cancelar;
    - na cena 20, a tela bloqueada às 03:13, com o aviso do envio;
  - **as duas opções lado a lado,** para a pergunta final.

  Com `--rascunho`, ele desenha antes, em `rascunho/`, um cartão para cada desenho que falta. Cada cartão tem o número, o nome e a fala do roteiro. Os das cenas de celular têm a tela em branco no lugar certo, para as telas já se encaixarem. As imagens montadas com os cartões ficam em `rascunho/arte/`, fora do Git, e só o rascunho as usa.
- [`montar_timeline.py`](montar_timeline.py) junta o narrador, o Renato e o Ademir numa faixa, `../narracao-ep04.wav`, com as pausas de `PAUSES`. Ele monta as duas timelines seguindo o plano.
  - **Abertura:** os 2 primeiros segundos mostram o Ademir saindo para a luz, com a frase na tela desde o primeiro quadro. Depois vem o resumo de uns 8 s, com o perfil, o Renato pego, o empate e o jornal “A VOZ DO BAIRRO”.
  - **O resultado da votação:** `RESULTADO` escolhe a frase. Com `'empate'`, entra “Deu empate. No desempate: trocar.”. Com `'maioria'`, entra “Vocês decidiram: trocar.”, e aí `VOTE` recebe os números reais. A narração grava as duas.
  - **Os elementos:** balões das falas, etiquetas de nome, círculos e etiquetas com linha nas pistas, o painel que vira o relógio da foto, o café como momento leve e as opções com prós e contras.
  - **O ritmo do rascunho:** nos tempos estimados, cada voz fala no ritmo das gravações da Parte 3.

## Quando o material chegar

1. **Conferir as vozes** com o faster-whisper `medium`, sem dar o texto como dica, como pede o [`CLAUDE.md`](../../../CLAUDE.md).
2. **Ampliar os desenhos** e rodar `compor_cenas.py` sem `--rascunho`.
3. **Acertar as posições pelo desenho de verdade:** balões, círculos, etiquetas com linha e etiquetas sobre os personagens seguem por enquanto a composição do pedido (rostos entre 32% e 42% da altura). A placa do portão, na cena 4, também é pintada nessa hora, com o nome “FERRO-VELHO SÃO JORGE”.
4. **Conferir um quadro de cada plano** nas duas versões: nada atrás do painel, da etiqueta ou dos botões do TikTok, e nenhum corpo cortado.
5. **Fazer a capa** da Parte 4.
