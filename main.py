# main.py

# [모듈과 패키지]
# core 패키지 안에 있는 tidied 모듈에서 Tidied 클래스를 가져옵니다.
from core.tidied import TIDIED

# [시작점(Entry Point)]
# 이 파일이 직접 실행될 때만 아래 코드가 작동합니다. (다른 곳에서 import 할 땐 실행 안 됨!!)
if __name__ == "__main__":
    
    # [설계 결과]
    # 모든 복잡한 로직은 Tidied 클래스 안으로 숨겼습니다(캡슐화).
    # 덕분에 main.py는 단 2줄로 매우 깔끔해졌습니다.
    app = TIDIED() 
    
    # 앱 실행 (메인 루프 진입)
    app.run()