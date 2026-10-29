# Pedido para o Codex — a fala das 30 vagas no vídeo “Vire aliado”

Criado em 29/10/2026 no Claude Code, que não tem a geração de voz do OpusClip. O criador aumentou as vagas da Parte 3 de 10 para 30 e quer que o narrador fale isso no vídeo que chama aliados ([`README.md`](README.md)). A narração atual, [`narracao-chamada.wav`](narracao-chamada.wav), diz “São só dez vagas”, e por isso essa fala está cortada do vídeo. É 1 áudio. Não alterar nenhum outro arquivo do projeto.

## Narração

Gerar no OpusClip com os parâmetros de [`pedido-narracao-trinta-vagas.json`](pedido-narracao-trinta-vagas.json): a mesma voz (Charon) e o mesmo modelo de [`narracao-chamada-job.json`](narracao-chamada-job.json). O texto tem duas falas. A primeira já está no vídeo e só serve para a segunda sair no mesmo tom: o vídeo usa apenas a segunda, “São até trinta vagas, até sexta, às nove da noite.”. São uns 6 s. Se o campo `style` passar do limite do OpusClip, encurtar sem mudar o sentido e anotar no job.

Salvar como `narracao-trinta-vagas.wav`, com o registro do job em `narracao-trinta-vagas-job.json`, nesta pasta (`crimecarton-analise/chamada-aliado/`).

## Entrega

Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido. Fazer commit e push dos arquivos na `codex/crimecarton` do repositório `Mazinho021/Projetos`. Responder com a lista dos arquivos enviados e os créditos cobrados. A geração é paga e foi pedida pelo criador em 29/10/2026; mostrar o custo antes de executar.

Depois, o Claude Code põe a fala nova no vídeo, no lugar da pausa das vagas, e confere o áudio.
