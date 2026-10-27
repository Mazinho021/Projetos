# Perfil da série

Foto, nome e descrição do perfil novo de **A parte que faltou**, no Instagram e no TikTok. O perfil se liga ao do [@crimecarton](https://www.instagram.com/crimecarton/), em cujas histórias a série se inspira, pela foto e pela bio:

- A foto dele mostra um personagem preocupado com um saco de dinheiro, num quarto escuro iluminado por abajur. A nossa responde a ela: Zinho, preocupado, segura aberta a mochila que veio com roupa velha no lugar da parte dele, num quarto escuro à noite, com luz de abajur.
- A bio segue a mesma estrutura de linhas curtas com emoji, sem repetir as frases dele. Abre com “O assalto deu certo.”, a frase que abre o vídeo de referência e o episódio 1, e dá o crédito.

## Foto

As fotos vêm das ilustrações feitas no Codex para o perfil, conforme [`pedido-codex-perfil.md`](pedido-codex-perfil.md): Zinho de frente, preocupado, segurando aberta a mochila com roupa velha, num quarto escuro com luz de abajur.

- [`foto-perfil.png`](foto-perfil.png), a recomendada: ele olha para a câmera, o que chama mais atenção no feed e continua legível em tamanho pequeno. Vem de [`ilustracao-perfil.png`](ilustracao-perfil.png).
- [`foto-perfil-b.png`](foto-perfil-b.png): ele olha para dentro da mochila. Vem de [`ilustracao-perfil-b.png`](ilustracao-perfil-b.png).

[`gerar_foto_perfil.py`](gerar_foto_perfil.py) recorta as duas em 1080 × 1080, um pouco mais perto do rosto. As duas redes cortam a foto em círculo. [`previa-circular.png`](previa-circular.png) mostra esse corte nas duas versões, em tamanho grande e nos tamanhos pequenos do feed e dos comentários, em fundo escuro e claro. O recorte provisório da cena 3, usado antes das ilustrações, ficou no histórico do Git.

```bash
python crimecarton-analise/perfil/gerar_foto_perfil.py
```

## Nome

O criador vai escolher entre um nome no estilo de “Crime Cartoon”, o nome do perfil do @crimecarton, e o nome da série:

- **Golpe Cartoon** (`@golpecartoon`), a sugestão principal: tem o ritmo de “Crime Cartoon”, e golpe é o que Zinho levou.
- **Assalto Cartoon** (`@assaltocartoon`), a ligação mais direta com o assalto.
- **Cilada Cartoon** (`@ciladacartoon`), pela armadilha que o amigo à porta pode estar armando.
- **A Parte Que Faltou** (`@apartequefaltou`), o nome da série.

Com um nome “Cartoon”, “A parte que faltou” continua como título da série no texto dos posts. A bio serve para qualquer um deles. O nome não deve conter “Crime Cartoon”, para o perfil não ser confundido com o dele. A disponibilidade dos usuários nas duas redes ainda precisa ser conferida.

## Bio do Instagram

Limite de 150 caracteres. Esta tem 137, ou 141 se cada emoji contar como dois:

```
🎒 O assalto deu certo. A parte do Zinho, não.
💬 Você decide nos comentários
🧩 Inspirado nas histórias de @crimecarton
👇 Comece pelo Ep. 1
```

No Instagram, o @crimecarton vira link para o perfil dele.

## Bio do TikTok

Limite de 80 caracteres. Esta tem 75, ou 77 se cada emoji contar como dois:

```
🎒 A parte do Zinho não veio. Você decide.
🧩 Inspirado no Insta @crimecarton
```

“no Insta” indica que o @crimecarton é o perfil do Instagram: não foi encontrada conta dele no TikTok. Se houver uma com o mesmo nome, “no Insta” pode sair.

## Canal do YouTube

Para o canal próprio da série no YouTube, chamado Golpe Cartoon. O limite da descrição é de 1.000 caracteres, e esta tem 530:

```
Golpe Cartoon é uma série de histórias animadas de suspense sobre crime, golpes e traição.

🎒 A parte que faltou: o assalto deu certo, mas a parte do Zinho não veio. Agora ele precisa descobrir quem armou pra ele, e quem está batendo na porta.

💬 Você decide o próximo passo: no fim de cada parte, a resposta mais votada nos comentários vira a parte seguinte.

📺 Comece pela Parte 1 e assista na ordem pela playlist da série.

🧩 Inspirado nas histórias do crimecarton, no Instagram.

🔔 Inscreva-se para não perder a próxima parte.
```

O crimecarton vai sem @ porque, no YouTube, o @ aponta para um canal com esse nome. Palavras-chave do canal, em YouTube Studio → Configurações → Canal:

```
história animada, série animada, suspense, crime, assalto, golpe, traição, desenho animado, Zinho, A parte que faltou
```

Criar a playlist “A parte que faltou” com as partes em ordem e pôr os links do Instagram e do TikTok na seção de links do canal. A foto do canal é a mesma do perfil, [`foto-perfil.png`](foto-perfil.png).

## Ao publicar

- Fixar o Ep. 1 no topo do perfil nas duas redes, para o “Comece pelo Ep. 1” apontar para ele.
- A bio não promete frequência de episódios. Se houver um ritmo definido, ele pode entrar numa linha a mais no Instagram.
