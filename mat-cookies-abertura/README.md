# Abertura vintage · Mat Cookies & Coffee

Animação de abertura do site, em estilo de rótulo antigo e filme de cinema antigo. Ela dura uns 7 segundos:

1. o “projetor” liga, com granulado e um leve tremor de filme;
2. surgem os raios de sol e a moldura, e o selo se monta;
3. a xícara aparece com vapor, os grãos caem e o cookie entra rolando;
4. o nome **Mat** é escrito à mão, a faixa **COOKIES & COFFEE** se abre e o carimbo **FORNADA DO DIA** bate;
5. uma máquina de escrever bate “Pode entrar, o café está passando…”;
6. a íris de cinema fecha no selo e abre já mostrando o site.

## O que tem aqui

| Arquivo | Para quê |
| --- | --- |
| `previa.html` | Abra no navegador para ver a abertura sobre um site de exemplo. O botão “Ver a abertura de novo” repete. |
| `abertura-mat.js` | **O arquivo que vai no site.** Arquivo único (214 KB), com fontes, textura e desenho dentro. |
| `videos/abertura-mat-1920x1080.mp4` | Vídeo para computador (6,6 s, 3,3 MB). Termina com a tela escura. |
| `videos/abertura-mat-1080x1920.mp4` | Vídeo em pé, para celular (6,6 s, 2,9 MB). |
| `capa/` | Imagem parada do selo pronto, nos dois formatos. |
| `fonte/` e `ferramentas/` | Arquivos de origem, para mudar e gerar tudo de novo. |

## Como colocar no site

**Site com código próprio** (HTML, Netlify, feito com IA etc.):

1. copie `abertura-mat.js` para a pasta do site;
2. cole esta linha **logo depois da tag `<body>`** de cada página:

```html
<script src="abertura-mat.js"></script>
```

Pronto. Também funciona dentro do `<head>`. Nos dois lugares, o site só aparece depois da abertura, sem “piscar” antes.

**WordPress:** use um plugin de código, como o WPCode. Crie um trecho do tipo JavaScript, cole todo o conteúdo de `abertura-mat.js` e escolha a posição logo depois de `<body>`.

**Wix, Shopify, Nuvemshop, Canva e parecidos:** se a plataforma não deixar colocar código próprio, use o vídeo MP4 na primeira seção da página, com reprodução automática e sem som.

## Como ela se comporta

- Aparece **uma vez por visita**. Se a pessoa recarregar ou trocar de página, não repete. Numa aba nova, aparece de novo.
- Tem o botão **Pular**, no canto de baixo.
- A rolagem da página fica parada enquanto ela toca.
- No celular ou computador configurado para **reduzir movimento**, aparece o selo pronto, parado, por 2 segundos.
- **Para testar de novo**, abra o site com `?abertura` no fim do endereço (exemplo: `meusite.com/?abertura`).
- Quando ela termina, o site recebe o evento `mat-abertura:fim`, caso alguma animação do site deva começar depois dela.

## Mudar os textos

Não precisa mexer no arquivo. Coloque isto **antes** da linha da abertura e troque só o que quiser:

```html
<script>
  window.MAT_ABERTURA = {
    nome: 'Mat',
    faixa: 'Cookies & Coffee',
    anelTopo: 'Feito com carinho',
    anelBase: 'Quentinho do forno',
    carimbo: ['Fornada', '— do dia —'],
    saudacao: 'Seja bem-vindo',
    frase: 'Pode entrar, o café está passando…',
    umaVezPorSessao: true,  // false = mostra sempre
    botaoPular: true
  };
</script>
<script src="abertura-mat.js"></script>
```

Os textos do anel são curtos de propósito: frases bem mais longas não cabem na volta do selo.

## Mudar cores ou desenho e gerar de novo

As cores ficam no começo de `fonte/abertura.css` (`--ma-creme`, `--ma-tinta`, `--ma-vermelho` etc.), e o desenho do selo fica em `fonte/emblema.svg`. Depois de mudar:

```bash
python3 ferramentas/construir.py          # gera abertura-mat.js e previa.html
node ferramentas/exportar_video.js previa.html videos/abertura-mat-1920x1080 1920 1080
node ferramentas/exportar_video.js previa.html videos/abertura-mat-1080x1920 1080 1920
```

O vídeo precisa do Node com o Playwright (Chromium) e do `ffmpeg`. Cada quadro é posicionado no tempo exato da animação, então o vídeo fica idêntico ao site.

## Fontes e licenças

As fontes estão embutidas no arquivo e podem ser usadas em sites comerciais:

- **Yesteryear** (o nome “Mat”), **Josefin Sans** (anel e saudação) e **Fraunces** (faixa e carimbo): SIL Open Font License 1.1;
- **Special Elite** (máquina de escrever): Apache License 2.0.

As licenças estão em `fonte/fontes/`. A Fraunces foi reduzida ao peso usado, com `ferramentas/preparar_fontes.py`. As outras vão como vêm do Fontsource.

## Observação

O Instagram da loja não abriu por aqui, porque ele bloqueia acesso automático. Por isso, o selo foi desenhado a partir do nome **Mat Cookies & Coffee**. Se a loja tiver logo, cores ou fotos próprias, dá para trocar o desenho do centro e a paleta mantendo toda a animação.
