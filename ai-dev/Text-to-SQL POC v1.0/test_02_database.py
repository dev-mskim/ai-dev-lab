"""
2단계 테스트: 샘플 DB 점검
실행: python test_02_database.py
점검: DB 파일 존재, 테이블 구조, 데이터 건수, JOIN 쿼리
"""

import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
print("  2단계 테스트: 샘플 DB 점검")
print("=" * 50)

from sqlalchemy import create_engine, text, inspect

engine = create_engine("sqlite:///data/sample.db")

# ── DB 파일 및 연결 확인 ──────────────────────
print("\n[DB 파일 및 연결 확인]")

check("data/sample.db 파일 존재",
      lambda: "OK" if os.path.exists("data/sample.db")
      else (_ for _ in ()).throw(Exception("파일 없음 → python src/db_setup.py 실행 필요")))

check("DB 연결",
      lambda: engine.connect().execute(text("SELECT 1")) and "OK")

# ── 테이블 구조 확인 ──────────────────────────
print("\n[테이블 구조 확인]")

def check_table(table_name, required_columns):
    inspector = inspect(engine)
    tables = [t.upper() for t in inspector.get_table_names()]
    if table_name not in tables:
        raise Exception(f"{table_name} 테이블 없음")
    cols = [c["name"].upper() for c in inspector.get_columns(table_name)]
    missing = [c for c in required_columns if c not in cols]
    if missing:
        raise Exception(f"누락된 컬럼: {missing}")
    return f"{len(cols)}개 컬럼 확인"

check("CUSTOMERS 테이블 구조",
      lambda: check_table("CUSTOMERS", ["CUSTOMER_ID", "NAME", "EMAIL", "REGION"]))

check("PRODUCTS 테이블 구조",
      lambda: check_table("PRODUCTS", ["PRODUCT_ID", "PRODUCT_NAME", "CATEGORY", "UNIT_PRICE"]))

check("ORDERS 테이블 구조",
      lambda: check_table("ORDERS", ["ORDER_ID", "CUSTOMER_ID", "ORDER_DATE", "STATUS"]))

check("ORDER_ITEMS 테이블 구조",
      lambda: check_table("ORDER_ITEMS", ["ITEM_ID", "ORDER_ID", "PRODUCT_ID", "QUANTITY", "AMOUNT"]))

# ── 데이터 건수 확인 ──────────────────────────
print("\n[샘플 데이터 건수 확인]")

def check_count(table, expected):
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        if count < expected:
            raise Exception(f"{count}건 (최소 {expected}건 필요)")
        return f"{count}건"

check("CUSTOMERS 데이터",   lambda: check_count("CUSTOMERS", 1))
check("PRODUCTS 데이터",    lambda: check_count("PRODUCTS", 1))
check("ORDERS 데이터",      lambda: check_count("ORDERS", 1))
check("ORDER_ITEMS 데이터", lambda: check_count("ORDER_ITEMS", 1))

# ── 쿼리 검증 ─────────────────────────────────
print("\n[쿼리 검증]")

def check_join():
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT c.NAME, SUM(oi.AMOUNT) AS 총구매금액
            FROM CUSTOMERS c
            JOIN ORDERS o       ON c.CUSTOMER_ID = o.CUSTOMER_ID
            JOIN ORDER_ITEMS oi ON o.ORDER_ID    = oi.ORDER_ID
            GROUP BY c.NAME
            ORDER BY 총구매금액 DESC
            LIMIT 3
        """)).fetchall()
        if not rows:
            raise Exception("JOIN 결과 없음")
        return f"1위: {rows[0][0]} ({rows[0][1]:,.0f}원)"
check("고객별 총 구매금액 (3테이블 JOIN)", check_join)

def check_monthly():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT SUM(oi.AMOUNT)
            FROM ORDER_ITEMS oi
            JOIN ORDERS o ON oi.ORDER_ID = o.ORDER_ID
            WHERE o.ORDER_DATE LIKE '2026-03%'
        """)).scalar()
        if not result:
            raise Exception("3월 매출 데이터 없음")
        return f"2026년 3월 총매출: {result:,.0f}원"
check("월별 매출 집계", check_monthly)

def check_product_sales():
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT p.PRODUCT_NAME, SUM(oi.QUANTITY) AS 총판매량
            FROM PRODUCTS p
            JOIN ORDER_ITEMS oi ON p.PRODUCT_ID = oi.PRODUCT_ID
            GROUP BY p.PRODUCT_NAME
            ORDER BY 총판매량 DESC
            LIMIT 1
        """)).fetchone()
        if not row:
            raise Exception("상품별 판매량 결과 없음")
        return f"판매 1위: {row[0]} ({row[1]}개)"
check("상품별 판매량 집계", check_product_sales)

def check_status():
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT STATUS, COUNT(*) AS 건수
            FROM ORDERS
            GROUP BY STATUS
        """)).fetchall()
        if not rows:
            raise Exception("주문 상태 데이터 없음")
        return " / ".join([f"{r[0]}:{r[1]}건" for r in rows])
check("주문 상태별 집계 (COMPLETE/PENDING)", check_status)

# ── 결과 ──────────────────────────────────────
total = PASS + FAIL
print(f"\n{'=' * 50}")
print(f"  결과: {PASS}/{total} 항목 통과")
if FAIL == 0:
    print("  2단계 샘플 DB 완료! 3단계 진행 가능합니다.")
else:
    print("  [FAIL] 항목 확인 후 python src/db_setup.py 재실행")
print("=" * 50)
