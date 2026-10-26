# Pedido para o Codex — materiais da v4 do episódio 1

Criado em 26/10/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. São três materiais. Não alterar nenhum outro arquivo do projeto.

## 1. Retrato frontal do Zinho

É a foto que Zinho mandou ao amigo e que depois aparece no noticiário. Entra na TV e na comparação “A FOTO ENVIADA / A FOTO NO JORNAL”.

- Referência de rosto, cabelo e roupa: [`zinho-referencia-v3.png`](zinho-referencia-v3.png), no mesmo traço cartoon 2D das cenas do episódio 1.
- Retrato do peito para cima, de frente, olhando direto para a câmera, expressão tranquila com um meio sorriso, como uma foto casual tirada de dia na rua, com um muro pintado simples ao fundo.
- Mesmo cabelo cacheado com laterais em degradê, rosto sem barba, jaqueta azul-marinho com capuz vermelho e faixas brancas, camiseta preta.
- Formato horizontal 4:3, com pelo menos 1024 px de largura; rosto no centro e espaço acima do cabelo. Sem texto, logotipo ou marca d'água.
- Salvar como `crimecarton-analise/episodio-01/retrato-zinho.png`.

## 2. Folha de personagem do amigo

- Descrição, figurino e cores: [`ficha-amigo.md`](ficha-amigo.md). Referência de imagem: [`episodio-01/cena-09-porta.png`](episodio-01/cena-09-porta.png) e o recorte [`amigo-referencia-provisoria.png`](amigo-referencia-provisoria.png).
- Mesmo formato e traço de [`zinho-referencia-v3.png`](zinho-referencia-v3.png): corpo inteiro de frente, de lado e de costas, e três rostos com as expressões culpa contida, tensão e tentativa de sorriso.
- Manter o figurino da cena 9 (jaqueta verde-oliva aberta, camiseta cinza-escuro, jeans escuro) e o mesmo rosto, cabelo e barba.
- Horizontal 3:2. Sem texto, pois o nome ainda não foi definido; sem logotipo ou marca d'água.
- Salvar como `crimecarton-analise/amigo-referencia-v1.png`.

## 3. Narração do pedido de comentário

- Gerar no OpusClip com os parâmetros de [`pedido-narracao-cta-ep01.json`](pedido-narracao-cta-ep01.json): mesma voz (Charon) e mesmo estilo da narração principal.
- A geração é paga e foi autorizada pelo criador. Mostrar o custo antes de executar. **Não gerar de novo a narração principal.**
- Salvar o áudio como `crimecarton-analise/episodio-01/narracao-cta-ep01.wav` e o registro do job como `crimecarton-analise/episodio-01/narracao-cta-job.json`, como em `narracao-job.json`.

## Entrega

Fazer commit e push na branch `codex/crimecarton` do repositório `Mazinho021/Projetos` e responder com a lista dos arquivos enviados. O Claude Code integra os três na v4.
