# app.py
# 웹피이지 제작은 온전히 Gemini를 통해서만 만들었습니다.
import streamlit as st
import time
from crawlers.naver_crawler import NaverCrawler
from services.bookmark_manager import BookmarkManager

# 페이지 기본 설정 (제목, 아이콘 등)
st.set_page_config(
    page_title="TiDIED - 뉴스 수집기",
    page_icon="📰",
    layout="wide"
)

# --- [초기화] 세션 상태 관리 (새로고침 해도 데이터 유지) ---
if 'crawler' not in st.session_state:
    st.session_state.crawler = NaverCrawler()
if 'manager' not in st.session_state:
    st.session_state.manager = BookmarkManager()
if 'articles' not in st.session_state:
    st.session_state.articles = []

# --- 사이드바 메뉴 ---
st.sidebar.title("🗂️ TiDIED 메뉴")
menu = st.sidebar.radio("이동할 페이지를 선택하세요:", ["📰 뉴스 수집 (검색)", "💾 북마크 관리"])

# =========================================================
# 1. 뉴스 수집 페이지
# =========================================================
if menu == "📰 뉴스 수집 (검색)":
    st.title("📰 네이버 뉴스 크롤러")
    st.markdown("키워드를 입력하면 뉴스를 수집하여 요약해 드립니다.")

    # [입력 폼]
    with st.form("search_form"):
        col1, col2 = st.columns([3, 1])
        with col1:
            keyword = st.text_input("검색어 입력", placeholder="예: 삼성전자")
        with col2:
            pages = st.number_input("수집할 페이지 수", min_value=1, max_value=5, value=1)
        
        search_btn = st.form_submit_button("🚀 뉴스 수집 시작")

    # [크롤링 실행 로직]
    if search_btn and keyword:
        with st.spinner(f"'{keyword}' 관련 뉴스를 열심히 찾아오고 있습니다..."):
            # 1. 기사 목록 수집
            articles = st.session_state.crawler.search(keyword, pages=pages)
            
            # 2. 부제목 수집 (진행바 표시)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, article in enumerate(articles):
                status_text.text(f"📝 기사 내용 요약 중... ({i+1}/{len(articles)})")
                content = st.session_state.crawler.get_content(article.url)
                article.content = content if content else "" # 없으면 빈 문자열
                progress_bar.progress((i + 1) / len(articles))
            
            status_text.empty()
            progress_bar.empty()
            
          
            # 3. [추가됨] 정렬 로직 (Sorting)       
            articles.sort(key=lambda x: (
                0 if (x.url.startswith("https://n.news.naver.com") and x.content) else
                1 if (x.url.startswith("https://n.news.naver.com") and not x.content) else
                2
            ))

            # 세션에 저장 (화면이 리로드돼도 사라지지 않게)
            st.session_state.articles = articles
            st.success(f"✅ 총 {len(articles)}개의 기사를 찾았습니다! (중요도 순 정렬 완료)")
            

    # [결과 출력 및 저장]
    if st.session_state.articles:
        st.divider()
        st.subheader("🔎 검색 결과")

        # 다중 선택 기능 (Multiselect)
        # 객체 자체를 리스트로 보여주기 위해 제목을 라벨로 사용
        article_options = {f"{i+1}. {art.title}": art for i, art in enumerate(st.session_state.articles)}
        
        selected_keys = st.multiselect(
            "💾 저장할 기사를 선택하세요:",
            options=list(article_options.keys())
        )

        # 저장 옵션
        if selected_keys:
            with st.expander("📂 저장 옵션 (폴더 선택)", expanded=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    # 기존 폴더 목록 가져오기
                    existing_folders = list(st.session_state.manager.load_bookmarks().keys())
                    if not existing_folders:
                        existing_folders = ["스크랩"]
                    
                    folder_method = st.radio("폴더 선택 방식", ["기존 폴더 선택", "새 폴더 생성"], horizontal=True)
                    
                    if folder_method == "기존 폴더 선택":
                        folder_name = st.selectbox("폴더 선택", existing_folders)
                    else:
                        folder_name = st.text_input("새 폴더 이름", value="나의 스크랩")

                with col2:
                    st.write("") # 여백
                    st.write("") 
                    save_btn = st.button("💾 선택한 기사 저장")

            if save_btn:
                # 선택된 기사 객체들만 추출
                target_articles = [article_options[key] for key in selected_keys]
                st.session_state.manager.save_bookmarks(target_articles, folder_name)
                st.toast(f"✅ '{folder_name}' 폴더에 {len(target_articles)}개 저장 완료!", icon="🎉")

        # 기사 목록 카드 형태로 보여주기
        for i, article in enumerate(st.session_state.articles):
            with st.container():
                st.markdown(f"### [{i+1}] {article.title}")
                st.caption(f"출처: {article.source} | 링크: {article.url}")
                if article.content:
                    st.info(f"📝 {article.content[:100]}...")
                st.divider()

# =========================================================
# 2. 북마크 관리 페이지
# =========================================================
elif menu == "💾 북마크 관리":
    st.title("💾 북마크 뷰어")
    
    # 데이터 로드
    saved_data = st.session_state.manager.load_bookmarks()
    
    if not saved_data:
        st.warning("📂 저장된 북마크가 없습니다. 먼저 뉴스를 수집해 보세요!")
    else:
        folders = list(saved_data.keys())
        selected_folder = st.selectbox("📂 폴더를 선택하세요:", folders)

        if selected_folder:
            articles = saved_data[selected_folder]
            st.markdown(f"### '{selected_folder}' 폴더 ({len(articles)}개)")

            # 기사 리스트 출력
            for i, article in enumerate(articles):
                with st.expander(f"{i+1}. {article.title}"):
                    st.write(f"**출처**: [{article.source}]({article.url})")
                    if article.content:
                        st.write(f"**부제목**: {article.content}")
                    else:
                        st.write("**부제목**: (없음)")
                    
                    # 삭제/이동 버튼 (컬럼으로 배치)
                    col_del, col_move = st.columns([1, 3])
                    with col_del:
                        if st.button("🗑️ 삭제", key=f"del_{selected_folder}_{i}"):
                            st.session_state.manager.delete_article(selected_folder, i)
                            st.rerun() # 화면 즉시 새로고침
                    
                    with col_move:
                        # 이동은 UI 복잡도를 낮추기 위해 간단하게 구현
                        pass