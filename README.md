# 레벨 디자이너 포트폴리오 작업 저장소

손석완 · ProjectT(왕좌의 게임 IP) 레벨 디자인 포트폴리오를 만들고 다듬는 작업 공간.
**이 저장소는 private이며 사내 미공개 자산을 포함한다. 절대 public으로 바꾸지 말 것.**

## 새 대화를 시작할 때

[`인수인계_프롬프트.md`](인수인계_프롬프트.md) 를 통째로 붙여넣고 맨 아래 「지금 할 일」만 채운다.
파일명 규칙, 지켜야 할 제약, 도구 사용법, 환경 함정이 전부 거기 있다.

## 폴더

| | |
|---|---|
| `images/` | **118장. 거의 모든 작업의 입력.** `섹션-슬롯_지역_종류_인덱스` 순서가 곧 슬라이드 순서 |
| `assets/` | 평면도·목업 PNG 마스터. `images/` 의 상위 원본 |
| `도구/` | 파이썬 스크립트 8개 |
| `업무이력/` | 옵시디언 볼트 `70_업무이력` 사본. 진입점은 `업무이력 허브.md` |

## 산출물

최종본 **`포트폴리오_손석완_레벨디자이너_v14.pptx` (44장)** 는 용량 때문에
[Releases](../../releases) 에 올려 둔다. 저장소에는 없다.

HTML 판(`v11`~`v13`)은 `images/` 를 상대경로로 참조하므로 clone 후 바로 열린다.

## 도구

| 스크립트 | 하는 일 |
|---|---|
| `fix_pptx.py <pptx>` | **가장 중요.** 젠스파크 PPTX의 1024px 축소본을 `images/` 원본으로 교체하고, 합성본은 낱장 격자로 재배치. 슬라이드 분할·쪽번호 재기입까지 |
| `imgmatch.py` | 위가 쓰는 썸네일 서명 매칭 |
| `make_infographic2.py` | 업무 비중 인포그래픽(가로형 2600×860) 생성 |
| `classify2.py` | Perforce 서브밋 1,637건 분류 — 인포그래픽 수치의 근거 |
| `build_upload3.py` | 젠스파크 업로드 세트 생성(긴 변 1024 리샘플, 1차/2차 분할) |
| `build_replace.py` | 교체 필요한 슬라이드분만 뽑는 최소 첨부 세트 |
| `build_spec.py` | HTML → 슬라이드 스펙 Markdown |
| `build_v13.py` | HTML 버전 갱신 |

## 환경

```bash
py -3 -m pip install pillow python-pptx pymupdf
```

**이 PC는 `python` 명령이 깨져 있어 `py -3` 을 써야 한다.** node 없음.

검증은 PowerPoint COM 으로 슬라이드를 PNG 로 뽑아 눈으로 본다.

```powershell
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open("...\파일.pptx", $true, $false, $false)
$pres.Slides(6).Export("$env:TEMP\p6.png", "PNG", 1600, 900)
$pres.Close(); $app.Quit()
```

## 저장소에 없는 것

| | 어디 있나 |
|---|---|
| `완성 스크린샷/` 439MB | 로컬에만. `images/` 의 `*-3_*` 로 이미 증류됨 |
| `*.pptx` | Releases |
| `젠스파크_업로드/`, `젠스파크_교체분/`, `*.zip` | `build_upload3.py` / `build_replace.py` 로 재생성 |
| 초기 HTML `v1`~`v10` | base64 이미지를 통째로 품어 47MB. 버렸다 |
