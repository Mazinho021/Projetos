# Parte 2 — montagem

Esta pasta monta a Parte 2, “A dívida”, com as ferramentas de [`episodio-01/montagem/`](../../episodio-01/montagem/README.md): o renderizador, a camada de gráficos e o alinhador. O roteiro, com a voz de cada fala, está em [`../roteiro-ep02.txt`](../roteiro-ep02.txt), e o plano de cenas em [`../plano-ep02.md`](../plano-ep02.md).

## Quando o Codex entregar

As ilustrações `cena-01-porta-aberta.png` a `cena-08-retrato-amigo.png` e as duas vozes, `narracao-ep02-narrador.wav` e `narracao-ep02-amigo.wav`, chegam em `episodio-02/`. A partir da raiz do repositório:

1. Alinhar cada voz ao próprio texto, com o mesmo alinhador da Parte 1:

   ```bash
   A=crimecarton-analise/episodio-02
   .venv/bin/python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py \
     --audio $A/narracao-ep02-narrador.wav --script $A/narracao-ep02-narrador.txt --output $A/montagem/alinhamento-narrador.json
   .venv/bin/python crimecarton-analise/episodio-01/montagem/alinhar_narracao.py \
     --audio $A/narracao-ep02-amigo.wav --script $A/narracao-ep02-amigo.txt --output $A/montagem/alinhamento-amigo.json
   ```

2. Ajustar em `montar_timeline.py` os enquadramentos dentro das ilustrações novas (`FRIEND02`, `ZINHO02`, `FRIEND03`, `EYES03`, `CALENDAR04`, `FACE05`, `HAND06`, `CAR07`) e o nome e o telefone pintados no calendário da foto da divisão (`CALENDAR_PAINT`). Enquanto valem `None`, a cena usa a ilustração inteira.

3. Montar o áudio e as timelines, e renderizar as duas versões:

   ```bash
   python crimecarton-analise/episodio-02/montagem/montar_timeline.py
   for v in "" "-vertical"; do
     python crimecarton-analise/episodio-01/montagem/render_animatic.py \
       --timeline crimecarton-analise/episodio-02/montagem/timeline$v.json \
       --output crimecarton-analise/episodio-02/parte-02-a-divida$v.mp4
   done
   ```

## Como a timeline é montada

`montar_timeline.py` junta, na ordem do roteiro, a vinheta, as falas do narrador e as do amigo numa só faixa, `narracao-ep02.wav`. A vinheta são as 17 primeiras palavras da narração da Parte 1, com a mesma voz. A faixa ainda leva as pausas abertas para os sons da história. As falas são cortadas só onde a voz muda ou onde entra uma pausa; os volumes da vinheta e do amigo são igualados ao do narrador. Cortes, gráficos e efeitos ficam presos a palavras do roteiro, achadas pelo texto (`N('Toca três vezes.')`, `A('Oitenta mil.')`), então a edição acompanha as vozes se elas forem geradas ou alinhadas de novo.

As pausas, em `PAUSES`, entram depois destas palavras:

| Depois de | Pausa | Som |
|---|---|---|
| “Vocês decidiram: abrir.” | 0,3 s | o carimbo da opção vencedora |
| “Você destranca a porta.” | 0,9 s | a tranca e a porta abrindo |
| “…apaga a luz da sala.” | 0,35 s | o interruptor, com a cena escurecendo |
| “Toca três vezes.” | 2,75 s | o segundo e o terceiro toque; o primeiro soa sob a fala; depois alguém atende |
| “Você desliga sem dizer nada.” | 0,5 s | o fim da ligação |
| “…vibra em cima da mesa.” | 1,2 s | o celular vibrando duas vezes na mesa |
| “…em frente ao portão.” | 1,4 s | o carro parando lá fora |
| “De farol apagado.” | 0,6 s | o respiro antes da votação |

O script grava `timeline.json`, a versão do Instagram, e `timeline-vertical.json`, a do TikTok e do Shorts. Na vertical, o painel, as etiquetas e os cartões descem para baixo da barra de busca do TikTok. Da metade de baixo, tudo fica à esquerda de x = 590, longe da coluna de botões: os elementos centram em x = 330, as frases ficam 9% menores, os cartões andam 25 px para a esquerda e a TV encolhe para 88%. O script recusa frases mais largas que cada versão permite.

### Abertura padrão

`abertura()` monta o bloco que toda parte repete, descrito no [guia de estilo](../../guia-de-estilo-referencia.md#abertura-das-partes-seguintes). Ele leva a ilustração da mochila com a etiqueta “PARTE N” e as três frases fixas na voz da Parte 1, com o contador até R$ 10.000.000. Depois vêm a tela preta “VOCÊ FICOU COM / O ROSTO NO JORNAL.”, com as cinco estrelas de suspeita, e o aviso “CHEGOU AGORA? A PARTE N−1 TÁ NO PERFIL” com o @golpecartoon. Por fim, as barras com o resultado real da votação anterior e o carimbo da vencedora. Nas próximas partes, basta passar o número da parte, as opções com as porcentagens e as palavras do narrador que abrem o aviso e o resultado.

### Votação do nome

A Parte 2 termina com a votação livre do nome do amigo, sem opções, como pediu o criador. Na tela aparecem “QUAL É O / NOME DELE?”, “COMENTA UM NOME” e uma caixa de comentário vazia com o cursor piscando, a regra “O MAIS CURTIDO VENCE” e a caixa “PARTE 3”.

## Efeitos sonoros

`gerar_efeitos.py` grava em `efeitos/` os sons próprios da Parte 2. Whoosh, tique, impactos, pop e notificação vêm de `efeitos/` da Parte 1, que o renderizador também consulta.

- Sintetizados, com numpy e filtros do FFmpeg: `chamada-longa.wav` (um toque de 425 Hz, o tom de chamada no Brasil), `atende.wav`, `desliga.wav`, `interruptor.wav`, `vibracao.wav` (o celular vibrando numa mesa de madeira) e `carro.wav` (um carro que chega devagar e fica ligado, ouvido pela janela).
- Gravações do pacote RPG Audio de Kenney, em domínio público (CC0, ver `efeitos/LICENCA-kenney-rpg-audio.txt`): `tranca.wav` (metalLatch), `porta-abre.wav` (doorOpen_1), `porta-fecha.wav` (doorClose_4) e `passos.wav` (footstep00 e footstep02). Para convertê-las de novo, passe o pacote descompactado com `--kenney`.

```bash
python crimecarton-analise/episodio-02/montagem/gerar_efeitos.py
```

## Prévia antes das vozes

`--estimar DIR` monta tudo em `DIR`, fora do repositório, com tempos estimados para as duas vozes novas e silêncio no lugar delas. A vinheta mantém o áudio real da Parte 1, e as ilustrações que faltam são trocadas pela cena 1 da Parte 1. Serve para conferir a edição e as duas versões antes da entrega do Codex.

```bash
python crimecarton-analise/episodio-02/montagem/montar_timeline.py --estimar /tmp/parte-02
```
