#crawlers/naver_crawler.py

import requests
from bs4 import BeautifulSoup
import time 
import os

from crawlers.base_crawler import NewsCrawler
from models.article import Article

class NaverCrawler(NewsCrawler):
    """
    네이버 뉴스 검색 결과 페이지에서 '제목'과 '링크'만 수집하는 클래스입니다.
    """

    # [유지보수 포인트] 클래스 이름이 바뀌면 여기만 수정하세요!
    NEWS_TITLE_CLASS = "fender-ui_228e3bd1"


    def __init__(self):
        super().__init__()

    def search(self, keyword: str, pages: int = 2) -> list[Article]:
        print(f"\n[NaverCrawler] '{keyword}' 검색 시작 (중복 제거 및 필터링 적용)...")
        
        articles: list[Article] = []
        visited_urls = set()  # [필터링 1] 이미 수집한 URL을 기억하는 집합(Set)
        
        for page in range(pages):
            start_num = (page * 10) + 1
            params = {
                "where": "news", "query": keyword, "sm": "tab_pge", 
                "sort": "0", "start": start_num
            }
            
            try:
                response = requests.get(
                    "https://search.naver.com/search.naver",
                    params=params, headers=self.headers, timeout=10
                )
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # CSS 선택자도 변수를 사용하도록 수정
                # f-string을 사용하여 변수를 선택자에 넣습니다.
                selector = f"a.{self.NEWS_TITLE_CLASS}" 
                news_links = soup.select(selector)
                
                if not news_links:
                    print(f"  -> {page + 1}페이지: 검색 결과 요소를 찾지 못했습니다.")
                    break

                for link in news_links:
                    title = str(link.get('title', '')).strip()
                    href = str(link.get('href', ''))
                    
                    if not title:
                        title = link.get_text().strip()

                    # ---------------- [강력해진 필터링 로직] ----------------
                    
                    # 1. URL이나 제목이 없으면 패스
                    if not href.startswith("http"):
                        continue
                        # [관련뉴스 10건 전체보기] 에러 나는 거 수정
                    
                    # 2. 제목이나 링크가 비어있으면 패스
                    if not href or not title:
                        continue
                    
                    # 3. [중복 제거] 이미 수집한 URL이면 패스
                    if href in visited_urls:
                        continue
            
                    # 4. [쓰레기 제거] '언론사 홈' 링크(press) 제외
                    if "media.naver.com/press" in href:
                        continue

                    # 5. [제목 길이 필터] 제목이 너무 짧으면(네이버뉴스, 로고 등) 패스
                    if len(title) < 5:
                        continue
                        
                    # 6. [네이버 뉴스 우선] 
                    # 같은 기사라면 n.news.naver.com 링크를 선호하지만,
                    # 지금은 일단 수집된 모든 유효한 링크를 저장합니다.
                    # -------------------------------------------------------

                    # 필터를 통과한 기사만 저장
                    article = Article(title=title, url=href, source="Naver")
                    articles.append(article)
                    visited_urls.add(href)  # 수집 목록에 추가
                
                print(f"  -> {page + 1}페이지 완료: {len(news_links)}개 감지 -> {len(articles)}개 유효 수집")
                time.sleep(1)

            except Exception as e:
                print(f"  -> [오류] 페이지 처리 중 문제 발생: {e}")

        print(f"[완료] 총 {len(articles)}개의 깔끔한 기사 목록을 확보했습니다.")
        return articles
    

    def get_content(self, url: str) -> str | None:
        """
        URL에서 기사의 부제목(요약문)을 추출합니다.
        여러 HTML 클래스명을 순차적으로 탐색하여 가장 적합한 텍스트를 찾습니다.
        """
        try:
            # 1. HTTP 요청 (File 4th: requests 라이브러리 사용)
            response = requests.get(url, headers=self.headers)
            response.raise_for_status() # 404, 500 에러 시 예외 발생 (File 7th)

            # 2. 파싱 준비 (BeautifulSoup)
            soup = BeautifulSoup(response.text, "html.parser")

            # 3. 부제목(또는 요약)을 담고 있을 확률이 높은 클래스명 후보군 리스트
            # 'media_end_summary': 최신 네이버 뉴스 상단 요약
            # 'sub_title': 일반적인 부제목
            # 'sh_sub_head': 구형 레이아웃의 부제목
            candidates = ["media_end_summary", "sub_title", "sh_sub_head", "media_end_head_headline"]

            for class_name in candidates:
                element = soup.find(class_=class_name)
                
                # 요소를 찾았고, 텍스트가 비어있지 않다면 반환
                if element and element.get_text(strip=True):
                    # 텍스트 양옆 공백 제거 (File 1st: 문자열 함수)
                    return element.get_text(strip=True)

            # 4. 모든 후보군을 뒤져도 없으면 None 반환
            return None

        except requests.exceptions.RequestException as e:
            # 네트워크 관련 에러 처리 (File 7th)
            print(f"[Error] 요청 실패: {e}")
            return None
        except Exception as e:
            # 그 외 파싱 중 발생한 예상치 못한 에러 처리
            print(f"[Error] 파싱 중 오류 발생: {e}")
            return None