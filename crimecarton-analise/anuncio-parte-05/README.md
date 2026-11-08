# Anúncio — a Parte 5 sai amanhã, às 12h

Vídeo pedido pelo criador na noite de 07/11/2026, enquanto o Codex desenhava a Parte 5. Ele avisa que a Parte 5 sai no dia seguinte, ao meio-dia, e chama para as vagas de aliado da Parte 6: a Parte 5 sai sem aliados, e o site já vende os passes da Parte 6, ainda sem prazo.

É vertical, 1080 × 1920 a 30 fps, com 16,8 s, para os stories, o feed e o TikTok. Não tem voz nova: o narrador diz falas que já tinha gravado para a [chamada de aliados](../chamada-aliado/), cortadas nas pausas dele. Os planos da chamada que mostram onde o @ aparece entram como eram, com “Parte 6” no lugar de “Parte 3”.

| Narração | Na tela |
|---|---|
| (sem voz) | As mãos do Zinho com a roupa velha da mochila (Parte 1), com “PARTE 5”, “SAI AMANHÃ”, “ÀS 12H” e “QUEM ENCHEU A SUA MOCHILA?” |
| “Vire aliado do Zinho.” | O Zinho sobe apontando para quem assiste, com “VIRE / ALIADO / DO ZINHO” |
| “O seu arroba entra no episódio: no celular dele, num muro, na TV ou nos créditos.” | Os planos da chamada: o @ digitado, o celular, o muro, a TV e os créditos da Parte 6 |
| “Nove e noventa no Pix, direto no site. O link tá na bio.” | “R$ 9,90”, “NO PIX, DIRETO NO SITE”, “PARTE 6 · 30 VAGAS”, as 30 vagas e “LINK NA BIO” |
| (sem voz) | O Zinho chamando, com “PARTE 5”, “AMANHÃ, 12H” e “VIRE ALIADO DA PARTE 6” |

Medido no MP4: -16,0 LUFS, com pico de -2,3 dBFS, como o anúncio da Parte 3. O reconhecimento de fala (faster-whisper `medium`, sem dica) transcreve as falas inteiras.

## Arquivos

- `anuncio-parte-05.mp4`: o vídeo.
- `capa-anuncio-parte-05.jpg`: o quadro de 1,6 s, para usar de capa se for para o feed.
- `animar.py`: desenha o vídeo quadro a quadro e mixa o som, com as ferramentas, os planos e as falas da chamada de aliados.

Para refazer, a partir desta pasta: `python animar.py`, ou `python animar.py --quadros 1.6 6 13.4` para ver alguns quadros em `work/`.
