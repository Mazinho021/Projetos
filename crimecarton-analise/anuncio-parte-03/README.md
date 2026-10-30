# Anúncio — a Parte 3 sai hoje à noite

Vídeo pedido pelo criador na manhã de 30/10/2026, o dia em que as vagas de aliado da Parte 3 fecham, às 21h. Ele avisa que a Parte 3 sai à noite e chama para as últimas horas de aliado. A ideia do criador era perguntar ao público se a Parte 3 saía ao meio-dia ou às 21h, mas ao meio-dia ela não ficaria pronta. Além disso, os @ de quem pagar até as 21h precisam entrar no episódio. Por isso, virou um anúncio.

É vertical, 1080 × 1920 a 30 fps, com 12,4 s, para os stories e o feed. Não tem voz nova: o narrador diz três falas que já tinha gravado para a [chamada de aliados](../chamada-aliado/), cortadas nas pausas dele.

| Narração | Na tela |
|---|---|
| (sem voz) | O carro de farol apagado da Parte 2, no portão, com “PARTE 3”, “SAI HOJE” e “À NOITE” |
| “Quer aparecer na parte três?” | “QUER APARECER / NA PARTE 3?”, com a carta da Parte 3 virando para “hoje à noite” |
| “Vire aliado do Zinho.” | O Zinho sobe apontando para quem assiste, com “VIRE / ALIADO / DO ZINHO” |
| “São até trinta vagas, até sexta, às nove da noite.” | “ATÉ 30 VAGAS”, as 30 vagas e “SÓ ATÉ HOJE, 21H” |
| (sem voz) | O Zinho chamando, com “PARTE 3”, “HOJE À NOITE” e “VIRE ALIADO ATÉ 21H” |

Medido no MP4: -16,0 LUFS, com pico de -2,0 dBFS. Em cada palavra, a voz fica pelo menos 9,2 dB acima dos efeitos. O reconhecimento de fala (faster-whisper) transcreve as três falas sem erro.

## Arquivos

- `anuncio-parte-03.mp4`: o vídeo.
- `capa-anuncio-parte-03.jpg`: o quadro de 1,2 s, para usar de capa se for para o feed.
- `animar.py`: desenha o vídeo quadro a quadro e mixa o som. Usa as ferramentas e as falas da chamada de aliados. A segunda gravação da chamada é igualada à primeira pela frase que as duas dizem.

Para refazer, a partir desta pasta: `python animar.py`, ou `python animar.py --quadros 1.2 3.9 8.2` para ver alguns quadros em `work/`.
