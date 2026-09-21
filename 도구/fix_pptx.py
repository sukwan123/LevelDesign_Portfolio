# -*- coding: utf-8 -*-
r"""젠스파크 PPTX 보정.

1) 슬라이드 안의 1024px 축소본을 전부 원본 해상도로 되돌린다(도형 위치·크기 그대로).
2) 내가 미리 합성했던 몽타주 7장은 낱장 원본 격자로 다시 짠다.
   9장짜리는 덱의 '03 실작업' 관례대로 (1/2)(2/2) 두 장으로 나눈다.
3) 슬라이드가 늘어난 만큼 쪽번호를 다시 매긴다.
"""
import io, os, re, sys, copy
from PIL import Image
from pptx import Presentation
from pptx.util import Emu, Pt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from imgmatch import sig, build, match
Image.MAX_IMAGE_PIXELS = None

BASE   = r"C:\Users\seokwan\Desktop\포트폴리오 for Claude"
IMG    = os.path.join(BASE, "images")
THRESH = 12.0
PIC    = 13                      # MSO_SHAPE_TYPE.PICTURE
MIN_PX = 100                     # 짧은 변이 이보다 작으면 장식용 선·악센트 바

# 합성본이 들어간 슬라이드 → 낱장 파일 접두사
REPLACE = {6: "01-2_", 10: "02-2_", 14: "03-2_", 18: "04-2_",
           35: "09-2_", 31: "07-3_"}
INFO = os.path.join(BASE, "assets", "infographic_workshare_wide.png")
INFO_AFTER = 4                   # 이 슬라이드 뒤에 인포그래픽 전용 장을 넣는다

EMU = 12700                      # 1pt
def pt(v): return Emu(int(round(v * EMU)))

def content_pics(slide):
    out = []
    for sh in slide.shapes:
        if sh.shape_type == PIC and min(sh.image.size) >= MIN_PX:
            out.append(sh)
    return out

def drop(sh):
    sh._element.getparent().remove(sh._element)

# ---------- 격자 배치 ----------
def layout_rows(paths, rect, per_row=3, gap=14.0):
    """행 단위 높이 정규화 패킹. 확대 없음, crop 없음, 비율 유지."""
    L, T, W, H = rect
    rows = [paths[i:i+per_row] for i in range(0, len(paths), per_row)]
    ar = [[Image.open(p).width / Image.open(p).height for p in r] for r in rows]
    h = (H - gap * (len(rows) - 1)) / len(rows)
    # 가장 넓은 행이 폭을 넘으면 전체를 줄인다
    for r in ar:
        wsum = sum(a * h for a in r) + gap * (len(r) - 1)
        if wsum > W:
            h *= W / wsum
    placed, y = [], T + (H - (h * len(rows) + gap * (len(rows) - 1))) / 2
    for r, a in zip(rows, ar):
        ws = [x * h for x in a]
        x = L + (W - (sum(ws) + gap * (len(r) - 1))) / 2
        for p, w in zip(r, ws):
            placed.append((p, x, y, w, h))
            x += w + gap
        y += h + gap
    return placed

def put(slide, placed):
    for p, x, y, w, h in placed:
        slide.shapes.add_picture(p, pt(x), pt(y), pt(w), pt(h))

# ---------- 슬라이드 복제 ----------
def clone(pr, src):
    """텍스트·장식만 복사한 빈 슬라이드를 만든다(그림은 호출측에서 채운다)."""
    new = pr.slides.add_slide(src.slide_layout)
    for sh in list(new.shapes):
        drop(sh)
    tree = new.shapes._spTree
    for sh in src.shapes:
        if sh.shape_type == PIC:
            if min(sh.image.size) < MIN_PX:      # 장식 선은 블롭으로 다시 삽입
                b = io.BytesIO(sh.image.blob)
                new.shapes.add_picture(b, sh.left, sh.top, sh.width, sh.height)
            continue
        tree.append(copy.deepcopy(sh._element))
    return new, list(pr.slides._sldIdLst)[-1]

def move_after(pr, el, pos):
    """pos 는 0-based 목표 위치. 자기 자신을 떼어내고 그 자리에 다시 끼운다."""
    sl = pr.slides._sldIdLst
    sl.remove(el)
    sl.insert(pos, el)

def set_text(slide, old, new):
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == old:
            p = sh.text_frame.paragraphs[0]
            p.runs[0].text = new
            for r in p.runs[1:]:
                r.text = ""
            return True
    return False

# ---------- 본체 ----------
def main(src):
    dst = os.path.splitext(src)[0] + "_보정.pptx"
    lib = build(IMG)
    pr = Presentation(src)
    SW = Emu(pr.slide_width).pt

    # 잘 나온 실작업 슬라이드에서 콘텐츠 영역을 역산
    ref = None
    for s in pr.slides:
        ps = content_pics(s)
        if len(ps) >= 6:
            xs = [Emu(p.left).pt for p in ps]; ys = [Emu(p.top).pt for p in ps]
            x1 = max(Emu(p.left).pt + Emu(p.width).pt for p in ps)
            y1 = max(Emu(p.top).pt + Emu(p.height).pt for p in ps)
            ref = (min(xs), min(ys), x1 - min(xs), y1 - min(ys))
            break
    print(f"콘텐츠 영역 역산: L{ref[0]:.0f} T{ref[1]:.0f} {ref[2]:.0f}x{ref[3]:.0f}pt")

    files = sorted(os.listdir(IMG))
    added = []        # (원본 인덱스, 새 슬라이드)
    relinked = 0

    for idx, slide in enumerate(pr.slides, 1):
        pics = content_pics(slide)
        if idx in REPLACE:
            pre = REPLACE[idx]
            g = [os.path.join(IMG, f) for f in files if f.startswith(pre)]
            for sh in pics:
                drop(sh)
            if len(g) <= 6:
                put(slide, layout_rows(g, ref))
                print(f"  p{idx:02d} 합성본 → 낱장 {len(g)}장 격자")
            else:                                            # 6 + 나머지
                a, b = g[:6], g[6:]
                put(slide, layout_rows(a, ref))
                title = next(sh.text_frame.text.strip() for sh in slide.shapes
                             if sh.has_text_frame and
                             re.match(r"^\d\d ", sh.text_frame.text.strip()))
                ns, nel = clone(pr, slide)
                for sh in content_pics(ns):
                    drop(sh)
                put(ns, layout_rows(b, ref))
                set_text(slide, title, f"{title} (1/2)")
                set_text(ns, title, f"{title} (2/2)")
                added.append((idx, nel))
                print(f"  p{idx:02d} 합성본 → 낱장 {len(g)}장, (1/2) {len(a)}장 + (2/2) {len(b)}장 분할")
        else:
            for sh in pics:
                name, d = match(sig(Image.open(io.BytesIO(sh.image.blob))), lib)
                if name and d / 1024 <= THRESH:
                    part = sh._element.blipFill.blip.rEmbed
                    ip = slide.part.related_part(part)
                    op = os.path.join(IMG, name)
                    same = (os.path.splitext(op)[1].lower() in (".jpg", ".jpeg")) ==                            (ip.content_type == "image/jpeg")
                    if same:                       # 재인코딩 없이 원본 바이트 그대로
                        blob = open(op, "rb").read()
                    else:
                        o = Image.open(op); buf = io.BytesIO()
                        if ip.content_type == "image/png":
                            o.save(buf, "PNG", optimize=True)
                        else:
                            o.convert("RGB").save(buf, "JPEG", quality=95,
                                optimize=True, progressive=True, subsampling=0)
                        blob = buf.getvalue()
                    ip._blob = blob
                    relinked += 1

    # 인포그래픽 전용 슬라이드
    src4 = pr.slides[INFO_AFTER - 1]
    for sh in content_pics(src4):
        drop(sh)
    for sh in list(src4.shapes):                       # 사라진 그림의 캡션 제거
        if sh.has_text_frame and sh.text_frame.text.strip().startswith("레벨 기능 블록아웃"):
            drop(sh)
    # 그림이 빠져 아래가 비므로 본문 행 간격을 콘텐츠 영역에 맞춰 넓힌다
    rows = sorted({Emu(sh.top).pt for sh in src4.shapes
                   if sh.has_text_frame and 200 < Emu(sh.top).pt < 700})
    if len(rows) >= 2:
        top, bottom = ref[1] - 24, ref[1] + ref[3]
        pitch = (bottom - top) / len(rows)
        newtop = {old: top + pitch * i for i, old in enumerate(rows)}
        for sh in src4.shapes:
            if sh.has_text_frame and Emu(sh.top).pt in newtop:
                sh.top = pt(newtop[Emu(sh.top).pt])
        print(f"  p{INFO_AFTER:02d} 본문 {len(rows)}행 간격 {rows[1]-rows[0]:.0f} → {pitch:.0f}pt")

    ins, iel = clone(pr, src4)
    KEEP = ("기능 기획", "레벨 관련 각종 기능·기믹 기획", "2022 – 2024",
            "손석완 · 레벨 디자이너 포트폴리오 · ProjectT")
    for sh in list(ins.shapes):
        if sh.has_text_frame:
            t = sh.text_frame.text.strip()
            if t and t not in KEEP and not re.fullmatch(r"\d+\s*/\s*\d+", t):
                drop(sh)
    set_text(ins, "레벨 관련 각종 기능·기믹 기획", "업무 비중")
    # 다른 슬라이드의 설명문과 같은 자리에 기준을 적어 둔다
    desc = next(sh for sh in pr.slides[5].shapes
                if sh.has_text_frame and Emu(sh.top).pt == 225.0)
    cap = copy.deepcopy(desc._element)
    ins.shapes._spTree.append(cap)
    tb = ins.shapes[-1]
    tb.left, tb.top, tb.width = pt(72), pt(225), pt(1296)
    tb.text_frame.paragraphs[0].runs[0].text = (
        "Perforce 서브밋 1,637건 · Jira 이슈 554건(사무 IT 요청 제외)을 분류한 결과.")
    iim = Image.open(INFO)
    L, T, W, H = ref
    w = min(W, H * iim.width / iim.height)
    h = w * iim.height / iim.width
    put(ins, [(INFO, L + (W - w) / 2, T, w, h)])
    added.append((INFO_AFTER, iel))
    added.sort(key=lambda x: x[0])
    print(f"  p{INFO_AFTER:02d} 블록아웃 제거 → 인포그래픽 전용 슬라이드 신설 ({w:.0f}x{h:.0f}pt)")

    # 새 슬라이드를 원래 자리 뒤로 이동 (뒤에서부터 넣어야 인덱스가 안 밀린다)
    for off, (idx, nel) in enumerate(added):
        move_after(pr, nel, idx + off)

    total = len(pr.slides._sldIdLst)
    for i, slide in enumerate(pr.slides, 1):
        for sh in slide.shapes:
            if sh.has_text_frame and re.fullmatch(r"\d+\s*/\s*\d+", sh.text_frame.text.strip()):
                p = sh.text_frame.paragraphs[0]
                p.runs[0].text = f"{i:02d} / {total}"
                for r in p.runs[1:]:
                    r.text = ""
    pr.save(dst)
    print(f"\n원본 해상도 복구 {relinked}장 / 슬라이드 {total}장 (원래 39장)")
    print("저장:", dst, f"{os.path.getsize(dst)/1048576:.0f}MB")
    return dst

if __name__ == "__main__":
    main(sys.argv[1])
