# Agradecimento — 100 seguidores

> Em 29/10/2026, o vídeo foi refeito do zero, com outras animações e “mais de 100 seguidores”: ver [`mais-de-100/`](mais-de-100/). Este aqui fica como a primeira versão.

Vídeo vertical de 14,4 s para agradecer os 100 primeiros seguidores do perfil, no estilo da série e **sem narração**, então não gasta crédito: o som são os efeitos que já existem (Kenney, CC0, e os sintetizados por `gerar_efeitos.py`), sem trilha, como nos episódios. O texto fica entre y = 190 e y = 1010 e as linhas têm até 570 px, longe das barras e dos botões que Stories, Reels e TikTok desenham por cima.

| Tempo | Imagem | Na tela | Som |
|---|---|---|---|
| 0–2,8 s | Zinho abrindo a mochila, [`cena-01-base.png`](../episodio-01/cena-01-base.png) | “O ASSALTO / DEU CERTO.” e o painel “A SUA PARTE: R$ 0” | impacto |
| 2,8–5,4 s | Zinho preocupado com a mochila, [`ilustracao-perfil.png`](../perfil/ilustracao-perfil.png) | “MAS A SUA PARTE / ERA OUTRA.” | whoosh, pop |
| 5,4–8,9 s | Tela preta | “AGORA SÃO” e um contador de 0 a 100. Ao chegar, entra “SEGUIDORES.”, o painel vira “100 SEGUIDORES” em verde e o confete estoura | tiques, impacto, notificação |
| 8,9–11,9 s | Retrato sorrindo, `zinho-obrigado.png` | “OBRIGADO! / A CADA UM / DE VOCÊS.” | whoosh, pops |
| 11,9–14,4 s | O carro no portão, [`cena-07-carro.png`](../episodio-02/cena-07-carro.png), com borda vermelha | “A PARTE 3 / TÁ A CAMINHO.” | whoosh, impacto suave |

Medido no MP4: 720 × 1280 a 25 fps, volume de -17,3 LUFS (só efeitos) e pico de -2,4 dBFS.

## Arquivos

- `agradecimento-100-seguidores.mp4`: o vídeo.
- `zinho-obrigado.png`: o retrato sorrindo ([`retrato-zinho.png`](../episodio-01/retrato-zinho.png)) cortado em 9:16 em volta do rosto, com um degradê escuro embaixo, porque a parede é creme e o texto branco não aparece nela. Gerado por `montar_agradecimento.py`.
- `silencio.wav`: a trilha de voz vazia que o renderizador pede, com a duração do vídeo menos o `tail`.
- `montagem/montar_agradecimento.py`: gera os dois arquivos acima e `timeline.json`. Os textos e os tempos estão todos em `build()`.
- `montagem/confete.py`: o elemento `confetti`, que o `graficos.py` não tem. Joga as peças em leque a partir de (`x`, `y`), com resistência do ar, giro e “virada” de papel; tudo com semente fixa, então todos os quadros veem as mesmas peças.
- `montagem/render_agradecimento.py`: o `render_animatic.py` da série, depois de carregar o confete.

## Refazer

A partir da raiz do repositório, com os mesmos requisitos do [renderizador](../episodio-01/montagem/README.md):

```bash
python crimecarton-analise/agradecimento-100/montagem/montar_agradecimento.py
python crimecarton-analise/agradecimento-100/montagem/render_agradecimento.py \
  --timeline crimecarton-analise/agradecimento-100/montagem/timeline.json \
  --output crimecarton-analise/agradecimento-100/agradecimento-100-seguidores.mp4
```

Para outra marca de seguidores, trocar o `100` em `build()` (o contador, o painel e as frases) e rodar de novo.

## Com voz

Se o criador quiser narração, é preciso gerar a fala, com crédito e autorização dele, como nos pedidos ao Codex da série. Depois, é só pôr o áudio nesta pasta, trocar `audio` na timeline e ajustar os tempos em `build()` às palavras.
