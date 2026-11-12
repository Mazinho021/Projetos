# Parte 7 — montagem

Esta pasta monta a Parte 7, **“A casa da mãe”**, com as ferramentas de [`episodio-01/montagem/`](../../episodio-01/montagem/) e o molde da [montagem da Parte 6](../../episodio-06/montagem/README.md). O roteiro está em [`../roteiro-ep07-falar.txt`](../roteiro-ep07-falar.txt), o plano cena por cena em [`../plano-ep07.md`](../plano-ep07.md) e o pedido ao Codex em [`../pedido-codex-ep07.md`](../pedido-codex-ep07.md).

**Situação em 12/11/2026:** a Parte 7 foi refeita, depois que o criador apontou o rosto do Zinho diferente nas cenas 18, 23 e 25, o celular do tamanho de um tablet nas cenas 7 e 25 e a porta do carro aberta e fechada ao mesmo tempo na cena 8. O Codex refez as cenas 7, 8, 18, 23, 24 e 25 ([`../pedido-codex-ep07-refazer.md`](../pedido-codex-ep07-refazer.md)), e os rostos e os objetos foram conferidos em tamanho grande antes da montagem. Ela está pronta nas duas versões, com 2 min 14,5 s: [`../parte-07-a-casa-da-mae.mp4`](../parte-07-a-casa-da-mae.mp4), para o Instagram, e [`../parte-07-a-casa-da-mae-vertical.mp4`](../parte-07-a-casa-da-mae-vertical.mp4), para o TikTok e o Shorts. Os 25 desenhos e as 4 vozes vieram do Codex, por 5 créditos de voz. A capa é [`../../capas/capa-parte-07.png`](../../capas/capa-parte-07.png).

É a primeira parte com as regras de 10/11/2026:

- começa direto no gancho, o dinheiro na mesa, sem a vinheta;
- “PARTE 7” e “PARTES 1 A 6 NO PERFIL” só entram depois do gancho, em “Uma hora antes”;
- o resultado da Parte 6 vira um carimbo no carro (“PARTE 6 · VOCÊS ESCOLHERAM FALAR”);
- a pergunta vem logo depois da virada, e as opções têm um pró e um contra, sem pausa em silêncio;
- o jornal “A VOZ DO BAIRRO” entra junto com o pedido de comentário, e o fim pede para seguir e compartilhar.

## Refazer

Os comandos rodam a partir da raiz do repositório e precisam de:

- Pillow, NumPy e FFmpeg;
- faster-whisper e praat-parselmouth;
- onnxruntime, só para ampliar os desenhos.

```bash
A=crimecarton-analise/episodio-07
# 1. Os desenhos do Codex (941 × 1672, em ../originais/) ampliados para 1440 × 2560
python crimecarton-analise/episodio-03/montagem/ampliar_cenas.py --episodio $A
# 2. A fala do parceiro com a pausa da vírgula antes do "Zinho" (ver "As vozes")
ffmpeg -y -i $A/narracao-ep07-parceiro.wav -filter_complex \
  "[0]atrim=1.25:2.535,asetpts=N/SR/TB,afade=t=out:st=1.275:d=0.01[a];anullsrc=r=24000:cl=mono,atrim=0:0.22[s];[0]atrim=2.535,asetpts=N/SR/TB,afade=t=in:d=0.008[b];[a][s][b]concat=n=3:v=0:a=1" \
  -ac 1 -ar 24000 $A/montagem/vozes/parceiro.wav
# 3. As vozes, alinhadas ao próprio texto
for v in narrador ademir celia; do
  python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
    --audio $A/narracao-ep07-$v.wav --script $A/narracao-ep07-$v.txt --output $A/montagem/alinhamento-$v.json
done
python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py --model medium \
  --audio $A/montagem/vozes/parceiro.wav --script $A/montagem/vozes/parceiro.txt --output $A/montagem/alinhamento-parceiro.json
# 4. A voz do Ademir (a do cobrador, ao vivo)
python crimecarton-analise/episodio-04/montagem/voz_ademir.py \
  --fonte $A/narracao-ep07-ademir.wav --saida $A/montagem/vozes/ademir.wav
# 5. Os closes dos celulares e as opções
python $A/montagem/compor_cenas.py
# 6. A faixa de narração, as duas timelines e os vídeos
python $A/montagem/montar_timeline.py
for v in "" "-vertical"; do
  python crimecarton-analise/episodio-01/montagem/render_animatic.py \
    --timeline $A/montagem/timeline$v.json --output $A/parte-07-a-casa-da-mae$v.mp4 --workers 4
done
```

## As vozes

- **Os textos das vozes são os do roteiro.** O Codex tinha trocado os `narracao-ep07-*.txt` pela transcrição do Whisper (“Robou”, “Sélia”, “ferro velho”), e eles voltaram ao texto pedido. O alinhamento acha cada palavra mesmo assim.
- **As dúvidas do Codex,** conferidas com `pontuar.py`, nos modelos `medium` e `small`: “canta junto”, “com o dinheiro”, “no jornal” e “Se entregar” (o Whisper ouviu “Sem entregar”). Em todas, os dois modelos discordam ou a diferença é só a emenda de uma palavra na outra, e o sentido não muda. O texto ficou como no roteiro, e a tela diz as palavras importantes, como “OPÇÃO 1 · ENTREGAR”.
- **A fala do parceiro** saiu sem a pausa da vírgula, e soava “Família primeirozinho”. A montagem abre 0,22 s de silêncio antes do “z” de “Zinho” (em 2,535 s da gravação, onde começa o chiado do “z”) e corta o 1,25 s de respiração do começo. Depois disso, o Whisper ouve “Família primeiro” e “Zinho” separados.

## O que cada script faz

- [`compor_cenas.py`](compor_cenas.py) faz em `arte/`:
  - **os closes dos celulares** (regra do criador de 12/11/2026): os desenhos mostram o Zinho com um celular de tamanho normal, e a mensagem aparece logo depois, num celular de tamanho médio sobre o desenho desfocado e escuro, de 300 px de largura no quadro de 720:
    - na cena 7, os “Apagados recentemente” com a foto da divisão (a da Parte 2) e o botão “Recuperar”; depois, a foto com “Foto recuperada” e o jornal “A VOZ DO BAIRRO” entre os contatos para enviar;
    - na cena 25, a foto e o botão “ENVIAR” para o jornal, num celular de 250 px;
  - **as duas opções lado a lado,** para o pedido de comentário.
- [`montar_timeline.py`](montar_timeline.py) junta o narrador, o Ademir, a Dona Célia e o parceiro numa faixa, `../narracao-ep07.wav`, com as pausas de `PAUSES`, e monta as duas timelines.
  - **Os recortes:** a cena 4 sobe e vai para a esquerda (`CROP_04`), para o rosto do Ademir sair da coluna de botões do TikTok; a cena 13 mostra só as pernas e os chinelos (`CROP_13`), que estavam baixos demais; e a cena 21 desce o rosto do Ademir para longe do painel (`CROP_21`).
  - **O painel muda com a história:** “A SUA PARTE R$ 5 MI?” no gancho, “R$ 0” no carro, “O PARCEIRO É O IRMÃO”, em vermelho e tremendo, na virada, e “R$ 5 MI?” de novo quando o dinheiro cai na mesa.
  - **As lembranças:** o parceiro com as bolsas (Parte 4) e o cartão de TV com o rosto do Zinho, no lugar da vinheta; o Renato (Parte 4) em polaroide; e o Ademir com o alicate na porta do galpão (Parte 6), em “O alicate, o Ademir já trouxe.”.
  - **Os elementos:** etiquetas de nome do Ademir, da Dona Célia e do parceiro; os balões das quatro vozes; os carimbos “FALAR”, “ROUBOU VOCÊ”, “E O ADEMIR”, “DESAFINADO”, “SUA ARMA” e “SÓ A CULPA”; o contador até R$ 10.000.000; e o pagode desafinado como momento leve.
  - **As posições** de balões, círculos e etiquetas foram medidas em cada desenho, e cada plano foi conferido nas duas versões.
