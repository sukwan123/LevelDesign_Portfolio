import io,re,collections
V=r"C:\Users\seokwan\Documents\Obsidian for Seokwan\Obsidian for Seokwan\70_업무이력\_raw\p4_submitted.tsv"
rows=[l.split("\t") for l in io.open(V,encoding="utf-8",errors="replace").read().splitlines()[1:] if l.strip()]
CAT=[("던전 레벨디자인", r"그리핀|크라켄|장벽\s*너머|하렌홀|맘모스|매머드|제단|던전"),
     ("레벨 기능·기믹",   r"기믹|가젯|사다리|엘리베이터|렛지|로프|도개|스위치|파괴|장막|트리거|끌차|피직스|볼팅"),
     ("월드 품질·최적화", r"네비|길찾기|컬리전|미니맵|실내맵|최적화|쿠킹|데이터레이어|HLOD|스트리밍|라이트|불필요|제거"),
     ("필드 지역 레벨디자인", r"최북단|올드타운|올타|하이가든|크로우즈|크네|시타델|라스트|윈터펠|브라이트|브워킵|넥|트윈스|스톰|리치|북부|월드|지역|마을|유적|은신처|성소|오두막|점령|평원|숲|해안|도시"),
     ("브랜치 반영·빌드 대응", r"Trunk=>|QA=>|=>Trunk|Asia_|AL01|UP01|Marketing|Live")]
c=collections.Counter(); ex=collections.defaultdict(list)
for r in rows:
    d=r[3] if len(r)>3 else ""
    for name,pat in CAT:
        if re.search(pat,d):
            c[name]+=1; ex[name].append(d[:44]); break
    else:
        c["기타"]+=1; ex["기타"].append(d[:44])
tot=sum(c.values())
print("총 %d건"%tot)
for k,v in c.most_common():
    print("  %-20s %5d  %5.1f%%"%(k,v,v/tot*100))
print("\n기타 샘플:")
for s in ex["기타"][:8]: print("   ",s)
