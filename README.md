# TiDIED - Tidied Information

>   사용자가 입력한 키워드로 네이버 + 구글 뉴스를 크롤링 
    → 자동 요약 
    → 북마크 저장하는 OOP 프로젝트  

>   중앙대학교 2025 객체지향프로그래밍 PROJECT (박재혁)

## 프로젝트 목표
- 네이버 뉴스 + 구글 뉴스에서 키워드 검색
- 기사 제목/본문 자동 요약
- 북마크(저장) 기능
- OOP 개념 최대한 활용 (상속·다형성·캡슐화·추상화·SOLID·디자인패턴·예외처리·요구사항분석)/바보똥개

## 폴더 구조
TiDIED/
├─ 01.crawlers/
│   ├─ __init__.py              ← 만든 이유 설명해주기
│   ├─ base_crawler.py          ← 추상 클래스
│   ├─ naver_crawler.py
│   └─ google_crawler.py         
├─ 02.models/
│   ├─ __init__.py
│   └─ article.py
├─ 03.services/
│   ├─ __init__.py
│   ├─ summarizer.py
│   └─ bookmark_manager.py
├─ 04.core/
│   ├─ __init__.py
│   └─ tidied.py                ← 메인 클래스
├─ 05.gui/
│   └─ (나중에 만들기)
├─ 06.data/
│   └─ bookmarks.json           ← 자동 생성될 예정
├─ main.py                      ← 실행용
└─ README.md                  
