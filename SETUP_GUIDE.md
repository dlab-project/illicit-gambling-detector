# Gemini 기반 불법 도박 사이트 탐지 시스템 - 설정 가이드

## 개요
이 시스템은 Google Gemini API를 사용하여 검색된 URL의 HTML 콘텐츠를 분석하고, 불법 온라인 도박 사이트를 자동으로 판별합니다.

## 설정 단계

### 1. Gemini API 키 설정

#### Option A: settings.json에 직접 설정 (간단함)
```json
{
  "search_engine": "google",
  "headless_mode": true,
  "delay_between_searches": 5,
  "output_file": "results.json",
  "remove_tracking_params": true,
  "use_gemini_classifier": true,
  "gemini_api_key": "YOUR_ACTUAL_GEMINI_API_KEY"
}
```

#### Option B: 환경변수 설정 (안전함)
```bash
export GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
```

### 2. Gemini API 키 얻기
1. [Google AI Studio](https://aistudio.google.com) 방문
2. "Get API Key" 클릭
3. 새 프로젝트 생성 또는 기존 프로젝트 선택
4. API 키 생성 및 복사

## 시스템 아키텍처

### 데이터 흐름
```
Google 검색 → URL 추출 → HTML 다운로드 → Gemini 판별 → 불법 사이트만 저장
```

### 주요 컴포넌트

#### 1. GeminiClassifier (`src/gemini_classifier.py`)
- **역할**: Gemini API를 호출하여 불법 도박 사이트 판별
- **입력**: URL과 HTML 콘텐츠
- **출력**: 
  ```json
  {
    "url": "http://example.com",
    "is_illegal": true,
    "confidence": 0.95,
    "reason": "판단 이유",
    "detected_keywords": ["casino", "betting"],
    "error": null
  }
  ```

#### 2. 업데이트된 JSONStorage (`src/json_storage.py`)
- 분류 결과를 JSON에 저장
- 각 항목에 다음 필드 포함:
  - `is_illegal`: 불법 도박 사이트 여부
  - `gemini_confidence`: 신뢰도 (0.0-1.0)
  - `gemini_reason`: 판단 이유
  - `detected_keywords`: 탐지된 키워드
  - `gemini_error`: 분류 오류 (있으면)

#### 3. 통합된 Crawler (`src/crawler.py`)
- 새로운 기능:
  1. URL 접속 및 HTML 다운로드
  2. Gemini로 불법 사이트 판별
  3. 판별된 사이트만 JSON에 저장
  4. 판별 실패 시 자동으로 건너뛰기

## 사용 방법

### 기본 실행
```bash
# 가상환경 활성화
source .venv/bin/activate

# 크롤러 실행
python main.py
```

### 출력 예시

#### 콘솔 출력
```
Starting gambling domain crawler...
Generated 5 keywords to search
[1/5] Searching for: online casino betting
Found 3 new URLs
  Fetching content from: http://example1.com
  Classifying: http://example1.com
  ✓ Illegal site detected: http://example1.com (confidence: 0.92)
  Fetching content from: http://example2.com
  Classifying: http://example2.com
  ✗ Not an illegal gambling site: http://example2.com
Saved 1 illegal gambling URLs for keyword: online casino betting
```

#### results.json 출력
```json
[
  {
    "url": "http://example1.com",
    "keyword_used": "online casino betting",
    "collected_at": "2024-11-15T16:45:30.123456",
    "is_illegal": true,
    "gemini_confidence": 0.92,
    "gemini_reason": "웹사이트에 베팅, 카지노, 실시간 결제 관련 내용이 포함되어 있으며, 신용카드와 가상화폐를 결제 수단으로 제시하고 있습니다.",
    "detected_keywords": ["casino", "betting", "real money", "deposit"]
  }
]
```

## Gemini 판별 프롬프트

시스템은 다음 기준으로 불법 도박 사이트를 판별합니다:

1. **베팅/도박 관련 키워드**
   - 영문: betting, casino, poker, slots, sports betting, etc.
   - 한글: 도박, 베팅, 카지노, 슬롯머신, 스포츠베팅 등

2. **결제 수단 제공**
   - 신용카드, 가상화폐, 송금, deposit, withdraw 등

3. **회원가입/로그인 시스템**
   - login, signup, register, 회원가입, 로그인 등

4. **불법성 암시 표현**
   - 은폐, 익명, 추적 불가, VPN, anonymous, hidden 등

5. **지역 규제 회피 표현**
   - 우회, bypass, offshore, 규제 회피 등

## 설정 옵션

### settings.json 상세 설정
```json
{
  "search_engine": "google",           // 검색 엔진 (현재 google만 지원)
  "headless_mode": true,               // Selenium 헤드리스 모드
  "delay_between_searches": 5,         // 검색 간 대기 시간 (초)
  "output_file": "results.json",       // 결과 저장 파일
  "remove_tracking_params": true,      // URL 추적 파라미터 제거
  "use_gemini_classifier": true,       // Gemini 분류기 사용 여부
  "gemini_api_key": "YOUR_API_KEY"     // Gemini API 키
}
```

## 오류 처리

### API 호출 실패
- 자동으로 해당 URL을 건너뜀
- `gemini_error` 필드에 오류 메시지 기록
- 크롤링은 계속 진행

### HTML 다운로드 실패
- URL 접속 실패 시 자동으로 건너뜀
- 다음 URL로 계속 진행

### API 키 오류
- 시작 시 오류 발생
- 환경변수 또는 settings.json 확인 필요

## 성능 고려사항

1. **API 호출 비용**
   - Gemini API는 무료 티어 제공
   - 대량 크롤링 시 비용 확인 필요

2. **API 레이트 제한**
   - 많은 URL 분류 시 딜레이 추가 고려
   - `delay_between_searches` 조정으로 제어 가능

3. **HTML 콘텐츠 크기**
   - 50KB 이상인 경우 자동으로 제한됨
   - Gemini API 입력 크기 제한 대응

## 문제 해결

### "Gemini API key not found" 오류
```bash
# 환경변수 설정 확인
echo $GEMINI_API_KEY

# 또는 settings.json의 gemini_api_key 필드 확인
cat settings.json
```

### 분류 실패가 많음
- 네트워크 확인
- API 키 유효성 확인
- Gemini API 상태 확인
- HTML 콘텐츠 인코딩 확인

### 저장된 URL이 없음
- 검색 키워드 확인 (keywords.json)
- 검색 엔진 작동 확인
- URL 추출 로직 확인
- Gemini 판별 기준 재검토
