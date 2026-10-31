# Parte 3 — montagem

Os scripts desta pasta montaram a versão recusada da Parte 3, “A noite”, e ficam como molde para o roteiro novo, “O preço” ([`../roteiro-ep03.txt`](../roteiro-ep03.txt) e [`../plano-ep03.md`](../plano-ep03.md)). As imagens, as vozes e os vídeos da versão recusada saíram do repositório e continuam no histórico do Git, no commit `442918d`.

Quando o Codex entregar as 13 imagens e as 3 vozes do [pedido](../pedido-codex-ep03.md), a montagem fica assim:

- [`voz_renato.py`](voz_renato.py) continua igual: passa as falas do Renato pela transformação de `voz_amigo.py`, com tom médio de 112 Hz.
- **A voz do cobrador** ganha uma transformação nova: mais grave, perto de 80 Hz, e com som de mensagem de áudio de celular.
- [`igualar_vozes.py`](igualar_vozes.py) continua igual: leva a vinheta da Parte 1 ao tom e ao timbre do narrador novo.
- [`compor_cenas.py`](compor_cenas.py) fazia o beco, o plantão na TV, as conversas e a votação da versão recusada. Passa a fazer a tela de mensagem do número do Renato, com a foto e o áudio, a tela com 01:12 e a votação TROCAR ou DEIXAR.
- [`montar_timeline.py`](montar_timeline.py) segue o da Parte 2, com cada corte, gráfico e efeito preso a uma palavra do roteiro. Ganha a voz do cobrador, as pausas e os planos novos.

Antes de entregar:

- conferir um quadro de cada plano nas duas versões, como manda o [`CLAUDE.md`](../../../CLAUDE.md), para nenhum rosto, mão, celular ou frase ficar atrás do painel, da etiqueta ou dos botões;
- ouvir as três vozes com o faster-whisper `medium`, sem o texto como dica.
