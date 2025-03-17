# 데이터 파싱 기능(BeautifulSoup, 정규식)

import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def extract_text(element):
    """불필요한 태그를 제거하고 텍스트만 추출"""
    soup = BeautifulSoup(element.get_attribute("outerHTML"), "html.parser")
    
    for a in soup.find_all("a"):
        a.decompose()

    return soup.get_text(separator=" ", strip=True)

def extract_transaction(article):
    """거래 내역 추출"""
    try:
        transaction_block = article.find_element(By.CSS_SELECTOR, "section._1sihfl61 div.z6n2t5x")
        text = transaction_block.text.strip()

        match = re.search(r"(\S+)\s(\d+)주\s(구매|판매)", text)
        price_match = re.search(r"1주당\s([\d,]+)원", text)
        date_match = re.search(r"(\d+월 \d+일 \d+:\d+)", text)
        profit_match = re.search(r"([\+\-]?\d+,\d+원\s\([\d\.]+%\))", text)

        if match:
            stock_name, quantity, transaction_type = match.groups()
            quantity = int(quantity.replace(",", ""))
        else:
            return None

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
        return None

def extract_time(article):
    """댓글 작성 시간 추출"""
    try:
        time_element = article.find_element(By.CSS_SELECTOR, "time._1tvp9v40")
        return time_element.get_attribute("datetime") if time_element else None
    except:
        return None
