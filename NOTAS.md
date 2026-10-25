# Estado do projeto — Zinho

Atualizado em **25 de outubro de 2026**, depois da primeira prova completa do episódio 1. O backup do Codex foi retomado no Claude Code, onde foram feitos o alinhamento da narração, a timeline e a prova v1. Alguns documentos de planejamento ainda apresentam etapas já concluídas como futuras; para retomar, usar o estado registrado aqui e os arquivos existentes.

## Objetivo e decisões

Produzir uma série ficcional de suspense para TikTok, com foco em retenção, continuidade entre episódios e receita por visualizações. O objetivo do criador não é vender curso. A conta informada tem aproximadamente 19 mil seguidores; a elegibilidade e a receita do programa de monetização ainda não foram verificadas.

O título de trabalho é **A parte que faltou**. O protagonista é **Zinho**, participante de um assalto que encontra roupas velhas na mochila da divisão enquanto seu rosto aparece no noticiário. O episódio 1, **A mochila**, termina com o amigo à porta e a pergunta “Você deixa ele entrar?”. O arco proposto tem cinco episódios: A mochila, A dívida, A divisão, A proposta e O preço.

A referência visual atual é [`crimecarton-analise/zinho-referencia-v3.png`](crimecarton-analise/zinho-referencia-v3.png): personagem adulto, cabelo preto cacheado no topo e laterais em degradê, jaqueta azul-marinho com capuz vermelho e faixas brancas. A versão 4 com tranças foi descartada pelo usuário. As versões anteriores permanecem arquivadas. Manter o traço cartoon 2D, a identidade e o figurino da versão 3 nas próximas cenas.

## Pronto

- Roteiro de narração do episódio 1, com 170 palavras, em [`crimecarton-analise/narracao-ep01-zinho.txt`](crimecarton-analise/narracao-ep01-zinho.txt).
- Premissa, arco dos cinco episódios, identidade visual e planejamento de cenas em [`producao-zinho.md`](crimecarton-analise/producao-zinho.md) e [`plano-animacao-ep01.md`](crimecarton-analise/plano-animacao-ep01.md).
- Quatro imagens base verticais em `crimecarton-analise/episodio-01/`: `cena-01-base.png` (mochila), `cena-03-roupas.png` (descoberta), `cena-07-audio.png` (mensagem do amigo) e `cena-09-porta.png` (amigo do lado de fora).
- Narração concluída, com **71,28 segundos**, em `narracao-original.wav` e `narracao-zinho-ep01.mp3`. A geração utilizou os **2 créditos do OpusClip já autorizados e cobrados**. Reutilizar esses arquivos; não repetir a cobrança. Os registros estão em `narracao-job.json` e `estado-producao.json`.
- Renderizador local [`render_animatic.py`](crimecarton-analise/episodio-01/montagem/render_animatic.py), com câmera sobre ilustrações, enquadramentos recortados das imagens base, cartões de TV/celular, legendas ASS e saída vertical de 720 × 1280 a 25 fps por padrão.
- Alinhamento palavra por palavra da narração em [`alinhamento-narracao.json`](crimecarton-analise/episodio-01/montagem/alinhamento-narracao.json), gerado por [`alinhar_narracao.py`](crimecarton-analise/episodio-01/montagem/alinhar_narracao.py) com reconhecimento de fala local: as 170 palavras do roteiro têm início e fim medidos na voz, com as bordas ajustadas às pausas do áudio.
- Timeline final em [`montagem/timeline.json`](crimecarton-analise/episodio-01/montagem/timeline.json): **20 planos e 40 legendas** de 0 a 72,48 s, isto é, a locução de 71,28 s mais **1,2 s de pausa** no último plano depois da pergunta final. A foto enviada, o “Visualizado”, a comparação das fotografias e o cartão de áudio entram nas palavras correspondentes; o marcador do áudio percorre a barra durante a fala do amigo. As falas do amigo usam legenda âmbar em itálico.
- **Primeira prova completa:** [`piloto-zinho-ep01-v1.mp4`](crimecarton-analise/episodio-01/piloto-zinho-ep01-v1.mp4), com 72,48 s. As legendas e os cartões ficam acima da área inferior em que o TikTok sobrepõe legenda e nome de usuário. As pausas do áudio final coincidem com as da narração original; o volume integrado ficou em cerca de -17 LUFS.
- Testes curtos de montagem em `montagem/smoke.mp4` e `montagem/smoke-audio.mp4`. `render-report.json` e `timeline-used.json` agora correspondem à prova v1.

## Em andamento e pendências

- **A prova v1 aguarda revisão do criador**: ritmo, cortes, legendas, pausa final e escolha dos enquadramentos.
- O renderizador produz um **animatic**, isto é, uma prova de ritmo com ilustrações, câmera e elementos gráficos. Ainda não foi gerada animação corporal contínua de Zinho abrindo a mochila, retirando roupas ou caminhando.
- O retrato da TV e da comparação é um recorte da cena 1, com Zinho olhando para baixo. Uma imagem frontal dedicada deixaria mais clara a pista de que a foto enviada ao amigo é a mesma do jornal.
- O marcador “A PARTE QUE FALTOU” no topo fica sob as abas do TikTok. Decidir na versão final se ele sai ou muda de lugar.
- O amigo aparece na cena 9, mas ainda não tem ficha visual própria. Criá-la a partir dessa cena antes do episódio 2.
- Trilha, efeitos sonoros e mixagem final ainda precisam ser definidos e revisados. Os tempos de 75–85 segundos nos documentos iniciais eram alvos de planejamento; a sincronização deve seguir a locução real de 71,28 segundos.
- Houve estimativa de geração de um teste de vídeo de 8 segundos, mas essa geração não foi autorizada nem executada. Qualquer serviço pago adicional precisa de orçamento e autorização próprios.
- Não houve publicação do piloto no TikTok. O formato e as hipóteses de retenção ainda precisam ser testados; os materiais não comprovam monetização ou alcance.

## Como retomar

1. Revisar a prova v1 e anotar os ajustes de ritmo, cortes, legendas e final.
2. Aplicar os ajustes em `montagem/timeline.json`, usando os tempos de `alinhamento-narracao.json`, e renderizar a v2. Os campos da timeline estão no [`README da montagem`](crimecarton-analise/episodio-01/montagem/README.md).
3. Definir trilha, efeitos sonoros e mixagem.
4. Decidir quais planos precisam de movimento corporal e produzir esses planos mantendo a referência visual v3. Geração paga só com orçamento e autorização próprios.
5. Revisar a versão final, exportar com `--clean` e usar os resultados reais de retenção para orientar os episódios seguintes.

Requisitos locais do renderizador: **Python 3 com Pillow, FFmpeg com libass, FFprobe e fontes DejaVu Sans**. Os caminhos de fontes usados no script são os convencionais de Linux em `/usr/share/fonts/truetype/dejavu/`; adaptar se necessário em outro sistema. O alinhamento precisa também de faster-whisper, instalado à parte conforme o README da montagem.

Para renderizar, executar a partir da raiz do repositório:

```bash
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --audio crimecarton-analise/episodio-01/narracao-original.wav \
  --timeline crimecarton-analise/episodio-01/montagem/timeline.json \
  --output crimecarton-analise/episodio-01/piloto-zinho-ep01-v1.mp4 \
  --workers 2
```

Sem `--timeline`, o script usa uma distribuição provisória de cenas e não adiciona legendas. Esse modo serve para teste técnico, não confirma sincronização. `--prepare-only` prepara cartões e legendas sem codificar o vídeo. Para uma nova versão, trocar o nome do arquivo em `--output` (por exemplo, `-v2.mp4`).

## Escopo do backup e arquivos excluídos

As cinco pastas solicitadas são preservadas com sua estrutura: `crimecarton-analise/`, `generated_images/`, `library-files/`, `scratch/` e `shared/`.

O inventário anterior à inclusão deste documento e dos marcadores de diretório contém **60 arquivos**, somando **52.604.320 bytes**. **Nenhum arquivo ultrapassa 100 MB (100.000.000 bytes); nenhum foi excluído por tamanho.** Os arquivos temporários e os testes existentes fazem parte do backup solicitado.

Como o Git não armazena diretórios vazios, arquivos `.gitkeep` preservam `library-files/`, `scratch/` e `shared/downloads/`. Os diretórios internos de ferramentas e credenciais do ambiente não fazem parte das cinco pastas solicitadas.

Desde a prova v1, `montagem/work/` deixou de ser versionada, porque o renderizador a recria a cada execução. Os intermediários do backup original continuam no histórico do Git e na branch `codex/crimecarton`.
