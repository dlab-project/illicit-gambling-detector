import requests
from urllib.parse import quote_plus


class SearchEngine:
    def __init__(self, headless: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_google(self, keyword: str) -> str:
        try:
            encoded_keyword = quote_plus(keyword)
            search_url = f"https://www.google.com/search?q={encoded_keyword}"

            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()

            return response.text
        except Exception as e:
            print(f"Error searching for '{keyword}': {str(e)}")
            return ""

    def close(self):
        if self.session:
            self.session.close()