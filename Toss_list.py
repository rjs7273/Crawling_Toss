from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# 1. 크롬 드라이버 설정
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 백그라운드 실행 (원하면 주석 처리)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_experimental_option("detach", True)  # 브라우저가 자동으로 닫히지 않도록 설정


# 2. 웹드라이버 실행
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 3. 페이지 이동
url = "https://tossinvest.com/stocks/A005930/community"  # 토스증권 삼성전자 커뮤니티 URL
driver.get(url)
time.sleep(3)  # 페이지 로딩 대기

comment_selectors = [
    # "span.tw-1r5dc8g0._1sihfl60",  # 첫 번째 댓글 요소
    "span.tw-1r5dc8g0._60z0ev1._60z0ev6._60z0ev0._1tvp9v41._1sihfl60"  # 두 번째 댓글 요소
]

data = []

# 스크롤 함수
def scroll_down():
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # 스크롤 후 대기


# 5. 댓글 크롤링 (공통 클래스 기반 CSS 선택자)

def crawl():
    for selector in comment_selectors:
        comments = driver.find_elements(By.CSS_SELECTOR, selector)
        for comment in comments:
            text = comment.text.strip().replace("\n", " ")  # 개행 문자 제거
            if text:  # 빈 문자열이 아닌 경우만 저장
                data.append({"comment": text})


for _ in range(5):
    crawl()
    scroll_down()


# 6. 데이터 저장
df = pd.DataFrame(data)
df.to_csv("samsung_comments.csv", index=False, encoding="utf-8-sig")

# 7. 웹드라이버 종료
# driver.quit()

# 8. 크롤링한 데이터 확인
print(df.head())
