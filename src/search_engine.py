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

    def visit_search_result_links(self, max_links: int = 10) -> list:
        """
        검색 결과 페이지에서 링크를 찾아 각각 방문하고 HTML을 수집합니다.
        
        Args:
            max_links: 방문할 최대 링크 수
            
        Returns:
            [(url, html_content), ...] 형태의 리스트
        """
        results = []
        
        try:
            # rso 영역에서 링크 요소들 찾기
            rso_element = self.driver.find_element(By.ID, "rso")
            link_elements = rso_element.find_elements(By.TAG_NAME, "a")
            
            # 유효한 링크만 필터링 (href 속성이 있고 http로 시작하는 것)
            valid_links = []
            for link_element in link_elements:
                href = link_element.get_attribute("href")
                if href and (href.startswith("http://") or href.startswith("https://")):
                    # 구글 내부 링크 제외
                    if "google.com" not in href:
                        valid_links.append(link_element)
            
            # 최대 링크 수만큼만 방문
            links_to_visit = valid_links[:max_links]
            print(f"  Found {len(valid_links)} valid links, visiting {len(links_to_visit)} links")
            
            # 각 링크 방문
            for i, link_element in enumerate(links_to_visit, 1):
                try:
                    # 링크 URL 저장 (클릭 후에는 접근 불가능)
                    target_url = link_element.get_attribute("href")
                    print(f"    [{i}/{len(links_to_visit)}] Clicking: {target_url}")
                    
                    # 링크 클릭
                    link_element.click()
                    
                    # 페이지 로딩 대기
                    time.sleep(random.uniform(2, 3))
                    
                    # 현재 페이지의 HTML 수집
                    current_url = self.driver.current_url
                    html_content = self.driver.page_source
                    
                    results.append((current_url, html_content))
                    print(f"    ✓ Collected HTML from: {current_url}")
                    
                    # 뒤로가기
                    self.driver.back()
                    
                    # 검색 결과 페이지 로딩 대기
                    time.sleep(random.uniform(1, 2))
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "rso"))
                    )
                    
                    # rso 영역 다시 찾기 (페이지가 새로 로드되었으므로)
                    rso_element = self.driver.find_element(By.ID, "rso")
                    link_elements = rso_element.find_elements(By.TAG_NAME, "a")
                    
                    # 다음 링크를 위해 valid_links 재구성
                    valid_links = []
                    for link_element in link_elements:
                        href = link_element.get_attribute("href")
                        if href and (href.startswith("http://") or href.startswith("https://")):
                            if "google.com" not in href:
                                valid_links.append(link_element)
                    
                    # 다음에 방문할 링크 업데이트 (이미 방문한 것 제외)
                    links_to_visit = valid_links[:max_links]
                    
                except Exception as e:
                    print(f"    ✗ Error visiting link: {e}")
                    # 에러 발생 시 검색 결과 페이지로 돌아가기 시도
                    try:
                        self.driver.back()
                        time.sleep(1)
                    except:
                        pass
                    continue
        
        except Exception as e:
            print(f"  Error finding search result links: {e}")
        
        return results

    def close(self):
        # 드라이버 종료
        if self.driver:
            self.driver.quit()
            self.driver = None