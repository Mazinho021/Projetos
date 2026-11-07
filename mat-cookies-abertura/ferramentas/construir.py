"""Monta os arquivos finais da abertura a partir da pasta fonte/.

Saídas (na pasta mat-cookies-abertura/):
  abertura-mat.js  arquivo único para o site: estilo, fontes, textura e desenho embutidos
  previa.html      página de teste que mostra a abertura sobre um site de exemplo

Uso: python3 ferramentas/construir.py
"""
import base64
import json
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FONTE = RAIZ / 'fonte'


def data_uri(caminho, tipo):
    return f'data:{tipo};base64,' + base64.b64encode(caminho.read_bytes()).decode('ascii')


def montar_css():
    css = (FONTE / 'abertura.css').read_text(encoding='utf-8')
    trocas = {
        '__FONTE_LETREIRO__': data_uri(FONTE / 'fontes' / 'yesteryear-latin-400.woff2', 'font/woff2'),
        '__FONTE_FAIXA__': data_uri(FONTE / 'fontes' / 'fraunces-soft-900.woff2', 'font/woff2'),
        '__FONTE_ANEL__': data_uri(FONTE / 'fontes' / 'josefin-sans-latin-700.woff2', 'font/woff2'),
        '__FONTE_MAQUINA__': data_uri(FONTE / 'fontes' / 'special-elite-latin-400.woff2', 'font/woff2'),
        '__PAPEL__': data_uri(FONTE / 'papel.webp', 'image/webp'),
    }
    for marca, valor in trocas.items():
        css = css.replace(marca, valor)
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{};>])\s*', r'\1', css)
    css = re.sub(r',\s+', ',', css)
    return css.strip()


def montar_svg():
    svg = (FONTE / 'emblema.svg').read_text(encoding='utf-8')
    svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S)
    svg = re.sub(r'>\s+<', '><', svg)
    svg = re.sub(r'\s+', ' ', svg)
    return svg.strip()


def para_js(texto):
    return json.dumps(texto, ensure_ascii=False).replace('</', '<\\/')


def main():
    js = (FONTE / 'abertura.js').read_text(encoding='utf-8')
    js = js.replace('"__CSS__"', para_js(montar_css())).replace('"__SVG__"', para_js(montar_svg()))
    assert '__CSS__' not in js and '__SVG__' not in js
    (RAIZ / 'abertura-mat.js').write_text(js, encoding='utf-8')

    modelo = (FONTE / 'previa-modelo.html').read_text(encoding='utf-8')
    em_linha = '<script>\n' + js.replace('</script', '<\\/script') + '</script>'
    (RAIZ / 'previa.html').write_text(modelo.replace('<!--SCRIPT-->', em_linha), encoding='utf-8')

    for nome in ('abertura-mat.js', 'previa.html'):
        print(nome, round((RAIZ / nome).stat().st_size / 1024, 1), 'KB')


if __name__ == '__main__':
    main()
