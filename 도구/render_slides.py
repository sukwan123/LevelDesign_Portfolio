# -*- coding: utf-8 -*-
r"""PPTX 슬라이드를 PNG 로 뽑아 눈으로 검증한다. 윈도우·리눅스 양쪽에서 동작.

  py -3 render_slides.py <pptx> [페이지...]      # 윈도우
  python3 render_slides.py <pptx> [페이지...]    # 리눅스(클라우드 세션)

페이지를 생략하면 전부. 결과는 <pptx이름>_render/ 에 pNN.png 로 떨어진다.

윈도우면 PowerPoint COM 을 쓰고(가장 정확), 없으면 LibreOffice headless 로
PDF 를 거쳐 pymupdf 로 렌더한다. 클라우드 세션에는 PowerPoint 가 없으므로 후자로 간다.
"""
import os, sys, shutil, subprocess, tempfile

DPI = 110


def out_dir(pptx):
    d = os.path.splitext(pptx)[0] + "_render"
    os.makedirs(d, exist_ok=True)
    return d


def via_powerpoint(pptx, pages, dst):
    """윈도우 전용. PowerPoint 가 직접 그리므로 폰트·도형이 100% 정확하다."""
    ps = r"""
$app  = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open("{pptx}", $true, $false, $false)
$pages = @({pages})
if ($pages.Count -eq 0) {{ $pages = 1..$pres.Slides.Count }}
foreach ($p in $pages) {{
  $pres.Slides($p).Export(("{dst}\p{{0:d2}}.png" -f $p), "PNG", 1600, 900)
}}
Write-Output $pres.Slides.Count
$pres.Close(); $app.Quit()
""".format(pptx=os.path.abspath(pptx), dst=os.path.abspath(dst),
           pages=",".join(str(p) for p in pages))
    r = subprocess.run(["powershell", "-NonInteractive", "-Command", ps],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:400])
    return int(r.stdout.strip().splitlines()[-1])


def via_libreoffice(pptx, pages, dst):
    """리눅스·맥. LibreOffice 로 PDF 를 만든 뒤 pymupdf 로 래스터화."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError(
            "LibreOffice 가 없다. 설치: sudo apt-get install -y libreoffice-impress")
    import pymupdf
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp,
             os.path.abspath(pptx)],
            capture_output=True, text=True, timeout=600)
        pdfs = [f for f in os.listdir(tmp) if f.lower().endswith(".pdf")]
        if not pdfs:
            raise RuntimeError("PDF 변환 실패: " + (r.stderr or r.stdout)[:400])
        doc = pymupdf.open(os.path.join(tmp, pdfs[0]))
        todo = pages or range(1, doc.page_count + 1)
        for p in todo:
            doc[p - 1].get_pixmap(dpi=DPI).save(os.path.join(dst, f"p{p:02d}.png"))
        return doc.page_count


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pptx = sys.argv[1]
    if not os.path.isfile(pptx):
        sys.exit("파일 없음: " + pptx)
    pages = [int(x) for x in sys.argv[2:]]
    dst = out_dir(pptx)

    if os.name == "nt":
        try:
            n = via_powerpoint(pptx, pages, dst)
            engine = "PowerPoint COM"
        except Exception as e:
            print("PowerPoint 실패, LibreOffice 로 대체:", e)
            n = via_libreoffice(pptx, pages, dst)
            engine = "LibreOffice"
    else:
        n = via_libreoffice(pptx, pages, dst)
        engine = "LibreOffice"

    got = sorted(f for f in os.listdir(dst) if f.endswith(".png"))
    print(f"{engine} · 전체 {n}장 중 {len(got)}장 렌더 → {dst}")


if __name__ == "__main__":
    main()
