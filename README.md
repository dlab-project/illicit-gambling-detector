# illicit-gambling-detector

불법 도박 도메인 탐지 크롤러 - 키워드 기반 검색, URL 수집 및 Gemini AI 분석

## 주요 기능

- 🔍 키워드 조합을 통한 자동 검색 (Google)
- 🌐 검색 결과에서 URL 자동 추출 및 방문
- 🤖 Google Gemini AI를 활용한 불법 도박 사이트 자동 판별
- 💾 결과를 JSON 파일 및 Supabase PostgreSQL 데이터베이스에 저장
- 📊 수집 데이터 통계 및 분석 기능

## 설치 및 설정

### 1. 환경 요구사항
- Python 3.12 이상
- Chrome/Chromium 브라우저

### 2. 설치
```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -e .
```

### 3. 환경 변수 설정

`env_template.txt` 파일을 `.env`로 복사하고 실제 값을 입력하세요:

```bash
# 템플릿 파일 복사
cp env_template.txt .env
```

`.env` 파일 내용:
```bash
# Supabase PostgreSQL 연결 정보
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_supabase_host.supabase.co
DB_PORT=5432
DB_NAME=postgres

# Google Gemini API Key (불법 도박 사이트 판별)
GEMINI_API_KEY=your_gemini_api_key_here
```

**⚠️ 중요**: `.env` 파일은 절대 Git에 커밋하지 마세요! (이미 `.gitignore`에 포함되어 있음)

### 4. 설정 파일 (settings.json)

크롤러 동작 방식을 `settings.json`에서 조정할 수 있습니다:

```json
{
  "search_engine": "google",
  "headless_mode": false,
  "delay_between_searches": 5,
  "max_links_per_search": 10,
  "output_file": "results.json",
  "remove_tracking_params": true,
  "use_gemini_classifier": true
}
```

## 사용 방법

### 크롤러 실행
```bash
python main.py
```

### Gemini 분류기 테스트
```bash
python test_gemini.py
```

### 데이터베이스에 데이터 저장
```bash
# 데이터베이스 연결 테스트 및 데이터 임포트
python test_database.py

# 또는 직접 임포트
python -c "from src.database import import_from_json; import_from_json('results.json')"
```

## 프로젝트 구조

```
illicit-gambling-detector/
├── src/
│   ├── crawler.py              # 메인 크롤러 orchestrator
│   ├── keyword_manager.py      # 키워드 로드 및 조합 생성
│   ├── search_engine.py        # 검색 엔진 (Selenium/requests)
│   ├── url_extractor.py        # URL 추출 및 정제
│   ├── gemini_classifier.py    # Gemini AI 기반 사이트 판별
│   ├── json_storage.py         # JSON 파일 저장
│   └── database.py             # Supabase PostgreSQL 연동
├── keywords.json               # 검색 키워드 목록
├── settings.json               # 크롤러 설정
├── results.json                # 수집된 URL 결과 (자동 생성)
├── .env                        # 환경 변수 (직접 생성 필요)
├── env_template.txt            # 환경 변수 템플릿
├── main.py                     # 크롤러 실행 진입점
├── test_gemini.py              # Gemini 분류기 테스트
└── test_database.py            # 데이터베이스 테스트
```

## 데이터베이스 스키마

`gambling_urls` 테이블 구조:

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | SERIAL | 기본 키 |
| url | TEXT | URL (UNIQUE) |
| keyword_used | TEXT | 검색에 사용된 키워드 |
| collected_at | TIMESTAMP | 수집 시각 |
| is_illegal | BOOLEAN | 불법 도박 사이트 여부 |
| gemini_confidence | NUMERIC(3,2) | Gemini 신뢰도 (0.00~1.00) |
| gemini_reason | TEXT | Gemini 판단 이유 |
| gemini_error | TEXT | Gemini 에러 메시지 |
| detected_keywords | JSONB | 탐지된 키워드 배열 |
| created_at | TIMESTAMP | 생성 시각 |
| updated_at | TIMESTAMP | 수정 시각 (자동 업데이트) |

## API 키 발급 방법

### Google Gemini API Key
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Create API Key" 클릭
3. 발급받은 키를 `.env` 파일의 `GEMINI_API_KEY`에 입력

### Supabase 데이터베이스
1. [Supabase](https://supabase.com/) 가입
2. 새 프로젝트 생성
3. Settings > Database에서 연결 정보 확인
4. `.env` 파일에 연결 정보 입력

## 라이선스

MIT License