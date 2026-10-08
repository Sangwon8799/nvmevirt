#!/usr/bin/env python3
"""Make a self-contained HTML gallery (images embedded) of every graph of one experiment.

usage: python3 make_gallery.py results/<EXP> [out.html]
Reads results/<EXP>/analysis/fig_*.png (analyze.py) and results/<EXP>/plots/*.png (plot.py all).
"""
import base64
import html
import sys
from pathlib import Path

EXP = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else EXP / f"gallery_{EXP.name}.html"

# (group title, [(file pattern relative to EXP, caption)])
GROUPS = [
    ("1. 대역폭 — 핵심", [
        ("plots/bs_bw_MiBps.png", "60 s 평균 쓰기 대역폭. x = fio bs, 선 = 매핑 단위, 패널 = 변형(캐시 조건), 오차막대 = 표준편차"),
        ("plots/heatmap_bw_MiBps.png", "매핑 단위 × bs 평균 대역폭 열지도(변형별 패널)"),
        ("plots/map_bw_MiBps.png", "같은 값을 매핑 단위 축으로: 선 = bs"),
        ("plots/compare_bw_MiBps.png", "변형 비교(주 데이터셋: drop vs nodrop, 보조: base vs wbuffix). 회색 = bs < 매핑 단위"),
        ("plots/bs_iops.png", "IOPS (로그 축)"),
        ("plots/map_iops.png", "IOPS, 매핑 단위 축 (로그 축)"),
    ]),
    ("2. GC 전후 나눠 보기", [
        ("plots/bs_gc_onset_s.png", "fio 시작부터 첫 GC 까지의 시간"),
        ("plots/map_gc_onset_s.png", "첫 GC 시각, 매핑 단위 축"),
        ("plots/heatmap_gc_onset_s.png", "첫 GC 시각 열지도"),
        ("plots/bs_bw_pre_gc_MiBps.png", "GC 이전 구간 평균 대역폭 — NAND 프로그램 한계(× bs/매핑)를 보여 준다"),
        ("plots/map_bw_pre_gc_MiBps.png", "GC 이전 대역폭, 매핑 단위 축"),
        ("plots/bs_bw_post_gc_MiBps.png", "GC 이후 구간 평균 대역폭"),
        ("plots/map_bw_post_gc_MiBps.png", "GC 이후 대역폭, 매핑 단위 축"),
        ("plots/heatmap_bw_post_gc_MiBps.png", "GC 이후 대역폭 열지도"),
        ("analysis/fig_bw_last20s_vs_bs_*.png", "마지막 20 s(40–60 s) 평균 대역폭 — GC 이후 정상 상태에 가까운 구간"),
    ]),
    ("3. 쓰기 증폭 (WAF)", [
        ("plots/bs_waf_total.png", "전체 쓰기 증폭 WAF_total = NAND 바이트 ÷ 호스트 바이트 (로그 축)"),
        ("plots/map_waf_total.png", "WAF_total, 매핑 단위 축"),
        ("plots/heatmap_waf_total.png", "WAF_total 열지도"),
        ("plots/compare_waf_total.png", "WAF_total 변형 비교"),
        ("analysis/fig_waf_heatmap_*.png", "WAF_total 열지도 (변형별 파일)"),
    ]),
    ("4. 지연", [
        ("plots/bs_clat_mean_us.png", "평균 완료 지연 (로그 축)"),
        ("plots/map_clat_mean_us.png", "평균 완료 지연, 매핑 단위 축"),
        ("plots/compare_clat_mean_us.png", "평균 완료 지연 변형 비교"),
        ("plots/bs_clat_p99_us.png", "p99 완료 지연 (로그 축)"),
        ("plots/map_clat_p99_us.png", "p99 완료 지연, 매핑 단위 축"),
    ]),
    ("5. 시간에 따른 변화 (0.5 s 평균)", [
        ("analysis/fig_timeseries_*.png", "조합별 대역폭 시계열 — 3 회차를 겹침, 점선 = 첫 GC"),
        ("plots/ts_bw_all_rep1.png", "1 회차 대역폭 시계열 — 변형을 한 그림에"),
        ("plots/ts_clat_all_rep1.png", "1 회차 완료 지연 시계열 (로그 축)"),
    ]),
    ("6. analyze.py 기본 그림 (변형별 파일)", [
        ("analysis/fig_bw_vs_bs_*.png", "대역폭 vs bs"),
        ("analysis/fig_bw_heatmap_*.png", "대역폭 열지도"),
        ("analysis/fig_clat_mean_vs_bs_*.png", "평균 완료 지연 vs bs"),
        ("analysis/fig_clat_p99_vs_bs_*.png", "p99 완료 지연 vs bs"),
        ("analysis/fig_variant_compare.png", "변형 비교 (매핑 단위별 패널)"),
    ]),
]

TITLE = {"main3x3_20261008": "주 데이터셋 — 매핑 4K·16K·32K × bs 4K·16K·32K × 3 회 × 페이지 캐시 drop/no-drop (wbuffix)",
         "main_20261008": "보조 데이터셋 — 첫 설계 6×6 중 측정한 부분 (base 20 회 + 실패 1, wbuffix 53 회)"}.get(EXP.name, EXP.name)


def img(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


used, sections, toc = set(), [], []
for gi, (gtitle, items) in enumerate(GROUPS):
    cards = []
    for pat, cap in items:
        for f in sorted(EXP.glob(pat)):
            if f in used:
                continue
            used.add(f)
            name = f.relative_to(EXP)
            cards.append(f'<figure><img loading="lazy" src="{img(f)}" alt="{html.escape(cap)}"><figcaption><b>{html.escape(cap)}</b>'
                         f'<span>{html.escape(str(name))}</span></figcaption></figure>')
    if cards:
        sections.append(f'<section id="g{gi}"><h2>{html.escape(gtitle)}</h2>{"".join(cards)}</section>')
        toc.append(f'<a href="#g{gi}">{html.escape(gtitle)}</a>')
rest = [f for f in sorted(EXP.glob("analysis/*.png")) + sorted(EXP.glob("plots/*.png")) if f not in used]
if rest:
    sections.append('<section id="rest"><h2>기타</h2>' + "".join(
        f'<figure><img loading="lazy" src="{img(f)}"><figcaption><span>{html.escape(str(f.relative_to(EXP)))}</span></figcaption></figure>' for f in rest) + "</section>")
    toc.append('<a href="#rest">기타</a>')

page = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>KSC2026 그래프 — {html.escape(EXP.name)}</title>
<style>
:root {{ --bg:#f9f9f7; --card:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --line:#e1e0d9; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:14px/1.5 system-ui,-apple-system,"Segoe UI","Malgun Gothic",sans-serif; padding:0 16px 48px; }}
header {{ max-width:1200px; margin:0 auto; padding:24px 0 8px; }}
h1 {{ font-size:20px; margin:0 0 4px; }} h2 {{ font-size:17px; margin:32px 0 12px; border-bottom:1px solid var(--line); padding-bottom:6px; }}
p.sub {{ color:var(--ink2); margin:0 0 12px; }}
nav {{ display:flex; flex-wrap:wrap; gap:8px; }} nav a {{ color:var(--ink2); text-decoration:none; border:1px solid var(--line); border-radius:999px; padding:2px 10px; background:var(--card); }}
main {{ max-width:1200px; margin:0 auto; }}
section {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(520px,1fr)); gap:16px; }}
section h2 {{ grid-column:1/-1; }}
figure {{ margin:0; background:var(--card); border:1px solid var(--line); border-radius:8px; padding:10px; }}
figure img {{ width:100%; height:auto; display:block; cursor:zoom-in; }}
figcaption {{ margin-top:6px; color:var(--ink2); font-size:13px; }} figcaption span {{ display:block; font-family:ui-monospace,Consolas,monospace; font-size:11px; color:#898781; }}
@media (max-width:600px) {{ section {{ grid-template-columns:1fr; }} }}
</style></head><body>
<header><h1>KSC2026 NVMeVirt 매핑 단위 실험 — 그래프 모음</h1>
<p class="sub">{html.escape(TITLE)} · 원본 폴더 exp/results/{html.escape(EXP.name)}/ · 그림 {len(used) + len(rest)} 장 · 이미지를 누르면 새 탭에서 크게 볼 수 있다</p>
<nav>{"".join(toc)}</nav></header>
<main>{"".join(sections)}</main>
<script>document.querySelectorAll("figure img").forEach(i=>i.addEventListener("click",()=>{{const w=window.open();if(w){{w.document.write('<img src="'+i.src+'" style="max-width:100%">');}}}}));</script>
</body></html>"""
OUT.write_text(page)
print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB, {len(used) + len(rest)} images)")
