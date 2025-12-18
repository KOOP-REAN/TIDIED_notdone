# services/bookmark_manager.py

import json
import os
from models.article import Article

class BookmarkManager:
    """
    수집한 기사(Article 객체)들을 '폴더별'로 JSON 파일에 저장하거나 불러옵니다.
    """

    def __init__(self, filepath: str = "data/bookmarks.json"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    def _load_json_data(self) -> dict:
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}

    def save_bookmarks(self, articles: list[Article], folder_name: str = "기본 폴더") -> None:
        if not articles:
            return

        try:
            all_data = self._load_json_data()

            if folder_name not in all_data:
                all_data[folder_name] = []

            # to_dict()가 호출되면서 한글 키로 변환됩니다.
            new_data = [article.to_dict() for article in articles]
            
            all_data[folder_name].extend(new_data)

            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            
            print(f"\n💾 [저장 완료] '{folder_name}' 폴더에 {len(articles)}개의 기사를 저장했습니다.")

        except Exception as e:
            print(f"❌ [Error] 파일 저장 중 오류 발생: {e}")

    # [수정됨] 한글 키를 인식해서 Article 객체로 복원하는 로직
    def load_bookmarks(self):
        """
        다음 단계(3. 조회 및 관리)에서 사용할 로직입니다.
        한글 키(기사 제목, 부제목...)를 읽어서 Article 객체로 만듭니다.
        """
        all_data = self._load_json_data()
        if not all_data:
            return {} # 데이터가 없으면 빈 딕셔너리 반환

        restored_data = {}
        
        for folder, items in all_data.items():
            restored_data[folder] = []
            for item in items:
                # 한글 키로 데이터 읽기
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
        성공하면 True, 실패하면 False를 반환합니다.
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
            
            # 4. 폴더가 비었으면 폴더 자체를 삭제할 수도 있음 (여기선 유지)
            
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
        """
        try:
            all_data = self._load_json_data()

            # 1. 소스 폴더 확인
            if src_folder not in all_data:
                print("❌ 원본 폴더가 없습니다.")
                return False
            
            # 2. 인덱스 확인
            if index < 0 or index >= len(all_data[src_folder]):
                print("❌ 잘못된 번호입니다.")
                return False

            # 3. 데이터 꺼내기 (pop)
            item_to_move = all_data[src_folder].pop(index)

            # 4. 목적지 폴더 확인 및 생성
            if dest_folder not in all_data:
                all_data[dest_folder] = [] # 새 폴더 생성

            # 5. 목적지에 추가
            all_data[dest_folder].append(item_to_move)

            # 6. 저장
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            
            print(f"\n🚚 [이동 완료] '{src_folder}' -> '{dest_folder}' 로 이동했습니다.")
            return True

        except Exception as e:
            print(f"❌ [Error] 이동 중 오류 발생: {e}")
            return False