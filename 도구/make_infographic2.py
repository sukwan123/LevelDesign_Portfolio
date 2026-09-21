# -*- coding: utf-8 -*-
"""업무 비중 인포그래픽 가로형 — 범례를 도넛 오른쪽으로 빼 세로를 줄였다.
슬라이드 콘텐츠 영역(1272x448pt, 2.84:1)에 최대한 크게 들어가게 하기 위함."""
import os, math
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:\Users\seokwan\Desktop\포트폴리오 for Claude\assets\infographic_workshare_wide.png"
W, H = 2600, 860
BG = (255, 255, 255)
INK = (21, 24, 28); INK2 = (74, 82, 92); INK3 = (123, 132, 143)
LINE = (227, 230, 234)
RAMP = [(31, 95, 139), (64, 135, 180), (110, 170, 205), (162, 199, 222), (208, 224, 234)]

F = r"C:\Windows\Fonts\malgun.ttf"
FB = r"C:\Windows\Fonts\malgunbd.ttf"
def f(sz, bold=False):
    return ImageFont.truetype(FB if bold else F, sz)

im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)

def donut(cx, cy, r, inner, data, title, sub, lx, lw):
    d.text((cx - r, cy - r - 92), title, font=f(38, True), fill=INK)
    d.text((cx - r, cy - r - 44), sub, font=f(25), fill=INK3)
    tot = sum(v for _, v in data)
    a = -90.0
    for i, (lab, v) in enumerate(data):
        sweep = 360.0 * v / tot
        d.pieslice([cx-r, cy-r, cx+r, cy+r], a, a+sweep, fill=RAMP[i % len(RAMP)])
        if v / tot >= 0.15:
            mid = math.radians(a + sweep/2)
            tx = cx + math.cos(mid) * (r + inner) / 2
            ty = cy + math.sin(mid) * (r + inner) / 2
            s = f"{v/tot*100:.0f}%"
            bb = d.textbbox((0, 0), s, font=f(38, True))
            d.text((tx - bb[2]/2, ty - bb[3]/2), s, font=f(38, True),
                   fill=(255, 255, 255) if i < 3 else INK)
        a += sweep
    d.ellipse([cx-inner, cy-inner, cx+inner, cy+inner], fill=BG)
    s = f"{tot:,}"
    bb = d.textbbox((0, 0), s, font=f(54, True))
    d.text((cx - bb[2]/2, cy - bb[3]/2 - 15), s, font=f(54, True), fill=INK)
    bb2 = d.textbbox((0, 0), "건", font=f(25))
    d.text((cx - bb2[2]/2, cy + 32), "건", font=f(25), fill=INK3)
    # 범례 — 도넛 오른쪽, 세로 가운데 정렬
    rh = 52
    ly = cy - (len(data) * rh) / 2 + 6
    for i, (lab, v) in enumerate(data):
        d.rounded_rectangle([lx, ly, lx+24, ly+24], 5, fill=RAMP[i % len(RAMP)])
        d.text((lx+38, ly-3), lab, font=f(27, True), fill=INK2)
        s = f"{v:,}건   {v/tot*100:.1f}%"
        bb = d.textbbox((0, 0), s, font=f(25))
        d.text((lx + lw - bb[2], ly-1), s, font=f(25), fill=INK3)
        ly += rh

donut(430, 350, 228, 122, [
    ("필드 지역", 722), ("레벨 기능·기믹", 342), ("던전", 182),
    ("월드 품질", 164), ("기타", 227),
], "무엇을 만들었나", "Perforce 서브밋 분류", 700, 500)

donut(1730, 350, 228, 122, [
    ("타 부서 배분", 339), ("직접 수행", 132), ("타 부서 발주", 83),
], "어떻게 일했나", "Jira 이슈의 내 역할", 2000, 500)

d.line([(80, 648), (W-80, 648)], fill=LINE, width=2)
cards = [("76%", "내 이슈 중 타 부서로\n넘어간 작업 비중"),
         ("10", "담당 콘텐츠\n필드 5 · 던전 5"),
         ("6", "기믹 하나에 붙인\n협업 부서 수"),
         ("53%", "AI 활용률\n시간 절감 31%")]
cw = (W - 160) / len(cards)
for i, (big, small) in enumerate(cards):
    x = 80 + cw * i
    if i:
        d.line([(x-30, 686), (x-30, 822)], fill=LINE, width=2)
    d.text((x, 682), big, font=f(56, True), fill=RAMP[0])
    yy = 754
    for ln in small.split("\n"):
        d.text((x, yy), ln, font=f(25), fill=INK2); yy += 34

im.save(OUT, "PNG", optimize=True)
print("saved", OUT, im.size, f"{os.path.getsize(OUT)/1024:.0f}KB",
      f"비율 {im.width/im.height:.2f}:1")
