# Pedido para o Codex — Parte 5, “A divisão”

Criado em 07/11/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. O criador aprovou o roteiro, [`roteiro-ep05-cancelar.txt`](roteiro-ep05-cancelar.txt), em 07/11/2026 (“Vamos lá”). O plano cena por cena está em [`plano-ep05.md`](plano-ep05.md).

O pedido tem duas partes:

- **4 gravações:** o narrador, o Ademir, o Renato e o Toninho;
- **19 ilustrações,** em três lotes.

Não alterar nenhum outro arquivo do projeto. Fazer tudo numa tarefa só, sem abrir agentes em paralelo.

## Ordem

1. **As vozes,** com o custo mostrado antes. Commit e push logo depois delas.
2. **Os desenhos, lote por lote,** com commit e push **logo depois de cada cena pronta**, uma por vez:
   - [`LOTE-01-CENAS-01-A-07.md`](LOTE-01-CENAS-01-A-07.md): cenas 1 a 7, no ferro-velho;
   - [`LOTE-02-CENAS-08-A-13.md`](LOTE-02-CENAS-08-A-13.md): cenas 8 a 13, no carro e na cozinha da Dona Célia;
   - [`LOTE-03-CENAS-14-A-19.md`](LOTE-03-CENAS-14-A-19.md): cenas 14 a 19, a confissão e as opções.
3. Se o limite de uso acabar no meio, o que já tiver push está salvo. Na volta, conferir na `codex/crimecarton` o que já existe e seguir da próxima cena.

## Vozes

Gerar as quatro gravações e salvar tudo em `crimecarton-analise/episodio-05/`.

1. **Narrador:** a voz Charon de sempre.
   - Gerar com [`pedido-narracao-ep05.json`](pedido-narracao-ep05.json) e salvar em `narracao-ep05-narrador.wav`, com o registro em `narracao-ep05-narrador-job.json`.
2. **Ademir:** Charon, no estilo do cobrador das Partes 3 e 4.
   - Gerar com [`pedido-narracao-ademir-ep05.json`](pedido-narracao-ademir-ep05.json) e salvar em `narracao-ep05-ademir.wav`, com o registro em `narracao-ep05-ademir-job.json`.
3. **Renato:** a voz Algenib, escolhida pelo criador.
   - Gerar com [`pedido-narracao-renato-ep05.json`](pedido-narracao-renato-ep05.json) e salvar em `narracao-ep05-renato.wav`, com o registro em `narracao-ep05-renato-job.json`.
4. **Toninho:** a voz Orus, nova na série.
   - Gerar com [`pedido-narracao-toninho-ep05.json`](pedido-narracao-toninho-ep05.json) e salvar em `narracao-ep05-toninho.wav`, com o registro em `narracao-ep05-toninho-job.json`.

**Custo:** pelas Partes 2 a 4, deve custar uns **5 créditos**, mas o valor certo é o que o Codex mostrar antes de executar. A geração é paga e foi pedida pelo criador.

- O narrador, com uns 80 s, deve custar 2.
- O Ademir, o Renato e o Toninho, com uns 10, 6 e 30 s, devem custar 1 cada.

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

**Corpo inteiro e cenário.**

- Os personagens não podem sair cortados, fundidos ou atravessados pelo cenário.
- Cada parte do corpo que aparece tem que fazer sentido com o que está na frente e atrás dela: mesa, banco do carro, volante, portão ou sucata.
- Quando o plano corta o corpo, o corte é da borda do quadro, como num plano médio, e nunca de um objeto do cenário.

**Variedade.**

- Cada imagem é um plano diferente, como num storyboard: aberto, close, detalhe, de cima, de baixo, outro lugar.
- Nenhuma pode parecer um recorte de outra nem repetir um enquadramento da Parte 4.

**Qualidade:**

- **Um arquivo PNG por cena,** nunca uma folha com várias cenas.
- **Formato:** vertical 9:16, no maior tamanho que o gerador permitir. O Claude Code amplia depois para 1440 × 2560.
- **Traço:** o cartoon 2D da série, igual ao das cenas da Parte 4, em `crimecarton-analise/episodio-04/originais/`: traço limpo e firme, contorno escuro, cores chapadas com sombra pintada suave e texturas sutis.
- **Luz:** noturna, de cinema, com a luz amarela da lâmpada e dos postes, a luz azulada da lua e reflexos no chão molhado. A cozinha da Dona Célia é a exceção: luz quente de casa.
- **Mãos e rostos:** sem deformação. Cinco dedos, olhos alinhados e expressões fortes.

**Sem texto:**

- Nada de letras, números, logotipo ou marca d'água, nem em placas de carro, no posto ou no rádio do carro.
- **As telas de celular** ficam acesas, lisas e em branco, numa cor clara uniforme, com os quatro cantos visíveis, porque a interface entra na montagem. Dedos podem passar por cima da tela, com o contorno escuro de sempre.

**Lugares:**

- **O Ferro-Velho São Jorge,** como na Parte 4: chão de cimento rachado e molhado, montes de sucata e carcaças, a cobertura de zinco com uma única lâmpada e a lua. Ver [`../episodio-04/originais/cena-05-chegada.png`](../episodio-04/originais/cena-05-chegada.png) e [`../episodio-04/originais/cena-21-opcao-cancelar.png`](../episodio-04/originais/cena-21-opcao-cancelar.png).
- **O barracão e a mesa da divisão:** a mesa de madeira de [`../episodio-04/originais/cena-09-mesa-da-foto.png`](../episodio-04/originais/cena-09-mesa-da-foto.png) e da foto da divisão, [`../episodio-02/cena-04-foto-divisao.png`](../episodio-02/cena-04-foto-divisao.png).
- **O portão** é o portão de tela de [`../episodio-04/originais/cena-04-portao-aberto.png`](../episodio-04/originais/cena-04-portao-aberto.png).
- **O carro do Toninho** é o sedã preto de [`../episodio-04/originais/cena-21-opcao-cancelar.png`](../episodio-04/originais/cena-21-opcao-cancelar.png) e [`../episodio-03/cena-30-casa-da-mae.png`](../episodio-03/cena-30-casa-da-mae.png). Por dentro: bancos escuros gastos, painel com luz âmbar fraca e um terço pendurado no retrovisor.
- **A cozinha da Dona Célia** é a de [`../episodio-03/cena-11-almoco.png`](../episodio-03/cena-11-almoco.png), anos depois: azulejos claros, prateleira com potes, plantas, toalha de crochê na mesa e fogão antigo.
- **O posto fechado:** um posto de gasolina pequeno, de bairro, fechado de madrugada, com as bombas cobertas e uma única luz fluorescente piscando.

**Personagens:**

- **Zinho:** como em [`../zinho-referencia-v3.png`](../zinho-referencia-v3.png) e nas cenas da Parte 4. Cabelo preto cacheado no topo, laterais em degradê e sem barba. Jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, camiseta preta.
- **Ademir:** como em [`../episodio-04/originais/cena-12-cafe.png`](../episodio-04/originais/cena-12-cafe.png) e [`../episodio-04/originais/cena-16-ademir-inclina.png`](../episodio-04/originais/cena-16-ademir-inclina.png). Uns 60 anos, alto e corpulento, cabelo branco penteado para trás, bigode branco, jaqueta de couro preta, medalha de São Jorge e o anel grosso de ouro no dedo médio da mão direita.
- **Toninho, o motorista:** como em [`../episodio-04/originais/cena-15-motorista.png`](../episodio-04/originais/cena-15-motorista.png). Uns 35 anos, magro, boné escuro, barba rala, jaqueta corta-vento cinza e calça jeans.
- **Renato:** como em [`../episodio-04/originais/cena-13-renato-aceita.png`](../episodio-04/originais/cena-13-renato-aceita.png). Jaqueta verde-oliva, camiseta cinza-escuro, barba curta, lábio cortado e pulsos vermelhos da corda.
- **Dona Célia, a mãe do Renato:** a mãe de [`../episodio-03/cena-11-almoco.png`](../episodio-03/cena-11-almoco.png), uns 15 anos mais velha. Uns 60 anos, baixinha, cabelo cacheado grisalho preso no alto, avental florido, rosto cansado e carinhoso.

**Onde salvar:** em `crimecarton-analise/episodio-05/originais/`, com os nomes de cada lote.

## Entrega

1. Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido.
2. Fazer commit e push de todos os arquivos gerados na `codex/crimecarton` do repositório `Mazinho021/Projetos`, **nesta mesma conversa em que eles forem gerados**: depois das vozes e logo depois de cada cena pronta.
3. Responder com o link do commit e os créditos cobrados.

Depois, o Claude Code confere as vozes, passa a do Ademir pela voz do cobrador, amplia os desenhos e monta a Parte 5 nas duas versões.
