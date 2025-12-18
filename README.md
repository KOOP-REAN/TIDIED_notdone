# TiDIED - Tidied Information

>   사용자가 입력한 키워드로 네이버 뉴스를 크롤링 
    → 뉴스 기사 제목/부제목/링크 보여주기
    → 북마크 저장하는 OOP 프로젝트  

>   중앙대학교 2025 객체지향프로그래밍 PROJECT (박재혁)

## 프로젝트 목표
- 네이버 뉴스에서 키워드 검색
- 북마크(저장) 기능(JSON 파일 관리)
- OOP 개념 최대한 활용 [상속·다형성·캡슐화·추상화·SOLID·디자인패턴·예외처리·요구사항분석]

## 폴더 구조
TiDIED/
├─ crawlers/
│   ├─ __init__.py              
│   ├─ base_crawler.py          ← 추상 클래스
│   ├─ naver_crawler.py          
├─ models/
│   ├─ __init__.py
│   └─ article.py               ← (DTO, 캡슐화 적용)
├─ services/
│   ├─ __init__.py
│   └─ bookmark_manager.py          
├─ core/
│   ├─ __init__.py
│   └─ TIDIED.py                ← 메인 클래스
├─ gui/
│   └─ (나중에 만들어야 함)
├─ data/
│   └─ bookmarks.json           ← 자동 생성될 예정
├─ utils/
│   └─ __init__.py
│   └─ naver_class_finder.py    ← 유지보수(만들었음)
├─ main.py                      ← 실행용
├─ main.py                      ← 웹페이지 실행
├─ .gitignore                   ← GitHub 업로드 이상 방지.
└─ README.md                    ← GitHub 업로드 시 활용.
                 
