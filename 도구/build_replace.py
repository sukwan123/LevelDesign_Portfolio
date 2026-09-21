# -*- coding: utf-8 -*-
"""이미 뽑힌 39장 덱에서 '합성본이라 깨진 슬라이드'만 교체하기 위한 최소 첨부 세트.
대상: PDF 이미지-원본 매칭에 실패한 7개 슬라이드 = 전부 내가 미리 합성한 몽타주."""
import os, shutil
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

BASE = r"C:\Users\seokwan\Desktop\포트폴리오 for Claude"
SRC  = os.path.join(BASE, "images")
OUT  = os.path.join(BASE, "젠스파크_교체분")
CAP  = 1024

# (접두사, 덱 페이지, 설명)
TARGET = [("01-2_", 6,  "최북단 목업"),
          ("02-2_", 10, "올드타운 목업"),
          ("03-2_", 14, "하이가든 목업"),
          ("04-2_", 18, "크로우즈네스트 목업"),
          ("09-2_", 35, "하렌홀 목업"),
          ("07-3_", 31, "장벽너머 실작업"),
          ("10-1_", 4,  "레벨 기능 인포그래픽")]

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

files = sorted(os.listdir(SRC))
tot = 0
for pre, page, desc in TARGET:
    g = [f for f in files if f.startswith(pre)]
    for n in g:
        im = Image.open(os.path.join(SRC, n))
        if max(im.size) > CAP:
            s = CAP / max(im.size)
            im = im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
        dst = os.path.join(OUT, n)
        if n.lower().endswith(".png"):
            im.save(dst, "PNG", optimize=True)
        else:
            im.convert("RGB").save(dst, "JPEG", quality=92, optimize=True,
                                   progressive=True, subsampling=0)
        tot += os.path.getsize(dst)
    print(f"  p{page:02d} {desc:18} {len(g):2}장")

print(f"\n합계 {len(os.listdir(OUT))}개 / {tot/1048576:.1f}MB")
