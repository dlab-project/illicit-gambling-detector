# 📌 PRD (MVP Version): Keyword-Based Illegal Gambling Domain Detection Crawler

## 1. Overview
This project aims to build a **minimal viable product (MVP)** for detecting potentially illegal gambling-related domains by **searching keywords, extracting URLs from search engine result pages (SERPs), and storing them locally**.

The system:
- Generates keyword combinations
- Searches them automatically using Selenium
- Extracts URLs from the search results (first page only)
- Stores them in a local database (JSON or SQLite)

➡ **No domain analysis, no risk scoring, no UI, no scheduler — purely URL collection.**

---

## 2. Objectives
- Load a keyword list from a local file  
- Generate simple keyword combinations  
- Automate search using Selenium  
- Extract URLs from the SERP  
- Store extracted URLs locally  

---

## 3. Scope (MVP Features)

### ✔ 3.1 Keyword List Loading
- Load keywords from `keywords.json`
- Allow single keywords and 2-keyword combinations

### ✔ 3.2 Keyword Combination Engine (Simple)
- Combine every pair of keywords
- Example:  
  - `["sports", "betting"]` → `["sports", "betting", "sports betting"]`

### ✔ 3.3 Selenium Search Automation
- Support **one search engine** (Google or Naver)
- Fetch only **page 1** of results
- Support headless mode

### ✔ 3.4 URL Extraction
- Extract all anchor tag URLs (`<a href="...">`)
- Remove duplicates
- Option to remove tracking params (e.g., `?utm_source=...`)

### ✔ 3.5 Local Database Storage
- Store results in SQLite or JSON
- Required fields:
  - `url`
  - `keyword_used`
  - `collected_at` (timestamp)

---

## 4. Out of Scope (Not Included in MVP)
The following features are intentionally excluded:

- Domain risk scoring (WHOIS, VirusTotal, etc.)  
- AI/ML domain pattern detection  
- Multi-search-engine support  
- Automated scheduling (manual run only)  
- Proxy/anti-blocking systems  
- Admin dashboard UI  
- Crawling inside the target website  
- Messaging platform scraping (Telegram, Discord, etc.)

➡ **MVP = "Keyword → Search → URL → Save" only.**

---

## 5. Workflow

1. Load `keywords.json`  
2. Generate keyword combinations  
3. Run Selenium for each keyword  
4. Load the SERP  
5. Extract URLs  
6. Remove duplicates  
7. Save to DB (SQLite/JSON)  
8. Repeat for next keyword  

---

## 6. Technical Requirements

### Language & Libraries
- Python 3.10+
- Selenium
- BeautifulSoup4 (optional)
- SQLite / JSON
- ChromeDriver / Chromium

### Execution Environment
- CLI-based Python script
- `settings.json` handles:
  - search engine selection
  - headless mode
  - DB mode (json/sqlite)

---

## 7. Recommended Directory Structure

