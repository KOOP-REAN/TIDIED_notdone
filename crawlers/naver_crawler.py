# crawlers/naver_crawler.py

import requests
from bs4 import BeautifulSoup
import time 
import os

# [WEEK03 모듈] 직접 만든 모듈 불러오기
from crawlers.base_crawler import NewsCrawler 
from models.article import Article

class NaverCrawler(NewsCrawler):
    """
    [WEEK05 상속] NewsCrawler 부모 클래스를 상속받아 구현한 '네이버 뉴스 전용' 크롤러입니다.
    """
    # -------------------------------------------------------------------------
    # [시행착오]
    # 네이버 뉴스의 기사 제목 클래스명은 주기적으로 변경(난독화)됩니다.
    # 처음엔 고정된 이름인 줄 알았으나, 크롤링이 갑자기 안 되는 문제를 겪고 나서
    # 이를 상수로 빼서 관리하도록 구조를 변경했습니다.
    # 변경 시 utils/naver_class_finder.py 도구로 찾아내어 여기에 업데이트해야 합니다.
    # -------------------------------------------------------------------------
    NEWS_TITLE_CLASS = "fender-ui_228e3bd1"

    def __init__(self):
        super().__init__()

    # [WEEK05 오버라이딩] 부모의 메서드를 재정의
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
            
            # [예외 처리] 네트워크 통신은 언제든 실패할 수 있으므로 try-except 필수!!!
            try:
                response = requests.get(
                    "https://search.naver.com/search.naver",
                    params=params, headers=self.headers, timeout=10
                )
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 1순위: 우리가 찾아낸 동적 클래스 / 2순위: 혹시 몰라 남겨둔 표준 클래스
                title_tags = soup.select(f"a.{self.NEWS_TITLE_CLASS}")
                if not title_tags:
                    title_tags = soup.select("a.news_tit")
                
                if not title_tags:
                    print(f"  -> {page + 1}페이지: 검색 결과 없음")
                    break

                for title_tag in title_tags:
                    title = ""
                    target_link = ""
                
                    extracted_title = title_tag.get('title')
                    if extracted_title:
                        title = str(extracted_title)
                    else:
                        title = title_tag.get_text(strip=True)
                    target_link = str(title_tag['href'])
                    
                    # [하이브리드 전략] 링크를 정확히 찾기 위해 부모 태그까지 거슬러 올라가 탐색
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
                    

                    # ---------------- [데이터 필터링] ----------------
                    ## 1. http로 시작 안 하면 버림
                    if not target_link.startswith("http"):
                        continue
                    
                    ## 2. [추가된 필터] 언론사 구독 페이지(press)는 기사가 아니므로 제외!
                    if "https://media.naver.com/press/" in target_link:
                        continue

                    ## 3. 이미 수집한 링크면 버림
                    if target_link in visited_urls:
                        continue
                        
                    ## 4. 제목이 "네이버뉴스"면 버림
                    if title == "네이버뉴스":
                        continue

                    ## 최종 저장
                    article = Article(title=title, url=target_link, source="Naver")
                    articles.append(article)
                    visited_urls.add(target_link)

                print(f"  -> {page + 1}페이지 완료: {len(title_tags)}개 감지 -> {len(articles)}개 유효 수집")
                time.sleep(1)

            except Exception as e:
                print(f"  -> [오류] {e}")

        return articles
    


    def get_content(self, url: str) -> str | None:
        """
        [가장 많은 고난을 겪었던 메서드 ㅠㅠ]
        단순히 태그 하나만 찾으면 될 줄 알았으나, 기사마다/환경마다(PC vs 모바일) 
        HTML 구조가 달라서 부제목을 못 가져오는 경우가 많았습니다.
        이를 해결하기 위해 Plan A -> B 로 이어지는 2단계 전략을 수립했습니다!!
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status() 

            soup = BeautifulSoup(response.text, "html.parser")

            # -----------------------------------------------------------------
            # [Plan A] 알려진 클래스 이름으로 찾기
            # 시행착오: 처음엔 'media_end_head_headline'도 포함했으나, 
            # 이것이 '기사 제목'을 가리키는 바람에 부제목 자리에 제목이 중복 저장되는 
            # 버그가 발생하여 삭제했습니다.
            # -----------------------------------------------------------------
            candidates = ["media_end_summary", "sub_title", "sh_sub_head"]

            for class_name in candidates:
                element = soup.find(class_=class_name)
                if element and element.get_text(strip=True):
                    return element.get_text(strip=True)

            # -----------------------------------------------------------------
            # [Plan B] 클래스가 없을 때: 본문 내의 굵은 글씨 찾기
            # 시행착오 1: 모바일과 PC 버전의 본문 ID가 다름 (#dic_area vs #articleBodyContents)
            # 시행착오 2: find(["<strong", "<b>"]) 처럼 꺽쇠를 넣는 문법 실수로 인해
            # 한동안 태그를 못 찾아서 고생함. -> find(["strong", "b"]) 로 수정하여 해결.
            # -----------------------------------------------------------------
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