"""
미국 주요 기업 주가 → stocks.json (GitHub Actions용, 무료 yfinance)
──────────────────────────────────────────────────────────────
매일 GitHub Actions가 실행 → stocks.json 커밋 → raw URL로 공개.
대시보드의 예약 작업이 그 URL을 읽어 '미국 주요 기업' 섹션에 반영.

로컬 테스트:  pip install yfinance && python stocks_fetch.py
"""
import json, datetime
import yfinance as yf

# 티커: 한글명(원하면 자유롭게 추가/삭제)
TICKERS = {
    # 미국 주요 기업
    "AAPL": "애플",
    "MSFT": "마이크로소프트",
    "NVDA": "엔비디아",
    "GOOGL": "알파벳(구글)",
    "AMZN": "아마존",
    "META": "메타",
    "TSLA": "테슬라",
    "AVGO": "브로드컴",
    # 섹터 대표 ETF (국내 상장 프록시) — KRX 티커는 .KS 접미사
    "091160.KS": "KODEX 반도체",
    "139260.KS": "TIGER 200 IT",
    "315270.KS": "TIGER 200 커뮤니케이션",
    "091180.KS": "KODEX 자동차",
    "305720.KS": "KODEX 2차전지산업",
    "139250.KS": "TIGER 200 에너지화학",
    "139240.KS": "TIGER 200 철강소재",
    "139230.KS": "TIGER 200 중공업",
    "091170.KS": "KODEX 은행",
    "139280.KS": "TIGER 200 경기소비재",
    "139220.KS": "TIGER 200 건설",
    "227540.KS": "TIGER 200 헬스케어",
}
N = 66  # 최근 거래일 수(약 3개월)

def main():
    out = {"asOf": datetime.date.today().isoformat(), "series": {}}
    df = yf.download(list(TICKERS), period="5mo", interval="1d",
                     auto_adjust=True, progress=False)
    close = df["Close"]
    for tk, name in TICKERS.items():
        try:
            s = close[tk].dropna().tail(N)
            out["series"][tk] = {
                "name": name,
                "d": [d.strftime("%m.%d") for d in s.index],
                "v": [round(float(v), 2) for v in s.values],
            }
        except Exception as e:
            out["series"][tk] = {"name": name, "error": str(e)}
    with open("stocks.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print("wrote stocks.json:", out["asOf"], "| tickers:", list(out["series"].keys()))

if __name__ == "__main__":
    main()
