"""
4단계 테스트: 핵심 로직 점검
실행: python test_04_sql_generator.py
점검: 스키마 검색, SQL 생성, 보안 검증, DB 실행, 자연어 요약, 통합 흐름
"""

import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

PASS = 0
FAIL = 0


def check(label, fn):
    global PASS, FAIL
    try:
        result = fn()
        msg = f" → {result}" if isinstance(result, str) else ""
        print(f"  [OK] {label}{msg}")
        PASS += 1
    except Exception as e:
        print(f"  [FAIL] {label}")
        print(f"         └ {e}")
        FAIL += 1


print("=" * 50)
print("  4단계 테스트: 핵심 로직 점검")
print("=" * 50)

# sql_generator 내부 함수 직접 접근
from src.sql_generator import (
    ask,
    _search_schema,
    _generate_sql,
    _execute_sql,
    _summarize,
    _is_safe_sql,
)


# ── 보안 검증 테스트 ──────────────────────────
print("\n[보안 검증: SELECT 외 쿼리 차단]")

check("SELECT 쿼리 허용",
      lambda: "OK" if _is_safe_sql("SELECT * FROM CUSTOMERS") else (_ for _ in ()).throw(Exception("SELECT가 차단됨")))

check("DELETE 쿼리 차단",
      lambda: "OK" if not _is_safe_sql("DELETE FROM CUSTOMERS") else (_ for _ in ()).throw(Exception("DELETE가 허용됨")))

check("DROP 쿼리 차단",
      lambda: "OK" if not _is_safe_sql("DROP TABLE CUSTOMERS") else (_ for _ in ()).throw(Exception("DROP이 허용됨")))

check("UPDATE 쿼리 차단",
      lambda: "OK" if not _is_safe_sql("UPDATE CUSTOMERS SET NAME='X'") else (_ for _ in ()).throw(Exception("UPDATE가 허용됨")))

check("INSERT 쿼리 차단",
      lambda: "OK" if not _is_safe_sql("INSERT INTO CUSTOMERS VALUES(1,'X')") else (_ for _ in ()).throw(Exception("INSERT가 허용됨")))

check("TRUNCATE 쿼리 차단",
      lambda: "OK" if not _is_safe_sql("TRUNCATE TABLE CUSTOMERS") else (_ for _ in ()).throw(Exception("TRUNCATE가 허용됨")))


# ── 스키마 검색 테스트 ────────────────────────
print("\n[스키마 검색 정확도]")

def check_schema_contains(question, expected_keyword):
    schema = _search_schema(question)
    if expected_keyword not in schema:
        raise Exception(f"'{expected_keyword}' 가 검색된 스키마에 없음")
    return f"'{expected_keyword}' 포함 확인"

check("매출 질문 → ORDERS 테이블 포함",
      lambda: check_schema_contains("이번 달 매출 알려줘", "ORDERS"))

check("고객 질문 → CUSTOMERS 테이블 포함",
      lambda: check_schema_contains("고객 목록 보여줘", "CUSTOMERS"))

check("상품 질문 → UNIT_PRICE 컬럼 포함",
      lambda: check_schema_contains("상품 단가 알려줘", "UNIT_PRICE"))


# ── SQL 생성 테스트 ───────────────────────────
print("\n[SQL 생성]")

def check_sql_generated(question, expected_keywords: list):
    schema = _search_schema(question)
    sql = _generate_sql(question, schema)
    sql_upper = sql.upper()
    missing = [k for k in expected_keywords if k not in sql_upper]
    if missing:
        raise Exception(f"SQL에 누락된 키워드: {missing}\n생성된 SQL: {sql}")
    return sql.split("\n")[0][:60]

check("단순 조회 SQL 생성",
      lambda: check_sql_generated("고객 목록 보여줘", ["SELECT", "CUSTOMERS"]))

check("집계 SQL 생성 (SUM/GROUP BY)",
      lambda: check_sql_generated("고객별 총 구매금액 알려줘", ["SELECT", "SUM", "GROUP BY"]))

check("JOIN SQL 생성",
      lambda: check_sql_generated("이번 달 매출 TOP 3 고객", ["SELECT", "JOIN", "ORDER BY"]))

check("조건 필터 SQL 생성",
      lambda: check_sql_generated("서울 지역 고객 목록", ["SELECT", "WHERE"]))

def check_sql_no_bad_columns(question):
    schema = _search_schema(question)
    sql = _generate_sql(question, schema)
    sql_upper = sql.upper()
    if "OI.UNIT_PRICE" in sql_upper or "ORDER_ITEMS.UNIT_PRICE" in sql_upper:
        raise Exception(f"ORDER_ITEMS에 없는 UNIT_PRICE 컬럼 사용됨\nSQL: {sql}")
    return "AMOUNT 컬럼 정상 사용"
check("매출 집계 시 AMOUNT 컬럼 사용 (UNIT_PRICE 오용 방지)",
      lambda: check_sql_no_bad_columns("이번 달 매출 TOP 3 고객 알려줘"))


# ── SQL 실행 테스트 ───────────────────────────
print("\n[SQL 실행]")

def check_execute(sql, min_rows=0):
    result = _execute_sql(sql)
    if len(result) < min_rows:
        raise Exception(f"{len(result)}건 반환 (최소 {min_rows}건 필요)")
    return f"{len(result)}건 반환"

check("전체 고객 조회",
      lambda: check_execute("SELECT * FROM CUSTOMERS", min_rows=1))

check("조건 필터 조회",
      lambda: check_execute("SELECT * FROM CUSTOMERS WHERE REGION = '서울'", min_rows=1))

check("JOIN 쿼리 실행",
      lambda: check_execute("""
          SELECT c.NAME, SUM(oi.AMOUNT) AS 총구매금액
          FROM CUSTOMERS c
          JOIN ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
          JOIN ORDER_ITEMS oi ON o.ORDER_ID = oi.ORDER_ID
          GROUP BY c.NAME
          ORDER BY 총구매금액 DESC
          LIMIT 3
      """, min_rows=1))

def check_dangerous_blocked():
    try:
        _execute_sql("DELETE FROM CUSTOMERS")
        raise Exception("차단되지 않음")
    except ValueError:
        return "위험 쿼리 정상 차단"
check("위험 쿼리 실행 시 예외 발생",
      check_dangerous_blocked)

def check_result_is_dict():
    result = _execute_sql("SELECT * FROM CUSTOMERS LIMIT 1")
    if not isinstance(result[0], dict):
        raise Exception(f"결과가 dict 형태가 아님: {type(result[0])}")
    return f"dict 형태 확인: {list(result[0].keys())}"
check("실행 결과가 dict 리스트 형태",
      check_result_is_dict)


# ── 자연어 요약 테스트 ────────────────────────
print("\n[자연어 요약]")

def check_summary():
    sample_result = [
        {"NAME": "홍길동", "총구매금액": 2200000},
        {"NAME": "김철수", "총구매금액": 89000},
    ]
    answer = _summarize(
        question="매출 TOP 고객 알려줘",
        sql="SELECT NAME, SUM(AMOUNT) FROM ...",
        result=sample_result
    )
    if len(answer) < 10:
        raise Exception(f"요약이 너무 짧음: {answer}")
    if "홍길동" not in answer:
        raise Exception("요약에 결과 데이터가 반영되지 않음")
    return f"{len(answer)}자 요약 생성"
check("결과를 자연어로 요약", check_summary)

def check_empty_result():
    answer = _summarize("없는 데이터 조회", "SELECT ...", [])
    if not answer:
        raise Exception("빈 결과에 대한 답변 없음")
    return "빈 결과 처리 확인"
check("빈 결과 처리 (데이터 없을 때)", check_empty_result)


# ── 통합 흐름 테스트 (ask 함수) ───────────────
print("\n[통합 흐름: ask() 함수]")

def check_ask(question, check_fn):
    res = ask(question)
    if "sql" not in res or "result" not in res or "answer" not in res:
        raise Exception(f"반환값 형식 오류: {res.keys()}")
    if not res["sql"]:
        raise Exception("SQL이 비어있음")
    if not res["answer"]:
        raise Exception("답변이 비어있음")
    return check_fn(res)

check("통합: 단순 조회",
      lambda: check_ask("서울 고객 목록 보여줘",
          lambda r: f"SQL생성+{len(r['result'])}건+답변생성 OK"))

check("통합: 집계 질문",
      lambda: check_ask("상품 카테고리별 평균 단가는?",
          lambda r: f"카테고리 {len(r['result'])}개 집계 OK"))

check("통합: 반환값 구조 확인 (sql/result/answer)",
      lambda: check_ask("전체 상품 목록",
          lambda r: f"키: {sorted(r.keys())}"))


# ── 최종 결과 ─────────────────────────────────
total = PASS + FAIL
print(f"\n{'=' * 50}")
print(f"  결과: {PASS}/{total} 항목 통과")
if FAIL == 0:
    print("  4단계 핵심 로직 완료! 5단계 진행 가능합니다.")
else:
    print("  [FAIL] 항목을 확인하세요. TROUBLESHOOTING.md 참고")
print("=" * 50)
