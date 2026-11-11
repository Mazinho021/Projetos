---
name: rotina
description: "Tarefas de rotina da série A parte que faltou, no modelo mais leve com esforço médio: atualizar o site depois de uma parte, contar os votos de uma gravação de tela, escrever os textos dos posts, ajustar documentos e consertos pequenos com vários passos. Use no começo desses pedidos. Não use para roteiro, análise de números que muda a história ou montagem de vídeo."
model: sonnet
effort: medium
---

# Rotina

Esta skill deixa o resto da vez no modelo mais leve com esforço médio, que gasta bem menos que o modelo forte (ver “Modelo e esforço” no `CLAUDE.md`). Ela serve para tarefas de vários passos com o caminho já escrito. Uma resposta curta não precisa de skill: ao trocar de modelo, o novo modelo lê a conversa inteira de novo, e por pouca coisa isso gasta mais do que economiza.

**Se a tarefa pedir uma decisão de história, de roteiro ou de montagem,** parar e chamar a skill `roteiro` ou `montagem`.

## Site da série

- O passo a passo está na seção “Site da série” do `CLAUDE.md` e em `crimecarton-analise/ideia-site-da-serie.md`.
- Testar com `node --test crimecarton-analise/site/testes/*.test.mjs` e montar com `node montar.mjs`, dentro de `crimecarton-analise/site`, que escreve `dist/index.html`.
- Antes de publicar, ver a página na largura de celular: `node .claude/skills/rotina/scripts/site-shot.cjs <caminho absoluto do dist/index.html> <pasta>` tira o topo, a votação, os aliados e os capítulos, e diz a largura da página (mais de 390 quer dizer rolagem para o lado).
- Publicar com a ferramenta de deploy do Netlify e conferir no ar a página, o `/api/aliados` e as imagens novas.
- Nunca fazer compra de teste nem criar pagamento Pix, e não mostrar ao criador o token do deploy.

## Votos

- Tirar quadros da gravação de tela com o FFmpeg, ler os comentários e contar cada opção, dizendo como cada voto foi contado. Anotar no plano da parte.
- Quem comentou não ganha nome, e os dados pessoais das telas não se repetem.

## Texto dos posts

- Seguir a seção “Texto dos posts” do `CLAUDE.md`.
