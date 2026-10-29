# Agradecimento — mais de 100 seguidores

O vídeo dos 100 seguidores refeito do zero, a pedido do criador, em 29/10/2026. Ele tem animações novas, o Zinho em todas as cenas e “mais de 100 seguidores” no lugar de “100 seguidores”. O vídeo brinca com a mochila da Parte 1, que veio com roupa em vez do dinheiro: agora ela vem cheia de seguidores.

No mesmo dia, o criador pediu duas mudanças:

- **Narração:** o vídeo passou a ser narrado pelo narrador da série, com a voz Charon, num tom de suspense leve que vira agradecimento.
- **Zinho feliz:** na cena do “MAIS DE 100 SEGUIDORES”, ele aparece fazendo joia, e não mais assustado.

O Codex gerou a voz e o desenho, pelo pedido [`pedido-codex-narrado.md`](pedido-codex-narrado.md).

É vertical, 1080 × 1920 a 30 fps, com 21,2 s. Tudo segue as palavras da narração. O som tem a voz, os efeitos da série (Kenney, CC0, e os sintetizados por `gerar_efeitos.py`) e três sons feitos aqui: aplausos, uma subida antes do 100 e um brilho de sininhos. Os efeitos abaixam sozinhos enquanto o narrador fala. As cores são as do Zinho, as mesmas do site. O texto fica entre y = 280 e y = 1515, longe das barras e dos botões que Reels e TikTok desenham por cima.

| Narração | Na tela | Animação |
|---|---|---|
| “Lembra da mochila?” | “LEMBRA DA / MOCHILA?” | O palco vazio sob um holofote. O Zinho entra deslizando com a mochila, e um traço vermelho de caneta circula a mochila. |
| “Na primeira vez, ela veio só com roupa velha.” | Uma polaroide da Parte 1 | O palco escurece. A foto da Parte 1, com a mochila cheia de roupa, entra girando, e o carimbo “SÓ ROUPA VELHA” bate em “roupa”. |
| “Dessa vez… veio cheia.” | “DESSA VEZ / VEIO CHEIA!” e o contador de seguidores | A câmera chega perto e a mochila treme na pausa do narrador. Em “cheia”, ela explode em seguidores (bolinhas com bonequinho e etiquetas “+1”). O contador roda como um odômetro, de 0 a 100. |
| “Mais de cem seguidores. O Zinho aprovou.” | “MAIS DE / 100 / SEGUIDORES” | Um clarão. O 100 sai do contador e toma o centro, sobre raios vermelhos que giram, e dois canhões de confete disparam dos cantos. Em “O Zinho”, ele sobe de baixo, feliz, fazendo joia, e em “aprovou” o polegar brilha. |
| “Obrigado, aliados. Cada um de vocês faz parte dessa história.” | “OBRIGADO, / ALIADOS!” e a frase | Uma faixa vermelha passa e abre o papel creme. Uma polaroide do Zinho sorrindo (“valeu demais!”) cai e balança, e corações sobem. |
| “E a parte três já tá chegando. Segue o perfil pra não perder.” | “A PARTE 3 / TÁ CHEGANDO.” e “SEGUE @GOLPECARTOON” | Uma faixa azul passa e abre as listras da jaqueta. As capas das Partes 1 e 2 entram em leque, e a carta do meio vira de “?” para “Parte 3, em breve”, com o carimbo “VOCÊ DECIDE”. |

Para o contador ter tempo de rolar depois da explosão, a pausa do narrador antes de “Mais de cem” foi esticada em 0,7 s. Medido no MP4: -16,0 LUFS, com pico de -2,0 dBFS. Em cada palavra, a voz fica pelo menos 7 dB acima dos efeitos (23 dB na mediana). O reconhecimento de fala (faster-whisper) transcreve o áudio final inteiro sem erro.

## Arquivos

- `agradecimento-mais-de-100-seguidores.mp4`: o vídeo.
- `capa-mais-de-100.jpg`: o quadro de 11,7 s, com o “MAIS DE 100 SEGUIDORES” e o Zinho fazendo joia, para usar de capa no Instagram e no TikTok.
- `narracao-mais-de-100.wav`, com o registro `narracao-mais-de-100-job.json`: a narração, gerada pelo Codex no OpusClip com [`pedido-narracao-mais-de-100.json`](pedido-narracao-mais-de-100.json) (voz Charon, 1 crédito).
- `narracao-mais-de-100.txt` e `alinhamento-narracao.json`: o texto da narração e o tempo de cada palavra, medido por [`alinhar_narracao.py`](../../episodio-01/montagem/alinhar_narracao.py) com o modelo `medium` (43 de 46 palavras reconhecidas exatamente).
- `zinho-joia-a.png` e `zinho-joia-b.png`: as duas versões do Zinho fazendo joia que o Codex desenhou. O vídeo usa a B, que ficou mais próxima do retrato da série.
- `recortes/zinho-corpo.png` e `recortes/zinho-joia.png`: o Zinho de corpo inteiro com a mochila, recortado da folha de personagem [`zinho-referencia-v3.png`](../../zinho-referencia-v3.png), e o Zinho fazendo joia, recortado da versão B. Os dois saem de `recortar.py`.
- `recortar.py`: faz os recortes com o isnet-anime, o modelo de recorte de desenhos que o rembg usa, rodando no onnxruntime. O modelo tem 176 MB e não fica no repositório: o endereço está no começo do script.
- `animar.py`: desenha o vídeo quadro a quadro e mixa o som. Os tempos vêm do alinhamento: cada cena e cada efeito está preso a uma palavra, em `T`, logo no começo. Cada elemento é uma função do tempo, então os quadros saem em paralelo.

A polaroide do agradecimento usa o retrato [`retrato-zinho.png`](../../episodio-01/retrato-zinho.png), a da lembrança usa [`ilustracao-perfil.png`](../../perfil/ilustracao-perfil.png), e as cartas usam as capas de [`capas/`](../../capas).

## Refazer

Com Pillow, NumPy, onnxruntime (só para os recortes), faster-whisper (só para o alinhamento) e FFmpeg, a partir desta pasta:

```bash
python recortar.py /caminho/isnet-anime.onnx   # só se os recortes mudarem
python ../../episodio-01/montagem/alinhar_narracao.py --audio narracao-mais-de-100.wav \
  --script narracao-mais-de-100.txt --output alinhamento-narracao.json   # só se a narração mudar
python animar.py                              # o vídeo, em pouco mais de 1 minuto
python animar.py --quadros 4.1 11.3 18.6      # só alguns quadros, em work/, para conferir
```

Com uma narração nova, as cenas se ajustam sozinhas às palavras. Se o texto mudar, os números das palavras em `T` precisam acompanhar.
