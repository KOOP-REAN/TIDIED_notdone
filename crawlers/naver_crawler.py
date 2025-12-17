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
    NEWS_TITLE_CLASS = "_228e3bd1"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Connection": "keep-alive"
    }

    def search(self, keyword: str, pages: int = 2) -> list[Article]:
        print(f"\n[NaverCrawler] '{keyword}' 검색 시작 (중복 제거 및 필터링 적용)...")
        
        articles: list[Article] = []
        visited_urls = set()  # [필터링 1] 이미 수집한 URL을 기억하는 집합(Set)
        
        for page in range(pages):
            start_num = (page * 10) + 1
            
            params = {
                "where": "news",
                "query": keyword,
                "sm": "tab_pge",
                "sort": "0",
                "start": start_num
            }
            
            try:
                response = requests.get(
                    "https://search.naver.com/search.naver",
                    params=params,
                    headers=self.HEADERS,
                    timeout=10
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
                    if not href or not title:
                        continue
                        
                    # 2. [중복 제거] 이미 수집한 URL이면 패스
                    if href in visited_urls:
                        continue

                    # 3. [쓰레기 제거] '언론사 홈' 링크(press) 제외
                    if "media.naver.com/press" in href:
                        continue

                    # 4. [제목 길이 필터] 제목이 너무 짧으면(네이버뉴스, 로고 등) 패스
                    if len(title) < 5:
                        continue
                        
                    # 5. [네이버 뉴스 우선] 
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
    
    def get_content(self, url: str) -> str:
        return "본문 수집 기능은 현재 비활성화 상태입니다."