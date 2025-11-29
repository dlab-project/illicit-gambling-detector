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
        
        # 뉴스 사이트 도메인 목록 (제외할 사이트)
        self.news_domains = [
            'news.', 'naver.com', 'daum.net', 'joins.com', 'chosun.com',
            'donga.com', 'khan.co.kr', 'hankyung.com', 'mk.co.kr',
            'yna.co.kr', 'newsis.com', 'ytn.co.kr', 'sbs.co.kr',
            'kbs.co.kr', 'mbc.co.kr', 'jtbc.co.kr', 'mt.co.kr',
            'sedaily.com', 'seoul.co.kr', 'hani.co.kr', 'kmib.co.kr',
            'segye.com', 'fnnews.com', 'newsway.co.kr', 'journalist.or.kr'
        ]

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
        
        # 드라이버 세션 유효성 검사 (세션이 끊어진 경우 재초기화)
        try:
            # 현재 URL 확인 시도 (세션이 유효한지 테스트)
            _ = self.driver.current_url
        except Exception as e:
            print(f"  ⚠️ 브라우저 세션 끊김, 드라이버 재초기화 중... ({e})")
            self.driver = None
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
                    # 구글 내부 링크 및 data: URL 제외
                    if "google.com" not in href and not href.startswith("data:"):
                        # 뉴스 사이트 제외
                        is_news_site = any(news_domain in href for news_domain in self.news_domains)
                        if not is_news_site:
                            valid_links.append(link_element)
                        else:
                            print(f"    ⏭️ 뉴스 사이트 건너뛰기: {href}")
            
            # 최대 링크 수만큼만 방문
            links_to_visit = valid_links[:max_links]
            print(f"  📋 {len(valid_links)}개의 유효 링크 발견, {len(links_to_visit)}개 방문 예정")
            
            # 각 링크 방문
            for i, link_element in enumerate(links_to_visit, 1):
                try:
                    # 링크 URL 저장 (클릭 후에는 접근 불가능)
                    target_url = link_element.get_attribute("href")
                    print(f"    [{i}/{len(links_to_visit)}] 🔗 클릭: {target_url}")
                    
                    # 링크 클릭
                    link_element.click()
                    
                    # 페이지 로딩 대기
                    time.sleep(random.uniform(2, 3))
                    
                    # 현재 페이지의 HTML 수집
                    current_url = self.driver.current_url
                    html_content = self.driver.page_source
                    
                    results.append((current_url, html_content))
                    print(f"    ✅ HTML 수집 완료: {current_url}")
                    
                    # 뒤로가기 (다음 검색을 위해 항상 검색 결과 페이지로 돌아감)
                    is_last_link = (i == len(links_to_visit))
                    # 뒤로가기
                    self.driver.back()
                    
                    # 검색 결과 페이지 로딩 대기
                    time.sleep(random.uniform(1, 2))
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "rso"))
                    )
                    
                    # 마지막 링크가 아니면 다음 링크 준비
                    if not is_last_link:
                        # rso 영역 다시 찾기 (페이지가 새로 로드되었으므로)
                        rso_element = self.driver.find_element(By.ID, "rso")
                        link_elements = rso_element.find_elements(By.TAG_NAME, "a")
                        
                        # 다음 링크를 위해 valid_links 재구성
                        valid_links = []
                        for link_element in link_elements:
                            href = link_element.get_attribute("href")
                            if href and (href.startswith("http://") or href.startswith("https://")):
                                if "google.com" not in href and not href.startswith("data:"):
                                    # 뉴스 사이트 제외
                                    is_news_site = any(news_domain in href for news_domain in self.news_domains)
                                    if not is_news_site:
                                        valid_links.append(link_element)
                        
                        # 다음에 방문할 링크 업데이트 (이미 방문한 것 제외)
                        links_to_visit = valid_links[:max_links]
                    
                except Exception as e:
                    print(f"    ❌ 링크 방문 오류: {e}")
                    # 에러 발생 시 검색 결과 페이지로 돌아가기 시도
                    try:
                        self.driver.back()
                        time.sleep(1)
                        # 검색 결과 페이지 확인
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.ID, "rso"))
                        )
                    except:
                        print(f"    ⚠️ 검색 결과 페이지로 복귀 실패")
                        pass
                    continue
        
        except Exception as e:
            print(f"  ❌ 검색 결과 링크 찾기 오류: {e}")
        
        return results

    def close(self):
        # 드라이버 종료
        if self.driver:
            self.driver.quit()
            self.driver = None