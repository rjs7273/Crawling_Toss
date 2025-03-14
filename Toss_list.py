import pandas as pd
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 크롬 드라이버 설정
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_experimental_option("detach", True)

# 웹드라이버 실행
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 페이지 이동
url = "https://tossinvest.com/stocks/A005930/community"
driver.get(url)
time.sleep(3)

# 스크롤 함수
def scroll_down():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

# 불필요한 태그를 제거하고 텍스트만 추출하는 함수
def extract_text(element):
    """불필요한 태그를 제거하고 텍스트만 추출"""
    soup = BeautifulSoup(element.get_attribute("outerHTML"), "html.parser")

    # 링크 제거
    for a in soup.find_all("a"):
        a.decompose()
    
    # 이미지 제거 (이모티콘, 차트 이미지 등)
    for img in soup.find_all("img"):
        img.decompose()
    
    # 블록(거래 내역 등) 제거
    for div in soup.find_all("div", class_=["ue35rv4", "kpufsn0", "z6n2t5x"]):
        div.decompose()
    
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

# 댓글 크롤링
data = []

def crawl():
    articles = driver.find_elements(By.CSS_SELECTOR, "article.comment")
    for article in articles:
        post_id = article.get_attribute("data-post-anchor-id")  # ID 추출
        
        # 제목 추출
        title_element = article.find_element(By.CSS_SELECTOR, "a span.tw-1r5dc8g0")
        title = title_element.text.strip() if title_element else None
        
        # 본문 추출
        content_element = article.find_element(By.CSS_SELECTOR, "a span.tw-1r5dc8g0._60z0ev1")
        content = extract_text(content_element) if content_element else None
        
        # 거래 내역 추출
        transaction_data = extract_transaction(article)

        row = {
            "id": post_id,
            "title": title,
            "content": content,
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
for _ in range(5):
    crawl()
    scroll_down()

# 데이터 저장
df = pd.DataFrame(data)

# ID를 기준으로 중복된 행 제거 (첫 번째 값 유지, 순서 유지)
df = df.drop_duplicates(subset=["id"], keep="first")

df.to_csv("samsung_comments.csv", index=False, encoding="utf-8-sig")

# 웹드라이버 종료
driver.quit()

# 결과 확인
print(df.head())
