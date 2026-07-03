"""
FRED → fred.json 생성 스크립트 (GitHub Actions용)
──────────────────────────────────────────────
매일 GitHub Actions가 실행 → fred.json 커밋 → raw URL로 공개.
대시보드의 매일 아침 예약 작업이 그 URL을 읽어 반영합니다.

로컬 테스트:  export FRED_API_KEY=발급키 && python fred_fetch.py
"""
import os, json, datetime
from fredapi import Fred

API_KEY = os.environ.get("FRED_API_KEY", "YOUR_API_KEY")  # Actions에서는 Secret으로 주입
N = 18  # 최근 개월 수(월간)

# 대시보드에 넣을 미국 거시 시리즈 (원하면 자유롭게 추가/삭제)
SERIES = {
    "us10":  ("DGS10",        "미국 10년 국채금리", "%",   2),
    "uspol": ("FEDFUNDS",     "미국 정책금리",       "%",   3),
    "unemp": ("UNRATE",       "미국 실업률",         "%",   1),
    "wti":   ("DCOILWTICO",   "WTI 유가",           "$",   1),
    "term":  ("T10Y2Y",       "미 장단기차 10Y-2Y", "%p",  2),
    "hyoas": ("BAMLH0A0HYM2", "하이일드 신용스프레드","%",  2),
    "dxy":   ("DTWEXBGS",     "달러인덱스(광의)",    "idx", 2),
    "claims":("ICSA",         "신규 실업수당 청구",  "천건", 0),
}

def monthly_tail(s, n=N):
    s = s.dropna().resample("ME").last().dropna().tail(n)
    return [d.strftime("%y.%m") for d in s.index], [round(float(v), 4) for v in s.values]

def main():
    fred = Fred(api_key=API_KEY)
    out = {"asOf": datetime.date.today().isoformat(), "series": {}}
    for key, (sid, desc, unit, fmt) in SERIES.items():
        try:
            d, v = monthly_tail(fred.get_series(sid))
            out["series"][key] = {"id": sid, "desc": desc, "unit": unit, "fmt": fmt, "d": d, "v": v}
        except Exception as e:
            out["series"][key] = {"id": sid, "desc": desc, "error": str(e)}
    # CPI 전년동월비(%)
    try:
        raw = fred.get_series("CPIAUCSL").dropna().resample("ME").last().dropna()
        yoy = ((raw / raw.shift(12) - 1) * 100).dropna().tail(N)
        out["series"]["cpi"] = {"id": "CPIAUCSL(YoY)", "desc": "미국 CPI 전년동월비", "unit": "%", "fmt": 2,
                                "d": [d.strftime("%y.%m") for d in yoy.index],
                                "v": [round(float(x), 2) for x in yoy.values]}
    except Exception as e:
        out["series"]["cpi"] = {"error": str(e)}

    with open("fred.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("wrote fred.json:", out["asOf"], "| series:", list(out["series"].keys()))

if __name__ == "__main__":
    main()
