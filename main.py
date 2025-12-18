# main.py

from core.tidied import TIDIED

if __name__ == "__main__":
    # TIDIED 객체 생성 (여기서 Crawler, Manager가 내부적으로 생성됨)
    app = TIDIED() 
    
    # 앱 실행 (메인 루프 진입)
    app.run()