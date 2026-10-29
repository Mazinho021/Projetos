# Ideia — site da série e “entre na história”

Proposta de 28/10/2026, a pedido do criador, para testar uma renda direta com a série. O criador mandou seguir em 28/10/2026. O site está no ar em **https://golpecartoon.netlify.app**, desde 28/10/2026. A página fica em [`site/index.html`](site/index.html), e a mesma página tem uma prévia privada no Claude.

Na terceira versão, também de 28/10/2026, o site segue de perto o crimecartoon.com, como pediu o criador, com nomes, textos e imagens próprios e sem contar as histórias. Na quarta, as cores passaram a ser as do Zinho, a pedido do criador, para o site não lembrar tanto o de referência:

- o marrom do quarto à noite no fundo;
- o vermelho do moletom nos botões e no que se clica;
- o azul da jaqueta na faixa de avisos, no relógio, nos créditos e nos ícones;
- o caramelo do abajur nos detalhes.

A faixa de avisos leva as duas listras brancas da manga da jaqueta. Na quinta versão, o passe passou a ser pago pelo Mercado Pago, com Pix ou cartão de crédito, também a pedido do criador. Na sexta, de 29/10/2026, o pagamento passou para dentro do próprio site, porque o criador não queria que a pessoa saísse para a página do Mercado Pago. O Pix abre numa janela com o QR Code e o copia e cola, como no site de referência. A lista de aliados se monta sozinha com os pagamentos aprovados. A página tem as seções abaixo, nesta ordem:

- **Topo e faixa azul:** a marca, o botão “Quero ser aliado” e uma faixa azul que roda com as vagas, o prazo, a votação aberta e o preço.
- **Abertura:** “O assalto deu certo. A sua parte, não.”, com o fim da Parte 2 num celular e o aviso das vagas com contagem regressiva.
- **Votação aberta:** FUGIR ou FICAR, o pedido do nome do amigo e o quadro “O caso até aqui”.
- **Passe de aliado:** R$ 9,90 por parte, no Pix ou no cartão, com o que o passe dá. Mostra também:
  - uma cena com “@seuperfil” na tela do celular, para mostrar onde o @ aparece;
  - a legenda do post;
  - a lista dos 30 aliados da Parte 3, com o número de cada um;
  - o formulário, com um botão para o Pix e outro para o cartão, que abrem a janela de pagamento.
- **Assista do começo:** as capas das partes, com o carimbo da escolha de cada votação, que levam aos vídeos.
- **Final:** as perguntas, os termos e a privacidade, e o rodapé.

Por decisão do criador, o site não cita o @crimecarton.

O Mercado Pago está ligado desde 28/10/2026, direto com o token de produção. No mesmo dia, o criador fez a primeira compra de verdade, um Pix de R$ 9,90 com o @ `teste.golpe`. O pagamento foi aprovado e o @ ficou fora da lista, como devia. Em 29/10/2026, o criador aumentou as vagas da Parte 3 de 10 para 30, no site e no vídeo que chama aliados ([`chamada-aliado/`](chamada-aliado/)). Faltam duas coisas do criador:

- a confirmação do prazo;
- os links dos Reels.

## Como funciona

1. **O link na bio** leva ao site da série: a votação aberta, o passe de aliado e as capas das partes, que abrem os vídeos.
2. **Assistir e votar é de graça.** A votação continua nos comentários, igual para todos, porque é ela que dá engajamento aos vídeos. O passe não vende voto.
3. **O passe de aliado custa R$ 9,90 por parte.** Quem paga tem o @ dentro do episódio, num lugar escolhido pela produção:
   - os contatos ou uma mensagem no celular do Zinho;
   - um muro da rua;
   - a reportagem da TV;
   - os créditos do fim.

   O @ também vai na legenda do post no Instagram, e o aliado ganha um número (#001, #002…), que guarda nas próximas partes. A legenda e os créditos com os @ servem de prova social para os próximos compradores.
4. **As vagas são limitadas por parte:** 10 na Parte 3, que fecham com a votação da Parte 2, em 30 de outubro, às 21h. Quem paga depois do prazo, ou com a lista cheia, entra na parte seguinte.

Os lugares do @ são feitos por código, como os textos de tela e o calendário da Parte 2, então entregar não custa crédito.

## Pagamento

O pagamento acontece no próprio site, processado pelo Mercado Pago, com Pix e cartão de crédito. O boleto fica de fora, porque pode levar dias e passar do prazo da lista. O cartão de débito também, a pedido do criador, em 28/10/2026, porque o Pix já faz o papel dele. O caminho de uma compra é este:

1. A pessoa preenche o @, o e-mail e a autorização, e toca em “Pagar R$ 9,90 no Pix” ou em “Pagar com cartão de crédito”. O total aparece logo acima dos botões.
2. A função `/api/checkout` confere os dados e vê em que parte o passe vai entrar. Ela recusa um @ que já está na lista daquela parte.
3. **No Pix,** a função cria o pagamento no Mercado Pago com a referência `aliado|<parte>|<@>` e devolve o código copia e cola e o QR Code. A página mostra os dois numa janela, com o tempo para pagar.
   - O Pix vence em 30 minutos, e um Pix sem pagamento não segura vaga.
   - A janela pergunta a `/api/pagamento` se o Pix foi pago a cada 4 segundos, e na hora em que a pessoa volta do app do banco.
   - Quando o pagamento é aprovado, a janela mostra “Pagamento aprovado” e o número de aliado, e a lista da página se atualiza na hora.
4. **No cartão,** a janela mostra o formulário de cartão do próprio Mercado Pago (o Card Payment Brick), nas cores do site. Os dados do cartão vão direto ao Mercado Pago, que devolve um código de uso único. A função cobra esse código, com o valor e uma parcela definidos no servidor, e a janela mostra a aprovação ou o motivo da recusa.

O formulário de cartão só aparece com a chave pública ligada (ver “Ligar o Mercado Pago”). Sem ela, ou se o formulário não carregar, o cartão abre a página do Mercado Pago, o Checkout Pro, como antes. Em 29/10/2026, o criador decidiu deixar o cartão na página do Mercado Pago, sem a chave pública.

O Pix aberto fica guardado no aparelho até ser pago ou vencer. Se o navegador do Instagram recarregar a página na volta do app do banco, a janela abre de novo e confirma o pagamento. O mesmo @ com o mesmo e-mail reabre o mesmo Pix, em vez de criar outro.

Sem JavaScript, o formulário vai direto para `/api/checkout`, que leva à página do Mercado Pago ou volta ao formulário com o erro. Quem paga na página do Mercado Pago volta ao site, e a função `/api/pagamento` confere o pagamento, em vez de confiar no endereço da volta. O `auto_return` só vai na preferência quando o site está num endereço `https` público, porque o Mercado Pago recusa a preferência com endereço local.

A lista vem dos próprios pagamentos, sem banco de dados.

- **Montagem:** a função `/api/aliados` busca no Mercado Pago os pagamentos feitos desde 28/10 e separa os passes aprovados. A resposta fica guardada por um minuto, então um pagamento aparece na página em até um minuto.
- **Números:** cada aliado tem o número do seu primeiro passe aprovado. Um passe devolvido sai da lista, mas o número continua reservado, para ninguém mudar de número.
- **Vagas:** quando uma parte enche, os passes seguintes vão para a próxima.
- **Correções:** um @ digitado errado se corrige em `correcoes`, no arquivo `site/netlify/lib/serie.mjs`, com `{ errado: 'certo' }`. Um @ ofensivo sai da lista com `{ ofensivo: '' }`, e o valor deve ser devolvido. O @ `teste.golpe` já está fora da lista: é o @ das compras de teste do criador, que não ocupam vaga nem número.

A integração segue os guias do plugin oficial do Mercado Pago para o Claude, instalado em 28/10/2026. O Pix e o formulário de cartão usam a API de pagamentos (`/v1/payments`), como o guia pede para o Card Payment Brick, e assim todos os passes aparecem na mesma busca de pagamentos que monta a lista.

O plugin tem três checagens:

- A checagem do servidor do Checkout Pro (`validate-checkout-pro-server.mjs`) passa.
- A do botão do Checkout Pro (`validate-checkout-cta.mjs`) deixou de valer, porque os botões abrem a janela.
- A do formulário de cartão (`validate-bricks-integration.mjs`) pede uma página separada para o formulário, e o site usa a janela, a pedido do criador. Os outros avisos dela procuram nomes e trechos de código que o site escreve de outro jeito, sem apontar falha.

Os testes ficam em `site/testes/`:

```bash
node --test crimecarton-analise/site/testes/*.test.mjs
```

### Ligar o Mercado Pago

1. Entrar em https://www.mercadopago.com.br/developers/panel/app com a conta do Mercado Pago que vai receber o dinheiro. Criar uma aplicação para pagamentos online com o Checkout Pro.
2. Em “Credenciais de produção”, ativar as credenciais, informando o ramo e o site `https://golpecartoon.netlify.app`, e copiar o **Access Token**, que começa com `APP_USR-`.
3. Cadastrar uma chave Pix na mesma conta, no app do Mercado Pago. Sem chave, a página de pagamento não mostra o Pix.
4. No Netlify, no projeto `golpecartoon`, ir em **Project configuration → Environment variables** e criar `MP_ACCESS_TOKEN` com o token, marcado como secreto e com escopo **Functions**.
5. Para o cartão também ser pago dentro do site, copiar a **Public Key** da mesma página de credenciais de produção e criar no Netlify a variável `MP_PUBLIC_KEY` com ela. A Public Key também começa com `APP_USR-`, mas é mais curta que o token e não é secreta. A função só entrega à página um valor com o formato de chave pública, então um token posto ali por engano não chega à página.
6. Publicar de novo, como em “Publicar” abaixo, porque as variáveis só valem a partir da publicação seguinte. Depois disso, os botões de pagamento voltam a funcionar.

Para testar antes de vender, usar primeiro o token da aba **Teste**:

1. Na página de pagamento, entrar com uma conta de comprador de teste, criada no painel em “Contas de teste”.
2. Pagar com um cartão de teste: Visa 4235 6477 2802 5682 ou Mastercard 5031 4332 1540 6351, CVV 123, validade 11/30, CPF 12345678909. O nome no cartão define o resultado: APRO aprova e FUND recusa por saldo.
3. Depois, trocar pelo token da aba **Produção**.

Enquanto o token de teste estiver no site, ninguém consegue pagar de verdade, então o teste deve ser rápido e antes de divulgar o link.

O token dá acesso à conta, então não vai no código nem no GitHub.

Para uma compra de teste com o token de produção, usar o @ `teste.golpe` e um e-mail que não seja o da conta do Mercado Pago que recebe, porque ela não pode pagar a si mesma. Na página do Mercado Pago, isso também quer dizer não entrar nessa conta: o melhor é uma aba anônima. No teste de 28/10, o Itaú mostrou “Instabilidade no banco de destino” na primeira tentativa, e o mesmo Pix foi aprovado depois.

## Atualizar a cada parte

Quando uma parte abre a sua lista, mudar `parte`, `vagas` e `fecha` em `site/netlify/lib/serie.mjs`. Mudar também os mesmos valores no começo do script da página, em `CONFIG`, que valem enquanto a lista não carrega. No HTML:

1. **A capa.** Gravar a capa de `capas/` em `site/img/parte-NN.jpg`, em 540 × 960, e copiar um item da lista “Assista do começo”. Na parte que acabou de ser votada, o carimbo azul “Em votação” vira o carimbo com a escolha e a porcentagem.
2. **A votação.** Trocar a pergunta, as duas opções e o link do Reel no cartão da votação.
3. **Os textos fixos.** Trocar o número da parte e o prazo na faixa azul, no aviso das vagas e nos créditos.
4. **O link do Reel.** Até o criador mandar os links dos Reels, as capas e os botões de voto abrem o perfil.

As imagens do site vêm do próprio material da série:

- `votacao-parte-02.jpg` é o quadro de 131 s da Parte 2 vertical, com FUGIR ou FICAR.
- `aliado-na-cena.jpg` é a cena 6 da Parte 2 com a tela de bloqueio feita pelo `on_screen()` do renderizador, com “@seuperfil · Tô contigo, Zinho.” no lugar da mensagem da cobrança.
- `perfil.jpg`, `icone-32.png` e `icone-180.png` vêm da foto de perfil.
- `compartilhar.jpg` (1200 × 630) é a imagem das prévias de link no WhatsApp e no direct, com o Zinho da capa da Parte 1 e as cores do site.

## Publicar

O site é o projeto `golpecartoon` no Netlify do criador. Fica aberto ao público em produção, e as prévias de publicação pedem o login da equipe. A pasta `site/` é publicada inteira:

- **Construção:** o Netlify roda `node montar.mjs`, que embrulha `index.html` num documento completo em `dist/`. O embrulho leva as tags de prévia de link e os ícones, e as imagens vão junto.
- **Funções:** as funções de `netlify/functions/` viram `/api/checkout`, `/api/aliados` e `/api/pagamento`.

Para publicar de novo, pedir ao Claude, que chama a operação `deploy-site` do Netlify para o projeto e roda o comando que ela devolve dentro de `crimecarton-analise/site/`. A prévia no Claude usa o mesmo `index.html`, mas nela o pagamento e a lista não funcionam, porque não há funções.

## Cuidados

- Dizer com clareza o que a pessoa compra, em que parte o @ entra e até quando.
- Compra pela internet tem 7 dias de arrependimento (art. 49 do Código de Defesa do Consumidor). A devolução se faz no próprio Mercado Pago, no mesmo meio de pagamento, e tira o @ da lista.
- Só @ que a pessoa autoriza. Recusar @ ofensivo, de marca ou de outra pessoa, e devolver o valor.
- O Mercado Pago cobra uma taxa por venda, maior no cartão do que no Pix. As taxas atuais estão no app.
- Manter no site o aviso de que imagens e vozes são feitas com IA. Por decisão do criador, em 28/10/2026, o site não cita o @crimecarton.
- No TikTok, a conta pessoal com mais de mil seguidores já pode pôr link na bio. Não mudar para conta comercial, que perde o Programa de Recompensas.
- A renda precisa ser declarada; se crescer, vale abrir um MEI.

## Teste

Começar com a Parte 3: 30 vagas a R$ 9,90 até 30 de outubro, às 21h. Medir três coisas:

- os cliques no link da bio, nos insights do Instagram;
- as visitas ao site;
- as compras.

Se vender, manter nas próximas partes e testar um nível maior, como um personagem desenhado com o rosto da pessoa. Se não vender, mudar a oferta ou o preço.
