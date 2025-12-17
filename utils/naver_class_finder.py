# utils/naver_class_finder.py
import requests
from bs4 import BeautifulSoup
from collections import Counter

def find_naver_class(keyword="삼성전자"):
    """
    네이버 뉴스 검색 결과에서 기사 제목으로 추정되는 클래스 이름을 찾아냅니다.
    """
    print(f"\n🕵️‍♂️ [진단 도구] 네이버 뉴스 클래스 이름 탐색 시작 (키워드: {keyword})...")

    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_pge&sort=0&start=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 모든 a 태그 수집
        links = soup.find_all("a")
        
        # 후보군 리스트
        class_candidates = []

        for link in links:
            text = link.get_text().strip()
            classes = link.get("class")
            
            # 1. 키워드가 텍스트에 포함되어 있고
            # 2. 텍스트 길이가 적당히 길며 (제목일 가능성)
            # 3. 클래스 속성을 가지고 있는 경우
            if keyword in text and len(text) > 10 and classes:
                # 클래스 리스트 중 첫 번째 것을 후보로 등록 (보통 첫 번째가 식별자)
                # 예: ['_228e3bd1', 'other_class'] -> '_228e3bd1'
                class_candidates.append(classes[0])

        if not class_candidates:
            print("❌ 클래스 후보를 찾지 못했습니다. 차단되었거나 구조가 완전히 바뀌었을 수 있습니다.")
            return None

        # 가장 많이 등장한 클래스 이름 찾기 (Counter 사용)
        most_common = Counter(class_candidates).most_common(1)
        best_class = most_common[0][0]
        count = most_common[0][1]

        print("-" * 50)
        print(f"✅ 분석 완료! 가장 유력한 클래스 이름: '{best_class}' (발견 횟수: {count}회)")
        print(f"👉 crawlers/naver_crawler.py 파일의 선택자를 'a.{best_class}' 로 변경하세요!")
        print("-" * 50)
        
        return best_class

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

# 직접 실행 시 테스트
if __name__ == "__main__":
    find_naver_class()