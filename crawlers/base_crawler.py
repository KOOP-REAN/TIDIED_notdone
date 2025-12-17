# crawlers/base_crawler.py
from abc import ABC, abstractmethod
from models.article import Article      # 상대경로 import (WEEK03 모듈)

class NewsCrawler(ABC):
    """
    모든 뉴스 크롤러가 상속받을 추상 클래스(부모 클래스)
    [WEEK05 상속&추상화 내용 +  abc 모듈] 활용
    """

    @abstractmethod
    # 키워드로 뉴스 검색 → Article 객체 리스트 반환
    def search(self, keyword: str, pages: int = 2) -> list[Article]:
        pass

    @abstractmethod
    # 기사 URL로 본문 텍스트 가져오기
    def get_content(self, url: str) -> str:
        pass