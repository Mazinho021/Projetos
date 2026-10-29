#!/usr/bin/env python3
"""Render the 100-followers thank-you: the series' own renderer, with the confetti element.

Takes the same arguments as episodio-01/montagem/render_animatic.py, which does all the
work; this only loads confete.py first, so a timeline can use {"type": "confetti"}.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'episodio-01' / 'montagem'))
sys.path.insert(0, str(HERE))

import confete  # noqa: E402,F401  (registers the "confetti" graphics element)
import render_animatic  # noqa: E402

if __name__ == '__main__':
    render_animatic.main()
