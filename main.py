# main.py

import sys
from crawlers.naver_crawler import NaverCrawler
from utils.naver_class_finder import find_naver_class 

def run_crawler():
    # 1. 크롤러 객체 생성
    crawler = NaverCrawler()

    # 2. 사용자 입력
    keyword = input("\n1. 검색할 키워드를 입력하세요 (예: 삼성전자): ") or "파이썬"
    try:
        page_input = input("2. 크롤링할 페이지 수를 입력하세요 (기본 1): ")
        pages = int(page_input) if page_input.isdigit() else 1
    except ValueError:
        pages = 1

    print(f"\n🚀 '{keyword}' 키워드로 {pages}페이지 크롤링을 시작합니다...\n")

    # 3. 실행
    articles = crawler.search(keyword, pages=pages)

    # 4. 결과 출력
    if articles:
        print(f"\n✅ 크롤링 성공! 총 {len(articles)}개의 기사를 찾았습니다.\n")
        print("-" * 60)
        for i, article in enumerate(articles):
            print(f"{i+1:02d}. [{article.source}] {article.title}")
            print(f"    🔗 링크: {article.url}")

            #[부제목 테스트 코드]
            content = crawler.get_content(article.url)

            if content:
                print(f"    📝 부제목: {content[:60]}...") # 너무 기니까 30자만 출력
            else:
                print("    📝 부제목: (없음)")
            
            print() # 줄바꿈
        print("-" * 60)
    else:
        print("\n❌ 검색 결과가 없습니다. '진단 모드'를 실행하여 클래스명을 확인해보세요!")

def run_diagnosis():
    print("\n [관리자 모드] 네이버 뉴스 클래스 이름 변경 탐지")
    keyword = input("검색 테스트에 사용할 키워드 (기본: 삼성전자): ") or "삼성전자"
    find_naver_class(keyword)

if __name__ == "__main__":
    while True:
        print("\n=========================================")
        print("   TiDIED Project: 뉴스 수집기")
        print("=========================================")
        print("1. 네이버 뉴스 크롤링 시작")
        print("9. [관리자] 네이버 클래스명 진단 도구 실행")
        print("0. 종료")
        print("=========================================")
        
        choice = input("메뉴를 선택하세요: ")
        
        if choice == "1":
            run_crawler()
        elif choice == "9":
            run_diagnosis()
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다.")