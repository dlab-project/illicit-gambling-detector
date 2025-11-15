import time
import json
import requests
from typing import Dict, Any
from urllib.parse import urlparse

from .keyword_manager import KeywordManager
from .search_engine import SearchEngine
from .url_extractor import URLExtractor
from .json_storage import JSONStorage
from .gemini_classifier import GeminiClassifier


class GamblingDomainCrawler:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings = self._load_settings(settings_file)
        self.keyword_manager = KeywordManager()
        self.search_engine = SearchEngine(headless=self.settings.get("headless_mode", True))
        self.url_extractor = URLExtractor(
            remove_tracking_params=self.settings.get("remove_tracking_params", True)
        )
        self.storage = JSONStorage(self.settings.get("output_file", "results.json"))
        
        # Gemini 분류기 초기화
        try:
            self.classifier = GeminiClassifier(
                api_key=self.settings.get("gemini_api_key")
            )
            self.use_classifier = self.settings.get("use_gemini_classifier", True)
        except ValueError as e:
            print(f"Warning: Gemini classifier not initialized - {e}")
            self.classifier = None
            self.use_classifier = False

    def _load_settings(self, settings_file: str) -> Dict[str, Any]:
        # 설정 파일 로드
        with open(settings_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _fetch_html_from_url(self, url: str, timeout: int = 10) -> str:
        """URL에서 HTML 콘텐츠를 가져옵니다"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.encoding = response.apparent_encoding or 'utf-8'
            return response.text
        except Exception as e:
            print(f"Failed to fetch URL {url}: {e}")
            return ""

    def _classify_and_filter_urls(self, urls: list) -> tuple:
        """
        URL 목록을 분류하고 불법 도박 사이트만 필터링합니다
        
        Returns:
            (filtered_urls, classification_results) 튜플
        """
        if not self.use_classifier or not self.classifier:
            return urls, None

        filtered_urls = []
        classification_results = []

        for url in urls:
            # URL에서 HTML 콘텐츠 가져오기
            print(f"  Fetching content from: {url}")
            html_content = self._fetch_html_from_url(url)

            if not html_content:
                # HTML을 가져올 수 없으면 건너뛰기
                print(f"  Skipping {url} - could not fetch content")
                continue

            # Gemini로 불법 사이트 판별
            print(f"  Classifying: {url}")
            result = self.classifier.classify_url(url, html_content)
            classification_results.append(result)

            # 오류가 없고 불법 사이트면 필터링된 목록에 추가
            if result.get("error") is None and result.get("is_illegal"):
                print(f"  ✓ Illegal site detected: {url} (confidence: {result.get('confidence', 0):.2f})")
                filtered_urls.append(url)
            elif result.get("error"):
                print(f"  ⚠ Classification error for {url}: {result.get('error')}")
            else:
                print(f"  ✗ Not an illegal gambling site: {url}")

        return filtered_urls, classification_results

    def crawl(self):
        print("Starting gambling domain crawler...")

        # 키워드 조합 생성
        keywords = self.keyword_manager.generate_combinations()
        print(f"Generated {len(keywords)} keywords to search")

        delay = self.settings.get("delay_between_searches", 2)
        existing_urls = self.storage.get_existing_urls()

        # 모든 키워드에 대해 검색 수행
        for i, keyword in enumerate(keywords, 1):
            print(f"[{i}/{len(keywords)}] Searching for: {keyword}")

            # Google 검색 수행
            html_content = self.search_engine.search_google(keyword)

            # URL 추출
            urls = self.url_extractor.extract_urls_from_html(html_content)
            new_urls = [url for url in urls if url not in existing_urls]

            # 새로운 URL이 있으면 분류 및 저장
            if new_urls:
                print(f"Found {len(new_urls)} new URLs")
                
                # Gemini 분류기를 사용하여 불법 사이트만 필터링
                filtered_urls, classification_results = self._classify_and_filter_urls(new_urls)
                
                if filtered_urls:
                    # 불법 사이트로 판별된 URL만 저장
                    self.storage.save_results(filtered_urls, keyword, classification_results)
                    existing_urls.update(filtered_urls)
                    print(f"Saved {len(filtered_urls)} illegal gambling URLs for keyword: {keyword}")
                else:
                    print(f"No illegal gambling sites found for keyword: {keyword}")
            else:
                print(f"No new URLs found for keyword: {keyword}")

            # 다음 검색 전 대기
            if i < len(keywords):
                print(f"Waiting {delay} seconds before next search...")
                time.sleep(delay)

        # 브라우저 종료 및 결과 출력
        self.search_engine.close()
        self._print_final_stats()

    def _print_final_stats(self):
        stats = self.storage.get_stats()
        print("\n" + "="*50)
        print("CRAWLING SUMMARY")
        print("="*50)
        print(f"Total entries: {stats['total_entries']}")
        print(f"Unique URLs: {stats['unique_urls']}")
        print(f"Keywords used: {stats['keywords_used']}")
        print(f"Output file: {self.settings.get('output_file', 'results.json')}")
        print("="*50)
