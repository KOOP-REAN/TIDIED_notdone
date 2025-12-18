# models/article.py

from typing import Optional

class Article:
    """
    [WEEK05 클래스와 객체] 
    뉴스 기사 데이터를 구조화하여 관리하기 위한 클래스입니다!
    기사 제목, 링크, 언론사, 본문 요약 내용을 하나의 객체로 묶어서 다룹니다.
    """

    def __init__(self, title: str, url: str, source: str):
        # [WEEK08 캡슐화 & 정보 은닉]
        # 변수명 앞에 언더바(_)를 붙여 외부에서 함부로 수정하지 못하도록 보호합니다.
        self._title = title         
        self._url = url
        self._source = source             
        self._content: Optional[str] = None # 초기값은 비어있음 (None)

    # -------------- [WEEK08] 캡슐화: Getter 메서드 --------------
    # 외부에서 값을 읽을 수는 있지만(Read-Only), 직접 수정할 수는 없게 만듭니다.
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
    
    
    # -------------- [WEEK08] 캡슐화: Setter 메서드 --------------
    # 값을 수정할 때 유효성 검사를 거치도록 코드를 추가했습니다.
    @content.setter
    def content(self, text: str | None) -> None: 
        # Python 3.10+ 유니온 타입 사용해야 함,, 이거 때문에 고생 많이 함
        # Optional[str] 대신 str | None과 .strip() 사용
        if text:
            self._content = text.strip() 
        else:
            self._content = None


  
    def to_dict(self) -> dict:
        """
        객체 데이터를 JSON 파일로 저장하기 위해 딕셔너리 형태로 변환합니다.
        사용자가 보기 편하도록 한글 키(Key)를 사용했습니다.
        """
        return {
            "기사 제목": self._title,
            "부제목": self._content if self._content else "", # 내용이 없으면 빈 문자열
            "출처(링크)": self._url,
            "사이트": self._source
        }


    # -------------- [WEEK05] 가독성 높이기 --------------
    # 객체를 print()로 출력했을 때 보기 좋은 문자열이 나오도록 오버라이딩했습니다.
    def __str__(self) -> str:
        return f"[{self._source}] {self._title}"
    
    def __repr__(self) -> str:
        return f"Article(title='{self._title}', url='{self._url}')"
    