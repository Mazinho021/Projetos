# Pedido para o Codex — Parte 3, “O preço”: cenas novas e voz do Renato

Criado em 31/10/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. O criador viu a Parte 3 montada e pediu três mudanças:

1. Refazer a cena 4, porque o corpo do Renato saiu cortado pelo muro.
2. Dar ao Renato uma voz normal de homem adulto, no lugar da voz do narrador transformada.
3. Usar uma imagem diferente para cada coisa que a narração conta, sem repetir a mesma imagem só com zoom.

São **23 ilustrações**: 22 novas e a cena 4 refeita. Também são **3 gravações curtas do Renato**, uma em cada voz de teste, para o criador escolher. O roteiro não muda: está em [`roteiro-ep03.txt`](roteiro-ep03.txt). Não alterar nenhum outro arquivo do projeto. Fazer tudo numa tarefa só, sem abrir agentes em paralelo.

## Ilustrações

### Regras para todas

**Composição.** O vídeo cobre o topo de cada imagem com um painel (“A SUA PARTE · SUSPEITA”) e uma etiqueta. A parte de baixo fica com as legendas, e a borda direita com os botões do TikTok. Então:

- **Os 25% de cima** ficam só com fundo calmo: céu, teto, parede ou escuro. Nada de rosto, cabeça, mão, celular, anel ou objeto importante.
- **Rostos, mãos e a ação principal** ficam **entre 30% e 60% da altura**, no meio da largura.
- **Os 20% de baixo** ficam só com chão ou fundo.
- **A borda direita** (os 20% da direita, entre 45% e 80% da altura) fica sem nada importante.

**Corpo inteiro e cenário.** Os personagens não podem sair cortados, fundidos ou atravessados pelo cenário. Cada parte do corpo que aparece tem que fazer sentido com o que está na frente e atrás dela: muro, banco, mesa ou porta.

**Variedade.** Cada imagem é um plano diferente, como num storyboard: aberto, close, detalhe, de cima, de baixo, outro lugar. Nenhuma pode parecer um recorte de outra.

**Qualidade:**

- **Formato:** vertical 9:16, no maior tamanho que o gerador permitir. O Claude Code amplia depois para 1440 × 2560.
- **Traço:** o cartoon 2D da série, igual ao das cenas 1 a 13 da Parte 3: traço limpo e firme, contorno escuro, cores chapadas com sombra pintada suave e texturas sutis.
- **Luz:** noturna, de cinema, com a luz amarela dos postes e a luz azulada da lua.
- **Mãos e rostos:** sem deformação. Cinco dedos, olhos alinhados e expressões fortes.

**Personagens:**

- **Zinho:** como em [`../zinho-referencia-v3.png`](../zinho-referencia-v3.png). Cabelo preto cacheado no topo, laterais em degradê e sem barba. Jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, e camiseta preta.
- **Renato:** como em [`../amigo-referencia-v1.png`](../amigo-referencia-v1.png) e em [`cena-05-renato-grita.png`](cena-05-renato-grita.png). Jaqueta verde-oliva aberta, camiseta cinza-escuro, barba curta com bigode e cabelo crespo baixo.
- **O cobrador:** o rosto nunca aparece. A mão direita é grande, com um anel grosso de ouro no dedo médio, e sai da manga de uma jaqueta de couro preta.

**Sem texto:** nada de letras, números, logotipo ou marca d'água. As telas de celular ficam acesas, lisas e em branco, numa cor clara uniforme, com os quatro cantos visíveis, porque a conversa e o relógio entram na montagem.

**Onde salvar:** em `crimecarton-analise/episodio-03/originais/`, com os nomes abaixo. A cena 4 vai por cima do arquivo que já existe.

### A cena refeita

- **`cena-04-mao-anel.png`** — “Quando ele agarra o muro, uma mão puxa a jaqueta dele por trás.”
  - **Ponto de vista:** visto do quintal, à noite.
  - **Renato:** está pendurado no muro, de costas para a câmera, com as duas mãos no topo e os pés tentando subir. O corpo inteiro aparece, da cabeça aos pés, e nada atravessa nem corta o corpo dele.
  - **A mão:** uma mão grande, com o anel grosso de ouro no dedo médio, sai de uma manga de couro preta pela esquerda do quadro e puxa a gola da jaqueta verde-oliva para trás.
  - **Rosto:** Renato vira o rosto por cima do ombro, com medo e dor.
  - **Posição:** o topo do muro fica perto de 30% da altura, a cabeça do Renato entre 32% e 45%, e os pés perto de 75%.

### As 22 cenas novas

Cada cena vem com a frase do roteiro que ela ilustra.

1. **`cena-14-mochila.png`** — “Mas fugir tem um preço.” A sala escura da casa. Renato espia pela fresta da cortina. Atrás dele, Zinho põe a mochila nas costas. A luz dos faróis do carro lá fora entra pela janela e risca a parede.
2. **`cena-15-mao-no-escuro.png`** — “E esta noite, quem paga é ele.” A mão do cobrador, aberta, sai da escuridão na direção da câmera, com a manga de couro preta e o anel de ouro. O fundo é todo escuro, com luz lateral fria só na mão.
3. **`cena-16-renato-puxa.png`** — “Pelos fundos. Vai!” Renato segura o braço do Zinho e aponta para o corredor dos fundos, sussurrando. Atrás deles, o facho da lanterna passa pela janela.
4. **`cena-17-muro-alto.png`** — “No quintal, o muro é mais alto do que você lembrava.” O muro do quintal, visto de baixo, alto, com uns 3 metros. Os dois chegam correndo, de costas para a câmera e pequenos diante do muro. Há um varal com roupas e a lua.
5. **`cena-18-sobe.png`** — “Sobe. Eu vou atrás.” Close do Renato encostado no muro, visto de baixo. Ele olha para cima, suado e decidido, com as mãos juntas segurando o tênis do Zinho, que já está subindo.
6. **`cena-19-do-outro-lado.png`** — “Você sobe, pula e cai do outro lado.” Um beco estreito e escuro, do outro lado do muro. Zinho acaba de cair, agachado, com uma mão no chão, e olha para trás, para o alto do muro.
7. **`cena-20-anel-gola.png`** — “No dedo, um anel grosso de ouro.” Close extremo da mão com o anel grosso de ouro no dedo médio, agarrando com força a gola da jaqueta verde-oliva. Aparecem a manga de couro preta e um pedaço da nuca do Renato.
8. **`cena-21-sem-folego.png`** — “Só para quando o ar acaba.” Zinho curvado, com as mãos nos joelhos e sem fôlego, debaixo de um poste aceso numa rua vazia.
9. **`cena-22-onibus-fora.png`** — “No fim da linha, um ônibus abandonado.” Um ônibus urbano abandonado num terreno baldio no fim da linha. Tem mato alto, pneus murchos, vidros sujos e a porta da frente aberta, sob a luz da lua. Zinho, pequeno, corre até a porta.
10. **`cena-23-celular-chave.png`** — “No bolso, o celular e a chave de uma casa para onde você não pode voltar.” Close das mãos do Zinho no colo, dentro do ônibus escuro. Numa mão está o celular de tela apagada; na outra, uma chave de casa com um chaveiro simples.
11. **`cena-24-sozinho.png`** — “Pela primeira vez na noite, você está sozinho.” Plano aberto do corredor do ônibus abandonado, visto da frente, com bancos rasgados dos dois lados. Lá no fundo, Zinho está pequeno, sentado no chão, abraçando os joelhos, com a luz da lua entrando pelas janelas.
12. **`cena-25-por-cima-do-ombro.png`** — “Primeiro, uma foto.” Visto por cima do ombro do Zinho: o celular na mão dele, com a tela acesa, lisa e em branco, de frente para a câmera. A tela fica no meio do quadro, de 35% a 65% da altura, com os quatro cantos visíveis.
13. **`cena-26-sucata.png`** — “Atrás dele, montes de sucata.” Montes de sucata e carcaças de carro empilhadas num ferro-velho à noite, sob uma única lâmpada, sem pessoas.
14. **`cena-27-mao-no-ombro.png`** — “No ombro dele, a mão com o anel.” Com cara de foto de celular com flash forte, como a cena 9: close da mão com o anel de ouro pousada, pesada, no ombro da jaqueta verde-oliva do Renato. Aparecem só o ombro e o lado do pescoço dele.
15. **`cena-28-play.png`** — “Depois, um áudio.” Close da mão do Zinho segurando o celular, com a tela acesa, lisa e em branco, de frente. O polegar dele chega perto da tela, e ao fundo está o escuro do ônibus. O enquadramento é mais fechado que o da cena 8.
16. **`cena-29-cobrador-grava.png`** — “Vamos trocar: você por ele.” O cobrador no ferro-velho, em silhueta contra a lâmpada, segura um celular perto da boca para gravar um áudio. O rosto fica todo na sombra. O anel de ouro brilha na mão, e ao fundo, desfocado, está o Renato na cadeira.
17. **`cena-30-casa-da-mae.png`** — “Se chamar a polícia, a mãe dele é a próxima.” A casa simples da mãe do Renato, à noite, numa rua de bairro, com uma janela acesa e cortina florida. Em frente, um carro escuro está parado de faróis apagados, com a silhueta de um homem no banco do motorista.
18. **`cena-31-olhos.png`** — “Você escuta outra vez. A voz é calma. Calma demais.” Close extremo do rosto do Zinho de perfil, no escuro do ônibus. O celular está colado na orelha, e os olhos, arregalados, fixos no nada, com uma gota de suor. A luz da tela ilumina o rosto de baixo.
19. **`cena-32-hora.png`** — “Você olha a hora: uma e doze.” O celular na mão do Zinho, visto de cima, com a tela acesa, lisa e em branco, de frente, e o chão do ônibus ao fundo.
20. **`cena-33-renato-sozinho.png`** — “O homem que vendeu o seu nome agora paga por ele.” Plano aberto do ferro-velho à noite. Renato está amarrado numa cadeira de metal, sozinho e pequeno no meio dos montes de sucata, sob a única lâmpada, de cabeça baixa.
21. **`cena-34-maos-degrau.png`** — “Mas foi esse mesmo homem que te deu pé no muro.” Uma lembrança, com as cores desbotadas e um leve brilho: close das mãos do Renato juntas como um degrau, com o tênis do Zinho pisando nelas e o muro ao fundo.
22. **`cena-35-calma.png`** — “A voz é calma. Calma demais.” O cobrador, sentado tranquilo num caixote no ferro-velho, gira o anel de ouro no dedo, com o rosto todo na sombra. Ao lado dele, sobre o caixote, está o celular do Renato, com a tela apagada.

### Onde cada imagem entra

As cenas 1 a 13 que já existem continuam, cada uma uma vez só. A abertura e as imagens das Partes 1 e 2 usadas como lembrança já existem.

| Trecho | Imagem |
|---|---|
| “Mas fugir tem um preço. E esta noite, quem paga é ele.” | 14 e 15 |
| “Lá fora, dois homens descem do carro. Um deles acende uma lanterna.” | 1 |
| “Pelos fundos. Vai!” | 16 |
| “Vocês atravessam a cozinha no escuro. No quintal, o muro é mais alto do que você lembrava.” | 2 e 17 |
| “Renato junta as mãos e te dá pé.” e “Sobe. Eu vou atrás.” | 3 e 18 |
| “Você sobe, pula e cai do outro lado.” | 19 |
| “Quando ele agarra o muro (…) No dedo, um anel grosso de ouro. O mesmo anel da foto da divisão.” | 4, 20 e a foto da Parte 2 |
| “Corre, Zinho! Corre!” e “Você corre. E cada passo pesa mais que o outro.” | 5 e 6 |
| “Só para quando o ar acaba. No fim da linha, um ônibus abandonado. Você se esconde lá dentro, no escuro.” | 21, 22 e 7 |
| “No bolso, o celular e a chave (…)” e “Pela primeira vez na noite, você está sozinho.” | 23 e 24 |
| “Então o celular vibra. É o número do Renato. Mas não é ele.” | 8 |
| “Primeiro, uma foto. Renato numa cadeira (…) Atrás dele, montes de sucata. No ombro dele, a mão com o anel.” | 25, 9, 26 e 27 |
| “Depois, um áudio.” | 28 |
| O áudio do cobrador | 10, 29, 12 e 30 |
| “Você escuta outra vez.” e “A voz é calma. Calma demais.” | 31 e 35 |
| “A mãe dele. A mesma que te dava almoço (…)” | 11 |
| “Você olha a hora: uma e doze. Faltam menos de duas horas.” | 32 |
| “O homem que vendeu o seu nome agora paga por ele. Mas foi esse mesmo homem que te deu pé no muro.” | 33 e 34 |
| “Trocar ou deixar?” e o pedido de comentário | 13 |

## Voz do Renato

O criador achou feia a voz do Renato, que era a voz do narrador transformada. Ele quer uma voz normal de homem adulto. Gerar as mesmas falas em **três vozes de teste**, para ele escolher:

1. **Orus:** gerar com [`pedido-narracao-renato-ep03-orus.json`](pedido-narracao-renato-ep03-orus.json) e salvar em `narracao-ep03-renato-orus.wav`, com o registro em `narracao-ep03-renato-orus-job.json`.
2. **Achird:** gerar com [`pedido-narracao-renato-ep03-achird.json`](pedido-narracao-renato-ep03-achird.json) e salvar em `narracao-ep03-renato-achird.wav`, com o registro em `narracao-ep03-renato-achird-job.json`.
3. **Algenib:** gerar com [`pedido-narracao-renato-ep03-algenib.json`](pedido-narracao-renato-ep03-algenib.json) e salvar em `narracao-ep03-renato-algenib.wav`, com o registro em `narracao-ep03-renato-algenib-job.json`.

Regras para as gravações:

- Salvar todas em `crimecarton-analise/episodio-03/`.
- São uns 7 s cada uma, e deve custar 1 crédito por voz, 3 no total. A geração é paga e foi pedida pelo criador: mostrar o custo antes de executar.
- **Não editar os áudios.** Registrar no job de cada um a transcrição do faster-whisper `medium` sem dar o texto como dica. O Claude Code confere o “Zinho” de “Corre, Zinho! Corre!”.
- Não gerar de novo a narração nem o áudio do cobrador.

## Entrega

1. Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido.
2. Fazer commit e push de todos os arquivos gerados na `codex/crimecarton` do repositório `Mazinho021/Projetos`, **nesta mesma conversa em que eles forem gerados**.
3. Responder com o link do commit e os créditos cobrados.

Depois, o Claude Code amplia as imagens, monta uma prévia das três vozes para o criador escolher e refaz a montagem com uma imagem por trecho.
