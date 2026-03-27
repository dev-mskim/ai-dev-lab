"""
5단계: Streamlit 웹 UI
실행: streamlit run src/app.py
"""

import sys
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())

import streamlit as st
import pandas as pd
from src.sql_generator import ask

# ─────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ERP 챗봇",
    page_icon="🤖",
    layout="wide"
)

# ─────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ─────────────────────────────────────────
# 테마 CSS 주입
# ─────────────────────────────────────────
DARK_CSS = """
<style>
    /* 전체 배경 */
    .stApp {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #2c2c2c;
    }
    /* 입력창 */
    .stChatInput textarea, .stTextInput input {
        background-color: #3a3a3a !important;
        color: #e0e0e0 !important;
        border-color: #555 !important;
    }
    /* 채팅 메시지 */
    [data-testid="stChatMessage"] {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 4px;
    }
    /* expander */
    [data-testid="stExpander"] {
        background-color: #2a2a2a;
        border: 1px solid #444;
    }
    /* 버튼 */
    .stButton button {
        background-color: #3a3a3a;
        color: #e0e0e0;
        border: 1px solid #555;
    }
    .stButton button:hover {
        background-color: #4a4a4a;
        border-color: #777;
    }
    /* 코드 블록 */
    .stCode {
        background-color: #2d2d2d !important;
    }
    /* divider */
    hr {
        border-color: #444;
    }
    /* 캡션 */
    .stCaption {
        color: #aaa !important;
    }
    /* 데이터프레임 */
    [data-testid="stDataFrame"] {
        background-color: #2a2a2a;
    }
</style>
"""

LIGHT_CSS = """
<style>
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    [data-testid="stChatMessage"] {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 4px;
    }
</style>
"""

st.markdown(DARK_CSS if st.session_state.dark_mode else LIGHT_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────
with st.sidebar:

    # 다크/라이트 모드 토글
    mode_label = "☀️ 라이트 모드" if st.session_state.dark_mode else "🌙 다크 모드"
    if st.button(mode_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.divider()

    st.header("📋 질문 예시")
    examples = [
        "이번 달 매출 TOP 5 고객",
        "서울 지역 고객 목록",
        "상품 카테고리별 평균 단가",
        "홍길동 고객의 주문 내역",
        "전체 주문 건수 알려줘",
        "가장 비싼 상품 TOP 3",
        "월별 매출 추이 보여줘",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.selected_example = ex

    st.divider()

    if st.button("대화 초기화", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("⚠️ SELECT 쿼리만 허용됩니다.")
    st.caption("📦 데모 DB: SQLite 샘플 데이터")

# ─────────────────────────────────────────
# 메인 화면 헤더
# ─────────────────────────────────────────
st.title("🤖 ERP 챗봇")
st.caption("자연어로 질문하면 DB에서 결과를 찾아드립니다.")
st.divider()

# ─────────────────────────────────────────
# 이전 대화 히스토리 출력
# ─────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.write(msg["content"])
        else:
            st.write(msg["answer"])
            col1, col2 = st.columns(2)
            with col1:
                with st.expander("📝 생성된 SQL"):
                    st.code(msg["sql"], language="sql")
            with col2:
                with st.expander(f"📊 조회 결과 ({len(msg['result'])}건)"):
                    if msg["result"]:
                        st.dataframe(pd.DataFrame(msg["result"]), use_container_width=True)
                    else:
                        st.info("조회된 데이터가 없습니다.")

# ─────────────────────────────────────────
# 사이드바 예시 버튼 클릭 처리
# ─────────────────────────────────────────
if "selected_example" in st.session_state:
    user_input = st.session_state.pop("selected_example")
else:
    user_input = None

# ─────────────────────────────────────────
# 채팅 입력창
# ─────────────────────────────────────────
chat_input = st.chat_input("질문을 입력하세요. 예) 이번 달 매출 TOP 5 고객")
if chat_input:
    user_input = chat_input

# ─────────────────────────────────────────
# 질문 처리 및 응답 생성
# ─────────────────────────────────────────
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("SQL 생성 및 조회 중..."):
            try:
                res = ask(user_input)

                st.write(res["answer"])

                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("📝 생성된 SQL"):
                        st.code(res["sql"], language="sql")
                with col2:
                    with st.expander(f"📊 조회 결과 ({len(res['result'])}건)"):
                        if res["result"]:
                            st.dataframe(pd.DataFrame(res["result"]), use_container_width=True)
                        else:
                            st.info("조회된 데이터가 없습니다.")

                st.session_state.messages.append({
                    "role":   "assistant",
                    "answer": res["answer"],
                    "sql":    res["sql"],
                    "result": res["result"],
                })

            except ValueError as e:
                st.error(f"⛔ 허용되지 않는 요청입니다: {e}")
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {e}")
