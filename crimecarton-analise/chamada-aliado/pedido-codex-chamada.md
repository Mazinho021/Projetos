# Pedido para o Codex — narração e ilustrações do vídeo “Vire aliado”

Criado em 29/10/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. O criador pediu um vídeo que chame o público para virar aliado da Parte 3. O aliado compra o passe de R$ 9,90 no site, e o @ dele aparece dentro do episódio. O vídeo segue o estilo do agradecimento [`../agradecimento-100/mais-de-100/`](../agradecimento-100/mais-de-100/) e é narrado pelo narrador da série. São 1 áudio e 4 ilustrações. Não alterar nenhum outro arquivo do projeto.

## Narração

Gerar no OpusClip com os parâmetros de [`pedido-narracao-chamada.json`](pedido-narracao-chamada.json): a mesma voz (Charon) e o mesmo modelo das narrações anteriores, como em [`../agradecimento-100/mais-de-100/narracao-mais-de-100-job.json`](../agradecimento-100/mais-de-100/narracao-mais-de-100-job.json). São 7 falas curtas, em ordem, uns 27 s. Se o campo `style` passar do limite do OpusClip, encurtar sem mudar o sentido e anotar no job.

Salvar como `narracao-chamada.wav`, com o registro do job em `narracao-chamada-job.json`.

## Ilustrações

Regras para todas:

- O traço é o cartoon 2D da série, com contorno escuro, cores chapadas e sombra suave, como em [`../episodio-02/cena-07-carro.png`](../episodio-02/cena-07-carro.png) e [`../episodio-01/cena-01-base.png`](../episodio-01/cena-01-base.png).
- O Zinho é o de [`../zinho-referencia-v3.png`](../zinho-referencia-v3.png) e de [`../agradecimento-100/mais-de-100/zinho-joia-b.png`](../agradecimento-100/mais-de-100/zinho-joia-b.png). Ele tem cabelo preto cacheado no topo, laterais em degradê e não tem barba. Veste a jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, e camiseta preta.
- Sem texto, letras, números, logotipo ou marca d'água em nenhuma imagem: o @ e as notícias entram na montagem.
- Salvar em `crimecarton-analise/chamada-aliado/`, com os nomes abaixo.

1. **`zinho-apontando-a.png`** e **`zinho-apontando-b.png`:** duas versões da mesma cena, para o Claude Code escolher a que ficar mais fiel ao Zinho. O Zinho aparece da cintura para cima, de frente, apontando o indicador direito para quem assiste, como num cartaz de “quero você”. Ele tem um sorriso confiante e uma sobrancelha levantada, de quem está chamando para uma coisa boa. O fundo é liso, creme claro, sem textura, pinceladas, sombra ou objetos, porque o Zinho vai ser recortado do fundo. A mão, o dedo e o cabelo ficam inteiros dentro da imagem, com folga nas bordas, e o corte de baixo fica na cintura. Vertical 2:3 (por exemplo, 1024 × 1536) ou maior.
2. **`cena-muro.png`:** um muro de rua à noite, no bairro do Zinho (o mesmo da rua da Parte 2, com casas baixas, portões e poste de luz amarela). O muro ocupa quase todo o quadro: reboco gasto, um pouco de tinta velha descascando e calçada embaixo. No meio, à altura dos olhos, fica uma área lisa e vazia, larga, onde a montagem vai pintar o @ como pichação. Sem pichação, letras ou cartazes. Vertical 9:16, com pelo menos 1080 × 1920.
3. **`cena-tv.png`:** o quarto da Parte 1 à noite, com a mesa de madeira, a lâmpada pendurada e a janela com as luzes da cidade, de perto numa TV antiga de tubo sobre o móvel, ligada. A tela fica quase de frente para a câmera, ocupa pelo menos 40% da largura do quadro e tem um brilho azul-claro liso, vazio, porque o telejornal é desenhado na montagem. Vertical 9:16, com pelo menos 1080 × 1920.

## Entrega

Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido. Fazer commit e push dos arquivos na `codex/crimecarton` do repositório `Mazinho021/Projetos`. Responder com a lista dos arquivos enviados e os créditos cobrados. A geração é paga e foi pedida pelo criador em 29/10/2026; mostrar o custo antes de executar.

Depois, o Claude Code recorta o Zinho, alinha a narração ao texto e monta o vídeo no tempo da voz.
