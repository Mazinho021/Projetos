# Pedido para o Codex — ajustes da Parte 2

Criado em 28/10/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. São uma ilustração e um áudio, pedidos pelo criador depois de ver a Parte 2. Não alterar nenhum outro arquivo do projeto. Fazer tudo numa tarefa só, sem abrir agentes em paralelo.

## Ilustração

O criador quer que, quando a mensagem “Já tá com ele?” chega, apareça Zinho perguntando ao amigo o que é aquilo, em vez da mão do amigo parada sobre o celular. A narração continua: “Ele não responde a mensagem. Nem a você.”

- **`cena-09-pergunta.png`:** a sala escura da Parte 2, iluminada pela tela acesa do celular em cima da mesa e pela luz azulada da janela. Zinho em primeiro plano, à direita, de três quartos e virado para o amigo. Ele está espantado: olhos arregalados, sobrancelhas erguidas, a boca aberta no meio de uma pergunta e uma mão apontando para o celular. O amigo está sentado à mesa, à esquerda, com a mochila preta aberta ao lado. Ele olha para baixo, para o celular, com o maxilar travado, sem responder e evitando o olhar de Zinho. O celular fica na mesa, entre os dois, com a tela acesa e em branco.
- As mesmas regras das cenas da Parte 2: o traço de [`cena-03-versao.png`](cena-03-versao.png) e [`cena-05-ligacao.png`](cena-05-ligacao.png), Zinho como em [`../zinho-referencia-v3.png`](../zinho-referencia-v3.png) e o amigo como em [`../amigo-referencia-v1.png`](../amigo-referencia-v1.png).
- Vertical 9:16, no tamanho das outras cenas da Parte 2. Os dois rostos ficam entre 12% e 75% da altura.
- Sem texto, números, logotipo ou marca d'água; a tela do celular fica em branco.
- Salvar em `crimecarton-analise/episodio-02/`.

## Voz do amigo

O criador quer que o amigo tenha na Parte 2 a mesma voz da mensagem de áudio da Parte 1. Essa voz é a do narrador (Charon), transformada pelo Claude Code. Então as falas dele precisam ser gravadas de novo, com a voz Charon.

- Gerar no OpusClip com os parâmetros de [`pedido-narracao-amigo-charon-ep02.json`](pedido-narracao-amigo-charon-ep02.json). São as mesmas 5 falas de [`narracao-ep02-amigo.txt`](narracao-ep02-amigo.txt), com uns 16 s, interpretadas como o amigo, nervoso e com culpa.
- A geração é paga e foi autorizada pelo criador. Mostrar o custo antes de executar; deve custar 1 crédito. **Não gerar de novo nenhuma outra narração.**
- Salvar como `crimecarton-analise/episodio-02/narracao-ep02-amigo-charon.wav`, com o registro do job em `narracao-ep02-amigo-charon-job.json`.

## Entrega

Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido. Fazer commit e push dos três arquivos na `codex/crimecarton` do repositório `Mazinho021/Projetos` e responder com a lista dos arquivos enviados e os créditos cobrados.
