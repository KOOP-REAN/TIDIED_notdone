# services/bookmark_manager.py

import json
import os
from models.article import Article

class BookmarkManager:
    """
    [파일 입출력]
    수집한 기사(Article 객체)들을 JSON 파일로 영구 저장하고, 다시 불러오는 역할을 합니다.
    단순 텍스트 파일(txt) 대신 구조화된 데이터(JSON) 형식을 선택했습니다.
    """

    def __init__(self, filepath: str = "data/bookmarks.json"):
        self.filepath = filepath
        # 파일이 저장될 폴더가 없으면 에러가 나므로, os 모듈로 미리 생성해줍니다.
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    def _load_json_data(self) -> dict:
        """
        [내부 함수] 파일을 안전하게 열어서 데이터를 읽어오는 공통 로직입니다.
        """
        if not os.path.exists(self.filepath):
            return {}
        try:
            # [파일 읽기] 'r' 모드 사용, 인코딩은 utf-8 필수
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            # 파일이 깨져있거나 비어있을 경우 빈 딕셔너리로 초기화 (프로그램 뻗음 방지)
            return {}

    def save_bookmarks(self, articles: list[Article], folder_name: str = "기본 폴더") -> None:
        """
        [시행착오 기록 - 인코딩 문제]
        처음엔 json.dump()를 그냥 썼더니 한글이 유니코드 문자로 깨져서 저장되었습니다.
        구글링 결과 ensure_ascii=False 옵션을 줘야 한글이 그대로 저장된다는 것을 알게 되어 수정했습니다.
        """
        if not articles:
            return

        try:
            all_data = self._load_json_data()

            # [딕셔너리 자료구조] 폴더명을 Key, 기사 리스트를 Value로 관리
            if folder_name not in all_data:
                all_data[folder_name] = []

            # 객체(Article)는 JSON으로 바로 저장이 안 되므로, 딕셔너리로 변환(직렬화)해야 함
            new_data = [article.to_dict() for article in articles]
            
            # 기존 데이터에 추가 (extend)
            all_data[folder_name].extend(new_data)

            # [파일 쓰기] 'w' 모드로 덮어쓰기
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            
            print(f"\n💾 [저장 완료] '{folder_name}' 폴더에 {len(articles)}개의 기사를 저장했습니다.")

        except Exception as e:
            # [예외 처리] 파일 권한 문제 등으로 저장 실패 시 에러 메시지 출력
            print(f"❌ [Error] 파일 저장 중 오류 발생: {e}")

    # [수정됨] 한글 키를 인식해서 Article 객체로 복원하는 로직
    def load_bookmarks(self):
        """
        [시행착오 기록 - 객체 복원]
        JSON 파일에서 읽어온 데이터는 단순한 '딕셔너리(dict)' 상태입니다.
        이걸 그대로 쓰면 article.title 처럼 점(.)으로 접근할 수 없는 문제가 있었습니다.
        그래서 읽어온 딕셔너리를 다시 Article 객체로 변환(역직렬화)하는 과정을 추가했습니다.
        """
        all_data = self._load_json_data()
        if not all_data:
            return {} # 데이터가 없으면 빈 딕셔너리 반환

        restored_data = {}
        
        for folder, items in all_data.items():
            restored_data[folder] = []
            for item in items:
                # 딕셔너리의 한글 Key 값을 이용해 Article 객체 재조립
                article = Article(
                    title=item.get("기사 제목", "제목 없음"),
                    url=item.get("출처(링크)", ""),
                    source=item.get("사이트", "Unknown")
                )
                article.content = item.get("부제목", "")
                restored_data[folder].append(article)
                
        return restored_data
    

    def delete_article(self, folder_name: str, index: int) -> bool:
        """
        특정 폴더의 index 번째 기사를 삭제합니다.
        [리스트] pop() 메서드를 활용합니다.
        """
        try:
            # 1. 원본 데이터(딕셔너리) 불러오기
            all_data = self._load_json_data()

            # 2. 유효성 검사
            if folder_name not in all_data:
                return False
            if index < 0 or index >= len(all_data[folder_name]):
                return False

            # 3. 삭제 (pop)
            deleted_item = all_data[folder_name].pop(index)
            
            # 4. 폴더가 비었으면 폴더 자체를 삭제할 수도 있지만 
            # (여기선 0개 파일의 폴더도 유지하기로 결정했습니당)
            
            # 5. 변경된 데이터 저장
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            
            print(f"\n🗑️ [삭제 완료] '{deleted_item.get('기사 제목')}' 기사를 삭제했습니다.")
            return True

        except Exception as e:
            print(f"❌ [Error] 삭제 중 오류 발생: {e}")
            return False

    def move_article(self, src_folder: str, index: int, dest_folder: str) -> bool:
        """
        특정 기사를 다른 폴더로 이동시킵니다.
        삭제(pop) 후 추가(append)하는 로직을 조합했습니다.
        """
        try:
            all_data = self._load_json_data()

            # 1. 유효성 CHECK!!
            if src_folder not in all_data:
                print("❌ 원본 폴더가 없습니다.")
                return False
            if index < 0 or index >= len(all_data[src_folder]):
                print("❌ 잘못된 번호입니다.")
                return False

            # 2. 데이터 꺼내기 (pop)
            item_to_move = all_data[src_folder].pop(index)

            # 3. 목적지 폴더 확인 및 생성
            if dest_folder not in all_data:
                all_data[dest_folder] = [] 

            # 4. 목적지에 추가
            all_data[dest_folder].append(item_to_move)

            
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            
            print(f"\n🚚 [이동 완료] '{src_folder}' -> '{dest_folder}' 로 이동했습니다.")
            return True

        except Exception as e:
            print(f"❌ [Error] 이동 중 오류 발생: {e}")
            return False