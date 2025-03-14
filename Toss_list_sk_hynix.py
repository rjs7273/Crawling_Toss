import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

# 기존 CSV 파일에서 첫 번째 ID 불러오기
def get_latest_id(csv_filename):
    if os.path.exists(csv_filename):  # 파일이 존재하는 경우
        df_existing = pd.read_csv(csv_filename, encoding="utf-8-sig")
        if not df_existing.empty:
            return str(df_existing.iloc[0]["id"])  # 첫 번째 ID 반환
    return None  # 파일이 없거나 데이터가 없는 경우 None 반환

# 크롬 드라이버 설정
chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_experimental_option("detach", True)

# 웹드라이버 실행
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 페이지 이동
url = "https://tossinvest.com/stocks/A000660/community" # sk 하이닉스 url
driver.get(url)
time.sleep(3)

# 최신순 정렬 버튼 클릭
def change_recent_option():
    sort_button = driver.find_element(By.CSS_SELECTOR, "button[data-contents-label='인기순']")
    sort_button.click()
    time.sleep(3)

# 스크롤 함수
def scroll_down():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# 본문의 내용 추출 함수
def extract_text(element):
    """불필요한 태그를 제거하고 텍스트만 추출"""
    soup = BeautifulSoup(element.get_attribute("outerHTML"), "html.parser")

    for a in soup.find_all("a"):
        a.decompose()
    
    return soup.get_text(separator=" ", strip=True)

# 거래 내역을 추출하는 함수
def extract_transaction(article):
    """거래 내역 추출"""
    try:
        transaction_block = article.find_element(By.CSS_SELECTOR, "section._1sihfl61 div.z6n2t5x")
        text = transaction_block.text.strip()
        
        # 정규식을 이용하여 거래 정보 추출
        match = re.search(r"(\S+)\s(\d+)주\s(구매|판매)", text)
        price_match = re.search(r"1주당\s([\d,]+)원", text)
        date_match = re.search(r"(\d+월 \d+일 \d+:\d+)", text)
        profit_match = re.search(r"([\+\-]?\d+,\d+원\s\([\d\.]+%\))", text)
        
        if match:
            stock_name, quantity, transaction_type = match.groups()
            quantity = int(quantity.replace(",", ""))
        else:
            return None  # 거래 내역이 없으면 None 반환

        price = int(price_match.group(1).replace(",", "")) if price_match else None
        transaction_date = date_match.group(1) if date_match else None
        profit = profit_match.group(1) if profit_match else None

        return {
            "stock_name": stock_name,
            "quantity": quantity,
            "transaction_type": transaction_type,
            "price_per_share": price,
            "transaction_date": transaction_date,
            "profit": profit
        }
    
    except:
        return None  # 거래 내역이 없으면 None 반환

def extract_time(article):
    """댓글 작성 시간을 datetime 속성값에서 직접 추출"""
    try:
        time_element = article.find_element(By.CSS_SELECTOR, "time._1tvp9v40")
        absolute_time = time_element.get_attribute("datetime") if time_element else None

        return absolute_time  # 그대로 반환 (ISO 8601 형식)
    
    except Exception as e:
        print(f"시간 변환 오류: {e}")
        return None

# CSV 파일명 설정
csv_filename = "sk_hynix_comments.csv"
latest_id = get_latest_id(csv_filename)  # 기존 파일에서 첫 번째 ID 불러오기

# 댓글 크롤링
data = []
stop_crawling = False  # 탐색 중단 여부 플래그

def crawl():
    global stop_crawling
    articles = driver.find_elements(By.CSS_SELECTOR, "article.comment")
    for article in articles:
        post_id = article.get_attribute("data-post-anchor-id")  # ID 추출
        
        # 기존 ID와 일치하면 크롤링 중단
        if latest_id and post_id == latest_id:
            print(f"기존 ID ({latest_id})와 일치하는 댓글 발견. 크롤링 중단.")
            stop_crawling = True
            return

        # 제목 추출
        title_element = article.find_element(By.CSS_SELECTOR, "a span.tw-1r5dc8g0")
        title = title_element.text.strip() if title_element else None
        
        # 본문 추출
        content_element = article.find_element(By.CSS_SELECTOR, "a span.tw-1r5dc8g0._60z0ev1")
        content = extract_text(content_element) if content_element else None
        
        # 댓글 절대 시간 추출
        comment_time = extract_time(article)

        # 거래 내역 추출
        transaction_data = extract_transaction(article)

        row = {
            "id": post_id,
            "title": title,
            "content": content,
            "comment_time": comment_time,
            "stock_name": None,
            "quantity": None,
            "transaction_type": None,
            "price_per_share": None,
            "transaction_date": None,
            "profit": None
        }

        if transaction_data:
            row.update(transaction_data)

        data.append(row)

# 크롤링 실행
change_recent_option()
for _ in range(5):
    if stop_crawling:
        break
    crawl()
    scroll_down()

# 데이터 저장
df_new = pd.DataFrame(data)

# 기존 CSV 파일이 존재하면 데이터를 합치기 전에 새로운 데이터만 중복 제거
if os.path.exists(csv_filename):
    df_existing = pd.read_csv(csv_filename, encoding="utf-8-sig")

    # 새로운 데이터(df_new)만 중복 제거 (기존 데이터에는 영향 없음)
    df_new = df_new.drop_duplicates(subset=["id"], keep="first")

    # 기존 데이터와 병합
    df_combined = pd.concat([df_new, df_existing], ignore_index=True)
else:
    df_combined = df_new  # 파일이 없으면 새 데이터만 저장

# 최종 데이터 저장
df_combined.to_csv(csv_filename, index=False, encoding="utf-8-sig")

# 웹드라이버 종료
driver.quit()

# 결과 확인
print(df_combined.head())
