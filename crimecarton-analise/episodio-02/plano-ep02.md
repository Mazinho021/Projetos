# Parte 2 — A dívida

Roteiro em [`roteiro-ep02.txt`](roteiro-ep02.txt), com a voz de cada fala. O episódio montado tem **2 min 04 s**: a vinheta da Parte 1, 93 s do narrador, 16 s do amigo, as pausas de montagem (os três toques do telefone, a vibração, o carro parando e as revelações) e 2 s de final. Fica dentro da regra de 2 a 3 minutos. A montagem está em [`montagem/`](montagem/README.md).

## Estrutura

| Trecho | Voz | Imagem | Na tela |
|---|---|---|---|
| Vinheta | Áudio da Parte 1, palavras 0–16 | `../episodio-01/cena-01-base.png`, a mesma em todas as partes, com “PARTE 2” no topo | “O ASSALTO / DEU CERTO.”, o contador até R$ 10.000.000, e a tela preta com “VOCÊ FICOU COM / O ROSTO NO JORNAL.” e as cinco estrelas de suspeita enchendo |
| Aviso | “Chegou agora? A parte um está no perfil.” | A mesma da vinheta | “CHEGOU AGORA?”, “A PARTE 1 TÁ NO PERFIL” e “@golpecartoon”, com a seta para baixo, onde os apps mostram o perfil |
| Votação | “Vocês decidiram: abrir.” | Fundo escuro | “PARTE 1 · VOCÊS VOTARAM”, barras “ABRIR 86%” e “NÃO ABRIR 14%” (6 de 7 votos) e carimbo “ABRIR” |
| PISTA 1 · A VERSÃO DELE | Narrador e amigo | `cena-01-porta-aberta`, `cena-02-luz-apagada`, `cena-03-versao` | “R$ 80.000” contando, “PRA QUEM BANCOU / O ASSALTO.”, a lista “A DÍVIDA → R$ 80 MIL / A SAÍDA → ALGUÉM DE FORA / A CULPA → VOCÊ”, a TV da Parte 1 com o carimbo “FOI ELE” e “ELES SABIAM ONDE / A MINHA MÃE MORA.” |
| PISTA 2 · A FOTO DA DIVISÃO | Narrador | Cartão de celular com `cena-04-foto-divisao`, ampliado até o calendário | “A NOITE / DA DIVISÃO.” e, no calendário, “FERRO-VELHO SÃO JORGE” com telefone parcial, os dois aplicados por código |
| O teste | Narrador e três toques de chamada | `cena-05-ligacao` e a tela da ligação: “chamando…”, o número com dígitos escondidos, a chamada atendida e encerrada | “FERRO-VELHO / SÃO JORGE.”, “O LUGAR / EXISTE.” e o carimbo “VERDADE” |
| PISTA 3 · A MENSAGEM | Narrador | `cena-06-celular-mesa`, com a mensagem “COBRANÇA / Já tá com ele?” pintada por código na tela do celular dele | Borda vermelha |
| Virada | Narrador | `cena-07-carro` | “DE FAROL / APAGADO.” |
| O nome | “Ele vendeu o seu nome. Agora você escolhe o dele.” | `cena-08-retrato-amigo` | “ELE VENDEU / O SEU NOME. / AGORA VOCÊ / ESCOLHE O DELE.” |
| Votação | Pedido gravado à parte: “E com aquele carro lá fora: fugir ou ficar? Comenta a sua escolha e um nome. O mais curtido vira o nome dele na parte três.” | `cena-07-carro`, escurecida | “FUGIR OU / FICAR?”, “COMENTA A SUA ESCOLHA” com os botões FUGIR e FICAR, a caixa de comentário vazia “e um nome pra ele…” e a caixa “PARTE 3 · vence a maioria e o nome mais curtido” |

O painel do topo continua com “A SUA PARTE R$ 0 · SUSPEITA ★★★★★”. O pedido de comentário dura uns 9 s, mais que os 2 a 3 s da lição da Parte 1, porque traz as duas votações e a regra do nome; os botões, a caixa e as frases entram com a fala para encurtar a espera.

## Votações

Por decisão do criador, em 28/10/2026, a Parte 2 tem duas votações, como a Parte 1 teve ABRIR ou NÃO ABRIR. A primeira é FUGIR ou FICAR, e a maioria decide; ela muda a Parte 3, conforme [`producao-zinho.md`](../producao-zinho.md). A segunda é o nome do amigo. O nome é livre, por decisão do criador: sem opções. Vence o comentário com o nome mais curtido, somando as redes. Se o vencedor for ofensivo ou não funcionar como nome de personagem, vale o seguinte mais curtido. A Parte 3 abre com as barras de FUGIR e FICAR, no bloco “PARTE 2 · VOCÊS VOTARAM”, e com o nome vencedor.

## Versões

Instagram e vertical (TikTok e Shorts), como na Parte 1, mais a capa “PARTE 2” em `capas/gerar_capas.py` e os trechos para o TikTok.
