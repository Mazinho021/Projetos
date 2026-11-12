# Instruções para o Codex

Este repositório guarda a série “A parte que faltou”, do perfil Golpe Cartoon. Antes de qualquer tarefa:

1. **Regras:** ler o [`CLAUDE.md`](CLAUDE.md). As regras valem também para o Codex: composição das imagens, cenas, vozes e roteiros.
2. **Onde paramos:** ler a seção “Em andamento e pendências” do [`NOTAS.md`](NOTAS.md). O pedido em aberto para o Codex fica registrado ali, com o caminho do arquivo `pedido-codex-*.md`.
   - **Para economizar o limite de uso:** quando a mensagem já disser qual pedido ou lote executar, ler só este arquivo, o `pedido-codex-*.md` e o lote. Eles já trazem as regras que importam. Não ler o `CLAUDE.md` e o `NOTAS.md` inteiros nem reler arquivos grandes sem precisar.
3. **Branches:**
   - o estado mais novo do projeto está na `claude/ecstatic-brown-xb2qxd`, a branch padrão;
   - as entregas do Codex vão para a `codex/crimecarton`, depois de atualizá-la com a `claude/ecstatic-brown-xb2qxd`;
   - **se o pedido ou o lote disser outra branch,** como `codex/ep06-lote-01`, usar a dele. Isso deixa várias conversas trabalharem ao mesmo tempo sem uma atrapalhar o push da outra. Criar a branch a partir da `claude/ecstatic-brown-xb2qxd` e nunca usar `push --force`.
4. **Gerações pagas:** mostrar o custo e esperar o ok do criador antes de gerar imagens ou vozes.
5. **Commit e push:**
   - fazer na mesma conversa que gerou os arquivos, porque uma conversa nova não enxerga os arquivos de outra;
   - fazer logo depois de cada cena pronta, uma por vez, e de novo no fim. Assim nada se perde se o limite acabar no meio, como aconteceu com a cena 16 da Parte 4 em 05/11/2026.
6. **Arquivos que você não consegue baixar,** como os WAV do OpusClip: grave o nome e o link temporário de cada um em `links-temporarios.json`, na pasta da parte, faça commit e push e avise. O Claude baixa e salva os arquivos.
7. **Escopo:** não alterar arquivos fora do que o pedido manda. Os `narracao-*.txt` são o texto do roteiro: a transcrição vai só no `*-job.json`.
8. **Personagens iguais em todas as cenas:** antes de gerar cada desenho, passar ao gerador, como referência visual, a folha do personagem (como `crimecarton-analise/zinho-referencia-v3.png`) e as cenas boas que o pedido indicar. O rosto e o traço não podem mudar de uma cena para outra. Na Parte 7, o Zinho saiu mais realista e com outro rosto em três cenas, e elas foram refeitas.
