# main.py

import sys
from crawlers.naver_crawler import NaverCrawler
from utils.naver_class_finder import find_naver_class 
from services.bookmark_manager import BookmarkManager

# main.py 에 추가할 함수

def _get_folder_choice(manager):
    """
    사용자에게 [1. 기존 폴더 선택 / 2. 새 폴더 생성] 메뉴를 보여주고
    최종적으로 사용할 '폴더 이름(str)'을 반환하는 도우미 함수입니다.
    """
    # 1. 현재 존재하는 폴더 목록 가져오기
    saved_data = manager.load_bookmarks()
    folders = list(saved_data.keys())

    # 폴더가 하나도 없으면 선택할 게 없으므로 바로 생성으로 유도
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
            # f-string으로 보기 좋게 출력
            print(f"{i+1}. {f}")
        
        try:
            idx = int(input(">>> 폴더 번호 입력: ")) - 1
            if 0 <= idx < len(folders):
                return folders[idx] # 선택한 폴더 이름 반환
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

def run_crawler():
    # 1. 크롤러 객체 생성
    crawler = NaverCrawler()

    # 2. 사용자 입력
    keyword = input("\n1. 검색할 키워드를 입력하세요 (예: 삼성전자): ") or "파이썬"
    try:
        page_input = input("2. 크롤링할 페이지 수를 입력하세요 (기본 1): ")
        pages = int(page_input) if page_input.isdigit() else 1
    except ValueError:
        pages = 1

    print(f"\n🚀 '{keyword}' 키워드로 {pages}페이지 크롤링을 시작합니다...\n")

    # 3. 실행
    articles = crawler.search(keyword, pages=pages)

    if not articles:
        print("\n❌ 검색 결과가 없습니다.")
        return

    # 4. 결과 출력
    print(f"\n✅ 크롤링 성공! 총 {len(articles)}개의 기사를 찾았습니다.\n")
    print("-" * 60)
    for i, article in enumerate(articles):
        print(f"{i+1:02d}. [{article.source}] {article.title}")
        print(f"    🔗 {article.url}")
        
        # [중요 수정] 부제목을 가져와서 객체에 '저장'까지 해야 파일에 남습니다!
        content = crawler.get_content(article.url)
        if content:
            article.content = content  # <--- 여기에 데이터를 담습니다.
            print(f"    📝 부제목: {content[:60]}...") 
        else:
            article.content = ""       # 내용이 없으면 빈 문자열로 초기화
            print("    📝 부제목: (없음)")
        
        print() # 줄바꿈
    print("-" * 60)

    # 5. 저장 메뉴 (이전과 동일)
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
        
        # [수정] 매니저를 먼저 생성하고, 도우미 함수를 통해 폴더를 결정함
        manager = BookmarkManager()
        
        # 여기서 비서가 등판해서 물어봅니다!
        target_folder = _get_folder_choice(manager)
            
        manager.save_bookmarks(selected_articles, folder_name=target_folder)
    else:
        print("선택된 기사가 없어 저장하지 않았습니다.")

def run_diagnosis():
    print("\n [관리자 모드] 네이버 뉴스 클래스 이름 변경 탐지")
    keyword = input("검색 테스트에 사용할 키워드 (기본: 삼성전자): ")
    find_naver_class(keyword)

# main.py (함수 추가)

def run_bookmark_viewer():
    manager = BookmarkManager()
    
    while True:
        # 1. 데이터 최신화 (삭제/이동 후 반영을 위해 루프 안에서 로드)
        saved_data = manager.load_bookmarks() # dict[폴더명, list[Article]]

        if not saved_data:
            print("\n📂 저장된 북마크가 없습니다.")
            return

        # 2. 폴더 목록 출력
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
            _show_folder_contents(manager, selected_folder) # 내부 함수 호출
        else:
            print("❌ 잘못된 번호입니다.")

def _show_folder_contents(manager: BookmarkManager, folder_name: str):
    """
    [내부 함수] 특정 폴더의 기사 목록을 보여주고 삭제/이동 기능을 제공
    """
    while True:
        # 데이터 다시 로드 (삭제/이동 반영)
        saved_data = manager.load_bookmarks()
        if folder_name not in saved_data:
            print("📂 폴더가 비어있거나 삭제되었습니다.")
            break
            
        articles = saved_data[folder_name]
        if not articles:
            print("📂 폴더가 비어있습니다.")
            break

        print(f"\n--- 📂 '{folder_name}' 폴더 내부 ---")
        for i, article in enumerate(articles):
            print(f" \n {i+1}. {article.title}")
            
            # 1. 부제목 출력
            if article.content:
                 print(f"   └─ {article.content[:40]}...")
            
            # 2. [추가됨] 출처(링크) 출력
            print(f"   └─ 출처(링크): {article.url} \n")

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
                    manager.delete_article(folder_name, real_idx)
            
            elif action == "2":
                # [수정] 이동할 때도 도우미 함수 사용
                print("\n[기사 이동]")
                target_folder = _get_folder_choice(manager)
                
                # 원래 폴더와 같으면 이동할 필요 없음
                if target_folder == folder_name:
                    print("⚠️ 현재 폴더와 동일합니다. 이동하지 않습니다.")
                else:
                    manager.move_article(folder_name, real_idx, target_folder)
                    
        else:
            print("❌ 잘못된 번호입니다.")

if __name__ == "__main__":
    while True:
        print("\n=========================================")
        print("   TiDIED Project: 뉴스 수집기")
        print("=========================================")
        print("1. 네이버 뉴스 크롤링 시작")
        print("2. 북마크 확인 및 관리 (폴더/삭제/이동)") # [수정됨]
        print("9. [관리자] 네이버 클래스명 진단 도구 실행")
        print("0. 종료")
        print("=========================================")
        
        choice = input("메뉴를 선택하세요: ")
        
        if choice == "1":
            run_crawler()
        elif choice == "2":
            # [수정됨] 이제 단순 출력이 아니라 '뷰어' 함수를 실행합니다.
            run_bookmark_viewer()
        elif choice == "9":
            run_diagnosis()
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다.")