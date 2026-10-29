# Agradecimento — mais de 100 seguidores

O vídeo dos 100 seguidores refeito do zero, a pedido do criador, em 29/10/2026. Ele tem animações novas, o Zinho em todas as cenas e “mais de 100 seguidores” no lugar de “100 seguidores”. O vídeo brinca com a mochila da Parte 1, que veio com roupa em vez do dinheiro: agora ela vem cheia de seguidores.

É vertical, 1080 × 1920 a 30 fps, com 15,6 s e **sem narração**, então não gasta crédito. O som são os efeitos da série (Kenney, CC0, e os sintetizados por `gerar_efeitos.py`), mais três sons feitos aqui: aplausos, uma subida antes do 100 e um brilho de sininhos. As cores são as do Zinho, as mesmas do site. O texto fica entre y = 280 e y = 1515, longe das barras e dos botões que Reels e TikTok desenham por cima.

| Tempo | Na tela | Animação | Som |
|---|---|---|---|
| 0–2,8 s | “LEMBRA DA / MOCHILA?” | O palco vazio sob um holofote. O Zinho entra deslizando com a mochila, e um traço vermelho de caneta circula a mochila. | whoosh, pop, impacto |
| 2,8–6,0 s | “DESSA VEZ / VEIO CHEIA!” e o contador de seguidores | A câmera chega perto, a mochila treme e explode em seguidores (bolinhas com bonequinho e etiquetas “+1”). O contador roda como um odômetro, de 0 a 100. | vibração, impacto, pops, notificações, tiques, subida |
| 6,0–9,2 s | “MAIS DE / 100 / SEGUIDORES” | Um clarão. O 100 sai do contador e toma o centro, sobre raios vermelhos que giram. Dois canhões de confete disparam dos cantos, e o Zinho surpreso espia de baixo. | impacto, canhões, aplausos |
| 8,9–12,4 s | “OBRIGADO, / ALIADOS!” e “Cada um de vocês faz parte dessa história.” | Uma faixa vermelha passa e abre o papel creme. Uma polaroide do Zinho sorrindo (“valeu demais!”) cai e balança, e corações sobem. | whoosh, impactos suaves, brilho |
| 12,1–15,6 s | “A PARTE 3 / TÁ CHEGANDO.” e “SEGUE @GOLPECARTOON” | Uma faixa azul passa e abre as listras da jaqueta. As capas das Partes 1 e 2 entram em leque, e a carta do meio vira de “?” para “Parte 3, em breve”, com o carimbo “VOCÊ DECIDE”. | whooshes, impacto, brilho, notificação |

Medido no MP4: -16,2 LUFS, com pico de -1,5 dBFS.

## Arquivos

- `agradecimento-mais-de-100-seguidores.mp4`: o vídeo.
- `capa-mais-de-100.jpg`: o quadro de 7,6 s, com o “MAIS DE 100 SEGUIDORES”, para usar de capa no Instagram e no TikTok.
- `recortes/zinho-corpo.png` e `recortes/zinho-surpreso.png`: o Zinho de corpo inteiro com a mochila e o rosto surpreso, recortados da folha de personagem [`zinho-referencia-v3.png`](../../zinho-referencia-v3.png) por `recortar.py`.
- `recortar.py`: faz os recortes com o isnet-anime, o modelo de recorte de desenhos que o rembg usa, rodando no onnxruntime. O modelo tem 176 MB e não fica no repositório: o endereço está no começo do script.
- `animar.py`: desenha o vídeo quadro a quadro e mixa o som. Cada elemento é uma função do tempo, então os quadros saem em paralelo. Os textos, os tempos e os efeitos sonoros estão todos nele.

A polaroide usa o retrato [`retrato-zinho.png`](../../episodio-01/retrato-zinho.png), e as cartas usam as capas de [`capas/`](../../capas).

## Refazer

Com Pillow, NumPy, onnxruntime (só para os recortes) e FFmpeg, a partir desta pasta:

```bash
python recortar.py /caminho/isnet-anime.onnx   # só se os recortes mudarem
python animar.py                              # o vídeo, em cerca de 1 minuto
python animar.py --quadros 4.6 7.5 14.6       # só alguns quadros, em work/, para conferir
```

Para outra marca de seguidores, trocar o `100` de `contador()`, de `cena_cem()` e de `tiques()`, e as frases em `cena_mochila()`.
