# Estado do projeto — Zinho

Atualizado em **25 de outubro de 2026**. Este documento descreve o estado dos arquivos no momento do backup. Alguns documentos de planejamento ainda apresentam etapas já concluídas como futuras; para retomar, usar o estado registrado aqui e os arquivos existentes.

## Objetivo e decisões

Produzir uma série ficcional de suspense para TikTok, com foco em retenção, continuidade entre episódios e receita por visualizações. O objetivo do criador não é vender curso. A conta informada tem aproximadamente 19 mil seguidores; a elegibilidade e a receita do programa de monetização ainda não foram verificadas.

O título de trabalho é **A parte que faltou**. O protagonista é **Zinho**, participante de um assalto que encontra roupas velhas na mochila da divisão enquanto seu rosto aparece no noticiário. O episódio 1, **A mochila**, termina com o amigo à porta e a pergunta “Você deixa ele entrar?”. O arco proposto tem cinco episódios: A mochila, A dívida, A divisão, A proposta e O preço.

A referência visual atual é [`crimecarton-analise/zinho-referencia-v3.png`](crimecarton-analise/zinho-referencia-v3.png): personagem adulto, cabelo preto cacheado no topo e laterais em degradê, jaqueta azul-marinho com capuz vermelho e faixas brancas. A versão 4 com tranças foi descartada pelo usuário. As versões anteriores permanecem arquivadas. Manter o traço cartoon 2D, a identidade e o figurino da versão 3 nas próximas cenas.

## Pronto

- Roteiro de narração do episódio 1, com 170 palavras, em [`crimecarton-analise/narracao-ep01-zinho.txt`](crimecarton-analise/narracao-ep01-zinho.txt).
- Premissa, arco dos cinco episódios, identidade visual e planejamento de cenas em [`producao-zinho.md`](crimecarton-analise/producao-zinho.md) e [`plano-animacao-ep01.md`](crimecarton-analise/plano-animacao-ep01.md).
- Quatro imagens base verticais em `crimecarton-analise/episodio-01/`: `cena-01-base.png` (mochila), `cena-03-roupas.png` (descoberta), `cena-07-audio.png` (mensagem do amigo) e `cena-09-porta.png` (amigo do lado de fora).
- Narração concluída, com **71,28 segundos**, em `narracao-original.wav` e `narracao-zinho-ep01.mp3`. A geração utilizou os **2 créditos do OpusClip já autorizados e cobrados**. Reutilizar esses arquivos; não repetir a cobrança. Os registros estão em `narracao-job.json` e `estado-producao.json`.
- Renderizador local [`render_animatic.py`](crimecarton-analise/episodio-01/montagem/render_animatic.py), com câmera sobre ilustrações, cartões de TV/celular, legendas ASS e saída vertical de 720 × 1280 a 25 fps por padrão.
- Testes curtos de montagem em `montagem/smoke.mp4` e `montagem/smoke-audio.mp4`. O relatório atual corresponde ao teste de áudio de **2 segundos**, com uma cena e uma legenda. Os intermediários em `montagem/work/` também estão preservados.

## Em andamento e pendências

- A montagem do episódio completo estava em andamento. **Ainda não há um MP4 final do piloto.**
- O alinhamento da narração ao roteiro e às legendas ainda não foi concluído. Não há uma `timeline.json` final cobrindo os 71,28 segundos.
- `montagem/timeline-used.json` contém a timeline do teste curto de 2 segundos; não usar esse arquivo como montagem do episódio inteiro.
- O renderizador produz um **animatic**, isto é, uma prova de ritmo com ilustrações, câmera e elementos gráficos. Ainda não foi gerada animação corporal contínua de Zinho abrindo a mochila, retirando roupas ou caminhando.
- Trilha, efeitos sonoros e mixagem final ainda precisam ser definidos e revisados. Os tempos de 75–85 segundos nos documentos iniciais eram alvos de planejamento; a sincronização deve seguir a locução real de 71,28 segundos.
- Houve estimativa de geração de um teste de vídeo de 8 segundos, mas essa geração não foi autorizada nem executada. Qualquer serviço pago adicional precisa de orçamento e autorização próprios.
- Não houve publicação do piloto no TikTok. O formato e as hipóteses de retenção ainda precisam ser testados; os materiais não comprovam monetização ou alcance.

## Como retomar

1. Alinhar o roteiro à narração pronta, revisar pausas e criar legendas curtas sincronizadas.
2. Criar `crimecarton-analise/episodio-01/montagem/timeline.json`, cobrindo de 0 a 71,28 segundos, sem lacunas ou sobreposições. Usar os tipos de cena `art`, `tv`, `chat`, `comparison` e `audio`. A estrutura está no [`README da montagem`](crimecarton-analise/episodio-01/montagem/README.md).
3. Renderizar a primeira prova completa, revisar cortes, revelações, legibilidade das telas e pergunta final. Conferir especialmente se a fotografia e o áudio aparecem no momento correto da fala.
4. Ajustar som e ritmo; depois decidir quais planos precisam de movimento corporal e produzir esses planos mantendo a referência visual v3.
5. Revisar a versão final antes da publicação e usar os resultados reais de retenção para orientar os episódios seguintes.

Requisitos locais do renderizador: **Python 3 com Pillow, FFmpeg com libass, FFprobe e fontes DejaVu Sans**. Os caminhos de fontes usados no script são os convencionais de Linux em `/usr/share/fonts/truetype/dejavu/`; adaptar se necessário em outro sistema.

Depois de criar a timeline final, executar a partir da raiz do repositório:

```bash
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --audio crimecarton-analise/episodio-01/narracao-original.wav \
  --timeline crimecarton-analise/episodio-01/montagem/timeline.json \
  --output crimecarton-analise/episodio-01/piloto-zinho-ep01-v1.mp4 \
  --workers 2
```

Sem `--timeline`, o script usa uma distribuição provisória de cenas e não adiciona legendas. Esse modo serve para teste técnico, não confirma sincronização. `--prepare-only` prepara cartões e legendas sem codificar o vídeo. A documentação e o código podem ser continuados por outro editor ou agente, inclusive Claude Code quando disponível; não houve execução do Claude Code neste ambiente.

## Escopo do backup e arquivos excluídos

As cinco pastas solicitadas são preservadas com sua estrutura: `crimecarton-analise/`, `generated_images/`, `library-files/`, `scratch/` e `shared/`.

O inventário anterior à inclusão deste documento e dos marcadores de diretório contém **60 arquivos**, somando **52.604.320 bytes**. **Nenhum arquivo ultrapassa 100 MB (100.000.000 bytes); nenhum foi excluído por tamanho.** Os arquivos temporários e os testes existentes fazem parte do backup solicitado.

Como o Git não armazena diretórios vazios, arquivos `.gitkeep` preservam `library-files/`, `scratch/` e `shared/downloads/`. Os diretórios internos de ferramentas e credenciais do ambiente não fazem parte das cinco pastas solicitadas.
