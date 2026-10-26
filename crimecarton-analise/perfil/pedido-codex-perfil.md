# Pedido para o Codex — ilustração do perfil

**Entregue em 26/10/2026** (commit “Adiciona ilustrações de perfil de Zinho e variação do olhar”), com a variação. As duas viraram `foto-perfil.png` e `foto-perfil-b.png`.

Criado em 26/10/2026 no Claude Code, que não tem gerador de imagens. É uma ilustração, com uma variação opcional. Não alterar nenhum outro arquivo do projeto.

## Ilustração do perfil

É a foto de perfil da série no Instagram e no TikTok. As duas redes cortam a imagem em círculo e a mostram pequena, com uns 40 px nos comentários. Por isso o rosto precisa ser grande, o desenho simples e o personagem destacado do fundo. A foto atual, [`foto-perfil.png`](foto-perfil.png), é um recorte provisório da cena 3.

- **Ideia:** responder à foto de perfil do @crimecarton, em cujas histórias a série se inspira. Nela, um personagem preocupado segura um saco de dinheiro num quarto escuro iluminado por abajur. Aqui, Zinho segura aberta a mochila da divisão, com roupa velha amassada saindo dela e nenhum dinheiro. Não copiar o personagem nem a imagem do @crimecarton.
- **Referência:** rosto, cabelo e roupa de [`zinho-referencia-v3.png`](../zinho-referencia-v3.png), no mesmo traço cartoon 2D das cenas do episódio 1, como [`cena-03-roupas.png`](../episodio-01/cena-03-roupas.png): contorno escuro, cores chapadas e sombra suave.
- **Enquadramento:** do peito para cima, de frente e bem perto. A cabeça ocupa cerca de 40% da altura e fica no centro. Tudo o que importa cabe no círculo central, longe dos cantos. A mochila preta, igual à da referência, aparece embaixo, segura aberta com as duas mãos na altura do peito, com uma camiseta cinza velha pendurada para fora.
- **Expressão:** preocupado, sobrancelhas erguidas, olhando direto para a câmera, como quem acabou de descobrir que a mochila veio sem a parte dele.
- **Luz:** quarto escuro à noite, iluminado por um abajur de luz âmbar de um dos lados, com um contorno de luz no cabelo e no ombro. O fundo é escuro e simples, no máximo com uma janela desfocada e luzes da cidade.
- **Figurino:** cabelo preto cacheado no topo e laterais em degradê, rosto sem barba, jaqueta azul-marinho com capuz vermelho e faixas brancas, camiseta preta.
- **Formato:** quadrado 1:1, com pelo menos 1024 × 1024 px. Sem texto, logotipo, moldura ou marca d'água.
- **Arquivo:** salvar como `crimecarton-analise/perfil/ilustracao-perfil.png`.
- **Variação opcional:** a mesma cena com Zinho olhando para dentro da mochila em vez de para a câmera, salva como `crimecarton-analise/perfil/ilustracao-perfil-b.png`.

Prompt pronto, para usar com `zinho-referencia-v3.png` anexada:

```
Ilustração quadrada para foto de perfil, no mesmo traço cartoon 2D da referência anexada (contorno escuro, cores chapadas, sombra suave). Zinho, o mesmo personagem da referência: cabelo preto cacheado no topo com laterais em degradê, rosto sem barba, jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, camiseta preta. Do peito para cima, de frente e bem perto, com a cabeça no centro ocupando cerca de 40% da altura. Ele segura aberta, na altura do peito e com as duas mãos, uma mochila preta da qual sai uma camiseta cinza velha e amassada; não há dinheiro. Expressão preocupada, sobrancelhas erguidas, olhando direto para a câmera. Quarto escuro à noite, iluminado por um abajur de luz âmbar de um lado, com contorno de luz no cabelo e no ombro; fundo escuro e simples, com no máximo uma janela desfocada com luzes da cidade. Composição centrada que funcione recortada em círculo e em tamanho pequeno. Sem texto, logotipo, moldura ou marca d'água.
```

## Entrega

Atualizar a branch `codex/crimecarton` com a `claude/ecstatic-brown-xb2qxd`, que já contém este pedido. Fazer commit e push da ilustração na `codex/crimecarton` do repositório `Mazinho021/Projetos` e responder com a lista dos arquivos enviados. O Claude Code transforma a ilustração escolhida na foto de perfil, com a prévia do corte circular.
