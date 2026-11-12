---
name: roteiro
description: "Roteiro e decisões de história da série A parte que faltou, no modelo forte com esforço alto. Use no começo de todo pedido de roteiro (parte nova, lapidar, mudar falas ou o final), de análise dos números de uma parte (insights, retenção, comentários, votos que decidem o caminho) e de preparo do pedido de vozes e desenhos ao Codex, mesmo que o criador não diga a palavra roteiro."
model: opus
effort: high
---

# Roteiro, números e pedido ao Codex

Esta skill deixa o resto da vez no modelo forte com esforço alto, como o criador combinou em 10/11/2026 (ver “Modelo e esforço” no `CLAUDE.md`). O roteiro é o que mais pesa no resultado, e o esforço alto dá conta: o máximo custa umas 3,4 vezes mais e fica para a skill `maximo`, quando uma decisão grande travar.

## Roteiro de uma parte nova

1. Ler o plano e o roteiro da parte anterior, o resultado da votação e o arco em `crimecarton-analise/producao-zinho.md`.
2. Escrever pelas seções “Roteiros”, “Abertura” e “Final” do `CLAUDE.md`. O modelo é `crimecarton-analise/episodio-07/roteiro-ep07-falar.txt`.
3. Antes de mostrar, conferir frase por frase:
   - o gancho é uma situação concreta e perigosa, que quem nunca viu a série entende;
   - até os 30 s, quem chega sabe quem é o Zinho, o que ele quer e o que está em jogo;
   - no máximo três personagens com nome, cada um com o papel junto do nome;
   - cada frase traz uma pergunta nova ou uma revelação, e sai a que só leva alguém de um lugar a outro;
   - a pergunta moral vem logo na virada, e o final, com uns 25 s, termina pedindo para seguir e compartilhar;
   - umas 360 palavras, que dão uns 2 min 15 s.
4. Salvar o roteiro e o `plano-epNN.md` na pasta da parte, mostrar ao criador e **esperar o “ok” antes de qualquer geração paga**.

## Números de uma parte

- Tirar quadros da gravação de tela com o FFmpeg e ler as telas de números: visualizações, tempo médio, taxa de pulados, curtidas, comentários, salvamentos, compartilhamentos, visitas ao perfil, seguidores e a curva de retenção.
- Comparar com as partes anteriores na tabela do plano e dizer, em palavras simples, o que mudou e o que fazer na próxima parte.
- Votos: contar pelos comentários e dizer como cada um foi contado. Quem comentou não ganha nome (no jornal, só “— leitor”), e os dados pessoais das telas não se repetem.

## Pedido ao Codex

- O mesmo formato da parte anterior: `pedido-codex-epNN.md`, os `LOTE-*.md` (uma imagem por trecho, com as regras de composição, o celular de tamanho normal na mão, as imagens de referência de cada personagem e o estado dos objetos, como as portas do carro fechadas), os `pedido-narracao-*.json` e os `narracao-epNN-*.txt`.
- Mostrar o custo e dar ao criador a mensagem para colar no Codex, como na seção “Codex” do `CLAUDE.md`.
