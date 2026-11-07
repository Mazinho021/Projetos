"""Gera a Fraunces estática usada na faixa (peso 900, eixo SOFT 100, WONK 1).

As outras fontes (Yesteryear, Josefin Sans 700 e Special Elite) entram sem
modificação, no recorte "latin" distribuído pelo Fontsource.

Uso: python3 preparar_fontes.py <fraunces-latin-full-normal.woff2> <saida.woff2>
O arquivo de entrada vem do pacote npm @fontsource-variable/fraunces.
"""
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

entrada, saida = sys.argv[1], sys.argv[2]
# Latim básico + Latim-1 + aspas, travessões, reticências e ponto médio
unicodes = list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + [
    0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x2022]

fonte = instancer.instantiateVariableFont(
    TTFont(entrada), {'wght': 900, 'SOFT': 100, 'WONK': 1, 'opsz': 72})
opcoes = subset.Options()
opcoes.flavor = 'woff2'
opcoes.layout_features = ['kern', 'liga', 'calt', 'ccmp', 'locl', 'mark', 'mkmk']
opcoes.name_IDs = ['*']
sub = subset.Subsetter(opcoes)
sub.populate(unicodes=unicodes)
sub.subset(fonte)
fonte.flavor = 'woff2'
fonte.save(saida)
print(saida, os.path.getsize(saida), 'bytes')
