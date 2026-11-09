# Pedido para o Codex — Parte 6, “A recompensa”

Criado em 09/11/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. O criador aprovou o roteiro, [`roteiro-ep06-contar.txt`](roteiro-ep06-contar.txt), em 09/11/2026 (“Ok”). O plano cena por cena está em [`plano-ep06.md`](plano-ep06.md).

O pedido tem duas partes:

- **3 gravações:** o narrador, o Ademir e o Toninho;
- **19 ilustrações,** em três lotes.

Não alterar nenhum outro arquivo do projeto. Fazer tudo numa tarefa só, nesta mesma conversa, sem abrir agentes em paralelo.

## Ordem

1. **As vozes,** com o custo mostrado antes. Commit e push logo depois delas.
2. **Os desenhos, lote por lote,** com commit e push **logo depois de cada cena pronta**, uma por vez:
   - [`LOTE-01-CENAS-01-A-07.md`](LOTE-01-CENAS-01-A-07.md): cenas 1 a 7, o cartaz no bairro e a madrugada no São Jorge;
   - [`LOTE-02-CENAS-08-A-14.md`](LOTE-02-CENAS-08-A-14.md): cenas 8 a 14, o Toninho na cadeira;
   - [`LOTE-03-CENAS-15-A-19.md`](LOTE-03-CENAS-15-A-19.md): cenas 15 a 19, a virada e as opções.
3. Se o limite de uso acabar no meio, o que já tiver push está salvo. Na volta, conferir na `codex/crimecarton` o que já existe e seguir da próxima cena.

## Vozes

Gerar as três gravações e salvar tudo em `crimecarton-analise/episodio-06/`.

1. **Narrador:** a voz Charon de sempre.
   - Gerar com [`pedido-narracao-ep06.json`](pedido-narracao-ep06.json) e salvar em `narracao-ep06-narrador.wav`, com o registro em `narracao-ep06-narrador-job.json`.
2. **Ademir:** Charon, no estilo do cobrador das Partes 3 a 5.
   - Gerar com [`pedido-narracao-ademir-ep06.json`](pedido-narracao-ademir-ep06.json) e salvar em `narracao-ep06-ademir.wav`, com o registro em `narracao-ep06-ademir-job.json`.
3. **Toninho:** a voz Orus, a mesma da Parte 5.
   - Gerar com [`pedido-narracao-toninho-ep06.json`](pedido-narracao-toninho-ep06.json) e salvar em `narracao-ep06-toninho.wav`, com o registro em `narracao-ep06-toninho-job.json`.
   - A outra fala do Toninho na parte é a gravação da Parte 5 tocando no celular: ela não deve ser gerada.

**Custo:** pelas Partes 2 a 5, deve custar uns **4 créditos**, mas o valor certo é o que o Codex mostrar antes de executar. A geração é paga e foi pedida pelo criador.

- O narrador, com uns 85 s, deve custar 2.
- O Ademir e o Toninho, com uns 15 e 8 s, devem custar 1 cada.

**Regras para as gravações:**

- **Não editar os áudios.**
- **Conferir cada gravação:** registrar no job a transcrição do faster-whisper `medium`, sem dar o texto como dica.
- **Se uma palavra sair trocada:** avisar na resposta, sem gerar de novo. O Claude Code confere e decide.
- **Se o serviço de voz disser que já existe um job com a mesma `idempotencyKey`,** usar esse resultado em vez de pagar de novo.
- **Se não der para baixar os WAV,** seguir o item 6 do [`AGENTS.md`](../../AGENTS.md): gravar os links em `links-temporarios.json`, nesta pasta, fazer commit e push e avisar.

## Regras para todas as ilustrações

**Composição.** O vídeo cobre o topo de cada imagem com um painel (“A SUA PARTE · SUSPEITA”) e uma etiqueta. A parte de baixo fica com as legendas, e a borda direita com os botões do TikTok. Então:

- **Os 25% de cima** ficam só com fundo calmo: céu, teto, parede ou escuro. Nada de rosto, cabeça, mão, celular, anel ou objeto importante.
- **Rostos, mãos e a ação principal** ficam **entre 30% e 60% da altura**, no meio da largura.
- **Os 20% de baixo** ficam só com chão ou fundo.
- **A borda direita** (os 20% da direita, entre 45% e 80% da altura) fica sem nada importante.

**Celulares (regra nova, de 08/11/2026).** Na Parte 5, os celulares saíram pequenos e inclinados, e as mensagens encaixadas neles ficaram tortas e difíceis de ler. Agora:

- o celular fica **de frente para a câmera, reto, sem inclinação**, como uma foto tirada de frente para a tela;
- **a tela é grande:** ocupa **pelo menos 40% da largura** do desenho;
- a tela fica acesa, lisa e em branco, numa cor clara uniforme, com os **quatro cantos visíveis**. A interface entra na montagem;
- dedos podem passar por cima da borda da tela, com o contorno escuro de sempre, mas sem cobrir o meio dela.

**Corpo inteiro e cenário.**

- Os personagens não podem sair cortados, fundidos ou atravessados pelo cenário.
- Cada parte do corpo que aparece tem que fazer sentido com o que está na frente e atrás dela: cadeira, mesa, portão, carro ou sucata.
- Quando o plano corta o corpo, o corte é da borda do quadro, como num plano médio, e nunca de um objeto do cenário.

**Variedade.**

- Cada imagem é um plano diferente, como num storyboard: aberto, close, detalhe, de cima, de baixo, outro lugar.
- Nenhuma pode parecer um recorte de outra nem repetir um enquadramento das Partes 4 e 5.

**Qualidade:**

- **Um arquivo PNG por cena,** nunca uma folha com várias cenas.
- **Formato:** vertical 9:16, no maior tamanho que o gerador permitir. O Claude Code amplia depois para 1440 × 2560.
- **Traço:** o cartoon 2D da série, igual ao das cenas da Parte 5, em `crimecarton-analise/episodio-05/originais/`: traço limpo e firme, contorno escuro, cores chapadas com sombra pintada suave e texturas sutis.
- **Mãos e rostos:** sem deformação. Cinco dedos, olhos alinhados e expressões fortes.

**A luz conta as horas:**

- **Cenas 2 a 6, perto das 5 h:** ainda noite, com a luz amarela da lâmpada e dos postes, o azul da lua e o chão molhado.
- **Cenas 1, 7 e 17 a 19, depois das 6 h:** amanhecer, com o céu azul-claro e uma faixa alaranjada no horizonte.
- **Cenas 8 a 14 e 16, dentro do barracão:** a lâmpada e, pela porta aberta, a luz azulada do amanhecer.
- **Cena 15, a cozinha da Dona Célia às 4 h:** a luz quente de casa da Parte 5.

**Sem texto:**

- Nada de letras, números, logotipo ou marca d'água, nem em placas de carro, cartazes ou muros.
- O cartaz da cena 1 fica liso e em branco: o texto e o rosto entram na montagem.

**Lugares:**

- **O Ferro-Velho São Jorge,** como nas Partes 4 e 5: chão de cimento rachado e molhado, montes de sucata e carcaças, a cobertura de zinco e o barracão com uma única lâmpada. Ver [`../episodio-04/originais/cena-05-chegada.png`](../episodio-04/originais/cena-05-chegada.png) e [`../episodio-05/originais/cena-03-socio.png`](../episodio-05/originais/cena-03-socio.png).
- **A cadeira:** a cadeira de madeira velha em que o Renato ficou amarrado, em [`../episodio-04/originais/cena-06-renato-amarrado.png`](../episodio-04/originais/cena-06-renato-amarrado.png), no mesmo lugar, debaixo da lâmpada.
- **O portão** é o portão de tela de [`../episodio-04/originais/cena-04-portao-aberto.png`](../episodio-04/originais/cena-04-portao-aberto.png) e [`../episodio-05/originais/cena-07-portao-carro.png`](../episodio-05/originais/cena-07-portao-carro.png).
- **O carro do Toninho** é o sedã preto de [`../episodio-05/originais/cena-07-portao-carro.png`](../episodio-05/originais/cena-07-portao-carro.png).
- **A cozinha da Dona Célia** é a de [`../episodio-05/originais/cena-10-bolo.png`](../episodio-05/originais/cena-10-bolo.png): azulejos claros, prateleira com potes, plantas, toalha de crochê na mesa e fogão antigo.
- **A casa da Dona Célia,** por fora, é a de [`../episodio-03/cena-30-casa-da-mae.png`](../episodio-03/cena-30-casa-da-mae.png).
- **As duas bolsas** são as bolsas pretas de viagem de [`../episodio-04/originais/cena-17-parceiro.png`](../episodio-04/originais/cena-17-parceiro.png).

**Personagens:**

- **Zinho:** como em [`../zinho-referencia-v3.png`](../zinho-referencia-v3.png) e nas cenas da Parte 5. Cabelo preto cacheado no topo, laterais em degradê e sem barba. Jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, camiseta preta.
- **Ademir:** como em [`../episodio-05/originais/cena-03-socio.png`](../episodio-05/originais/cena-03-socio.png). Uns 60 anos, alto e corpulento, cabelo branco penteado para trás, bigode branco, jaqueta de couro preta, medalha de São Jorge e o anel grosso de ouro no dedo médio da mão direita.
- **Toninho, o motorista:** como em [`../episodio-05/originais/cena-17-toninho-encara.png`](../episodio-05/originais/cena-17-toninho-encara.png). Uns 35 anos, magro, boné escuro, barba rala, jaqueta corta-vento cinza e calça jeans. Depois de amarrado, fica sem o boné, com um corte na sobrancelha.
- **Dona Célia, a mãe do Renato:** como em [`../episodio-05/originais/cena-10-bolo.png`](../episodio-05/originais/cena-10-bolo.png). Uns 60 anos, baixinha, cabelo cacheado grisalho preso no alto e avental florido.
- **O parceiro dos dez milhões:** só aparece de costas, na cena 15. Nunca mostrar o rosto.

**Onde salvar:** em `crimecarton-analise/episodio-06/originais/`, com os nomes de cada lote.

## Entrega

1. Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido.
2. Fazer commit e push de todos os arquivos gerados na `codex/crimecarton` do repositório `Mazinho021/Projetos`, **nesta mesma conversa em que eles forem gerados**: depois das vozes e logo depois de cada cena pronta.
3. Responder com o link do commit e os créditos cobrados.

Depois, o Claude Code confere as vozes, passa a do Ademir pela voz do cobrador, amplia os desenhos e monta a Parte 6 nas duas versões.
