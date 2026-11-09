# Parte 6 — montagem

Esta pasta monta a Parte 6, **“A recompensa”**, com as ferramentas de [`episodio-01/montagem/`](../../episodio-01/montagem/) e o molde da [montagem da Parte 5](../../episodio-05/montagem/README.md). O roteiro está em [`../roteiro-ep06-contar.txt`](../roteiro-ep06-contar.txt), o plano cena por cena em [`../plano-ep06.md`](../plano-ep06.md) e o pedido ao Codex em [`../pedido-codex-ep06.md`](../pedido-codex-ep06.md).

**Situação em 09/11/2026:** a Parte 6 está pronta, nas duas versões: [`../parte-06-a-recompensa.mp4`](../parte-06-a-recompensa.mp4), para o Instagram, e [`../parte-06-a-recompensa-vertical.mp4`](../parte-06-a-recompensa-vertical.mp4), para o TikTok e o Shorts, com 2 min 11,6 s. Os 19 desenhos e as 3 vozes vieram do Codex. A vinheta vem da Parte 1, e a fala gravada do Toninho, da Parte 5. É a primeira parte com as regras de 08/11/2026: sem o “Chegou agora?” falado, com o resultado da votação e o jornal no final e com os celulares de frente nos desenhos.

## Refazer

Os comandos rodam a partir da raiz do repositório e precisam de:

- Pillow, NumPy e FFmpeg;
- faster-whisper e praat-parselmouth;
- onnxruntime, só para ampliar os desenhos.

```bash
A=crimecarton-analise/episodio-06
# 1. Os desenhos do Codex (941 × 1672, em ../originais/) ampliados para 1440 × 2560
python crimecarton-analise/episodio-03/montagem/ampliar_cenas.py --episodio $A
# 2. As vozes, alinhadas ao próprio texto. Conferir o começo de cada voz, como pede o CLAUDE.md
for v in narrador ademir toninho; do
  python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
    --audio $A/narracao-ep06-$v.wav --script $A/narracao-ep06-$v.txt --output $A/montagem/alinhamento-$v.json
done
# 3. A voz do Ademir (a do cobrador, ao vivo), a vinheta igualada e a gravação do Toninho da Parte 5
python crimecarton-analise/episodio-04/montagem/voz_ademir.py \
  --fonte $A/narracao-ep06-ademir.wav --saida $A/montagem/vozes/ademir.wav
python $A/montagem/igualar_vozes.py
python $A/montagem/gravacao_toninho.py
# 4. O cartaz, as telas dos celulares e as opções
python $A/montagem/compor_cenas.py
# 5. A faixa de narração, as duas timelines e os vídeos
python $A/montagem/montar_timeline.py
for v in "" "-vertical"; do
  python crimecarton-analise/episodio-01/montagem/render_animatic.py \
    --timeline $A/montagem/timeline$v.json --output $A/parte-06-a-recompensa$v.mp4 --workers 4
done
```

## As vozes

- **O texto foi acertado para as gravações,** sem gerar de novo. O faster-whisper e a pontuação das duas versões de cada trecho mostraram:
  - “Hoje, o seu rosto **ganhou** um preço.”, no lugar de “ganha”;
  - “Onde **está** o parceiro?” e “O seu parceiro **está** escondido…”, no lugar de “tá”.
- **O “bolo” do Toninho:** o Whisper ouviu “bula”, mas, num trecho curto, as duas leituras empatam, e a vogal medida soa como “o”. A palavra ficou como está, porque na montagem a frase “BOLO ÀS 4 DA MANHÃ” aparece na tela junto com a fala.
- **A gravação do Toninho tocando no celular** (“Me ajuda a pegar o dinheiro antes do Ademir, e a gente divide.”) é a da Parte 5, sem custo: [`gravacao_toninho.py`](gravacao_toninho.py) corta a fala pelo alinhamento da Parte 5 e põe o som de alto-falante de celular de `voz_cobranca.py`.

## O que cada script faz

- [`igualar_vozes.py`](igualar_vozes.py) leva a vinheta, cortada da narração da Parte 1, ao tom e ao timbre do narrador desta parte.
- [`gravacao_toninho.py`](gravacao_toninho.py) faz `vozes/toninho-gravacao.wav`, `gravacao-toninho.txt` e `alinhamento-toninho-gravacao.json`.
- [`compor_cenas.py`](compor_cenas.py) faz em `arte/`:
  - **o cartaz da recompensa** (cena 1): “RECOMPENSA”, o rosto do Zinho (o retrato da Parte 1, o mesmo da TV) e “R$ 50.000”, impressos no papel em branco do desenho, com a tinta multiplicada, para o papel manter a luz e as dobras;
  - **as telas dos celulares,** com letra grande, encaixadas com `encaixar_limpo`. Os celulares desta parte vieram de frente e grandes, como pede a regra de 08/11/2026, então a tela do próprio desenho já é o close:
    - na cena 3, o editor de áudio com a gravação do carro, com o trecho “A sua já saiu do São Jorge cheia de roupa velha.” marcado em vermelho e o botão “CORTAR TRECHO”; depois, o mesmo desenho com “Trecho cortado” e “SALVAR”;
    - na cena 11, a notícia do jornal: “Polícia oferece R$ 50 mil por suspeito do assalto”, com o rosto do Zinho;
    - na cena 16, a ligação para o Renato, na caixa postal;
  - **as duas opções lado a lado,** para a pergunta final.
- [`montar_timeline.py`](montar_timeline.py) junta a vinheta, o narrador, o Ademir, o Toninho e a gravação numa faixa, `../narracao-ep06.wav`, com as pausas de `PAUSES`, e monta as duas timelines.
  - **Abertura:** a vinheta, igual à da Parte 3; logo depois, aos 8 s, o cartaz da recompensa, com “O SEU ROSTO GANHOU UM PREÇO.”. **A história começa aos 11 s,** sem resumo falado, só com a etiqueta “PARTES 1 A 5 NO PERFIL”. Na Parte 5, ela começava aos 23 s.
  - **O final:** as duas opções com prós e contras; depois, o resultado da Parte 5 (CONTAR, 5 a 2), o jornal “A VOZ DO BAIRRO” com três comentários reais e “O SEU COMENTÁRIO PODE SAIR NO JORNAL DA PRÓXIMA PARTE.”; e a pergunta, com os botões FALAR e CALAR.
  - **O painel muda com a história:** “A SUA PARTE R$ 0”, “RECOMPENSA R$ 50 MIL”, em vermelho e tremendo, e “O PARCEIRO NA DONA CÉLIA”.
  - **Os elementos:** a gravação do Toninho num balão claro, com a etiqueta “A GRAVAÇÃO DO CARRO”; os balões do Ademir e do Toninho; os carimbos “DESSA VEZ, SIM” e “NÃO ATENDE”; as onomatopeias “ECA”, “TRANC” e “VRRR”; as polaroides “PARTE 4 · a cadeira”, “PARTE 5 · a mãe do Renato” e “PARTE 5 · o bolo”; e o café horrível como momento leve.
  - **As posições** de balões, círculos e etiquetas foram medidas em cada desenho, e cada plano foi conferido nas duas versões.
