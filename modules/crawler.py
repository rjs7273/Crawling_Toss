from dateutil import parser
from datetime import datetime
from modules.scraper import open_page, change_recent_option, scroll_down
from modules.parser import extract_text, extract_time, extract_transaction
from modules.storage import get_latest_id, save_to_csv

from selenium.webdriver.common.by import By

class Crawler:
    def __init__(self, driver, ticker, cutoff_time):
        """Crawler 클래스 초기화"""
        self.driver = driver
        self.ticker = ticker  # 티커 정보 저장
        self.url = f"https://tossinvest.com/stocks/A{ticker}/community"
        self.csv_filename = f"data/{ticker}_comments.csv"
        self.latest_id = get_latest_id(self.csv_filename)
        self.data = []
        self.stop_crawling = False
        self.cutoff_time = parser.isoparse(cutoff_time)

    def crawl_page(self):
        """현재 페이지에서 댓글 크롤링"""
        articles = self.driver.find_elements(By.CSS_SELECTOR, "article.comment")

        for article in articles:
            post_id = article.get_attribute("data-post-anchor-id")
            if self.latest_id and post_id == self.latest_id:
                print(f"[{self.ticker}] 기존 ID ({self.latest_id})와 일치하는 댓글 발견. 크롤링 중단.")
                self.stop_crawling = True
                return

            title_element = article.find_element(By.CSS_SELECTOR, "a span.tw-1r5dc8g0")
            title = title_element.text.strip() if title_element else None

            content_element = article.find_element(By.CSS_SELECTOR, "a span.tw-1r5dc8g0._60z0ev1")
            content = extract_text(content_element) if content_element else None

            comment_time_str = extract_time(article)
            comment_time = parser.isoparse(comment_time_str) if comment_time_str else None

            # 특정 시간 이전의 데이터가 나오면 중단
            if comment_time and comment_time < self.cutoff_time:
                print(f"[{self.ticker}] {comment_time} < {self.cutoff_time}, 수집 중단.")
                self.stop_crawling = True
                return

            transaction_data = extract_transaction(article)

            row = {
                "id": post_id,
                "flatform": 'toss',
                "ticker": self.ticker,
                "title": title,
                "content": content,
                "comment_time": comment_time_str,
                "stock_name": None,
                "quantity": None,
                "transaction_type": None,
                "price_per_share": None,
                "transaction_date": None,
                "profit": None
            }

            if transaction_data:
                row.update(transaction_data)

            self.data.append(row)

    def run(self):
        """전체 크롤링 실행 (while문 사용 + 특정 시간 이전 데이터 중지)"""
        open_page(self.driver, self.url)
        change_recent_option(self.driver)

        while not self.stop_crawling:
            self.crawl_page()
            if not self.stop_crawling:
                scroll_down(self.driver)

        save_to_csv(self.data, self.csv_filename)
        print(f"[{self.ticker}] 크롤링 완료. 저장된 데이터 개수: {len(self.data)}")
