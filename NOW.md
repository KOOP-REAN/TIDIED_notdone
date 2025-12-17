클래스 다이어그램
    1. 데이터 모델 (models)
    class Article {
        
        -str _title
        -str _url
        -str _source
        -str|None _content
        -str|None _summary

# -------------- 캡슐화 --------------
        +title() str
        +url() str
        +source() str
# -------------- setter --------------
        +content(text)
        +summary(text)
# -------------- 가독성 높이기 --------------
        +__str__()
        +__repr__()
    }

    2. 크롤러 (crawlers) (추상화 & 상속)
    class NewsCrawler {
        <<Abstract>>
        +search(keyword: str, pages: int) list[Article]*
# 위 한 줄이 매우 핵심이란 걸, 오류가 일어난 뒤 알게 됨.
        +get_content(url: str) str*
    }

    class NaverCrawler {
        +HEADERS: dict
        +NEWS_TITLE_CLASS: str
        +search(keyword: str, pages: int) list[Article]
        +get_content(url: str) str
    }

    3. 유틸리티 (함수)
    class NaverClassFinder {
        <<Function>>
        +find_naver_class(keyword)
    }
    << 관계 정의 >>
    NaverCrawler --|> NewsCrawler : 상속 (Inheritance)
    NewsCrawler ..> Article : 생성 (Creates)
    NaverCrawler ..> Article : 생성 (Creates)