# core/tidied.py

import sys
from crawlers.naver_crawler import NaverCrawler
from services.bookmark_manager import BookmarkManager
from utils.naver_class_finder import find_naver_class

class TIDIED:
    """
    TiDIED 애플리케이션의 중앙 제어 클래스 (Facade/Controller).
    UI(main.py)와 비즈니스 로직(Crawler, Manager) 사이를 중재합니다.
    """

    def __init__(self):
        # [Composition] 크롤러와 매니저를 부품으로 소유합니다.
        self.crawler = NaverCrawler()
        self.manager = BookmarkManager()

    def run(self):
        """
        프로그램의 메인 루프를 실행합니다.
        """
        while True:
            self._show_main_menu()
            choice = input("메뉴를 선택하세요: ").strip()

            if choice == "1":
                self._process_crawling()
            elif choice == "2":
                self._process_bookmark_management()
            elif choice == "9":
                self._run_diagnosis()
            elif choice == "0":
                print("프로그램을 종료합니다. 이용해 주셔서 감사합니다! 🙇")
                sys.exit(0)
            else:
                print("❌ 잘못된 입력입니다. 다시 선택해주세요.")

    def _show_main_menu(self):
        print("\n=========================================")
        print("   TiDIED Project: 정보 정돈 (Ver 1.0)")
        print("=========================================")
        print("1. 📰 네이버 뉴스 크롤링 시작")
        print("2. 💾 북마크 확인 및 관리 (폴더/삭제/이동)")
        print("9. 🛠️ [관리자] 네이버 클래스명 진단 도구")
        print("0. 🚪 종료")
        print("=========================================")

    # ------------------------------------------------------------------
    # 1. 크롤링 관련 로직 (기존 run_crawler 이식)
    # ------------------------------------------------------------------
    def _process_crawling(self):
        keyword = input("\n1. 검색할 키워드를 입력하세요 (예: 삼성전자): ") or "파이썬"
        try:
            page_input = input("2. 크롤링할 페이지 수를 입력하세요 (기본 1): ")
            pages = int(page_input) if page_input.isdigit() else 1
        except ValueError:
            pages = 1

        print(f"\n🚀 '{keyword}' 키워드로 {pages}페이지 크롤링을 시작합니다...\n")
        
        articles = self.crawler.search(keyword, pages=pages)

        if not articles:
            print("\n❌ 검색 결과가 없습니다.")
            return

        # -----------------------------------------------------
        # 1. 부제목(Content) 수집
        # -----------------------------------------------------
        print("📝 기사 내용을 요약하고 있습니다...", end="", flush=True)
        for article in articles:
            content = self.crawler.get_content(article.url)
            article.content = content if content else ""
            print(".", end="", flush=True) # 진행바 느낌
        print(" 완료!\n")

        # -----------------------------------------------------
        # 2. [추가됨] 요청하신 순서대로 정렬 (Sorting)
        # -----------------------------------------------------
        # lambda 함수를 이용해 정렬 우선순위를 정합니다.
        # 0순위: 네이버 뉴스 AND 부제목 있음
        # 1순위: 네이버 뉴스 AND 부제목 없음
        # 2순위: 그 외 (언론사 홈 등)
        articles.sort(key=lambda x: (
            0 if (x.url.startswith("https://n.news.naver.com") and x.content) else
            1 if (x.url.startswith("https://n.news.naver.com") and not x.content) else
            2
        ))

        # -----------------------------------------------------
        # 3. 결과 출력
        # -----------------------------------------------------
        print(f"✅ 총 {len(articles)}개의 기사를 정렬하여 출력합니다.")
        print("-" * 60)
        for i, article in enumerate(articles):
            print(f"{i+1:02d}. [{article.source}] {article.title}")
            print(f"    🔗 {article.url}")
            
            if article.content:
                print(f"    📝 부제목: {article.content[:60]}...")
            else:
                print("    📝 부제목: (없음)")
            print()
        print("-" * 60)

        # 저장 로직 연결
        self._handle_save_selection(articles)

    def _handle_save_selection(self, articles):
        print("\n[북마크 저장 메뉴]")
        print("저장하고 싶은 기사의 번호를 입력하세요 (쉼표로 구분, 예: 1,3,5)")
        print("※ 전체를 다 저장하려면 'all'이라고 입력하세요.")
        print("※ 저장하지 않으려면 엔터(Enter)를 누르세요.")
        
        selection = input(">>> 입력: ").strip()

        if not selection:
            return

        selected_articles = []
        if selection.lower() == 'all':
            selected_articles = articles
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(",")]
                for idx in indices:
                    real_idx = idx - 1 
                    if 0 <= real_idx < len(articles):
                        selected_articles.append(articles[real_idx])
                    else:
                        print(f"⚠️ {idx}번은 없는 번호입니다. 제외합니다.")
            except ValueError:
                print("❌ 잘못된 입력 형식입니다.")
                return

        if selected_articles:
            print(f"\n총 {len(selected_articles)}개의 기사가 선택되었습니다.")
            
            # [핵심] 비서 함수(_get_folder_choice)를 호출하여 폴더 결정
            target_folder = self._get_folder_choice()
            
            self.manager.save_bookmarks(selected_articles, folder_name=target_folder)
        else:
            print("선택된 기사가 없어 저장하지 않았습니다.")

    # ------------------------------------------------------------------
    # 2. 북마크 관리 관련 로직 (기존 run_bookmark_viewer 이식)
    # ------------------------------------------------------------------
    def _process_bookmark_management(self):
        while True:
            saved_data = self.manager.load_bookmarks()
            if not saved_data:
                print("\n📂 저장된 북마크가 없습니다.")
                return

            print("\n================ [내 폴더 목록] ================")
            folders = list(saved_data.keys())
            for i, folder in enumerate(folders):
                count = len(saved_data[folder])
                print(f"{i+1}. 📁 {folder} ({count}개)")
            print("0. 메인 메뉴로 돌아가기")
            print("================================================")

            try:
                choice = int(input(">>> 열어볼 폴더 번호를 입력하세요: "))
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
                continue

            if choice == 0:
                break
            
            if 1 <= choice <= len(folders):
                selected_folder = folders[choice - 1]
                self._show_folder_detail(selected_folder)
            else:
                print("❌ 잘못된 번호입니다.")

    def _show_folder_detail(self, folder_name):
        """
        특정 폴더의 기사 목록을 보여주고 삭제/이동 기능을 제공
        """
        while True:
            saved_data = self.manager.load_bookmarks()
            if folder_name not in saved_data:
                print("📂 폴더가 비어있거나 삭제되었습니다.")
                break
                
            articles = saved_data[folder_name]
            if not articles:
                print("📂 폴더가 비어있습니다.")
                break

            print(f"\n--- 📂 '{folder_name}' 폴더 내부 ---")
            for i, article in enumerate(articles):
                print(f"\n{i+1}. {article.title}")
                # [복구됨] 부제목 출력
                if article.content:
                     print(f"   └─ {article.content[:100]}...")
                # [복구됨] 링크 출력
                print(f"   └─ 출처(링크): {article.url}")

            print("\n[기능] 번호 선택: 기사 관리 / 0: 뒤로 가기")
            
            try:
                idx = int(input(">>> 선택: "))
            except ValueError:
                continue

            if idx == 0:
                break
            
            real_idx = idx - 1
            if 0 <= real_idx < len(articles):
                target_article = articles[real_idx]
                print(f"\n선택된 기사: [{target_article.title}]")
                print("1. 🗑️ 삭제하기")
                print("2. 🚚 다른 폴더로 이동하기")
                print("0. 취소")
                
                action = input(">>> 기능 선택: ")
                
                if action == "1":
                    check = input("정말 삭제하시겠습니까? (y/n): ")
                    if check.lower() == 'y':
                        self.manager.delete_article(folder_name, real_idx)
                
                elif action == "2":
                    print("\n[기사 이동]")
                    # [핵심] 이동 시에도 비서 함수 사용
                    target_folder = self._get_folder_choice()
                    
                    if target_folder == folder_name:
                        print("⚠️ 현재 폴더와 동일합니다. 이동하지 않습니다.")
                    else:
                        self.manager.move_article(folder_name, real_idx, target_folder)
            else:
                print("❌ 잘못된 번호입니다.")

    # ------------------------------------------------------------------
    # 3. 유틸리티 & 도우미 메서드 (기존 main.py의 _get_folder_choice 이식)
    # ------------------------------------------------------------------
    def _get_folder_choice(self):
        """
        사용자에게 [1. 기존 폴더 선택 / 2. 새 폴더 생성] 메뉴를 보여주고
        최종적으로 사용할 '폴더 이름(str)'을 반환하는 도우미 메서드
        """
        saved_data = self.manager.load_bookmarks()
        folders = list(saved_data.keys())

        if not folders:
            print("\n📂 기존 폴더가 없습니다. 새 폴더를 생성합니다.")
            new_folder = input(">>> 새 폴더 이름 입력 (기본: '스크랩'): ").strip()
            return new_folder if new_folder else "스크랩"

        print("\n[폴더 선택 메뉴]")
        print("1. 📂 기존 폴더에서 선택")
        print("2. ✨ 새 폴더 생성")
        
        choice = input(">>> 번호 선택: ").strip()

        if choice == "1":
            print("\n--- [현재 존재하는 폴더] ---")
            for i, f in enumerate(folders):
                print(f"{i+1}. {f}")
            
            try:
                idx = int(input(">>> 폴더 번호 입력: ")) - 1
                if 0 <= idx < len(folders):
                    return folders[idx]
                else:
                    print("⚠️ 잘못된 번호입니다. 기본값('스크랩')을 사용합니다.")
                    return "스크랩"
            except ValueError:
                print("⚠️ 숫자를 입력해주세요. 기본값('스크랩')을 사용합니다.")
                return "스크랩"

        elif choice == "2":
            new_folder = input(">>> 새 폴더 이름 입력: ").strip()
            return new_folder if new_folder else "스크랩"
        
        else:
            print("⚠️ 잘못된 입력입니다. 기본값('스크랩')을 사용합니다.")
            return "스크랩"

    def _run_diagnosis(self):
        print("\n [관리자 모드] 네이버 뉴스 클래스 이름 변경 탐지")
        keyword = input("검색 테스트에 사용할 키워드 (기본: 삼성전자): ") or "삼성전자"
        find_naver_class(keyword)