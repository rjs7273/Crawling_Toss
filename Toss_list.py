import pandas as pd
import re
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager



# 크롬 드라이버 설정
chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_experimental_option("detach", True)

# 웹드라이버 실행
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 페이지 이동
url = "https://tossinvest.com/stocks/A005930/community"
driver.get(url)
time.sleep(3)

# 최신순 정렬 버튼 클릭
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
    """거래 내역 추출
        이 부분도 일단 아래 내용 먼저 본 다음 분석하는게 나을듯?"""
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
    """댓글 작성 시간을 절대적인 시간으로 변환하여 추출"""
    try:
        time_element = article.find_element(By.CSS_SELECTOR, "time._1tvp9v40")
        relative_time = time_element.text.strip() if time_element else None

        # 예외 처리: relative_time이 None이면 반환
        if not relative_time:
            return None

        # 현재 시간
        now = datetime.now()

        # 상대 시간을 절대 시간으로 변환
        if "분 전" in relative_time:
            match = re.search(r"(\d+)분 전", relative_time)
            if match:
                minutes_ago = int(match.group(1))
                absolute_time = now - timedelta(minutes=minutes_ago)
        elif "시간 전" in relative_time:
            match = re.search(r"(\d+)시간 전", relative_time)
            if match:
                hours_ago = int(match.group(1))
                absolute_time = now - timedelta(hours=hours_ago)
        elif "일 전" in relative_time:
            match = re.search(r"(\d+)일 전", relative_time)
            if match:
                days_ago = int(match.group(1))
                absolute_time = now - timedelta(days=days_ago)
        else:
            # "YYYY-MM-DD HH:MM" 형식일 경우
            try:
                absolute_time = datetime.strptime(relative_time, "%Y-%m-%d %H:%M")
            except ValueError:
                return None  # 변환 실패 시 None 반환

        return absolute_time.strftime("%Y-%m-%d %H:%M:%S")  # 포맷 변환 후 반환

    except Exception as e:
        print(f"시간 변환 오류: {e}")
        return None



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
        
        # 댓글 절대 시간 추출
        comment_time = extract_time(article)

        # 거래 내역 추출
        transaction_data = extract_transaction(article)

        row = {
            "id": post_id,
            "title": title,
            "content": content,
            "comment_time": comment_time,  # 🕒 절대 시간으로 변환된 댓글 작성 시간 추가
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
