# Ideia — site da série e “entre na história”

Proposta de 28/10/2026, a pedido do criador, para testar uma renda direta com a série. O criador mandou seguir em 28/10/2026. O site está em [`site/index.html`](site/index.html), com prévia privada no Claude.

Na terceira versão, também de 28/10/2026, o site segue de perto o crimecartoon.com, como pediu o criador, com nomes, textos e imagens próprios e sem contar as histórias. Na quarta, as cores passaram a ser as do Zinho, a pedido do criador, para o site não lembrar tanto o de referência:

- o marrom do quarto à noite no fundo;
- o vermelho do moletom nos botões e no que se clica;
- o azul da jaqueta na faixa de avisos, no relógio, nos créditos e nos ícones;
- o caramelo do abajur nos detalhes.

A faixa de avisos leva as duas listras brancas da manga da jaqueta. A página tem as seções abaixo, nesta ordem:

- **Topo e faixa azul:** a marca, o botão “Quero ser aliado” e uma faixa azul que roda com as vagas, o prazo e a votação aberta.
- **Abertura:** “O assalto deu certo. A sua parte, não.”, com o fim da Parte 2 num celular e o aviso das vagas com contagem regressiva.
- **Votação aberta:** FUGIR ou FICAR, o pedido do nome do amigo e o quadro “O caso até aqui”.
- **Passe de aliado:** R$ 9,90 por parte, no Pix, com o que o passe dá. Mostra também:
  - uma cena com “@seuperfil” na tela do celular, para mostrar onde o @ aparece;
  - a legenda do post;
  - a lista dos 10 aliados da Parte 3;
  - o formulário e o passo do Pix.
- **Assista do começo:** as capas das partes, com o carimbo da escolha de cada votação, que levam aos vídeos.
- **Final:** as perguntas, os termos e a privacidade, e o rodapé.

Por decisão do criador, o site não cita o @crimecarton. O formulário (@, e-mail e autorização) usa os formulários do Netlify. Depois de enviado, ele mostra a chave Pix e pede o comprovante no direct.

Faltam quatro coisas do criador:

- a chave Pix;
- a confirmação do prazo e das vagas;
- os links dos Reels;
- a autorização para publicar.

## Como funciona

1. **O link na bio** leva ao site da série: a votação aberta, o passe de aliado e as capas das partes, que abrem os vídeos.
2. **Assistir e votar é de graça.** A votação continua nos comentários, igual para todos, porque é ela que dá engajamento aos vídeos. O passe não vende voto.
3. **O passe de aliado custa R$ 9,90 por parte.** Quem paga tem o @ dentro do episódio, num lugar escolhido pela produção:
   - os contatos ou uma mensagem no celular do Zinho;
   - um muro da rua;
   - a reportagem da TV;
   - os créditos do fim.

   O @ também vai na legenda do post no Instagram, e o aliado ganha um número (#001, #002…), que guarda nas próximas partes. A legenda e os créditos com os @ servem de prova social para os próximos compradores.
4. **As vagas são limitadas por parte:** 10 na Parte 3, que fecham com a votação da Parte 2, em 30 de outubro, às 21h. Quem paga depois entra na parte seguinte.

Os lugares do @ são feitos por código, como os textos de tela e o calendário da Parte 2, então entregar não custa crédito.

## Atualizar a cada parte

O que muda toda parte fica no começo do script, em `CONFIG`:

| Campo | O que guarda |
|---|---|
| `fecha` | A data e a hora em que as vagas e a votação fecham. |
| `vagas` | O número de vagas da parte. |
| `aliados` | Os @ confirmados, na ordem do Pix. |
| `proximoNumero` | O número do próximo aliado novo. |
| `chavePix` | A chave aleatória do Pix. |

A contagem, a lista dos créditos, a legenda e o número do próximo aliado saem daí. No HTML, a cada parte nova:

1. **A capa.** Gravar a capa de `capas/` em `site/img/parte-NN.jpg`, em 540 × 960, e copiar um item da lista “Assista do começo”. Na parte que acabou de ser votada, o carimbo azul “Em votação” vira o carimbo com a escolha e a porcentagem.
2. **A votação.** Trocar a pergunta, as duas opções e o link do Reel no cartão da votação.
3. **Os textos fixos.** Trocar o número da parte e o prazo na faixa azul, no aviso das vagas e nos créditos.
4. **O link do Reel.** Até o criador mandar os links dos Reels, as capas e os botões de voto abrem o perfil.

As imagens do site vêm do próprio material da série:

- `votacao-parte-02.jpg` é o quadro de 131 s da Parte 2 vertical, com FUGIR ou FICAR.
- `aliado-na-cena.jpg` é a cena 6 da Parte 2 com a tela de bloqueio feita pelo `on_screen()` do renderizador, com “@seuperfil · Tô contigo, Zinho.” no lugar da mensagem da cobrança.
- `perfil.jpg` é a foto de perfil.

## Publicar

Hoje o site só existe na prévia privada. Para publicar, por exemplo no Netlify, que já está conectado a esta sessão, com um endereço como `golpecartoon.netlify.app` ou um domínio próprio:

1. Embrulhar `index.html` com `<!doctype html>`, `<html lang="pt-BR">`, `<head>` com charset, viewport e as tags de prévia de link (título, descrição e imagem), e `<body>`, porque a prévia já faz esse embrulho e a página vem sem ele.
2. Pôr a chave Pix em `CONFIG`.
3. Conferir se o Netlify detectou o formulário `aliados`.

## Cuidados

- Dizer com clareza o que a pessoa compra, em que parte o @ entra e até quando.
- Compra pela internet tem 7 dias de arrependimento (art. 49 do Código de Defesa do Consumidor), então devolver o valor pelo mesmo Pix.
- Só @ que a pessoa autoriza. Recusar @ ofensivo, de marca ou de outra pessoa, e devolver o valor.
- Manter no site o aviso de que imagens e vozes são feitas com IA. Por decisão do criador, em 28/10/2026, o site não cita o @crimecarton.
- No TikTok, a conta pessoal com mais de mil seguidores já pode pôr link na bio. Não mudar para conta comercial, que perde o Programa de Recompensas.
- A renda precisa ser declarada; se crescer, vale abrir um MEI.
- O Netlify gratuito aceita 100 envios de formulário por mês. Por isso a votação do site manda comentar no Reel, em vez de usar um formulário, e deixa os envios para os aliados.

## Teste

Começar com a Parte 3: 10 vagas a R$ 9,90 até 30 de outubro, às 21h. Medir três coisas:

- os cliques no link da bio, nos insights do Instagram;
- as visitas ao site;
- as compras.

Se vender, manter nas próximas partes e testar um nível maior, como um personagem desenhado com o rosto da pessoa. Se não vender, mudar a oferta ou o preço.
