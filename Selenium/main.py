from modules.scraper import init_driver
from modules.crawler import Crawler

# 종목 코드 리스트
tickers = [
    # '096770',  # SK이노베이션
    # '005490',  # POSCO홀딩스
    # '000720',  # 현대건설
    # '005380',  # 현대자동차
    # '271560',  # 오리온
    # '207940',  # 삼성바이오로직스
    # '105560',  # KB금융
    '005930',  # 삼성전자 # 얘만 유난히 댓글량이 많아서 일단 제외
    # '035420',  # NAVER
    # '015760'   # 한국전력
]

# 종목 코드 → 종목명 매핑
stock_names = {
    # '096770': 'SK이노베이션',
    # '005490': 'POSCO홀딩스',
    # '000720': '현대건설',
    # '005380': '현대자동차',
    # '271560': '오리온',
    # '207940': '삼성바이오로직스',
    # '105560': 'KB금융',
    '005930': '삼성전자',
    # '035420': 'NAVER',
    # '015760': '한국전력'
}

# 수집 기준 시간
cutoff_time = "2025-03-21T13:00:00+09:00"  # KST 시간대 포함 (ISO 8601)

driver = init_driver()

for ticker in tickers:
    crawler = Crawler(driver, ticker, stock_names[ticker], cutoff_time)
    crawler.run()

driver.quit()
print("모든 종목 크롤링 완료.")
