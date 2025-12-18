# crawlers/base_crawler.py

from abc import ABC, abstractmethod
from models.article import Article      # [WEEK03 모듈과 패키지] 상대 경로 import

class NewsCrawler(ABC):
    """
    [WEEK05 상속과 추상화]
    네이버 뉴스 크롤러가 반드시 지켜야 할 
    공통 규칙(설계도)을 정의한 추상 클래스입니다.
    (abc 모듈의 ABC를 상속받아 구현)
    """
    def __init__(self):
        # 크롤링 시 봇(Bot)으로 차단당하지 않기 위해 브라우저 헤더 정보를 공통으로 설정합니다.
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
    @abstractmethod
    
    def search(self, keyword: str, pages: int = 2) -> list[Article]:
        """
        [추상 메서드] 자식 클래스에서 반드시 구현해야 하는 검색 기능입니다.
        키워드를 받아 Article 객체의 리스트를 반환해야 합니다.
        """
        pass

    @abstractmethod
    def get_content(self, url: str) -> str:
        """
        [추상 메서드] 자식 클래스에서 반드시 구현해야 하는 본문 수집 기능입니다.
        URL을 받아 기사 내용을 문자열로 반환해야 합니다.
        """
        pass