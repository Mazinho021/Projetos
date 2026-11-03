# Pedido para o Codex — Parte 4, “O dono do anel”

Criado em 02/11/2026 no Claude Code, que não tem gerador de imagens nem a geração de voz do OpusClip. O criador aprovou o roteiro, [`roteiro-ep04-trocar.txt`](roteiro-ep04-trocar.txt), e o plano cena por cena, [`plano-ep04.md`](plano-ep04.md).

O pedido tem duas partes:

- **22 ilustrações**, uma para cada trecho do roteiro;
- **3 gravações:** o narrador, o Ademir e o Renato.

Não alterar nenhum outro arquivo do projeto. Fazer tudo numa tarefa só, sem abrir agentes em paralelo.

**Situação em 03/11/2026:** a primeira conversa do Codex com este pedido travou no limite diário sem fazer push. Nada foi entregue, então o pedido começa do zero numa conversa nova.

## Ilustrações

### Regras para todas

**Composição.** O vídeo cobre o topo de cada imagem com um painel (“A SUA PARTE · SUSPEITA”) e uma etiqueta. A parte de baixo fica com as legendas, e a borda direita com os botões do TikTok. Então:

- **Os 25% de cima** ficam só com fundo calmo: céu, teto, parede ou escuro. Nada de rosto, cabeça, mão, celular, anel ou objeto importante.
- **Rostos, mãos e a ação principal** ficam **entre 30% e 60% da altura**, no meio da largura.
- **Os 20% de baixo** ficam só com chão ou fundo.
- **A borda direita** (os 20% da direita, entre 45% e 80% da altura) fica sem nada importante.

**Corpo inteiro e cenário.**

- Os personagens não podem sair cortados, fundidos ou atravessados pelo cenário.
- Cada parte do corpo que aparece tem que fazer sentido com o que está na frente e atrás dela: cadeira, mesa, carro, portão ou sucata.
- Quando o plano corta o corpo, o corte é da borda do quadro, como num plano médio, e nunca de um objeto do cenário.

**Variedade.**

- Cada imagem é um plano diferente, como num storyboard: aberto, close, detalhe, de cima, de baixo, outro lugar.
- Nenhuma pode parecer um recorte de outra.
- Nenhuma pode repetir um enquadramento das Partes 2 e 3.

**Qualidade:**

- **Formato:** vertical 9:16, no maior tamanho que o gerador permitir. O Claude Code amplia depois para 1440 × 2560.
- **Traço:** o cartoon 2D da série, igual ao das cenas da Parte 3: traço limpo e firme, contorno escuro, cores chapadas com sombra pintada suave e texturas sutis.
- **Luz:** noturna, de cinema, com a luz amarela da lâmpada e dos postes, a luz azulada da lua cheia e reflexos no chão molhado.
- **Mãos e rostos:** sem deformação. Cinco dedos, olhos alinhados e expressões fortes.

**Lugares:**

- **O ferro-velho São Jorge,** como em [`../episodio-03/cena-33-renato-sozinho.png`](../episodio-03/cena-33-renato-sozinho.png) e [`../episodio-03/cena-26-sucata.png`](../episodio-03/cena-26-sucata.png):
  - chão de cimento rachado e molhado;
  - montes de sucata e carcaças de carro;
  - uma cobertura de zinco com uma única lâmpada;
  - a lua cheia.
- **O portão do ferro-velho** é o portão de tela de [`../episodio-03/cena-12-ferro-velho.png`](../episodio-03/cena-12-ferro-velho.png).
- **O barracão:** um barracão de alvenaria dentro do terreno, com paredes bege. Lá dentro fica a mesa de madeira da foto da divisão, de [`../episodio-02/cena-04-foto-divisao.png`](../episodio-02/cena-04-foto-divisao.png).
- **O carro escuro** é o sedã preto de [`../episodio-03/cena-30-casa-da-mae.png`](../episodio-03/cena-30-casa-da-mae.png).
- **O ônibus abandonado** é o de [`../episodio-03/cena-24-sozinho.png`](../episodio-03/cena-24-sozinho.png).

**Personagens:**

- **Zinho:** como em [`../zinho-referencia-v3.png`](../zinho-referencia-v3.png). Cabelo preto cacheado no topo, laterais em degradê e sem barba. Jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, e camiseta preta.
- **Renato:** como em [`../amigo-referencia-v1.png`](../amigo-referencia-v1.png) e em [`../episodio-03/cena-05-renato-grita.png`](../episodio-03/cena-05-renato-grita.png). Jaqueta verde-oliva aberta e suja, camiseta cinza-escuro, barba curta com bigode e cabelo crespo baixo. Tem o lábio cortado e, depois de solto, os pulsos vermelhos da corda.
- **Ademir:** é o cobrador da Parte 3, agora com o rosto à mostra.
  - Usa as mesmas roupas e o mesmo anel de [`../episodio-03/cena-35-calma.png`](../episodio-03/cena-35-calma.png) e [`../episodio-03/cena-20-anel-gola.png`](../episodio-03/cena-20-anel-gola.png): jaqueta de couro preta, camisa escura, calça escura e tênis escuros.
  - Uns 60 anos, alto e corpulento, com mãos grandes.
  - Cabelo branco penteado para trás, bigode branco aparado, rugas fundas e olhar calmo.
  - Anel grosso de ouro no dedo médio da mão direita e uma pequena medalha dourada de São Jorge numa corrente fina.
- **O motorista do assalto:** uns 35 anos, magro, de boné escuro, barba rala, jaqueta corta-vento cinza e calça jeans.
- **O parceiro dos dez milhões:** só aparece de costas, de capuz escuro. O rosto nunca aparece.

**Sem texto:**

- Nada de letras, números, logotipo ou marca d'água, nem em placas de carro e viaturas.
- A placa do portão e o calendário da parede ficam em branco.
- As telas de celular ficam acesas, lisas e em branco, numa cor clara uniforme, com os quatro cantos visíveis, porque a mensagem e o relógio entram na montagem.

**Onde salvar:** em `crimecarton-analise/episodio-04/originais/`, com os nomes abaixo.

### As 22 cenas

Cada cena vem com a frase do roteiro que ela ilustra.

1. **`cena-01-passo-na-luz.png`** — “Quem sequestrou o seu amigo vai mostrar o rosto.”
   - **Lugar e ângulo:** no ferro-velho, debaixo da cobertura de zinco, visto por cima do ombro do Zinho. O ombro e a nuca dele ficam no canto inferior esquerdo, escuros e desfocados.
   - **O Ademir:** a uns três metros, no meio do quadro, ele dá um passo para dentro da luz da lâmpada. Aparece inteiro, da cabeça aos pés.
   - **O rosto:** a luz de cima pega o queixo, o bigode branco, a boca séria e o cabelo branco das laterais. A sombra da testa ainda cobre os olhos.
   - **O anel:** brilha forte na mão direita, à frente do corpo.
   - **Posição:** a boca perto de 38% da altura.
2. **`cena-02-onibus-decidido.png`** — “Mas você não vai de mãos vazias.”
   - **Lugar e ângulo:** dentro do ônibus abandonado, visto de lado, com a luz azulada da lua entrando pelas janelas.
   - **O Zinho:** sentado num banco rasgado, inteiro, inclinado para a frente e decidido. O celular aceso nas mãos ilumina o rosto dele de baixo, e a tela fica virada para ele.
   - **Posição:** o rosto entre 35% e 45% da altura.
3. **`cena-03-agendar.png`** — “No ônibus, você agenda uma mensagem para o jornal que publicou o seu rosto.”
   - **O celular:** as duas mãos do Zinho seguram o celular em pé, de frente para a câmera, com os dois polegares digitando.
   - **As mangas:** aparecem as mangas da jaqueta azul-marinho, com as faixas brancas.
   - **A tela:** acesa e em branco, de 30% a 70% da altura, no meio da largura.
   - **Fundo:** as janelas do ônibus e a lua, desfocadas.
4. **`cena-04-portao-aberto.png`** — “Duas e cinquenta e nove. O portão do Ferro-Velho São Jorge está aberto.”
   - **O portão:** o portão de tela, agora com uma folha aberta para dentro e a corrente com o cadeado pendurada solta.
   - **Ângulo:** visto de fora, mais baixo e mais de lado do que na Parte 3.
   - **A placa:** retangular e em branco, presa na folha fechada, à esquerda do centro, inteira e entre 35% e 50% da altura.
   - **O Zinho:** pequeno, inteiro e de costas, passa pela abertura.
   - **Lá dentro:** a luz amarela de uma única lâmpada.
5. **`cena-05-chegada.png`** — “Lá dentro, uma lâmpada só. E o Renato, amarrado numa cadeira.”
   - **Ângulo:** plano aberto, visto de trás do Zinho, que entra no terreno, inteiro, à esquerda do centro.
   - **O Renato:** lá na frente, debaixo da cobertura e da única lâmpada, amarrado numa cadeira de metal, inteiro, no meio dos montes de sucata.
6. **`cena-06-renato-amarrado.png`** — “Você veio? Por que você veio?”
   - **Ângulo:** o Renato de frente e de perto, da cabeça aos joelhos, amarrado na cadeira de metal debaixo da lâmpada.
   - **O corpo:** os braços estão presos atrás do encosto com corda grossa, e o lábio está cortado.
   - **O olhar:** ele olha para cima e para a esquerda, para o Zinho, que fica fora do quadro, com surpresa e raiva ao mesmo tempo.
   - **Posição:** o rosto entre 32% e 42% da altura.
7. **`cena-07-ademir-sai-da-sombra.png`** — “Da sombra sai um homem de uns sessenta anos, cabelo branco, jaqueta de couro.”
   - **O Ademir:** inteiro, da cabeça aos pés, sai do escuro entre dois montes de sucata para a luz da lâmpada, calmo e sem pressa, com as mãos à vista.
   - **O rosto:** agora aparece inteiro, como na descrição do personagem.
   - **Posição:** no meio do quadro, com o rosto entre 32% e 40% da altura e os pés perto de 80%.
8. **`cena-08-anel-canivete.png`** — “No dedo, o anel da foto.”
   - **A mão:** close da mão direita do Ademir, grande e enrugada, saindo da manga de couro preta e segurando um canivete fechado.
   - **O anel:** o mesmo anel grosso de ouro da Parte 3, no dedo médio, brilha com a luz da lâmpada.
   - **Fundo:** sucata escura e desfocada.
   - **Posição:** a mão entre 40% e 60% da altura.
9. **`cena-09-mesa-da-foto.png`** — “Pode me chamar de Ademir. O São Jorge é meu. E aquela mesa da foto também.”
   - **O Ademir:** em plano médio, da cabeça à cintura, à esquerda do centro. Fala calmo e aponta com o polegar para trás, por cima do ombro.
   - **O barracão:** atrás dele, a porta aberta, com uma lâmpada acesa lá dentro.
   - **A mesa:** a mesa de madeira da foto da divisão, vazia, sem dinheiro, entre 50% e 65% da altura.
   - **O calendário:** em branco, na parede bege.
   - **Posição:** o rosto entre 32% e 42% da altura.
10. **`cena-10-corda.png`** — “Ele corta a corda do Renato com um canivete, sem pressa.”
    - **Ângulo:** close atrás da cadeira de metal.
    - **O corte:** os pulsos do Renato estão amarrados com corda grossa no encosto, e a mão grande do Ademir, com o anel de ouro, corta a corda com o canivete aberto.
    - **As mangas:** aparecem a verde-oliva do Renato e a de couro preto do Ademir.
    - **Posição:** os pulsos entre 40% e 60% da altura.
11. **`cena-11-voce-fica.png`** — “Combinado é combinado. Ele sai, você fica.”
    - **Ângulo:** plano aberto debaixo da lâmpada, com os três inteiros.
    - **O Renato:** à esquerda, de pé ao lado da cadeira, esfrega os pulsos vermelhos.
    - **O Ademir:** no meio, calmo, aponta o canivete fechado para o Zinho.
    - **O Zinho:** à direita do centro, tenso, de punhos fechados.
    - **Posição:** os rostos entre 32% e 42% da altura e os três entre 15% e 75% da largura.
12. **`cena-12-cafe.png`** — “Aceita um café? Acabei de passar.”
    - **O Ademir:** em plano médio, na porta do barracão, serve café de uma garrafa térmica antiga em copinhos de plástico brancos, em cima da mesa de madeira da foto.
    - **Os copinhos:** sai fumaça deles.
    - **O olhar:** ele olha para a câmera, para o Zinho, com um meio sorriso educado.
    - **Posição:** o rosto entre 32% e 40% da altura, e a mesa e os copinhos entre 50% e 60%.
13. **`cena-13-renato-aceita.png`** — “Você não aceita. O Renato aceita.” e “Com açúcar, se tiver.”
    - **Ângulo:** os dois lado a lado, inteiros, debaixo da lâmpada.
    - **O Zinho:** à esquerda, duro, sério, de braços cruzados.
    - **O Renato:** à direita do centro, com o lábio cortado, segura um copinho de café com as duas mãos e sopra a fumaça, aliviado e meio sem graça.
    - **O tom:** é o momento leve da parte.
    - **Posição:** os rostos entre 32% e 42% da altura e os dois entre 20% e 75% da largura.
14. **`cena-14-isqueiro.png`** — “No fundo do terreno, um homem acende um cigarro.”
    - **Ângulo:** plano aberto do fundo do ferro-velho, mais escuro.
    - **O motorista:** pequeno e inteiro, encostado no carro escuro, entre montes de sucata, acendendo um cigarro.
    - **A luz:** a chama do isqueiro é a única luz perto dele e ilumina só um pedaço do rosto.
    - **Posição:** no meio do quadro, com a cabeça perto de 40% da altura.
15. **`cena-15-motorista.png`** — “Você conhece aquele rosto. Foi ele que dirigiu o carro do assalto.”
    - **O motorista:** close, com o cigarro na boca.
    - **A luz:** a brasa acesa ilumina o rosto dele de baixo, em laranja.
    - **O olhar:** frio, direto para a câmera.
    - **Posição:** o rosto entre 35% e 50% da altura, no meio.
16. **`cena-16-ademir-inclina.png`** — “E aí o Ademir diz a última coisa que você esperava ouvir.” e “Eu não quero você preso.”
    - **O Ademir:** close de frente, visto um pouco de baixo, inclinado para a câmera, para o Zinho, sério e calmo.
    - **A luz:** vem de trás e faz um contorno no cabelo branco. A lâmpada não aparece.
    - **A medalha:** aparece no peito.
    - **Posição:** o rosto entre 32% e 48% da altura.
17. **`cena-17-parceiro.png`** — “O seu parceiro sumiu com os dez milhões. Com a minha parte também.”
    - **O clima:** uma cena contada, com cores mais frias e desbotadas.
    - **O lugar:** uma rua escura de madrugada.
    - **O parceiro:** de costas e de capuz, entra num carro carregando duas bolsas de viagem pretas e pesadas, as mesmas da foto da divisão. O rosto nunca aparece.
    - **Posição:** inteiro e no meio do quadro, com a cabeça perto de 35% da altura.
18. **`cena-18-mao-no-ombro.png`** — “E você vai me levar até ele.”
    - **Ângulo:** os dois de perfil, frente a frente, do peito para cima.
    - **O Zinho:** à esquerda, tenso.
    - **O Ademir:** à direita do centro, calmo. A mão grande dele, com o anel de ouro, pousa pesada no ombro da jaqueta azul-marinho do Zinho, perto do capuz vermelho.
    - **O gesto:** repete o da Parte 3, quando a mão estava no ombro do Renato.
    - **Posição:** os rostos entre 32% e 42% da altura.
19. **`cena-19-isca.png`** — “Você nunca foi o culpado. Foi a isca. E continua sendo.”
    - **O Zinho:** close do rosto, de frente, com a luz dura da lâmpada vindo de cima.
    - **As sombras:** as de dois homens, o Ademir e o motorista, caem dos dois lados do rosto.
    - **A expressão:** a de quem entendeu tudo, com a boca entreaberta e os olhos parados.
    - **Posição:** o rosto entre 32% e 50% da altura.
20. **`cena-20-celular-escondido.png`** — “O celular vibra no seu bolso. Três e treze. Faltam dois minutos para a foto sair.”
    - **O Zinho:** da cintura para cima, de lado, tira o celular do bolso da jaqueta, baixo, perto da cintura, escondendo-o com o corpo.
    - **O Ademir:** fica de costas, desfocado ao fundo, perto do barracão.
    - **A tela:** acesa e em branco, virada para a câmera, entre 50% e 65% da altura, no meio da largura.
    - **Posição:** o rosto do Zinho entre 32% e 40% da altura, olhando para baixo, para o celular.
21. **`cena-21-opcao-cancelar.png`** — “Se você cancelar, vira sócio do homem que sequestrou o Renato, contra o parceiro que ficou com tudo.”
    - **O acordo:** o Zinho e o Ademir apertam as mãos debaixo da lâmpada, inteiros, de perfil e frente a frente.
    - **Fundo:** o motorista, desfocado, encostado no carro.
    - **A luz:** quente, de acordo selado.
    - **Posição:** os rostos entre 32% e 42% da altura e os dois entre 15% e 75% da largura.
22. **`cena-22-opcao-enviar.png`** — “Se deixar sair, a foto chega ao jornal, e a polícia chega aqui. Com você dentro.”
    - **Ângulo:** o portão do ferro-velho visto de dentro.
    - **A polícia:** lá fora piscam luzes vermelhas e azuis de viatura, com faróis. A viatura não aparece nítida e não tem nenhum texto.
    - **O Zinho:** em primeiro plano, inteiro, entre a sucata, olha para o portão, iluminado de vermelho e azul.
    - **Atrás dele:** o Ademir e o motorista se viram para o portão.
    - **Posição:** os rostos entre 32% e 45% da altura.

### Onde cada imagem entra

As lembranças das Partes 2 e 3, a grade do perfil e as telas dos celulares são montadas pelo Claude Code.

| Trecho | Imagem |
|---|---|
| “Quem sequestrou o seu amigo vai mostrar o rosto.” | 1 |
| O resumo e o resultado da votação | lembranças das Partes 2 e 3 |
| “Mas você não vai de mãos vazias.” | 2 |
| “No ônibus, você agenda uma mensagem (…) Só você pode cancelar.” | 3 |
| “Duas e cinquenta e nove (…) está aberto.” | 4 |
| “Lá dentro, uma lâmpada só. E o Renato, amarrado numa cadeira.” | 5 |
| “Você veio? Por que você veio?” | 6 |
| “Da sombra sai um homem (…) No dedo, o anel da foto.” | 7 e 8 |
| “Pode me chamar de Ademir (…)” | 9 |
| “Ele corta a corda (…)” e “Combinado é combinado (…)” | 10 e 11 |
| “Aceita um café? (…)”, “Você não aceita. O Renato aceita.” e “Com açúcar, se tiver.” | 12 e 13 |
| “No fundo do terreno (…) Foi ele que dirigiu o carro do assalto.” | 14 e 15 |
| “E aí o Ademir diz (…)” e a fala dele | 16, 17 e 18 |
| “Você nunca foi o culpado (…)” | 19 |
| “O celular vibra no seu bolso (…)” | 20 |
| As duas opções | 21 e 22 |

## Vozes

Gerar as três gravações abaixo e salvar tudo em `crimecarton-analise/episodio-04/`.

1. **Narrador:** usar a voz Charon de sempre.
   - Gerar com [`pedido-narracao-ep04.json`](pedido-narracao-ep04.json) e salvar em `narracao-ep04-narrador.wav`, com o registro em `narracao-ep04-narrador-job.json`.
   - A última frase, “Vocês decidiram: trocar.”, é uma alternativa para o resultado da votação: a montagem usa uma das duas versões.
2. **Ademir:** usar Charon, no estilo do cobrador da Parte 3.
   - Gerar com [`pedido-narracao-ademir-ep04.json`](pedido-narracao-ademir-ep04.json) e salvar em `narracao-ep04-ademir.wav`, com o registro em `narracao-ep04-ademir-job.json`.
3. **Renato:** usar a voz Algenib, escolhida pelo criador.
   - Gerar com [`pedido-narracao-renato-ep04.json`](pedido-narracao-renato-ep04.json) e salvar em `narracao-ep04-renato.wav`, com o registro em `narracao-ep04-renato-job.json`.

**Custo:** pelas Partes 2 e 3, deve custar uns **4 créditos**, mas o valor certo é o que o Codex mostrar antes de executar. A geração é paga e foi pedida pelo criador.

- O narrador, com uns 95 s, deve custar 2.
- O Ademir, com uns 30 s, deve custar 1.
- O Renato, com uns 5 s, deve custar 1.

**Regras para as gravações:**

- **Não editar os áudios.**
- **Conferir cada gravação:** registrar no job a transcrição do faster-whisper `medium`, sem dar o texto como dica.
- **Se uma palavra sair trocada:** avisar na resposta, sem gerar de novo. O Claude Code confere e decide.
- **Se o serviço de voz disser que já existe um job com a mesma `idempotencyKey`,** usar esse resultado em vez de pagar de novo. A conversa que travou pode ter gerado alguma voz.

## Entrega

1. Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido.
2. Fazer commit e push de todos os arquivos gerados na `codex/crimecarton` do repositório `Mazinho021/Projetos`, **nesta mesma conversa em que eles forem gerados**.
   - Fazer aos poucos: depois das vozes, a cada 5 cenas prontas e de novo no fim.
   - Assim nada se perde se o limite diário acabar no meio, como aconteceu na primeira tentativa.
3. Responder com o link do commit e os créditos cobrados.

Depois, o Claude Code amplia as imagens e confere as vozes. Também passa a voz do Ademir pela voz do cobrador, sem o som de celular, e monta a Parte 4 nas duas versões.
