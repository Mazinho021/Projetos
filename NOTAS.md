# Estado do projeto — Zinho

Atualizado em **26 de outubro de 2026**, depois da prova v4 do episódio 1, no estilo do vídeo de referência da série. O backup do Codex foi retomado no Claude Code, onde foram feitos o alinhamento da narração, as timelines, os efeitos sonoros e as provas v1 a v4; o Codex gerou o retrato de Zinho, a folha do amigo e a narração do pedido de comentário. Alguns documentos de planejamento ainda apresentam etapas já concluídas como futuras; para retomar, usar o estado registrado aqui e os arquivos existentes.

## Objetivo e decisões

Produzir uma série ficcional de suspense para TikTok, com foco em retenção, continuidade entre episódios e receita por visualizações. O objetivo do criador não é vender curso. A conta informada tem aproximadamente 19 mil seguidores; a elegibilidade e a receita do programa de monetização ainda não foram verificadas.

**Base da série:** o criador definiu o vídeo de referência “Design sem nome.mp4”, das histórias do perfil [@crimecarton](https://www.instagram.com/crimecarton/) no Instagram, como modelo de frases animadas, tema, história e acabamento. A análise está em [`guia-de-estilo-referencia.md`](crimecarton-analise/guia-de-estilo-referencia.md). A referência acompanha o parceiro que ficou com os dez milhões; o episódio 1 de Zinho é o outro lado do mesmo assalto e abre com a mesma frase.

**Formato definido pelo criador:** cenas ilustradas estáticas em sequência, com movimento de câmera, cartões de TV/celular, gráficos animados e narração. Não haverá animação corporal nem 3D. A publicação está prevista no **TikTok** e no **Instagram Reels**, com o mesmo vídeo vertical. O vídeo não leva selo da série no topo, que fica coberto pelas interfaces das duas redes: o nome da série e o episódio vão no texto do post, que também **credita o @crimecarton**, por decisão do criador. Texto sugerido:

```
A parte que faltou | Ep. 1: A mochila
Você deixaria ele entrar? 👇
Inspirado nas histórias de @crimecarton
#suspense #série #história
```

O título de trabalho é **A parte que faltou**. O protagonista é **Zinho**, participante de um assalto que encontra roupas velhas na mochila da divisão enquanto seu rosto aparece no noticiário. O episódio 1, **A mochila**, termina com o amigo à porta e a pergunta “Você deixa ele entrar?”. O arco proposto tem cinco episódios: A mochila, A dívida, A divisão, A proposta e O preço.

A referência visual atual é [`crimecarton-analise/zinho-referencia-v3.png`](crimecarton-analise/zinho-referencia-v3.png): personagem adulto, cabelo preto cacheado no topo e laterais em degradê, jaqueta azul-marinho com capuz vermelho e faixas brancas. A versão 4 com tranças foi descartada pelo usuário. As versões anteriores permanecem arquivadas. Manter o traço cartoon 2D, a identidade e o figurino da versão 3 nas próximas cenas.

## Pronto

- Roteiro de narração do episódio 1, com 170 palavras, em [`crimecarton-analise/narracao-ep01-zinho.txt`](crimecarton-analise/narracao-ep01-zinho.txt).
- Premissa, arco dos cinco episódios, identidade visual e planejamento de cenas em [`producao-zinho.md`](crimecarton-analise/producao-zinho.md) e [`plano-animacao-ep01.md`](crimecarton-analise/plano-animacao-ep01.md).
- Quatro imagens base verticais em `crimecarton-analise/episodio-01/`: `cena-01-base.png` (mochila), `cena-03-roupas.png` (descoberta), `cena-07-audio.png` (mensagem do amigo) e `cena-09-porta.png` (amigo do lado de fora).
- Narração concluída, com **71,28 segundos**, em `narracao-original.wav` e `narracao-zinho-ep01.mp3`. A geração utilizou os **2 créditos do OpusClip já autorizados e cobrados**. Reutilizar esses arquivos; não repetir a cobrança. Os registros estão em `narracao-job.json` e `estado-producao.json`.
- Narração do pedido de comentário, “Comenta uma palavra só: abrir ou não abrir. O que a maioria escolher vira a parte dois.”, com **6,68 s**, mesma voz e estilo, em `narracao-cta-ep01.wav`. Gerada no Codex, autorizada pelo criador, **1 crédito cobrado** (`narracao-cta-job.json`). `montar_timeline.py` a junta à narração principal em `narracao-ep01-com-cta.wav`, com +3 dB para igualar o volume.
- Retrato frontal de Zinho para a TV e a comparação em [`retrato-zinho.png`](crimecarton-analise/episodio-01/retrato-zinho.png), e folha de personagem do amigo em [`amigo-referencia-v1.png`](crimecarton-analise/amigo-referencia-v1.png), descrita em [`ficha-amigo.md`](crimecarton-analise/ficha-amigo.md). Os dois foram gerados no Codex conforme [`pedido-codex.md`](crimecarton-analise/pedido-codex.md).
- Renderizador local [`render_animatic.py`](crimecarton-analise/episodio-01/montagem/render_animatic.py), com câmera sobre ilustrações, enquadramentos recortados das imagens base, cartões de TV/celular e saída vertical de 720 × 1280 a 25 fps por padrão. A camada de gráficos animados está em [`graficos.py`](crimecarton-analise/episodio-01/montagem/graficos.py), com a fonte Poppins em [`fontes/`](crimecarton-analise/fontes/) (licença OFL).
- Alinhamento palavra por palavra da narração em [`alinhamento-narracao.json`](crimecarton-analise/episodio-01/montagem/alinhamento-narracao.json), gerado por [`alinhar_narracao.py`](crimecarton-analise/episodio-01/montagem/alinhar_narracao.py) com reconhecimento de fala local: as 170 palavras do roteiro têm início e fim medidos na voz, com as bordas ajustadas às pausas do áudio.
- Timeline atual em [`montagem/timeline.json`](crimecarton-analise/episodio-01/montagem/timeline.json), gerada por [`montar_timeline.py`](crimecarton-analise/episodio-01/montagem/montar_timeline.py): **21 planos, 22 elementos gráficos e 31 efeitos sonoros** de 0 a 79,16 s, isto é, a narração com o pedido de comentário (77,96 s) mais 1,2 s de final. Como na referência, não há legenda corrida: as frases-chave entram linha por linha na palavra falada. O painel “A SUA PARTE” passa de “R$ ?” a “R$ 0” em “Nenhuma nota” e as cinco estrelas de suspeita enchem em “suspeito identificado”. As etiquetas marcam PISTA 1 · A MOCHILA, PISTA 2 · O SILÊNCIO, PISTA 3 · A FOTO e PISTA 4 · O ÁUDIO. Entram ainda a lista “BOLSOS → VAZIOS”, o carimbo “A MESMA FOTO”, “TOC! TOC!”, “VENDEU / SEU NOME.” e o final “VOCÊ DEIXA / ELE ENTRAR?”. No pedido de comentário, a imagem volta para a cena inteira da janela, escurecida, e “ABRIR”, “NÃO ABRIR” e “PARTE 2” entram nas palavras faladas.
- **Prova v4, a mais recente:** [`piloto-zinho-ep01-v4.mp4`](crimecarton-analise/episodio-01/piloto-zinho-ep01-v4.mp4), com 79,16 s. É a v3 com o retrato frontal na TV e na comparação, o pedido de comentário narrado e o novo plano final. Áudio em estéreo, com a voz igual nos dois canais: volume integrado de -13,9 LUFS, perto do padrão das redes, e pico de -1,2 dBFS. A narração e o pedido de comentário ficam a 0,6 dB um do outro.
- Prova v3: [`piloto-zinho-ep01-v3.mp4`](crimecarton-analise/episodio-01/piloto-zinho-ep01-v3.mp4), com 74,28 s. É a v2 com **30 efeitos sonoros** nas pausas da voz, seguindo a referência: whoosh nas trocas de capítulo, tique no contador de dinheiro, impactos em “R$ 0”, “NADA.” e no carimbo (que passou para a pausa depois de “fotografia.”), toque de chamada em “ninguém atende”, notificação em “Chega um áudio”, o começo do áudio do amigo repetido em “Você escuta outra vez”, duas batidas na porta junto com “TOC! / TOC!” e “pops” nos botões do final. A voz fica intacta e na mesma posição; volume integrado de -17 LUFS, pico de -1,4 dBFS. Os efeitos estão em [`montagem/efeitos/`](crimecarton-analise/episodio-01/montagem/efeitos/).
- Prova v2, no estilo da referência e sem efeitos: [`piloto-zinho-ep01-v2.mp4`](crimecarton-analise/episodio-01/piloto-zinho-ep01-v2.mp4).
- Prova v1, anterior à referência, com legendas corridas: [`piloto-zinho-ep01-v1.mp4`](crimecarton-analise/episodio-01/piloto-zinho-ep01-v1.mp4). A timeline dela está no histórico do Git.
- Testes curtos de montagem em `montagem/smoke.mp4` e `montagem/smoke-audio.mp4`. `render-report.json` e `timeline-used.json` correspondem à prova v4.

## Em andamento e pendências

- **A prova v4 aguarda revisão do criador** antes da publicação.
- O final promete, como a referência, que “a maioria decide o próximo passo”. Se a maioria comentar NÃO ABRIR, o episódio 2 precisa seguir esse caminho; o arco em `producao-zinho.md` supõe que o amigo entra.
- O amigo ainda não tem nome. Definir antes do episódio 2.
- Outras histórias do @crimecarton só podem ser analisadas se o criador enviar os vídeos: o Instagram bloqueia o acesso automático.
- A referência não usa trilha de fundo, e o episódio também não usa.
- O teste de vídeo de 8 segundos estimado no Codex não será feito, porque o formato não usa animação. Qualquer serviço pago adicional precisa de orçamento e autorização próprios.
- Não houve publicação do piloto no TikTok. O formato e as hipóteses de retenção ainda precisam ser testados; os materiais não comprovam monetização ou alcance.

## Como retomar

1. Revisar a prova v4 e anotar os ajustes.
2. Aplicar os ajustes com `montagem/montar_timeline.py` (ou direto em `timeline.json`) e renderizar a próxima versão. Os campos da timeline, dos gráficos e dos efeitos estão no [`README da montagem`](crimecarton-analise/episodio-01/montagem/README.md); o estilo, no [guia da referência](crimecarton-analise/guia-de-estilo-referencia.md).
3. Revisar a versão final, publicar com o nome da série e o episódio no texto do post e usar os resultados reais de retenção no TikTok e nos Reels para orientar os episódios seguintes.

Requisitos locais do renderizador: **Python 3 com Pillow, FFmpeg com libass e FFprobe**; a fonte Poppins já está no repositório. O alinhamento precisa também de faster-whisper, instalado à parte conforme o README da montagem.

Para montar a timeline e renderizar, executar a partir da raiz do repositório:

```bash
python crimecarton-analise/episodio-01/montagem/montar_timeline.py
python crimecarton-analise/episodio-01/montagem/render_animatic.py \
  --timeline crimecarton-analise/episodio-01/montagem/timeline.json \
  --output crimecarton-analise/episodio-01/piloto-zinho-ep01-v5.mp4 \
  --workers 2
```

O áudio usado é o indicado na timeline (`narracao-ep01-com-cta.wav`, criado por `montar_timeline.py`). Sem `--timeline`, o script usa uma distribuição provisória de cenas sobre `narracao-original.wav`, sem gráficos nem legendas. Esse modo serve para teste técnico, não confirma sincronização. `--prepare-only` prepara fundos e cartões sem codificar o vídeo. Para cada nova versão, trocar o nome do arquivo em `--output`.

## Escopo do backup e arquivos excluídos

As cinco pastas solicitadas são preservadas com sua estrutura: `crimecarton-analise/`, `generated_images/`, `library-files/`, `scratch/` e `shared/`.

O inventário anterior à inclusão deste documento e dos marcadores de diretório contém **60 arquivos**, somando **52.604.320 bytes**. **Nenhum arquivo ultrapassa 100 MB (100.000.000 bytes); nenhum foi excluído por tamanho.** Os arquivos temporários e os testes existentes fazem parte do backup solicitado.

Como o Git não armazena diretórios vazios, arquivos `.gitkeep` preservam `library-files/`, `scratch/` e `shared/downloads/`. Os diretórios internos de ferramentas e credenciais do ambiente não fazem parte das cinco pastas solicitadas.

Desde a prova v1, `montagem/work/` deixou de ser versionada, porque o renderizador a recria a cada execução. Os intermediários do backup original continuam no histórico do Git e na branch `codex/crimecarton`.
