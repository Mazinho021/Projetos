---
name: montagem
description: "Montagem dos vídeos da série A parte que faltou, no modelo forte com esforço alto. Use no começo de todo pedido de montar uma parte depois da entrega do Codex (juntar a branch, conferir vozes, ampliar desenhos, compor telas, montar a timeline, renderizar as duas versões, conferir, capa e entrega) e de ajustes no vídeo pedidos pelo criador."
model: opus
effort: high
---

# Montagem e conferência

Esta skill deixa o resto da vez no modelo forte com esforço alto (ver “Modelo e esforço” no `CLAUDE.md`). Ela estava no médio até 12/11/2026, quando a Parte 7 saiu com o rosto do Zinho diferente em três cenas e uma porta de carro impossível. Se o mesmo problema falhar duas vezes, chamar a skill `maximo`.

## A ordem

O molde é o `montagem/README.md` da parte anterior, com os comandos na seção “Refazer”.

1. **Juntar a entrega:** `git fetch origin codex/crimecarton` e o merge dela. Depois do `git pull --rebase`, conferir com `git log` que os commits do Codex continuam na branch: um rebase já derrubou um deles.
2. **Vozes:** transcrever cada uma sem dar o texto (`transcrever.py`) e comparar com o roteiro. Na dúvida sobre uma palavra, `pontuar.py` diz qual texto a gravação fala; aí acertar o texto à gravação ou pedir a fala de novo. Depois de alinhar, conferir a primeira palavra de cada voz (`palavras.py`).
3. **Desenhos,** antes de qualquer tela ou timeline:
   - ampliar e olhar todos numa grade (`grade.py`): topo calmo, rostos entre 30% e 60% da altura, borda direita livre e corpo inteiro;
   - **rostos:** recortar o rosto de cada personagem em todos os desenhos e pôr lado a lado com a folha de referência (`zinho-referencia-v3.png` e as cenas boas de antes), em tamanho grande. Rosto mais realista, mais comprido, com outro olho ou outro cabelo volta para o Codex;
   - **objetos:** olhar cada desenho em tamanho grande, um por um, procurando porta aberta e fechada ao mesmo tempo, dedos a mais, coisas atravessadas ou duplicadas;
   - **celulares** de tamanho normal na mão, e a mensagem no close da tela, de tamanho médio (regra de 12/11/2026 no `CLAUDE.md`).
4. **Telas, timeline e render** das duas versões, com `--workers 4` (uns 5 a 8 min cada). Para acertar posições antes do render, `previa_quadros.py` mostra quadros da timeline.
5. **Antes de entregar:**
   - um quadro de cada cena nas duas versões (`conferir_video.py`), sem nada atrás do painel, da etiqueta ou dos botões do TikTok;
   - cada tela de celular lida num quadro de 360 px de largura, e os dedos vistos de perto;
   - a faixa do vídeo pronto transcrita, porque o alinhamento já cortou uma palavra.
6. **Entrega:** capa, texto do post, o `README.md` da montagem, o plano e o `NOTAS.md`; commit, push e os vídeos enviados ao criador.

## Os scripts

Ficam em `.claude/skills/montagem/scripts/` e rodam da raiz do repositório:

| Script | Para quê |
|---|---|
| `transcrever.py ARQUIVOS…` | transcrição com o faster-whisper `medium`, sem dica |
| `pontuar.py ARQUIVO início fim "texto 1" "texto 2"` | qual dos textos a gravação fala, pela probabilidade do Whisper |
| `palavras.py ARQUIVO início fim [medium small]` | tempo e probabilidade de cada palavra |
| `grade.py PASTA SAÍDA` | os desenhos em folhas, com linhas a cada 10% |
| `previa_quadros.py TIMELINE SAÍDA.jpg t1 t2… [--v] [--guias]` | quadros da timeline, sem renderizar |
| `conferir_video.py VÍDEO TIMELINE PASTA i\|v` | um quadro de cada cena do vídeo pronto, com as guias |

- Os três de voz e o `alinhar_narracao.py` usam o faster-whisper, que fica num venv na pasta de rascunho da sessão. Num ambiente novo: `python3 -m venv <rascunho>/venv` e `<rascunho>/venv/bin/pip install faster-whisper praat-parselmouth onnxruntime`. O modelo `medium` baixa sozinho na primeira vez.
- Os outros rodam no Python do sistema, com Pillow e FFmpeg.
