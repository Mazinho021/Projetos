# Perfil da série

Foto, nome e descrição do perfil novo de **A parte que faltou**, no Instagram e no TikTok. O perfil se liga ao do [@crimecarton](https://www.instagram.com/crimecarton/), em cujas histórias a série se inspira, pela foto e pela bio:

- A foto dele mostra um personagem preocupado com um saco de dinheiro, num quarto escuro iluminado por abajur. A nossa responde a ela: Zinho, preocupado, segura a roupa velha que veio na mochila no lugar da parte dele, no quarto da cena 3, à noite.
- A bio segue a mesma estrutura de linhas curtas com emoji, sem repetir as frases dele. Abre com “O assalto deu certo.”, a frase que abre o vídeo de referência e o episódio 1, e dá o crédito.

## Foto

[`foto-perfil.png`](foto-perfil.png), 1080 × 1080, recortada de [`cena-03-roupas.png`](../episodio-01/cena-03-roupas.png) por [`gerar_foto_perfil.py`](gerar_foto_perfil.py). As duas redes cortam a foto em círculo. [`previa-circular.png`](previa-circular.png) mostra esse corte em tamanho grande e nos tamanhos pequenos do feed e dos comentários, em fundo escuro e claro.

```bash
python crimecarton-analise/perfil/gerar_foto_perfil.py
```

## Nome

**A Parte Que Faltou**, com o usuário sugerido `@apartequefaltou`. A disponibilidade do usuário nas duas redes ainda precisa ser conferida.

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

## Ao publicar

- Fixar o Ep. 1 no topo do perfil nas duas redes, para o “Comece pelo Ep. 1” apontar para ele.
- A bio não promete frequência de episódios. Se houver um ritmo definido, ele pode entrar numa linha a mais no Instagram.
