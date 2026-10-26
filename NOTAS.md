# Estado do projeto — Zinho

Atualizado em **26 de outubro de 2026**, depois da prova v2 do episódio 1, refeita no estilo do vídeo de referência da série. O backup do Codex foi retomado no Claude Code, onde foram feitos o alinhamento da narração, as timelines e as provas v1 e v2. Alguns documentos de planejamento ainda apresentam etapas já concluídas como futuras; para retomar, usar o estado registrado aqui e os arquivos existentes.

## Objetivo e decisões

Produzir uma série ficcional de suspense para TikTok, com foco em retenção, continuidade entre episódios e receita por visualizações. O objetivo do criador não é vender curso. A conta informada tem aproximadamente 19 mil seguidores; a elegibilidade e a receita do programa de monetização ainda não foram verificadas.

**Base da série:** o criador definiu o vídeo de referência “Design sem nome.mp4” como modelo de frases animadas, tema, história e acabamento. A análise está em [`guia-de-estilo-referencia.md`](crimecarton-analise/guia-de-estilo-referencia.md). A referência acompanha o parceiro que ficou com os dez milhões; o episódio 1 de Zinho é o outro lado do mesmo assalto e abre com a mesma frase.

**Formato definido pelo criador:** cenas ilustradas estáticas em sequência, com movimento de câmera, cartões de TV/celular, gráficos animados e narração. Não haverá animação corporal nem 3D. A publicação está prevista no **TikTok** e no **Instagram Reels**, com o mesmo vídeo vertical. O vídeo não leva selo da série no topo, que fica coberto pelas interfaces das duas redes: o nome da série e o episódio vão no texto do post.

O título de trabalho é **A parte que faltou**. O protagonista é **Zinho**, participante de um assalto que encontra roupas velhas na mochila da divisão enquanto seu rosto aparece no noticiário. O episódio 1, **A mochila**, termina com o amigo à porta e a pergunta “Você deixa ele entrar?”. O arco proposto tem cinco episódios: A mochila, A dívida, A divisão, A proposta e O preço.

A referência visual atual é [`crimecarton-analise/zinho-referencia-v3.png`](crimecarton-analise/zinho-referencia-v3.png): personagem adulto, cabelo preto cacheado no topo e laterais em degradê, jaqueta azul-marinho com capuz vermelho e faixas brancas. A versão 4 com tranças foi descartada pelo usuário. As versões anteriores permanecem arquivadas. Manter o traço cartoon 2D, a identidade e o figurino da versão 3 nas próximas cenas.

## Pronto

- Roteiro de narração do episódio 1, com 170 palavras, em [`crimecarton-analise/narracao-ep01-zinho.txt`](crimecarton-analise/narracao-ep01-zinho.txt).
- Premissa, arco dos cinco episódios, identidade visual e planejamento de cenas em [`producao-zinho.md`](crimecarton-analise/producao-zinho.md) e [`plano-animacao-ep01.md`](crimecarton-analise/plano-animacao-ep01.md).
- Quatro imagens base verticais em `crimecarton-analise/episodio-01/`: `cena-01-base.png` (mochila), `cena-03-roupas.png` (descoberta), `cena-07-audio.png` (mensagem do amigo) e `cena-09-porta.png` (amigo do lado de fora).
- Narração concluída, com **71,28 segundos**, em `narracao-original.wav` e `narracao-zinho-ep01.mp3`. A geração utilizou os **2 créditos do OpusClip já autorizados e cobrados**. Reutilizar esses arquivos; não repetir a cobrança. Os registros estão em `narracao-job.json` e `estado-producao.json`.
- Renderizador local [`render_animatic.py`](crimecarton-analise/episodio-01/montagem/render_animatic.py), com câmera sobre ilustrações, enquadramentos recortados das imagens base, cartões de TV/celular e saída vertical de 720 × 1280 a 25 fps por padrão. A camada de gráficos animados está em [`graficos.py`](crimecarton-analise/episodio-01/montagem/graficos.py), com a fonte Poppins em [`fontes/`](crimecarton-analise/fontes/) (licença OFL).
- Alinhamento palavra por palavra da narração em [`alinhamento-narracao.json`](crimecarton-analise/episodio-01/montagem/alinhamento-narracao.json), gerado por [`alinhar_narracao.py`](crimecarton-analise/episodio-01/montagem/alinhar_narracao.py) com reconhecimento de fala local: as 170 palavras do roteiro têm início e fim medidos na voz, com as bordas ajustadas às pausas do áudio.
- Timeline atual em [`montagem/timeline.json`](crimecarton-analise/episodio-01/montagem/timeline.json): **20 planos e 22 elementos gráficos** de 0 a 74,28 s, isto é, a locução de 71,28 s mais **3 s de final** com o pedido de comentário. Como na referência, não há legenda corrida: as frases-chave entram linha por linha na palavra falada. O painel “A SUA PARTE” passa de “R$ ?” a “R$ 0” em “Nenhuma nota” e as cinco estrelas de suspeita enchem em “suspeito identificado”. As etiquetas marcam PISTA 1 · A MOCHILA, PISTA 2 · O SILÊNCIO, PISTA 3 · A FOTO e PISTA 4 · O ÁUDIO. Entram ainda a lista “BOLSOS → VAZIOS”, o carimbo “A MESMA FOTO”, “TOC! TOC!”, “VENDEU / SEU NOME.” e o final “VOCÊ DEIXA / ELE ENTRAR?” com “ABRIR / NÃO ABRIR” e “PARTE 2”.
- **Prova v2, no estilo da referência:** [`piloto-zinho-ep01-v2.mp4`](crimecarton-analise/episodio-01/piloto-zinho-ep01-v2.mp4), com 74,28 s. As pausas do áudio final coincidem com as da narração original.
- Prova v1, anterior à referência, com legendas corridas: [`piloto-zinho-ep01-v1.mp4`](crimecarton-analise/episodio-01/piloto-zinho-ep01-v1.mp4). A timeline dela está no histórico do Git.
- Testes curtos de montagem em `montagem/smoke.mp4` e `montagem/smoke-audio.mp4`. `render-report.json` e `timeline-used.json` correspondem à prova v2.

## Em andamento e pendências

- **A prova v2 aguarda revisão do criador**: ritmo, textos na tela, painel, etiquetas e final.
- **Retrato frontal do Zinho**, pedido pelo criador para a TV e a comparação: hoje é um recorte da cena 1, com Zinho olhando para baixo. A nova imagem deve ser gerada onde houver gerador de imagens (o Claude Code desta sessão não tem) e salva como `crimecarton-analise/episodio-01/retrato-zinho.png`. O renderizador passa a usá-la automaticamente quando o arquivo existe.
- O final promete, como a referência, que “a maioria decide o próximo passo”. Se a maioria comentar NÃO ABRIR, o episódio 2 precisa seguir esse caminho; o arco em `producao-zinho.md` supõe que o amigo entra.
- O final é só visual: a narração termina na pergunta. Narrar o pedido de comentário, como na referência, exigiria nova geração de voz, que é paga e precisa de autorização.
- O amigo aparece na cena 9, mas ainda não tem ficha visual própria. Criá-la a partir dessa cena antes do episódio 2.
- A referência não usa trilha de fundo. Efeitos sonoros (celular, batidas na porta) continuam opcionais e não foram feitos.
- O teste de vídeo de 8 segundos estimado no Codex não será feito, porque o formato não usa animação. Qualquer serviço pago adicional precisa de orçamento e autorização próprios.
- Não houve publicação do piloto no TikTok. O formato e as hipóteses de retenção ainda precisam ser testados; os materiais não comprovam monetização ou alcance.

## Como retomar

1. Revisar a prova v2 e anotar os ajustes.
2. Gerar o retrato frontal `retrato-zinho.png`, aplicar os ajustes em `montagem/timeline.json` (usando os tempos de `alinhamento-narracao.json`) e renderizar a v3. Os campos da timeline e dos gráficos estão no [`README da montagem`](crimecarton-analise/episodio-01/montagem/README.md); o estilo, no [guia da referência](crimecarton-analise/guia-de-estilo-referencia.md).
3. Decidir se entram efeitos sonoros.
4. Revisar a versão final, publicar com o nome da série e o episódio no texto do post e usar os resultados reais de retenção no TikTok e nos Reels para orientar os episódios seguintes.

Requisitos locais do renderizador: **Python 3 com Pillow, FFmpeg com libass e FFprobe**; a fonte Poppins já está no repositório. O alinhamento precisa também de faster-whisper, instalado à parte conforme o README da montagem.

Para renderizar, executar a partir da raiz do repositório:

```bash
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --audio crimecarton-analise/episodio-01/narracao-original.wav \
  --timeline crimecarton-analise/episodio-01/montagem/timeline.json \
  --output crimecarton-analise/episodio-01/piloto-zinho-ep01-v3.mp4 \
  --workers 2
```

Sem `--timeline`, o script usa uma distribuição provisória de cenas, sem gráficos nem legendas. Esse modo serve para teste técnico, não confirma sincronização. `--prepare-only` prepara fundos e cartões sem codificar o vídeo. Para cada nova versão, trocar o nome do arquivo em `--output`.

## Escopo do backup e arquivos excluídos

As cinco pastas solicitadas são preservadas com sua estrutura: `crimecarton-analise/`, `generated_images/`, `library-files/`, `scratch/` e `shared/`.

O inventário anterior à inclusão deste documento e dos marcadores de diretório contém **60 arquivos**, somando **52.604.320 bytes**. **Nenhum arquivo ultrapassa 100 MB (100.000.000 bytes); nenhum foi excluído por tamanho.** Os arquivos temporários e os testes existentes fazem parte do backup solicitado.

Como o Git não armazena diretórios vazios, arquivos `.gitkeep` preservam `library-files/`, `scratch/` e `shared/downloads/`. Os diretórios internos de ferramentas e credenciais do ambiente não fazem parte das cinco pastas solicitadas.

Desde a prova v1, `montagem/work/` deixou de ser versionada, porque o renderizador a recria a cada execução. Os intermediários do backup original continuam no histórico do Git e na branch `codex/crimecarton`.
