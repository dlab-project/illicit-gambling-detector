#!/usr/bin/env python
"""Gemini Classifier 테스트 스크립트"""

from src.gemini_classifier import GeminiClassifier

def test_gemini_classifier():
    """Gemini 분류기 테스트"""
    
    # 테스트용 HTML 콘텐츠 (불법 도박 사이트 예시)
    test_cases = [
        {
            "url": "http://example-casino.com",
            "html": """
            <html>
            <head><title>Best Online Casino - Play Now</title></head>
            <body>
            <h1>Welcome to Online Casino</h1>
            <p>Play blackjack, poker, slots for real money</p>
            <p>Win big with our exclusive casino games</p>
            <p>Deposit via credit card or Bitcoin</p>
            <button>Join Now and Get Bonus</button>
            <p>Sports betting available too</p>
            </body>
            </html>
            """
        },
        {
            "url": "http://legitimate-sports.com",
            "html": """
            <html>
            <head><title>Sports News Today</title></head>
            <body>
            <h1>Latest Sports News</h1>
            <p>Check out today's game scores and highlights</p>
            <p>Subscribe to our newsletter for updates</p>
            <button>Subscribe</button>
            </body>
            </html>
            """
        }
    ]
    
    try:
        print("=" * 60)
        print("Gemini Classifier 테스트")
        print("=" * 60)
        
        classifier = GeminiClassifier()
        print("✓ Gemini Classifier 초기화 성공\n")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"테스트 케이스 {i}: {test_case['url']}")
            print("-" * 60)
            
            result = classifier.classify_url(test_case['url'], test_case['html'])
            
            print(f"URL: {result['url']}")
            print(f"불법 도박 사이트: {result['is_illegal']}")
            print(f"신뢰도: {result['confidence']:.2f}")
            print(f"판단 이유: {result['reason']}")
            if result.get('detected_keywords'):
                print(f"탐지 키워드: {', '.join(result['detected_keywords'])}")
            if result.get('error'):
                print(f"오류: {result['error']}")
            
            print()
        
        print("=" * 60)
        print("✓ 테스트 완료")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gemini_classifier()
