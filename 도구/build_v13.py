# -*- coding: utf-8 -*-
"""v13: 레벨 기능 카드의 블록아웃 2장 -> 업무 비중 인포그래픽 1장으로 교체."""
import io, os, re, shutil, urllib.parse

BASE = r"C:\Users\seokwan\Desktop\포트폴리오 for Claude"
IMG  = os.path.join(BASE, "images")
V12  = os.path.join(BASE, "포트폴리오_손석완_레벨디자이너_v12.html")
V13  = os.path.join(BASE, "포트폴리오_손석완_레벨디자이너_v13.html")
INFO = os.path.join(BASE, "assets", "infographic_workshare.png")
NN   = "10-1_레벨기능_업무비중_인포그래픽.png"

# 블록아웃 2장 제거, 인포그래픽 투입 (PNG 그대로 — 차트 글자 선명도 유지)
for f in os.listdir(IMG):
    if f.startswith("10-"):
        os.remove(os.path.join(IMG, f))
shutil.copyfile(INFO, os.path.join(IMG, NN))

s = io.open(V12, encoding="utf-8").read()
i = s.index('<div class="figs two">')
j = s.index('</div>', s.index('</figure>', s.index('</figure>', i) + 1)) + 6

fig = ('<div class="figs one">\n'
       '    <figure><img src="images/' + urllib.parse.quote(NN) + '" '
       'alt="업무 비중 인포그래픽" loading="lazy">'
       '<figcaption><b>업무 비중</b> — Perforce 서브밋 1,637건과 Jira 이슈 554건을 '
       '분류한 결과. 서브밋의 21%가 레벨 기능·기믹이며, 이슈의 61%는 설계 후 타 부서로 넘긴 작업.'
       '</figcaption></figure>\n  </div>')
s = s[:i] + fig + s[j:]

# .figs one 스타일이 없으면 추가
if ".figs.one" not in s:
    s = s.replace("</style>",
                  "  .figs.one{grid-template-columns:1fr}\n"
                  "  .figs.one img{width:100%}\n</style>")

io.open(V13, "w", encoding="utf-8", newline="\n").write(s)
print("v13 작성", round(os.path.getsize(V13)/1024), "KB")
print("images/ 파일", len(os.listdir(IMG)), "개")
