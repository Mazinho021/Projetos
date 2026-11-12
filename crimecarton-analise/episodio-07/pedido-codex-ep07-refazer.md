# Pedido para o Codex — Parte 7, refazer 6 desenhos

Criado em 12/11/2026 no Claude Code, depois que o criador viu a Parte 7 montada e apontou três erros:

1. **O rosto do Zinho mudou** nas cenas 18, 23 e 25: saiu mais realista, com o rosto comprido, os olhos estreitos e outro cabelo. Nas cenas 4, 6 e 11, ele saiu certo.
2. **O celular ficou do tamanho de um tablet** nas cenas 7 e 25, com o Zinho segurando-o lá na frente e os dedos em volta. Era a regra antiga, de 40% da largura, que o criador derrubou: agora o celular é de tamanho normal.
3. **Na cena 8, a porta de trás do carro aparece aberta e fechada ao mesmo tempo.**

**Só imagens: nenhuma voz, sem custo de créditos de voz.** Não alterar nenhum outro arquivo do projeto. Fazer tudo nesta conversa, sem abrir agentes em paralelo.

## Ordem

1. Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido.
2. Gerar as 6 cenas abaixo, uma por vez, **substituindo o arquivo de mesmo nome** em `crimecarton-analise/episodio-07/originais/`.
3. **Commit e push na `codex/crimecarton` logo depois de cada cena pronta.**
4. No fim, responder com o link do commit.

## O Zinho igual em todas as cenas (o mais importante)

- **Antes de gerar cada cena, passar ao gerador como referência visual:**
  - a folha [`../zinho-referencia-v3.png`](../zinho-referencia-v3.png);
  - as cenas boas desta parte: [`originais/cena-06-pagode.png`](originais/cena-06-pagode.png) e [`originais/cena-11-bom-dia.png`](originais/cena-11-bom-dia.png).
- **O rosto dele:** arredondado, de menino de uns 20 anos; olhos grandes e redondos, com bastante branco em volta da íris; sobrancelhas grossas, mas curtas; nariz pequeno; queixo arredondado; cabelo preto cacheado e volumoso no topo, com as laterais curtas em degradê; sem barba.
- **O traço é o cartoon 2D da série,** igual ao das cenas 4, 6 e 11: contorno escuro, cores chapadas e expressões fortes. **Nunca realista:** nada de rosto comprido, olhos estreitos e pequenos, maçãs do rosto marcadas ou cabelo em bloco.
- **A roupa:** jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, camiseta preta, calça jeans escura e tênis branco.
- **Os outros personagens** seguem as referências do [`pedido-codex-ep07.md`](pedido-codex-ep07.md): o Ademir como em `originais/cena-05-retrovisor.png` e `originais/cena-21-metade-e-sua.png`, a Dona Célia como em `originais/cena-12-olhar-pro-quarto.png` e o parceiro como em `originais/cena-15-irmao.png` e `originais/cena-17-familia-primeiro.png`.

## Regras de sempre

- Vertical 9:16, no maior tamanho que o gerador permitir, um PNG por cena, sem nenhum texto, número, logotipo ou marca d'água.
- **Os 25% de cima** só com fundo calmo; **rostos e ação entre 30% e 60% da altura**, no meio da largura; **os 20% de baixo** só com chão; nada importante na borda direita, entre 45% e 80% da altura.
- Corpo inteiro coerente com o cenário, sem nada atravessado ou fundido.
- **O celular é de tamanho normal,** como um celular de verdade na mão de um adulto, numa pose natural. A tela pode ficar virada para o personagem: a mensagem entra na montagem, num close à parte.
- A mesma luz da manhã das outras cenas da parte.

## Cena 7 — `cena-07-foto-recuperada.png`

**Fala:** “No banco de trás, você faz uma coisa que ele não vê: recupera a única foto que liga o Ademir ao assalto.”

- **Dentro do sedã preto, visto do banco da frente, virado para trás, um pouco de lado:** o Zinho sentado no banco de trás, encolhido, olhando para baixo, para o celular que segura com as duas mãos na altura do colo, escondido.
- **O celular:** de tamanho normal, entre as mãos, com a tela virada para o Zinho. A tela acende o rosto dele de baixo, com uma luz azulada fraca.
- **O rosto do Zinho:** de três quartos, concentrado e desconfiado, entre 38% e 50% da altura, no meio. Igual à referência.
- **Primeiro plano, à esquerda, desfocado:** o encosto do banco do motorista e a nuca de cabelo branco do Ademir, que não vê nada.
- **Em cima:** o teto escuro do carro. **Embaixo:** o banco e as pernas do Zinho.

## Cena 8 — `cena-08-casa-da-mae.png`

**Fala:** “O carro para numa casa que você conhece: a da Dona Célia, mãe do Renato, o seu melhor amigo.”

- **Lugar:** a casa da Dona Célia por fora, como em [`originais/cena-08-casa-da-mae.png`](originais/cena-08-casa-da-mae.png): muro baixo, portão de ferro, janela com cortina florida e o varal no quintal.
- **O carro:** o sedã preto parado na frente do portão, de lado, **com todas as portas fechadas.** Nenhuma porta aberta, nem desenhada duas vezes.
- **O Zinho:** já fora do carro, de pé na calçada, à esquerda, de corpo inteiro, olhando para a casa, de três quartos de costas e com o rosto de lado. Ele fica afastado do carro, sem encostar na porta.
- **Posição:** a casa no meio, entre 30% e 70% da altura; o Zinho entre 40% e 80%.

## Cena 18 — `cena-18-zinho-traido.png`

**Fala:** “O seu melhor amigo te levou pro assalto. O irmão dele ficou com o dinheiro. E você ficou com a culpa.”

- **Close do Zinho, de frente,** com o rosto da referência: ele entende tudo de uma vez. Sobrancelhas franzidas, olhos grandes e molhados de raiva, a boca apertada. Traído, mas sem chorar.
- **Fundo:** a cozinha clara da Dona Célia, bem desfocada, com espaço livre dos dois lados do rosto, porque a montagem põe lembranças por cima.
- **Posição:** o rosto entre 35% e 55% da altura, no meio, ocupando uns 45% da largura.

## Cena 23 — `cena-23-pergunta.png`

**Fala:** “Você entregaria o irmão do seu melhor amigo por cinco milhões?”

- **A mesma composição de [`originais/cena-23-pergunta.png`](originais/cena-23-pergunta.png):** o Zinho sentado à mesa coberta de dinheiro, as mãos juntas na frente da boca, olhando direto para a câmera, sério e dividido. Atrás dele, desfocados, a Dona Célia abraçada ao filho, à esquerda, e o Ademir de braços cruzados, à direita do meio.
- **Só o Zinho muda:** o rosto da referência, arredondado e com os olhos grandes.
- **Posição:** o rosto do Zinho entre 35% e 45% da altura, no meio; o dinheiro entre 58% e 75%.

## Cena 24 — `cena-24-opcao-entregar.png`

**Fala:** “Se entregar, o dinheiro é seu, e a Dona Célia perde um filho.”

- **Plano médio, mais perto que antes, na frente da casa da Dona Célia,** com o sedã preto parado no portão, todas as portas fechadas menos a de trás, que o Ademir segura aberta.
- **O Ademir** leva o parceiro pelo braço até essa porta. O parceiro tem as mãos amarradas à frente com corda e olha para trás, para o Zinho, sem o meio sorriso.
- **A Dona Célia,** no portão, com as mãos no rosto, chorando.
- **O Zinho,** à esquerda, na calçada, com uma bolsa preta pesada em cada mão, de cabeça baixa. O rosto da referência, entre 35% e 45% da altura.
- **Posição:** os rostos entre 32% e 50% da altura, grandes o bastante para ver as expressões.

## Cena 25 — `cena-25-opcao-soltar.png`

**Fala:** “Se soltar, você ameaça o Ademir com a foto, e vira o próximo alvo dele.”

- **Na cozinha da Dona Célia, por cima do ombro do Ademir:** o ombro de couro preto e a mão do anel fechada em primeiro plano, à esquerda, desfocados.
- **O Zinho, de frente para o Ademir, a uns dois passos,** firme, com o celular de tamanho normal numa mão só, na altura do peito, a tela virada para o Ademir e o polegar pronto para apertar. O olhar desafia o Ademir.
- **O rosto do Zinho:** o da referência, entre 35% e 45% da altura, no meio.
- **Ao fundo, pela porta dos fundos aberta:** o parceiro fugindo, e a Dona Célia segurando a porta.
- **Corpo:** o Zinho da cintura para cima, numa pose natural, sem esticar os braços para a frente.
