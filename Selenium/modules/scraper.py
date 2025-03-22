import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    """크롬 드라이버 설정 및 실행"""
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_experimental_option("detach", True)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def open_page(driver, url):
    """URL 열기"""
    driver.get(url)
    time.sleep(2)

def change_recent_option(driver):
    """현재 정렬 상태를 확인하고 '최신순'이 아니면 변경"""
    sort_button = driver.find_element(By.CSS_SELECTOR, "button[data-parent-name='StocksFeedFilter']")
    current_label = sort_button.get_attribute("data-contents-label")

    if current_label == "인기순":
        sort_button.click()
        time.sleep(2)
    else:
        pass # 최신순인 경우


def scroll_down(driver):
    """스크롤 다운"""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
