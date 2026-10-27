# Pedido para o Codex — ilustrações e narração da Parte 2

Criado em 27/10/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. São 8 ilustrações e 2 áudios para a Parte 2, “A dívida”. O roteiro está em [`roteiro-ep02.txt`](roteiro-ep02.txt) e o plano de cenas em [`plano-ep02.md`](plano-ep02.md). Não alterar nenhum outro arquivo do projeto.

## Ilustrações

Regras para todas:

- Mesmo traço cartoon 2D das cenas da Parte 1, como [`../episodio-01/cena-01-base.png`](../episodio-01/cena-01-base.png) e [`../episodio-01/cena-09-porta.png`](../episodio-01/cena-09-porta.png): contorno escuro, cores chapadas, sombra suave, noite com luz quente.
- Zinho como em [`../zinho-referencia-v3.png`](../zinho-referencia-v3.png): cabelo preto cacheado no topo, laterais em degradê, sem barba, jaqueta azul-marinho com capuz vermelho e faixas brancas, camiseta preta.
- O amigo como em [`../amigo-referencia-v1.png`](../amigo-referencia-v1.png) e [`../ficha-amigo.md`](../ficha-amigo.md): jaqueta verde-oliva aberta, camiseta cinza-escuro, barba curta e bigode, cabelo crespo baixo.
- A casa é a da Parte 1: a sala com mesa de madeira, lâmpada pendurada e janela com luzes da cidade (cena 1), e a porta de madeira com cortina e janela para a rua (cena 9).
- Vertical 9:16, no tamanho das cenas da Parte 1 ou maior. Rostos e o que importa entre 12% e 75% da altura: em cima ficam as barras dos apps, embaixo as legendas. Sem texto, números, logotipo ou marca d'água; telas de celular e calendários ficam em branco, porque os textos entram na montagem.
- Salvar em `crimecarton-analise/episodio-02/` com os nomes abaixo.

1. **`cena-01-porta-aberta.png`:** por dentro, à noite, Zinho de costas, meio de lado, segura a porta entreaberta. Na soleira, o amigo, tenso, olha por cima do ombro para a rua escura, sob a luz quente da lâmpada da varanda.
2. **`cena-02-luz-apagada.png`:** a sala da Parte 1 quase no escuro. Junto à porta, o amigo gira a chave com uma mão e alcança o interruptor com a outra, com a lâmpada acabando de apagar. Zinho, no meio da sala, de braços cruzados e desconfiado, iluminado pela luz azulada da janela.
3. **`cena-03-versao.png`:** o amigo sentado à mesa, inclinado para a frente, mãos juntas, suando, explicando. Na mesa ainda está a mochila preta aberta com roupa velha, da Parte 1. Zinho em primeiro plano, de pé, visto por cima do ombro, de braços cruzados.
4. **`cena-04-foto-divisao.png`:** uma foto escondida de celular, tirada na noite da divisão. Visto de cima, há uma mesa coberta de pilhas de dinheiro e sacos pretos, com quatro mãos contando notas e nenhum rosto. Uma das mãos usa um anel grosso de ouro, pista para as próximas partes. Na parede ao fundo, um calendário de papel pendurado, em branco. Tem cara de foto com flash, levemente torta, com as bordas escuras.
5. **`cena-05-ligacao.png`:** close de Zinho com o celular no ouvido, na sala escura, com o rosto iluminado pela tela e os olhos fixos no amigo. O amigo aparece desfocado ao fundo, à mesa.
6. **`cena-06-celular-mesa.png`:** close da mesa de madeira. O celular do amigo está virado para cima, com a tela acesa e em branco, e a mão dele congelada a poucos centímetros. A roupa velha da mochila aparece na beira do quadro.
7. **`cena-07-carro.png`:** o ponto de vista de Zinho pela janela, atrás da cortina da cena 9 da Parte 1. Na rua, um carro escuro parado em frente ao portão, de farol apagado, com duas silhuetas dentro e um poste aceso na esquina. A mão de Zinho segura a cortina em primeiro plano.
8. **`cena-08-retrato-amigo.png`:** retrato do amigo do peito para cima, de frente, com culpa e medo, olhando levemente para o lado. Sala escura, com luz avermelhada de um lado e o rosto na metade de cima. É para o cartão final, “Qual é o nome dele?”.

## Narração

São dois áudios, e a vinheta inicial reaproveita o áudio da Parte 1; **não gerar de novo nenhuma narração da Parte 1**. A geração é paga e foi autorizada pelo criador em 27/10/2026; mostrar o custo antes de executar.

1. **Narrador:** gerar no OpusClip com os parâmetros de [`pedido-narracao-ep02.json`](pedido-narracao-ep02.json), com a mesma voz (Charon) e o mesmo estilo da Parte 1. São todas as falas do narrador, em ordem, uns 100 s. Salvar como `narracao-ep02-narrador.wav`, com o registro do job em `narracao-ep02-narrador-job.json`.
2. **Amigo:** gerar com os parâmetros de [`pedido-narracao-amigo-ep02.json`](pedido-narracao-amigo-ep02.json), numa voz masculina diferente da do narrador. A sugerida é Fenrir; se ela não existir ou soar cômica, usar uma das alternativas e anotar qual no job. São as 5 falas dele, em ordem, uns 15 s. Salvar como `narracao-ep02-amigo.wav`, com o registro em `narracao-ep02-amigo-job.json`.

Os dois áudios ficam em `crimecarton-analise/episodio-02/`. O Claude Code alinha cada um ao seu texto e intercala as falas na montagem.

## Entrega

Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido. Fazer commit e push dos arquivos na `codex/crimecarton` do repositório `Mazinho021/Projetos` e responder com a lista dos arquivos enviados e os créditos cobrados.
