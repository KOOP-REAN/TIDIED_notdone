# models/article.py
from typing import Optional

class Article:
    """
    하나의 뉴스 기사를 나타내는 클래스.
    [WEEK05 클래스/객체]
    [WEEK08 캡슐화]
    에서 배운 개념 적용됨.
    """

    def __init__(self, title: str, url: str, source: str):
        self._title = title         #private 변수
        self._url = url
        self._source = source             #"네버이" 또는 "구글"
        self._content: Optional[str] = None

    # -------------- 캡슐화(Getter) --------------
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def url(self) -> str:
        return self._url
    
    @property
    def source(self) -> str:
        return self._source
    
    @property
    def content(self) -> Optional[str]:
        return self._content
    
    
    # -------------- 캡슐화(Setter) --------------
    @content.setter
    def content(self, text: str | None) -> None: 
        # Python 3.10+ 유니온 타입 사용해야 함,, 이거 때문에 고생 많이 함
        # Optional[str] 대신 str | None과 .strip() 사용
        if text:
            self._content = text.strip() 
        else:
            self._content = None

    
    # -------------- 가독성 높이기 --------------
    def __str__(self) -> str:
        return f"[{self._source}] {self._title}"
    
    def __repr__(self) -> str:
        return f"Article(title='{self._title}', url='{self._url}')"
    
