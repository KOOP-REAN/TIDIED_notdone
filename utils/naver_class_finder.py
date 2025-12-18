# utils/naver_class_finder.py
"""
전부다 Gemini에게 도움을 받았습니다! 😅
"""
import requests
from bs4 import BeautifulSoup
from collections import Counter

def find_naver_class(keyword="삼성전자"):

    """
    [문제 해결을 위한 커스텀 도구]
    개발 도중 네이버 뉴스 페이지의 구조(클래스명)가 바뀌어 
    크롤러가 동작하지 않는 치명적인 문제가 발생했습니다.
    
    매번 개발자 도구(F12)를 켜서 수동으로 찾는 번거로움을 없애기 위해,
    알고리즘을 통해 '기사 제목 클래스'를 자동으로 탐지해주는 진단 도구를 개발했습니다.
    """
    
    print(f"\n🕵️‍♂️ [진단 도구] 네이버 뉴스 클래스 이름 탐색 시작 (키워드: {keyword})...")

    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_pge&sort=0&start=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # [WEEK03 라이브러리 활용] requests로 HTML 요청
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        links = soup.find_all("a")
        class_candidates = []

        for link in links:
            text = link.get_text().strip()
            classes = link.get("class")
            
            # [탐지 알고리즘] 제목일 가능성이 높은 태그의 특징을 정의
            # 1. 검색 키워드가 포함되어 있어야 함
            # 2. 제목이라기엔 너무 짧은 텍스트는 제외
            # 3. 반드시 class 속성을 가지고 있어야 함
            if keyword in text and len(text) > 10 and classes:
                class_candidates.append(classes[0])

        if not class_candidates:
            print("❌ 클래스 후보를 찾지 못했습니다. 차단되었거나 구조가 완전히 바뀌었을 수 있습니다.")
            return None

        # [데이터 분석] 수집된 후보 중 '가장 많이 등장한' 클래스가 정답일 확률이 높음 (Counter 활용)
        most_common = Counter(class_candidates).most_common(1)
        best_class = most_common[0][0]
        count = most_common[0][1]

        print("-" * 50)
        print(f"✅ 분석 완료! 가장 유력한 클래스 이름: '{best_class}' (발견 횟수: {count}회)")
        print(f"👉 crawlers/naver_crawler.py 파일의 NEWS_TITLE_CLASS 상수를 이 값으로 변경하세요!")
        print("-" * 50)
        
        return best_class

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    find_naver_class()