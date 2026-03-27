"""
3단계 테스트: Vector DB 점검
실행: python test_03_vectordb.py
점검: ChromaDB 연결, 스키마 저장 건수, 자연어 검색 정확도
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
print("  3단계 테스트: Vector DB 점검")
print("=" * 50)

import chromadb
from chromadb.utils import embedding_functions

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

# ── 기본 연결 확인 ────────────────────────────
print("\n[ChromaDB 연결 확인]")

check("vectordb/ 폴더 존재",
      lambda: "OK" if os.path.exists("vectordb")
      else (_ for _ in ()).throw(Exception("폴더 없음 → python src/schema_loader.py 실행 필요")))

def get_collection():
    client = chromadb.PersistentClient(path="vectordb")
    return client.get_collection(name="schema", embedding_function=ef)

check("schema 컬렉션 로드",
      lambda: get_collection() and "OK")

# ── 저장 건수 확인 ────────────────────────────
print("\n[스키마 저장 건수 확인]")

def check_count():
    col = get_collection()
    count = col.count()
    if count < 5:
        raise Exception(f"{count}개 저장됨 (5개 이상 필요) → schema_loader.py 재실행")
    return f"{count}개 저장 확인 (CUSTOMERS, PRODUCTS, ORDERS, ORDER_ITEMS, TABLE_RELATIONS)"
check("저장된 스키마 수", check_count)

# ── 테이블별 스키마 직접 조회 ─────────────────
print("\n[테이블별 스키마 존재 확인]")

def check_schema_exists(table_id):
    col = get_collection()
    result = col.get(ids=[table_id])
    if not result["documents"] or not result["documents"][0]:
        raise Exception(f"{table_id} 스키마 없음")
    return f"{len(result['documents'][0])}자 저장됨"

check("CUSTOMERS 스키마",      lambda: check_schema_exists("CUSTOMERS"))
check("PRODUCTS 스키마",       lambda: check_schema_exists("PRODUCTS"))
check("ORDERS 스키마",         lambda: check_schema_exists("ORDERS"))
check("ORDER_ITEMS 스키마",    lambda: check_schema_exists("ORDER_ITEMS"))
check("TABLE_RELATIONS 스키마", lambda: check_schema_exists("TABLE_RELATIONS"))

# ── 자연어 검색 정확도 확인 ───────────────────
print("\n[자연어 검색 정확도 확인]")

def check_search(query, expected_table):
    col = get_collection()
    results = col.query(query_texts=[query], n_results=2)
    matched = [r["table"] for r in results["metadatas"][0]]
    if expected_table not in matched:
        raise Exception(f"기대: {expected_table}, 실제: {matched}")
    return f"'{query}' → {matched}"

check("매출 질문 → ORDERS 검색",
      lambda: check_search("이번 달 매출 알려줘", "ORDERS"))

check("고객 질문 → CUSTOMERS 검색",
      lambda: check_search("고객 목록 보여줘", "CUSTOMERS"))

check("상품 질문 → PRODUCTS 검색",
      lambda: check_search("상품 카테고리별 개수", "PRODUCTS"))

check("주문 상세 질문 → ORDER_ITEMS 검색",
      lambda: check_search("상품별 판매 수량 합계", "ORDER_ITEMS"))

# ── 스키마 문서 내용 검증 ─────────────────────
print("\n[스키마 문서 내용 검증]")

def check_column_in_schema(table_id, column_name):
    col = get_collection()
    result = col.get(ids=[table_id])
    doc = result["documents"][0]
    if column_name not in doc:
        raise Exception(f"{table_id} 스키마에 {column_name} 컬럼 정보 없음")
    return f"{column_name} 포함 확인"

check("CUSTOMERS 스키마에 CUSTOMER_ID 포함",
      lambda: check_column_in_schema("CUSTOMERS", "CUSTOMER_ID"))

check("ORDERS 스키마에 ORDER_DATE 포함",
      lambda: check_column_in_schema("ORDERS", "ORDER_DATE"))

check("ORDER_ITEMS 스키마에 AMOUNT 포함",
      lambda: check_column_in_schema("ORDER_ITEMS", "AMOUNT"))

check("TABLE_RELATIONS 에 JOIN 예시 포함",
      lambda: check_column_in_schema("TABLE_RELATIONS", "JOIN"))

# ── 결과 ──────────────────────────────────────
total = PASS + FAIL
print(f"\n{'=' * 50}")
print(f"  결과: {PASS}/{total} 항목 통과")
if FAIL == 0:
    print("  3단계 Vector DB 완료! 4단계 진행 가능합니다.")
else:
    print("  [FAIL] 항목 확인 후 python src/schema_loader.py 재실행")
print("=" * 50)
