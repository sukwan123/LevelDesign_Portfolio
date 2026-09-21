# -*- coding: utf-8 -*-
"""젠스파크 업로드 세트 v3 — 긴 변 1024px로 내가 직접 리샘플.
젠스파크가 어차피 1024로 깎으므로, 원본을 올리는 건 업로드 시간만 낭비다.
리샘플을 내가 Lanczos로 한 번만 하면 화질은 같거나 낫고 용량은 1/8."""
import os, shutil
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

BASE = r"C:\Users\seokwan\Desktop\포트폴리오 for Claude"
SRC  = os.path.join(BASE, "images")            # 원본 해상도 보관본
OUT  = os.path.join(BASE, "젠스파크_업로드")
CAP  = 1024

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
b1 = os.path.join(OUT, "1차_평면도·목업·인포그래픽")
b2 = os.path.join(OUT, "2차_실작업_캡처")
os.makedirs(b1); os.makedirs(b2)

tot_src = tot_dst = 0
for n in sorted(os.listdir(SRC)):
    im = Image.open(os.path.join(SRC, n))
    src_b = os.path.getsize(os.path.join(SRC, n)); tot_src += src_b
    if max(im.size) > CAP:
        s = CAP / max(im.size)
        im = im.resize((round(im.width*s), round(im.height*s)), Image.LANCZOS)
    dst = os.path.join(b2 if "-3_" in n else b1, n)
    if n.lower().endswith(".png"):
        im.save(dst, "PNG", optimize=True)
    else:
        im.convert("RGB").save(dst, "JPEG", quality=92, optimize=True,
                               progressive=True, subsampling=0)
    tot_dst += os.path.getsize(dst)

for d in (b1, b2):
    fs = os.listdir(d)
    mb = sum(os.path.getsize(os.path.join(d, f)) for f in fs) / 1048576
    print(f"{os.path.basename(d):28} {len(fs):3}개  {mb:5.1f}MB")
print(f"합계 {tot_src/1048576:.0f}MB -> {tot_dst/1048576:.0f}MB "
      f"({tot_dst/tot_src*100:.0f}%)")
