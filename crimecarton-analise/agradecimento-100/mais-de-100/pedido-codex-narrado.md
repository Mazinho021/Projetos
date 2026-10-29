# Pedido para o Codex — narração e Zinho fazendo joia, para o vídeo dos mais de 100 seguidores

Criado em 29/10/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. O criador pediu que o vídeo [`agradecimento-mais-de-100-seguidores.mp4`](agradecimento-mais-de-100-seguidores.mp4) seja narrado pelo narrador da série. Também pediu que, na cena do “MAIS DE 100 SEGUIDORES”, o Zinho apareça feliz, fazendo joia, em vez de assustado. São 1 áudio e 2 ilustrações. Não alterar nenhum outro arquivo do projeto.

## Narração

Gerar no OpusClip com os parâmetros de [`pedido-narracao-mais-de-100.json`](pedido-narracao-mais-de-100.json): a mesma voz (Charon) e o mesmo modelo da narração das Partes 1 e 2, como em [`../../episodio-02/narracao-ep02-narrador-job.json`](../../episodio-02/narracao-ep02-narrador-job.json). São 7 falas curtas, em ordem, uns 20 s. Se o campo `style` passar do limite do OpusClip, encurtar sem mudar o sentido e anotar no job, como na Parte 2.

Salvar como `narracao-mais-de-100.wav`, com o registro do job em `narracao-mais-de-100-job.json`. A geração é paga e foi pedida pelo criador em 29/10/2026; mostrar o custo antes de executar.

## Ilustrações

São duas versões da mesma cena, para o Claude Code escolher a que ficar mais fiel ao Zinho:

- **`zinho-joia-a.png`** e **`zinho-joia-b.png`:** o Zinho feliz, da cintura para cima, de frente ou levemente de lado. Ele tem um sorriso aberto e os olhos alegres, e faz joia com a mão direita (o polegar para cima), na altura do peito.

Regras:

- O Zinho é o de [`../../zinho-referencia-v3.png`](../../zinho-referencia-v3.png) e de [`../../episodio-01/retrato-zinho.png`](../../episodio-01/retrato-zinho.png). Ele tem cabelo preto cacheado no topo, laterais em degradê e não tem barba. Veste a jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, e camiseta preta.
- O traço é o cartoon 2D da série, com contorno escuro, cores chapadas e sombra suave.
- O fundo é liso, creme claro, sem textura, pinceladas, sombra ou objetos, porque o Zinho vai ser recortado do fundo. A mão do joia, o cabelo e os ombros ficam inteiros dentro da imagem, com folga nas bordas, e o corte de baixo fica na cintura.
- Vertical 2:3 (por exemplo, 1024 × 1536) ou maior. Sem texto, números, logotipo ou marca d'água.
- Salvar em `crimecarton-analise/agradecimento-100/mais-de-100/`, com os nomes acima.

## Entrega

Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido. Fazer commit e push dos arquivos na `codex/crimecarton` do repositório `Mazinho021/Projetos`. Responder com a lista dos arquivos enviados e os créditos cobrados.

Depois, o Claude Code recorta o Zinho, alinha a narração ao texto e monta o vídeo narrado no tempo da voz.
