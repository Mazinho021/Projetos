# Pedido para o Codex — as vozes do roteiro novo da Parte 3

Criado em 31/10/2026 no Claude Code, que não tem a geração de voz do OpusClip. Depois de ver a prévia, o criador pediu um roteiro novo para a Parte 3, “A noite”, em [`roteiro-ep03.txt`](roteiro-ep03.txt). As 13 ilustrações continuam as mesmas, então **não gerar nenhuma imagem**. São 2 áudios, que substituem os gravados em 30/10. Não alterar nenhum outro arquivo do projeto. Fazer tudo numa tarefa só, sem abrir agentes em paralelo.

## Narração

A geração é paga e foi pedida pelo criador. Mostrar o custo antes de executar: a narração deve custar uns 2 créditos e as falas de Renato, 1. Não gerar de novo nenhuma narração das Partes 1 e 2.

1. **Narrador:** gerar no OpusClip com os parâmetros de [`pedido-narracao-ep03.json`](pedido-narracao-ep03.json), com a voz Charon e o mesmo estilo da narração da Parte 2. São todas as falas do narrador, em ordem e já com o pedido de comentário do fim, uns 125 s. Salvar por cima de `narracao-ep03-narrador.wav`, com o registro do job por cima de `narracao-ep03-narrador-job.json`.
2. **Renato:** gerar com os parâmetros de [`pedido-narracao-renato-ep03.json`](pedido-narracao-renato-ep03.json), também com a voz Charon, interpretando Renato. São as 5 falas dele, em ordem, uns 20 s. Salvar por cima de `narracao-ep03-renato.wav`, com o registro por cima de `narracao-ep03-renato-job.json`.

Os dois áudios ficam em `crimecarton-analise/episodio-03/`. Depois, o Claude Code alinha cada um ao seu texto e refaz a montagem.

## Entrega

Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido. Fazer commit e push dos 4 arquivos na `codex/crimecarton` do repositório `Mazinho021/Projetos`, **nesta mesma conversa em que os áudios forem gerados**, e responder com o link do commit e os créditos cobrados.
