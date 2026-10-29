# Chamada — Vire aliado

Vídeo que chama o público para virar aliado da Parte 3, pedido pelo criador em 29/10/2026. O aliado tem o @ dele dentro do episódio. No mesmo dia, o criador pediu duas mudanças:

- **Sem Pix, preço nem link:** o vídeo acaba no prazo das vagas, com o Zinho chamando quem assiste.
- **Até 30 vagas:** as vagas passaram de 10 para 30. O narrador fala isso numa fala nova, gerada depois.

É vertical, 1080 × 1920 a 30 fps, com 18,4 s. O narrador da série conta tudo, com a voz Charon. O estilo, as cores e os sons são os do agradecimento dos [mais de 100 seguidores](../agradecimento-100/mais-de-100/), de onde vêm as ferramentas de desenho e de som. Tudo segue as palavras da narração. Os efeitos abaixam sozinhos enquanto o narrador fala. O texto fica entre y = 240 e y = 1500, longe das barras e dos botões que Reels e TikTok desenham por cima.

| Narração | Na tela | Animação |
|---|---|---|
| “Quer aparecer na parte três?” | “QUER APARECER / NA PARTE 3?” | A carta da Parte 3 entra girando sobre as listras da jaqueta e vira para “Parte 3, em breve”. |
| “Vire aliado do Zinho.” | “VIRE / ALIADO / DO ZINHO” | Um clarão abre os raios cor de caramelo, e o Zinho sobe de baixo apontando para quem assiste. |
| “O seu arroba entra no episódio:” | “O SEU”, “@seuperfil” e “ENTRA NO EPISÓDIO” | Sob o holofote, o @ é digitado letra por letra numa caixa. |
| “no celular dele, num muro, na TV ou nos créditos.” | Uma etiqueta para cada lugar | Quatro cortes rápidos. A mensagem do @ chega no celular do Zinho, o da Parte 2. O @ é pichado com spray no muro do bairro, aparece no plantão de uma TV de tubo e sobe nos créditos da Parte 3. |
| “E vai na legenda do post, com o seu número de aliado.” | “NA LEGENDA DO POST” e “COM O SEU NÚMERO” | A legenda do post sobe com o @ sublinhado, e o crachá “Nº 001” bate na tela. |
| “São até trinta vagas, até sexta, às nove da noite.” | “ATÉ 30 VAGAS” e “ATÉ SEXTA, 21H” | Trinta vagas abertas pipocam, e um relógio marca o prazo. |
| (sem voz) | “FAÇA PARTE / DA HISTÓRIA” e “VIRE ALIADO” | Uma faixa vermelha abre os raios vermelhos. O Zinho sobe apontando para quem assiste, e estrelinhas piscam em volta do título. |

A voz vem de duas gravações, as duas geradas pelo Codex com a voz Charon:

- **A primeira, `narracao-chamada.wav`:** vale até “com o seu número de aliado.”. O resto dela falava em 10 vagas, no Pix e no link, que o criador tirou.
- **A segunda, `narracao-trinta-vagas.wav`:** repete “E vai na legenda do post, com o seu número de aliado.” só para dar o tom e depois diz “São até trinta vagas, até sexta, às nove da noite.”. Só essa última fala entra no vídeo.

A frase que as duas gravações repetem serve para igualar o volume: a segunda veio 2 dB mais alta e foi abaixada. A emenda cai no silêncio depois de “aliado.”, antes do “s” de “São”, e não se ouve.

Medido no MP4: -15,9 LUFS, com pico de -2,4 dBFS. Em cada palavra, a voz fica pelo menos 9,5 dB acima dos efeitos (20,9 dB na mediana). O reconhecimento de fala (faster-whisper) transcreve o áudio final inteiro, inclusive “São até 30 vagas, até sexta, às 9 da noite.”.

## Arquivos

- `chamada-aliado.mp4`: o vídeo.
- `capa-chamada-aliado.jpg`: o quadro de 17,1 s, com o Zinho apontando e “FAÇA PARTE DA HISTÓRIA”, para usar de capa no Instagram e no TikTok.
- `narracao-chamada.wav`, com o registro `narracao-chamada-job.json`: a narração. O Codex gerou o áudio no OpusClip com [`pedido-narracao-chamada.json`](pedido-narracao-chamada.json) (voz Charon, 1 crédito). O pedido completo ao Codex está em [`pedido-codex-chamada.md`](pedido-codex-chamada.md).
- `narracao-chamada.txt` e `alinhamento-narracao.json`: o texto da narração e o tempo de cada palavra, medido por [`alinhar_narracao.py`](../episodio-01/montagem/alinhar_narracao.py) com o modelo `medium` (53 de 60 palavras reconhecidas exatamente).
- `narracao-trinta-vagas.wav`, com o registro `narracao-trinta-vagas-job.json`: a segunda gravação, pedida em [`pedido-codex-trinta-vagas.md`](pedido-codex-trinta-vagas.md) com [`pedido-narracao-trinta-vagas.json`](pedido-narracao-trinta-vagas.json) (voz Charon, 1 crédito). O texto e o tempo de cada palavra estão em `narracao-trinta-vagas.txt` e `alinhamento-trinta-vagas.json` (20 de 22 palavras reconhecidas exatamente).
- `zinho-apontando-a.png` e `zinho-apontando-b.png`: as duas versões do Zinho apontando que o Codex desenhou. As duas ficaram fiéis ao retrato da série, então o vídeo usa as duas: a B, com a sobrancelha levantada, no “Vire aliado”, e a A, com o sorriso aberto, no fim.
- `recortes/zinho-apontando.png` e `recortes/zinho-chamando.png`: os dois recortes, da B e da A, que saem de `recortar.py`.
- `cena-muro.png` e `cena-tv.png`: o muro do bairro à noite e a TV de tubo do quarto. O Codex desenhou os dois sem nenhum texto. O @ é pintado no muro aqui, na perspectiva do muro e na luz do poste. O telejornal é encaixado no vidro da TV, com os cantos arredondados e a borda escura das TVs de tubo.
- `recortar.py`: recorta o Zinho com o mesmo recorte do agradecimento (o isnet-anime, no onnxruntime). Depois, limpa os pontinhos de papel que o modelo deixa entre os cachos. O modelo tem 176 MB e não fica no repositório: o endereço está no [script do agradecimento](../agradecimento-100/mais-de-100/recortar.py).
- `animar.py`: desenha o vídeo quadro a quadro e mixa o som. Os tempos vêm do alinhamento: cada cena e cada efeito está preso a uma palavra, em `T`, logo no começo. O fim sem voz dura 3 s depois da última fala.

O celular é a cena 6 da Parte 2 ([`cena-06-celular-mesa.png`](../episodio-02/cena-06-celular-mesa.png)), com a tela de bloqueio da montagem da série. A legenda do post usa a foto de perfil do site ([`perfil.jpg`](../site/img/perfil.jpg)), e a carta usa as capas de [`capas/`](../capas).

## Refazer

Com Pillow, NumPy, onnxruntime (só para os recortes), faster-whisper (só para o alinhamento) e FFmpeg, a partir desta pasta:

```bash
python recortar.py /caminho/isnet-anime.onnx   # só se os recortes mudarem
python ../episodio-01/montagem/alinhar_narracao.py --audio narracao-chamada.wav \
  --script narracao-chamada.txt --output alinhamento-narracao.json   # só se a narração mudar
python ../episodio-01/montagem/alinhar_narracao.py --audio narracao-trinta-vagas.wav \
  --script narracao-trinta-vagas.txt --output alinhamento-trinta-vagas.json   # idem, a segunda
python animar.py                              # o vídeo, em cerca de 1 minuto
python animar.py --quadros 2.6 6.9 12.5       # só alguns quadros, em work/, para conferir
```

Com uma narração nova, as cenas se ajustam sozinhas às palavras. Se o texto mudar, os números das palavras precisam acompanhar: os de `T`, o `ATE_ALIADO` (a última palavra da primeira gravação) e o `LINHA_30` (as palavras da segunda). Se a segunda gravação mudar, o `CORTE_30` (o silêncio antes de “São”) também precisa acompanhar.
