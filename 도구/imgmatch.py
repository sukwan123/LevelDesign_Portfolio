# -*- coding: utf-8 -*-
"""젠스파크가 1024px로 깎은 이미지를 원본과 매칭한다.
32x32 그레이 썸네일 서명 + 종횡비로 대조. 같은 그림의 축소판이므로 거의 정확히 맞는다."""
import os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

def sig(im):
    g = im.convert("L").resize((32, 32), Image.LANCZOS)
    px = list(g.getdata())
    m = sum(px) / len(px)
    return [p - m for p in px], im.width / im.height

def build(folder):
    out = {}
    for n in sorted(os.listdir(folder)):
        p = os.path.join(folder, n)
        if os.path.isfile(p):
            try:
                out[n] = sig(Image.open(p))
            except Exception:
                pass
    return out

def match(q, lib, ar_tol=0.03):
    (qs, qa) = q
    best, bd = None, None
    for n, (s, a) in lib.items():
        if abs(a - qa) / qa > ar_tol:
            continue
        d = sum(abs(x - y) for x, y in zip(qs, s))
        if bd is None or d < bd:
            best, bd = n, d
    return best, bd
