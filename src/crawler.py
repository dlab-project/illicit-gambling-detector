import time
import json
from typing import Dict, Any

from .keyword_manager import KeywordManager
from .search_engine import SearchEngine
from .url_extractor import URLExtractor
from .json_storage import JSONStorage


class GamblingDomainCrawler:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings = self._load_settings(settings_file)
        self.keyword_manager = KeywordManager()
        self.search_engine = SearchEngine(headless=self.settings.get("headless_mode", True))
        self.url_extractor = URLExtractor(
            remove_tracking_params=self.settings.get("remove_tracking_params", True)
        )
        self.storage = JSONStorage(self.settings.get("output_file", "results.json"))

    def _load_settings(self, settings_file: str) -> Dict[str, Any]:
        # 설정 파일 로드
        with open(settings_file, 'r', encoding='utf-8') as f:
            return json.load(f)

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

            # 새로운 URL 저장
            if new_urls:
                self.storage.save_results(new_urls, keyword)
                existing_urls.update(new_urls)
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