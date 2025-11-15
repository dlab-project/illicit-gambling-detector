import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class SearchEngine:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def setup_driver(self):
        # Chrome 옵션 설정
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # User-Agent 랜덤 설정
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")

        # ChromeDriver 설치 및 초기화
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # 자동화 탐지 우회
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def search_google(self, keyword: str) -> str:
        # 드라이버가 없으면 초기화
        if not self.driver:
            self.setup_driver()

        # Google 검색 실행
        search_url = f"https://www.google.com/search?q={keyword}"
        self.driver.get(search_url)

        # 랜덤 딜레이 (봇 탐지 회피)
        random_delay = random.uniform(2, 4)
        time.sleep(random_delay)

        # 검색 결과 로딩 대기
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#search"))
        )

        # 추가 딜레이
        time.sleep(random.uniform(1, 2))
        
        return self.driver.page_source

    def close(self):
        # 드라이버 종료
        if self.driver:
            self.driver.quit()
            self.driver = None