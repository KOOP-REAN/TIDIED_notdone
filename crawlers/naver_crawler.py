# crawlers/naver_crawler.py

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
    # 재혁 님이 찾아낸 동적 클래스명
    NEWS_TITLE_CLASS = "fender-ui_228e3bd1"

    def __init__(self):
        super().__init__()

    def search(self, keyword: str, pages: int = 2) -> list[Article]:
        print(f"\n[NaverCrawler] '{keyword}' 검색 시작 (언론사 홈 필터링 추가됨)...")
        
        articles: list[Article] = []
        visited_urls = set()
        
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
                
                # 1순위: 동적 클래스 / 2순위: 표준 클래스(news_tit)
                title_tags = soup.select(f"a.{self.NEWS_TITLE_CLASS}")
                if not title_tags:
                    title_tags = soup.select("a.news_tit")
                
                if not title_tags:
                    print(f"  -> {page + 1}페이지: 검색 결과 없음")
                    break

                for title_tag in title_tags:
                    # [방어적 초기화]
                    title = ""
                    target_link = ""
                    
                    # 1. 제목 추출
                    extracted_title = title_tag.get('title')
                    if extracted_title:
                        title = str(extracted_title)
                    else:
                        title = title_tag.get_text(strip=True)

                    # 2. 링크 추출 (일단 원본 링크로 저장)
                    target_link = str(title_tag['href'])
                    
                    # 3. [하이브리드 전략] 주변에서 '네이버 뉴스' 링크 찾기
                    container = title_tag.find_parent("div")
                    if not container:
                        container = title_tag.find_parent("li")
                    
                    if container:
                        info_links = container.select("a") 
                        for link in info_links:
                            link_href = str(link.get('href', ''))
                            if "n.news.naver.com" in link_href:
                                target_link = link_href 
                                break
                    
                    # -----------------------------------------------------
                    # [강력해진 필터링 로직]
                    # -----------------------------------------------------

                    # 1. http로 시작 안 하면 버림
                    if not target_link.startswith("http"):
                        continue
                    
                    # 2. [추가된 필터] 언론사 구독 페이지(press)는 기사가 아니므로 제외!
                    if "https://media.naver.com/press/" in target_link:
                        continue

                    # 3. 이미 수집한 링크면 버림
                    if target_link in visited_urls:
                        continue
                        
                    # 4. 제목이 "네이버뉴스"면 버림
                    if title == "네이버뉴스":
                        continue

                    # 최종 저장
                    article = Article(title=title, url=target_link, source="Naver")
                    articles.append(article)
                    visited_urls.add(target_link)

                print(f"  -> {page + 1}페이지 완료: {len(title_tags)}개 감지 -> {len(articles)}개 유효 수집")
                time.sleep(1)

            except Exception as e:
                print(f"  -> [오류] {e}")

        return articles
    

    def get_content(self, url: str) -> str | None:
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status() 

            soup = BeautifulSoup(response.text, "html.parser")

            # ---------------------------------------------------------
            # [Plan A] 우리가 아는 '부제목 클래스' 이름으로 찾기
            # ---------------------------------------------------------
            # [수정됨] 범인(media_end_head_headline)을 삭제했습니다!
            candidates = ["media_end_summary", "sub_title", "sh_sub_head"]

            for class_name in candidates:
                element = soup.find(class_=class_name)
                if element and element.get_text(strip=True):
                    return element.get_text(strip=True)

            # ---------------------------------------------------------
            # [Plan B] 클래스가 없을 때: 본문(#dic_area) 안의 첫 번째 굵은 글씨(strong, b) 찾기
            # ---------------------------------------------------------
            article_body = soup.select_one("#dic_area")
            
            # 본문 영역을 못 찾으면 다른 ID(articleBodyContents)일 수도 있음 (PC 버전 대응)
            if not article_body:
                article_body = soup.select_one("#articleBodyContents")

            if article_body:
                # 1. 굵은 글씨 태그가 있는지 확인 (태그 이름만 넣기!)
                first_bold = article_body.find(["strong", "b"])
                
                if first_bold and first_bold.get_text(strip=True):
                    text = first_bold.get_text(strip=True)
                    # 너무 길지 않으면(200자 미만) 부제목으로 인정
                    if len(text) < 200:
                        return text

            return None

        except Exception as e:
            return None