"""
핵심 로직: 자연어 → SQL → DB 실행 → 자연어 요약
역할: Spring의 @Service (비즈니스 로직 담당)
"""

import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import anthropic
import chromadb
from chromadb.utils import embedding_functions

load_dotenv(encoding="utf-8")

# ─────────────────────────────────────────
# 클라이언트 초기화 (Spring의 @Bean 설정과 동일)
# ─────────────────────────────────────────
_claude  = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
_engine  = create_engine("sqlite:///data/sample.db")
_chroma  = chromadb.PersistentClient(path="vectordb")
_ef      = embedding_functions.SentenceTransformerEmbeddingFunction(
               model_name="paraphrase-multilingual-MiniLM-L12-v2"
           )
_collection = _chroma.get_collection(name="schema", embedding_function=_ef)


# ─────────────────────────────────────────
# 보안 검증: SELECT 쿼리만 허용
# ─────────────────────────────────────────
DANGEROUS_KEYWORDS = ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE"]

def _is_safe_sql(sql: str) -> bool:
    """SELECT 외 위험 쿼리 차단"""
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith("SELECT"):
        return False
    for keyword in DANGEROUS_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_upper):
            return False
    return True


# ─────────────────────────────────────────
# Step 1: 관련 스키마 검색 (ChromaDB)
# ─────────────────────────────────────────
def _search_schema(question: str) -> str:
    """자연어 질문과 관련된 스키마 정보 검색"""
    results = _collection.query(query_texts=[question], n_results=3)
    return "\n\n".join(results["documents"][0])


# ─────────────────────────────────────────
# Step 2: SQL 생성 (Claude API)
# ─────────────────────────────────────────
def _generate_sql(question: str, schema: str) -> str:
    """자연어 질문 → SQL 변환"""
    prompt = f"""당신은 SQL 전문가입니다.
아래 DB 스키마를 참고하여 사용자 질문에 맞는 SQLite SQL을 작성하세요.

[DB 스키마]
{schema}

[규칙]
- SELECT 쿼리만 작성하세요
- SQL 코드만 반환하세요 (설명 없이)
- 마크다운 코드블록(```) 없이 순수 SQL만 반환하세요
- 컬럼명은 대문자로 작성하세요
- 결과가 많을 경우 LIMIT 20을 적용하세요
- 매출/금액 집계 시 ORDER_ITEMS.AMOUNT 컬럼을 직접 사용하세요 (QUANTITY * UNIT_PRICE 계산 금지)
- UNIT_PRICE 컬럼은 PRODUCTS 테이블에만 존재합니다

[사용자 질문]
{question}

SQL:"""

    response = _claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


# ─────────────────────────────────────────

# Step 3: SQL 실행 (SQLAlchemy)
# ─────────────────────────────────────────
def _execute_sql(sql: str) -> list[dict]:
    """SQL 실행 후 결과를 dict 리스트로 반환"""
    if not _is_safe_sql(sql):
        raise ValueError(f"허용되지 않는 쿼리입니다: {sql[:50]}...")

    with _engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]


# ─────────────────────────────────────────
# Step 4: 결과 자연어 요약 (Claude API)
# ─────────────────────────────────────────
def _summarize(question: str, sql: str, result: list[dict]) -> str:
    """쿼리 결과를 자연어로 요약"""
    if not result:
        return "조회된 데이터가 없습니다."

    result_text = "\n".join(str(row) for row in result[:20])

    prompt = f"""사용자의 질문과 DB 조회 결과를 바탕으로 친절하고 자연스러운 한국어로 답변해주세요.

[사용자 질문]
{question}

[실행된 SQL]
{sql}

[조회 결과]
{result_text}

[규칙]
- 숫자는 천 단위 콤마와 단위(원, 개, 건)를 붙여서 표현하세요
- 결과가 여러 건이면 순위나 목록 형태로 정리하세요
- 2~4문장으로 간결하게 답변하세요

답변:"""

    response = _claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


# ─────────────────────────────────────────
# 통합 함수: 질문 하나로 전체 흐름 실행
# ─────────────────────────────────────────
def ask(question: str) -> dict:
    """
    자연어 질문 → SQL 생성 → DB 실행 → 자연어 요약

    반환값:
        {
            "sql"    : 생성된 SQL,
            "result" : 쿼리 결과 (list of dict),
            "answer" : 자연어 요약
        }
    """
    # 1단계: 관련 스키마 검색
    schema = _search_schema(question)

    # 2단계: SQL 생성
    sql = _generate_sql(question, schema)

    # 3단계: SQL 실행
    result = _execute_sql(sql)

    # 4단계: 결과 요약
    answer = _summarize(question, sql, result)

    return {
        "sql": sql,
        "result": result,
        "answer": answer
    }


# ─────────────────────────────────────────
# 단독 실행 시 테스트
# ─────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    test_questions = [
        "홍길동의 거주지는 어디인가요?"
        # "이번 달 매출 TOP 3 고객 알려줘",
        # "서울 지역 고객 목록 보여줘",
        # "상품 카테고리별 평균 단가는?",
    ]

    for q in test_questions:
        print("\n" + "=" * 50)
        print(f"질문: {q}")
        print("=" * 50)
        try:
            res = ask(q)
            print(f"[SQL]\n{res['sql']}\n")
            print(f"[결과] {len(res['result'])}건")
            print(f"[답변] {res['answer']}")
        except Exception as e:
            print(f"[오류] {e}")
