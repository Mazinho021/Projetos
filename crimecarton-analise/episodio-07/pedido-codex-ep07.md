# Pedido para o Codex — Parte 7, “A casa da mãe”

Criado em 11/11/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. O criador aprovou o roteiro, [`roteiro-ep07-falar.txt`](roteiro-ep07-falar.txt), em 10/11/2026 (“Ok”). O plano cena por cena está em [`plano-ep07.md`](plano-ep07.md).

O pedido tem duas partes:

- **4 gravações:** o narrador, o Ademir, a Dona Célia e o parceiro do assalto;
- **25 ilustrações,** em três lotes.

Não alterar nenhum outro arquivo do projeto. Fazer tudo numa tarefa só, nesta mesma conversa, sem abrir agentes em paralelo.

## Ordem

1. **As vozes,** com o custo mostrado antes. Commit e push logo depois delas.
2. **Os desenhos, lote por lote,** com commit e push **logo depois de cada cena pronta**, uma por vez:
   - [`LOTE-01-CENAS-01-A-08.md`](LOTE-01-CENAS-01-A-08.md): cenas 1 a 8, o gancho e o carro do Ademir;
   - [`LOTE-02-CENAS-09-A-17.md`](LOTE-02-CENAS-09-A-17.md): cenas 9 a 17, a cozinha da Dona Célia e a virada;
   - [`LOTE-03-CENAS-18-A-25.md`](LOTE-03-CENAS-18-A-25.md): cenas 18 a 25, o dinheiro, a pergunta e as opções.
3. Se o limite de uso acabar no meio, o que já tiver push está salvo. Na volta, conferir na `codex/crimecarton` o que já existe e seguir da próxima cena.

## Vozes

Gerar as quatro gravações e salvar tudo em `crimecarton-analise/episodio-07/`.

1. **Narrador:** a voz Charon de sempre.
   - Gerar com [`pedido-narracao-ep07.json`](pedido-narracao-ep07.json) e salvar em `narracao-ep07-narrador.wav`, com o registro em `narracao-ep07-narrador-job.json`.
2. **Ademir:** Charon, no estilo do cobrador das Partes 3 a 6.
   - Gerar com [`pedido-narracao-ademir-ep07.json`](pedido-narracao-ademir-ep07.json) e salvar em `narracao-ep07-ademir.wav`, com o registro em `narracao-ep07-ademir-job.json`.
3. **Dona Célia:** voz nova, a Gacrux.
   - Gerar com [`pedido-narracao-celia-ep07.json`](pedido-narracao-celia-ep07.json) e salvar em `narracao-ep07-celia.wav`, com o registro em `narracao-ep07-celia-job.json`.
4. **O parceiro do assalto:** voz nova, a Umbriel.
   - Gerar com [`pedido-narracao-parceiro-ep07.json`](pedido-narracao-parceiro-ep07.json) e salvar em `narracao-ep07-parceiro.wav`, com o registro em `narracao-ep07-parceiro-job.json`.

**Custo:** pelas Partes 2 a 6, deve custar uns **5 créditos**, mas o valor certo é o que o Codex mostrar antes de executar. A geração é paga e foi pedida pelo criador.

- O narrador, com uns 115 s, deve custar 2 ou 3.
- O Ademir, a Dona Célia e o parceiro, com uns 12, 3 e 3 s, devem custar 1 cada.

**Regras para as gravações:**

- **Não editar os áudios.**
- **Conferir cada gravação:** registrar no job a transcrição do faster-whisper `medium`, sem dar o texto como dica.
- **Se uma palavra sair trocada:** avisar na resposta, sem gerar de novo. O Claude Code confere e decide.
- **Se o serviço de voz disser que já existe um job com a mesma `idempotencyKey`,** usar esse resultado em vez de pagar de novo.
- **Se não der para baixar os WAV,** seguir o item 6 do [`AGENTS.md`](../../AGENTS.md): gravar os links em `links-temporarios.json`, nesta pasta, fazer commit e push e avisar.

## Regras para todas as ilustrações

**Composição.** O vídeo cobre o topo de cada imagem com um painel (“A SUA PARTE · SUSPEITA”) e uma etiqueta. A parte de baixo fica com as legendas, e a borda direita com os botões do TikTok. Então:

- **Os 25% de cima** ficam só com fundo calmo: céu, teto, parede, teto do carro ou escuro. Nada de rosto, cabeça, mão, celular, anel ou objeto importante.
- **Rostos, mãos e a ação principal** ficam **entre 30% e 60% da altura**, no meio da largura.
- **Os 20% de baixo** ficam só com chão, piso ou fundo.
- **A borda direita** (os 20% da direita, entre 45% e 80% da altura) fica sem nada importante.

**Celulares (regra de 08/11/2026).** Na Parte 5, os celulares saíram pequenos e inclinados, e as mensagens encaixadas neles ficaram tortas e difíceis de ler. Por isso:

- o celular fica **de frente para a câmera, reto, sem inclinação**, como uma foto tirada de frente para a tela;
- **a tela é grande:** ocupa **pelo menos 40% da largura** do desenho;
- a tela fica acesa, lisa e em branco, numa cor clara uniforme, com os **quatro cantos visíveis**. A interface entra na montagem;
- dedos podem passar por cima da borda da tela, com o contorno escuro de sempre, mas sem cobrir o meio dela.

**Corpo inteiro e cenário.**

- Os personagens não podem sair cortados, fundidos ou atravessados pelo cenário: banco do carro, mesa, cadeira, batente de porta ou portão.
- Cada parte do corpo que aparece tem que fazer sentido com o que está na frente e atrás dela.
- Quando o plano corta o corpo, o corte é da borda do quadro, como num plano médio, e nunca de um objeto do cenário.

**Variedade.**

- Cada imagem é um plano diferente, como num storyboard: aberto, close, detalhe, de cima, de baixo, por cima do ombro.
- Nenhuma pode parecer um recorte de outra nem repetir um enquadramento das Partes 5 e 6.

**Qualidade:**

- **Um arquivo PNG por cena,** nunca uma folha com várias cenas.
- **Formato:** vertical 9:16, no maior tamanho que o gerador permitir. O Claude Code amplia depois para 1440 × 2560.
- **Traço:** o cartoon 2D da série, igual ao das cenas da Parte 6, em `crimecarton-analise/episodio-06/originais/`: traço limpo e firme, contorno escuro, cores chapadas com sombra pintada suave e texturas sutis.
- **Mãos e rostos:** sem deformação. Cinco dedos, olhos alinhados e expressões fortes.

**A luz conta as horas:**

- **Cenas 3 a 8, no carro, perto das 7 h:** manhã clara, sol baixo e amarelado entrando pelas janelas do carro, ruas do bairro acordando.
- **Cenas 1, 2 e 10 a 21, na cozinha da Dona Célia, perto das 8 h:** a luz da manhã entrando pela janela, clara e morna, com o sol desenhando o quadriculado da cortina na parede.
- **Cena 9, a lembrança da infância:** fim de tarde dourado, com cores mais suaves e um pouco desbotadas, como uma lembrança.
- **Cena 22, a cadeira no ferro-velho:** a única lâmpada do barracão, fria e azulada, com o resto no escuro.
- **Cenas 23 a 25:** a mesma manhã das cenas da cozinha.

**Sem texto:**

- Nada de letras, números, logotipo ou marca d'água, nem em placas de carro, notas de dinheiro, rádio do carro, jornais ou muros.
- As notas de dinheiro são maços de cédulas lisas, em tons de verde e azul, presas com elásticos, sem número nem rosto impresso.

**Lugares:**

- **O carro do Ademir** é o sedã preto das Partes 5 e 6, que era do Toninho, por fora como em [`../episodio-05/originais/cena-07-portao-carro.png`](../episodio-05/originais/cena-07-portao-carro.png). Por dentro, como em [`../episodio-05/originais/cena-08-toninho-volante.png`](../episodio-05/originais/cena-08-toninho-volante.png): bancos escuros gastos, painel com luz âmbar fraca e um terço pendurado no retrovisor. O Ademir dirige; o Zinho vai sozinho no banco de trás.
- **A cozinha da Dona Célia** é a de [`../episodio-05/originais/cena-10-bolo.png`](../episodio-05/originais/cena-10-bolo.png) e [`../episodio-06/originais/cena-15-bolo-das-quatro.png`](../episodio-06/originais/cena-15-bolo-das-quatro.png): azulejos claros, prateleira com potes, plantas, toalha de crochê na mesa e fogão antigo. **Novos nesta parte:** uma geladeira velha e branca com ímãs e fotos presas, uma janela com cortina quadriculada, e uma porta que dá para um corredor curto e escuro, onde fica o quarto dos fundos.
- **A casa da Dona Célia,** por fora, é a de [`../episodio-03/cena-30-casa-da-mae.png`](../episodio-03/cena-30-casa-da-mae.png) e [`../episodio-06/originais/cena-18-opcao-falar.png`](../episodio-06/originais/cena-18-opcao-falar.png): muro baixo, portão de ferro e janela com cortina florida.
- **As duas bolsas** são as bolsas pretas de viagem de [`../episodio-04/originais/cena-17-parceiro.png`](../episodio-04/originais/cena-17-parceiro.png).
- **O barracão do Ferro-Velho São Jorge e a cadeira:** a cadeira de madeira velha debaixo da única lâmpada, como em [`../episodio-04/originais/cena-06-renato-amarrado.png`](../episodio-04/originais/cena-06-renato-amarrado.png) e [`../episodio-06/originais/cena-08-toninho-amarrado.png`](../episodio-06/originais/cena-08-toninho-amarrado.png).

**Personagens:**

- **Zinho:** como em [`../zinho-referencia-v3.png`](../zinho-referencia-v3.png) e nas cenas da Parte 6. Cabelo preto cacheado no topo, laterais em degradê e sem barba. Jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, camiseta preta. Uns 20 anos.
- **Ademir:** como em [`../episodio-06/originais/cena-05-socio-de-verdade.png`](../episodio-06/originais/cena-05-socio-de-verdade.png). Uns 60 anos, alto e corpulento, cabelo branco penteado para trás, bigode branco, jaqueta de couro preta, medalha de São Jorge e o anel grosso de ouro no dedo médio da mão direita. **O alicate** fica no bolso da jaqueta, com o cabo vermelho para fora.
- **Dona Célia, a mãe do Renato:** como em [`../episodio-05/originais/cena-10-bolo.png`](../episodio-05/originais/cena-10-bolo.png). Uns 60 anos, baixinha, cabelo cacheado grisalho preso no alto e avental florido.
- **O parceiro do assalto, irmão mais velho do Renato (personagem novo, o rosto aparece pela primeira vez):**
  - uns 35 anos, alto, de ombros largos, como o homem de costas de [`../episodio-06/originais/cena-15-bolo-das-quatro.png`](../episodio-06/originais/cena-15-bolo-das-quatro.png);
  - **parecido com o Renato** de [`../episodio-04/originais/cena-13-renato-aceita.png`](../episodio-04/originais/cena-13-renato-aceita.png), como um irmão mais velho: o mesmo tom de pele, o mesmo nariz e as mesmas sobrancelhas grossas. Cabelo crespo baixo, com risca de navalha na lateral, e barba bem feita, só no queixo;
  - em casa, à vontade: camiseta branca limpa, bermuda escura e **chinelo de dedo**. Um relógio dourado novo e grosso no pulso esquerdo, o único luxo, e o moletom escuro de capuz pendurado numa cadeira;
  - expressão de quem não sente culpa: meio sorriso de canto, olhar debochado e tranquilo.
- **Renato:** só aparece na cena 9, criança, e na cena 16, numa foto antiga. Nesta parte, ele não entra em nenhuma cena como adulto.

**Onde salvar:** em `crimecarton-analise/episodio-07/originais/`, com os nomes de cada lote.

## Entrega

1. Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido.
2. Fazer commit e push de todos os arquivos gerados na `codex/crimecarton` do repositório `Mazinho021/Projetos`, **nesta mesma conversa em que eles forem gerados**: depois das vozes e logo depois de cada cena pronta.
3. Responder com o link do commit e os créditos cobrados.

Depois, o Claude Code confere as vozes, passa a do Ademir pela voz do cobrador, amplia os desenhos e monta a Parte 7 nas duas versões.
