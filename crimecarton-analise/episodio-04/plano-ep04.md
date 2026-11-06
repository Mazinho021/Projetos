# Parte 4 — “O dono do anel”

A votação da Parte 3 era **TROCAR ou DEIXAR**. Em 01/11/2026, às 14:24, o Instagram estava empatado em 4 a 4. Em 02/11/2026, o criador mandou seguir pelo **TROCAR**, o caminho que prende mais:

- **Promete uma resposta logo no começo:** o rosto do homem do anel, um segredo desde a foto da divisão, na Parte 2.
- **Tem um relógio correndo o vídeo inteiro:** a foto vai para o jornal às 3:15 se o Zinho não cancelar.
- **A reviravolta muda a série:** o sequestrador não quer o Zinho preso, porque o parceiro sumiu também com a parte dele, e o Zinho era a isca.
- **Só usa vozes que já existem:** o narrador, o Renato e a voz do cobrador. O DEIXAR precisaria de duas vozes novas.

**Falta conferir o TikTok e o Shorts.**

- Se o TROCAR tiver a maioria somando as três redes, o resumo diz “Vocês decidiram: trocar.” no lugar de “Deu empate. No desempate: trocar.” A narração grava as duas versões, para não pagar outra gravação.
- Se o DEIXAR tiver a maioria na soma, a maioria manda, e volta o roteiro “A casa da mãe”, guardado no fim deste plano.

O roteiro está em [`roteiro-ep04-trocar.txt`](roteiro-ep04-trocar.txt). **Em 02/11/2026, o criador aprovou o roteiro e o plano** (“Aceito”). O pedido ao Codex está em [`pedido-codex-ep04.md`](pedido-codex-ep04.md).

## O que mudou da primeira versão

A primeira versão continua no histórico do Git.

- **Abertura:** “Quem sequestrou o seu amigo vai mostrar o rosto.” Quem nunca viu a série não sabe quem é “o homem do anel”.
- **Resumo em uns 8 s**, com o empate e o jornal “A VOZ DO BAIRRO”.
- **O ônibus ficou mais curto:** de 49 para 36 palavras, porque é explicação e cai na faixa em que a Parte 3 perdia público (o tempo médio foi de 31 s). A mensagem agendada aparece na tela do celular.
- **O rosto aparece lá pelos 40 s**, contra uns 50 s na primeira versão. O anel no dedo do Ademir liga o rosto à foto, para quem não ouviu o áudio da Parte 3.
- **O momento leve:** o Ademir oferece café às três da manhã, e o Renato, que acabou de ser solto, aceita.
- **A frase do motorista ficou mais curta.**
- **A votação mostra o que acontece em cada opção.**

## Tamanho e vozes

São 300 palavras: 236 do narrador, 54 do Ademir e 10 do Renato.

- Pelo ritmo das vozes da Parte 3, a fala dá uns 2 min 13 s, e as pausas de leitura levam a uns 2 min 15 s a 2 min 20 s.
- Fica perto dos 2 min 13 s da Parte 3. Não tem vinheta: a abertura de 12 s não cabe na regra nova.

As vozes:

- **Narrador:** Charon, como sempre.
- **Renato:** Algenib, sem transformação.
- **Ademir:** é a voz do cobrador, para quem ouviu o áudio da Parte 3 reconhecer o homem.
  - As falas dele são geradas em Charon, no estilo calmo do pedido do cobrador ([`../episodio-03/pedido-narracao-cobranca-ep03.json`](../episodio-03/pedido-narracao-cobranca-ep03.json)).
  - Depois, passam pela mesma troca de voz de [`voz_cobranca.py`](../episodio-03/montagem/voz_cobranca.py), mas **sem o som de celular**, porque agora ele fala ao vivo.
  - Um teste grátis, feito com a gravação do cobrador da Parte 3, foi mandado ao criador em 02/11/2026: primeiro a voz no celular e depois ao vivo.

## Cena por cena

São **22 desenhos novos**. O resto são lembranças de partes anteriores e telas montadas aqui.

- A imagem pode ficar mais de um trecho, desde que entre algo novo por cima a cada fala.
- Todos os desenhos seguem a composição do `CLAUDE.md`:
  - os 25% de cima ficam só com fundo calmo;
  - rostos e ação ficam entre 30% e 60% da altura;
  - a borda direita fica livre entre 45% e 80% da altura;
  - os corpos aparecem inteiros e apoiados no cenário.

| # | Trecho | Imagem | Por cima |
|---|---|---|---|
| 0 | “O assalto deu certo. Seu parceiro ficou com dez milhões. Você ficou com o rosto no jornal.” | A arte da mochila da Parte 1: o “início de sempre”, em versão curta, pedido de volta pelo criador em 06/11/2026, antes de tudo | As frases de sempre, o contador de R$ 10.000.000 e as estrelas de suspeita, sem a tela preta |
| 1 | “Quem sequestrou o seu amigo vai mostrar o rosto.” | **Nova.** Por cima do ombro do Zinho, o homem da jaqueta de couro preta dá um passo para a luz da lâmpada. A luz pega o queixo, a boca e o cabelo branco, e os olhos ainda ficam na sombra. O anel brilha na mão direita. | Frase “ELE VAI MOSTRAR / O ROSTO”, relógio 03:00 e etiqueta “PARTE 4” |
| 2 | “Chegou agora? As outras partes estão no perfil.” | Montada: as capas das Partes 1, 2 e 3 lado a lado, como na grade do perfil | Seta “TODAS NO PERFIL” |
| 3 | “O Renato foi pego no seu lugar.” | Lembrança: a mão com o anel puxando o Renato no muro (Parte 3, cena 4) | Polaroide “PARTE 3 · pego no seu lugar” |
| 4 | “Deu empate. No desempate: trocar.” | Lembrança escurecida: o Zinho decidindo no ônibus (Parte 3, cena 13) | Resultado “EMPATE” → “DESEMPATE: TROCAR” e o jornal “A VOZ DO BAIRRO”, com 2 s a mais para ler |
| 5 | “Mas você não vai de mãos vazias.” | **Nova.** O Zinho sentado num banco rasgado do ônibus abandonado, decidido, com a luz do celular no rosto | Frase “MÃOS VAZIAS? / NÃO.” |
| 6 | “No ônibus, você agenda uma mensagem para o jornal que publicou o seu rosto. Às três e quinze, ela sai com a foto da divisão. Só você pode cancelar.” | **Nova.** Close das mãos do Zinho com o celular, com a tela em branco para montar a mensagem: “JORNAL · redação”, a foto anexada e “ENVIO AGENDADO · 03:15” | A foto da divisão em polaroide “PARTE 2”, com círculo e etiqueta “O ANEL”. No “cancelar”, círculo no botão, e o painel vira “A FOTO SAI ÀS 3:15” |
| 7 | “Duas e cinquenta e nove. O portão do Ferro-Velho São Jorge está aberto.” | **Nova.** O portão de ferro aberto à noite, com montes de sucata, e o Zinho de costas, entrando | A placa pintada pela montagem, como na Parte 3, e o relógio 02:59 |
| 8 | “Lá dentro, uma lâmpada só. E o Renato, amarrado numa cadeira.” | **Nova.** Plano aberto: uma clareira entre a sucata, uma lâmpada pendurada num fio e o Renato amarrado numa cadeira de metal, inteiro, com o lábio cortado | Círculo no Renato |
| 9 | RENATO: “Você veio? Por que você veio?” | **Nova.** O Renato amarrado, mais perto, olhando para o Zinho, surpreso e com raiva | Balão e etiqueta de nome “RENATO · seu amigo de infância · pego no seu lugar” |
| 10 | “Da sombra sai um homem de uns sessenta anos, cabelo branco, jaqueta de couro.” | **Nova.** O Ademir inteiro, saindo da sombra para a luz, calmo | Frase “O HOMEM / DO ANEL.” |
| 11 | “No dedo, o anel da foto.” | **Nova.** A mão grande com o anel grosso de ouro no dedo médio, segurando um canivete fechado, saindo da manga de couro preta | Zoom normal, círculo e etiqueta “O ANEL DA FOTO” |
| 12 | ADEMIR: “Pode me chamar de Ademir. O São Jorge é meu. E aquela mesa da foto também.” | **Nova.** O Ademir em plano médio, falando, com a mão apontando para trás. Ao fundo, a mesa de metal da foto da divisão | Balão, etiqueta de nome “ADEMIR · dono do Ferro-Velho São Jorge” e etiqueta com linha “A MESA DA FOTO” |
| 13 | “Ele corta a corda do Renato com um canivete, sem pressa.” | **Nova.** Close do canivete cortando a corda nos pulsos do Renato, atrás da cadeira, com o anel à vista | Onomatopeia “TSC” |
| 14 | ADEMIR: “Combinado é combinado. Ele sai, você fica.” | **Nova.** O Renato de pé, esfregando os pulsos, e o Ademir entre os dois, apontando o Zinho com o canivete fechado | Balão |
| 15 | ADEMIR: “Aceita um café? Acabei de passar.” | **Nova.** O Ademir servindo café de uma garrafa térmica em copinhos de plástico, na mesa de metal | Balão |
| 16 | “Você não aceita. O Renato aceita.” RENATO: “Com açúcar, se tiver.” | **Nova.** O Zinho de pé, duro, de braços cruzados. Do lado, o Renato segura o copinho com as duas mãos e sopra o café | Etiquetas “NÃO” e “SIM” e o balão do Renato |
| 17 | “No fundo do terreno, um homem acende um cigarro.” | **Nova.** Plano aberto do fundo do terreno: o carro escuro das Partes 2 e 3 e um homem encostado nele, com a chama do isqueiro como única luz | Onomatopeia “CLIC” e círculo no homem |
| 18 | “Você conhece aquele rosto. Foi ele que dirigiu o carro do assalto.” | **Nova.** Close do motorista, com o rosto iluminado pela brasa do cigarro | Etiqueta de nome “O MOTORISTA · dirigiu o carro do assalto” |
| 19 | “E aí o Ademir diz a última coisa que você esperava ouvir.” ADEMIR: “Eu não quero você preso.” | **Nova.** O Ademir se inclina para o Zinho, com a lâmpada atrás da cabeça e o rosto calmo | Balão |
| 20 | ADEMIR: “O seu parceiro sumiu com os dez milhões. Com a minha parte também.” | **Nova.** O parceiro de costas, à noite, entrando num carro com duas bolsas pesadas. O rosto dele nunca aparece | Balão, painel “A SUA PARTE R$ 0” tremendo e etiqueta “10 MILHÕES · COM ELE” |
| 21 | ADEMIR: “E você vai me levar até ele.” | **Nova.** A mão com o anel no ombro da jaqueta azul do Zinho, os dois de perfil. Repete o gesto da Parte 3, quando a mão estava no ombro do Renato | Balão |
| 22 | “Você nunca foi o culpado. Foi a isca. E continua sendo.” | **Nova.** Close do Zinho com luz de cima e as sombras do Ademir e do motorista dos lados | Carimbo “ISCA” |
| 23 | “O celular vibra no seu bolso. Três e treze. Faltam dois minutos para a foto sair.” | **Nova.** O Zinho tira o celular do bolso, baixo, escondendo-o do Ademir, que fica desfocado ao fundo. A tela fica em branco para montar “03:13 · sai em 2 min · CANCELAR” | Onomatopeia “VRRR”, relógio 03:13 em vermelho tremendo e carimbo “2 MIN” |
| 24 | “Se você cancelar, vira sócio do homem que sequestrou o Renato, contra o parceiro que ficou com tudo.” | **Nova.** O Zinho e o Ademir apertam as mãos debaixo da lâmpada, com o motorista ao fundo | “OPÇÃO 1 · CANCELAR” com prós e contras |
| 25 | “Se deixar sair, a foto chega ao jornal, e a polícia chega aqui. Com você dentro.” | **Nova.** Luzes vermelhas e azuis da polícia no portão. O Zinho está lá dentro, entre a sucata, e o Ademir e o motorista se viram para o portão | “OPÇÃO 2 · ENVIAR” com prós e contras e as estrelas de suspeita piscando |
| 26 | “Cancelar ou enviar? Comenta uma palavra só. O que a maioria escolher vira a parte cinco.” | Montada: as duas opções lado a lado | Botões CANCELAR e ENVIAR e a caixa “PARTE 5 · a maioria decide · todas as partes no perfil” |

## Personagens novos

Zinho e Renato seguem as referências da Parte 3. Os novos são estes:

- **Ademir:**
  - uns 60 anos, cabelo branco penteado para trás, bigode branco aparado e rugas fundas;
  - olhar calmo;
  - jaqueta de couro preta, a mesma manga das mãos da Parte 3, com camisa escura;
  - mãos grandes e o anel grosso de ouro no dedo médio da mão direita;
  - uma medalha de São Jorge numa corrente fina.
- **O motorista do assalto:**
  - uns 35 anos, magro, de boné escuro e barba rala;
  - jaqueta corta-vento cinza;
  - anda no carro escuro que aparece nas Partes 2 e 3.
- **O parceiro dos dez milhões:** sempre de costas, sem rosto, até a Parte 10 do arco.

## Painel que muda com a história

1. **Começo:** o painel mostra “A SUA PARTE R$ 0 · SUSPEITA ★★★★★”, como na Parte 3. Um relógio embaixo dele marca a hora de cada cena: 03:00, 02:59 e 03:13.
2. **Em “Só você pode cancelar”:** o lado esquerdo vira “A FOTO SAI ÀS 3:15”.
3. **Em “sumiu com os dez milhões”:** volta o “A SUA PARTE R$ 0”, tremendo.
4. **Em “Três e treze”:** o relógio fica vermelho e treme.

## Jornal “A VOZ DO BAIRRO”

São comentários reais da Parte 3, impressos como cartas de leitor e assinados só “— leitor”:

- “Trocar.”
- “Deixar.”
- “(…) só porque ajudou depois de arrependido faz diferença? Tem que deixar se lascar e ir proteger a família do cara.”
  - É um trecho do comentário. O começo tem um palavrão e ficou de fora.

Se chegarem comentários do TikTok e do Shorts, dá para trocar algum.

## Votação ilustrada

| Opção | Prós (verde) | Contras (vermelho) |
|---|---|---|
| **1 · CANCELAR** | O Ademir te ajuda a achar o parceiro. Chance de pegar a sua parte. | Vira sócio de um sequestrador. Continua sendo a isca. |
| **2 · ENVIAR** | O rosto do Ademir vai para o jornal. A foto vira prova. | A polícia te acha com eles. A suspeita sobe. |

## Pedido ao Codex

O pedido está em [`pedido-codex-ep04.md`](pedido-codex-ep04.md), e o Codex mostra o custo antes de executar.

- **22 desenhos.** Eles chegam com no máximo 941 × 1672 e são ampliados por `ampliar_cenas.py`. Na Parte 3, os desenhos não cobraram crédito.
- **Três gravações, uns 4 créditos:**
  - o narrador, em Charon, com uns 95 s: 2 créditos, como as narrações das Partes 2 e 3;
  - o Ademir, em Charon no estilo do cobrador, com uns 30 s: 1 crédito;
  - o Renato, em Algenib, com uns 5 s: 1 crédito.
- Os textos de cada voz estão em `narracao-ep04-*.txt`, e os parâmetros em `pedido-narracao-*-ep04.json` e `pedido-narracao-ep04.json`.

## O outro caminho, guardado: DEIXAR — “A casa da mãe”

O roteiro está em [`roteiro-ep04-deixar.txt`](roteiro-ep04-deixar.txt). Ele só volta se o DEIXAR tiver a maioria somando as três redes. Antes disso, precisa dos mesmos ajustes do TROCAR: abertura clara, resumo curto e momento leve.

- **O Zinho age:** ele não vai ao ferro-velho. Às 2:40, entra pelos fundos na casa da mãe do Renato, a **Dona Célia**, e conta a verdade a ela.
- **A pista nova:** a Dona Célia guarda numa lata de biscoito o que o Renato deixou para o Zinho: um pen drive e um bilhete, “Gravei a divisão inteira. Desculpa.”
- **A ameaça:** às 3:00, ninguém aparece no ferro-velho. Às 3:10, alguém bate na porta.
- **A reviravolta:** quem bate é o motorista do assalto, o **Toninho**. Ele é afilhado da Dona Célia e foi quem arrumou o serviço para o Renato. Agora veio buscar a madrinha a mando do Ademir.
- **Votação: ENTREGAR ou GUARDAR.**
  - Entregar o pen drive, a única prova de que o Zinho não armou nada, protege a Dona Célia.
  - Guardar a prova arrisca a Dona Célia.
- **Vozes:** o narrador e duas vozes novas, uma feminina para a Dona Célia e uma masculina para o Toninho.
