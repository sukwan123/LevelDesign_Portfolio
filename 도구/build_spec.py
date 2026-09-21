"""v12 HTML에서 슬라이드 스펙(Markdown)을 자동 생성한다. 젠스파크에 그대로 붙여넣는 용도."""
import io, os, re, html, urllib.parse

BASE = r"C:\Users\seokwan\Desktop\포트폴리오 for Claude"
V12 = os.path.join(BASE, "포트폴리오_손석완_레벨디자이너_v13.html")
OUT = os.path.join(BASE, "젠스파크_슬라이드_스펙.md")
s = io.open(V12, encoding="utf-8").read()

def txt(x):
    x = re.sub(r"<br\s*/?>", " ", x)
    x = re.sub(r"<[^>]+>", "", x)
    return html.unescape(re.sub(r"\s+", " ", x)).strip()

def imgs_in(block):
    return [urllib.parse.unquote(m).split("/")[-1]
            for m in re.findall(r'<img src="images/([^\"]+)"', block)]

PROMPT = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "genspark_prompt.txt"), encoding="utf-8").read()

lines = []
A = lines.append

A("# 젠스파크용 슬라이드 스펙 — 손석완 레벨 디자이너 포트폴리오")
A("")
A("`젠스파크_업로드/` 안의 두 폴더(55개 + 63개)를 나눠 첨부하고, 아래 프롬프트와 이 스펙을 붙여넣으면 됩니다.")
A("이미지는 전부 개별 원본입니다. 몽타주(격자 배치)는 젠스파크가 직접 만들도록 프롬프트에 지시해 두었습니다.")
A("")
A("---")
A("")
A("## 붙여넣을 프롬프트")
A("")
A("```")
A(PROMPT.strip())
A("```")
A("")
A("---")
A("")

# ---------- 헤더/요약 ----------
head = s[:s.index('<h2>Selected work</h2>')]
name = txt(re.search(r'<h1 class="name">(.*?)</h1>', head).group(1))
role = txt(re.search(r'<p class="role">(.*?)</p>', head).group(1))
meta = txt(re.search(r'<p class="meta">(.*?)</p>', head, re.S).group(1))
lead = txt(re.search(r'<p class="lead">(.*?)</p>', head, re.S).group(1))
bullets = [txt(x) for x in re.findall(r"<li>(.*?)</li>", head, re.S)]
metrics = [(txt(a), txt(b)) for a, b in
           re.findall(r'<span class="n">(.*?)</span><span class="l">(.*?)</span>', head, re.S)]

A("## 슬라이드 1 — 표지")
A(f"- 제목: **{name}** / {role}")
A(f"- 부제: {meta}")
A("")
A("## 슬라이드 2 — Summary")
A(f"- 리드: {lead}")
for b in bullets:
    A(f"- {b}")
A("")
A("## 슬라이드 3 — 숫자로 보는 경력")
for n_, l_ in metrics:
    A(f"- **{n_}** {l_}")
A("")

# ---------- 레벨 기능 카드 ----------
i = s.index('<h3>레벨 관련 각종 기능·기믹 기획</h3>')
j = s.index('<h2>Field regions</h2>')
blk = s[i:j]
A("## 슬라이드 4 — 레벨 관련 각종 기능·기믹 기획")
A(f"- 기간: {txt(re.search(r'<span class=.yr.>(.*?)</span>', blk).group(1))}")
for dt, dd in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", blk, re.S):
    A(f"- **{txt(dt)}** — {txt(dd)}")
A(f"- 이미지: {', '.join(imgs_in(blk))} (1장, 슬라이드 폭 가득 — 자르지 말 것)")
A("")

# ---------- 케이스 카드 ----------
A("---")
A("")
cards = s.split('<div class="case">')[1:]
no = 5
for c in cards:
    nxt = c.find('<div class="case">')
    if nxt > 0:
        c = c[:nxt]
    title = txt(re.search(r"<h3>(.*?)</h3>", c).group(1))
    yr = txt(re.search(r'<span class="yr">(.*?)</span>', c).group(1))
    sub = txt(re.search(r'<p class="sub">(.*?)</p>', c, re.S).group(1))
    role_m = re.search(r'<p class="role">(.*?)</p>', c, re.S)
    A(f"# {title}  ({yr})")
    A(f"- 한 줄: {sub}")
    if role_m:
        A(f"- 설명: {txt(role_m.group(1))}")
    A("")
    figs = re.findall(r'<figure>(.*?)</figure>', c, re.S)
    for f in figs:
        cap = txt(re.search(r"<figcaption>(.*?)</figcaption>", f, re.S).group(1))
        step = txt(re.search(r'<span class="step">(.*?)</span>', f).group(1))
        ims = imgs_in(f)
        A(f"## 슬라이드 {no} — {title} · {step}")
        A(f"- 캡션: {cap.replace(step, '', 1).strip()}")
        A(f"- 이미지 {len(ims)}장" + ("  (3열 격자)" if len(ims) > 1 else "  (1장 크게)"))
        for x in ims:
            A(f"  - `{x}`")
        A("")
        no += 1
    for e in re.findall(r'<div class="empty">(.*?)</div>', c, re.S):
        A(f"> (슬라이드 없음) {txt(e)}")
    vid = re.search(r'<a class="vid" href="([^"]+)".*?<span class="t">(.*?)</span>', c, re.S)
    if vid:
        A(f"- 플레이 영상 링크: {vid.group(1)} — {txt(vid.group(2))}")
    note = re.search(r'미공개 지역</b>(.*?)</p>', c, re.S)
    if note:
        A(f"> 미공개 지역 — {txt(note.group(1))}")
    A("")
    A("---")
    A("")

# ---------- 꼬리 카드 ----------
for h3 in ["이동 기믹 상세기획", "AI 작업 파이프라인 구축과 팀 확산"]:
    i = s.index("<h3>" + h3 + "</h3>")
    k = s.index("</div>", s.index('<div class="tags">', i))
    blk = s[i:k]
    A(f"## 슬라이드 {no} — {h3}")
    A(f"- 기간: {txt(re.search(r'<span class=.yr.>(.*?)</span>', blk).group(1))}")
    for dt, dd in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", blk, re.S):
        A(f"- **{txt(dt)}** — {txt(dd)}")
    A("")
    no += 1

# ---------- 연표 / 스킬 ----------
tl = s[s.index("<h2>Career timeline</h2>"):]
A(f"## 슬라이드 {no} — 경력 연표"); no += 1
for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tl, re.S)[1:]:
    tds = [txt(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
    if len(tds) == 3:
        A(f"- **{tds[0]}** / {tds[1]} — {tds[2]}")
A("")
A(f"## 슬라이드 {no} — Skills & Tools")
for dt, dd in re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", tl, re.S):
    A(f"- **{txt(dt)}** — {txt(dd)}")
A("")

io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("작성:", os.path.basename(OUT), f"{os.path.getsize(OUT)/1024:.0f}KB, 총 {no}장 슬라이드")
