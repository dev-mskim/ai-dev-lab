"""
스키마 정보를 Vector DB(ChromaDB)에 저장하는 스크립트
실행: python src/schema_loader.py
결과: vectordb/ 폴더에 스키마 정보 저장
"""

import chromadb
from chromadb.utils import embedding_functions

# ─────────────────────────────────────────
# 테이블 스키마 정의
# - 테이블명, 한글 설명, 컬럼 정보를 텍스트로 기술
# - LLM이 SQL을 잘 생성할 수 있도록 최대한 자세히 작성
# ─────────────────────────────────────────
SCHEMA_INFO = [
    {
        "id": "CUSTOMERS",
        "document": """
            테이블명: CUSTOMERS (고객 테이블)
            설명: 고객의 기본 정보를 관리하는 테이블
            컬럼:
              - CUSTOMER_ID (INTEGER): 고객 고유번호, 기본키
              - NAME (TEXT): 고객 이름
              - EMAIL (TEXT): 고객 이메일 주소
              - REGION (TEXT): 고객 지역 (서울, 부산, 대구, 인천, 광주 등)
              - CREATED_AT (TEXT): 고객 등록일 (YYYY-MM-DD 형식)
            관계: ORDERS 테이블의 CUSTOMER_ID와 연결됨
            사용 예: 고객 목록 조회, 지역별 고객 수 집계, 고객 검색
        """,
        "metadata": {"table": "CUSTOMERS", "type": "master"}
    },
    {
        "id": "PRODUCTS",
        "document": """
            테이블명: PRODUCTS (상품 테이블)
            설명: 판매 상품의 기본 정보를 관리하는 테이블
            컬럼:
              - PRODUCT_ID (INTEGER): 상품 고유번호, 기본키
              - PRODUCT_NAME (TEXT): 상품명
              - CATEGORY (TEXT): 상품 카테고리 (전자기기, 가구 등)
              - UNIT_PRICE (REAL): 상품 단가 (원 단위)
            관계: ORDER_ITEMS 테이블의 PRODUCT_ID와 연결됨
            사용 예: 상품 목록 조회, 카테고리별 상품 수, 가격 범위 검색
        """,
        "metadata": {"table": "PRODUCTS", "type": "master"}
    },
    {
        "id": "ORDERS",
        "document": """
            테이블명: ORDERS (주문 테이블)
            설명: 고객의 주문 정보를 관리하는 테이블
            컬럼:
              - ORDER_ID (INTEGER): 주문 고유번호, 기본키
              - CUSTOMER_ID (INTEGER): 주문한 고객 번호 (CUSTOMERS 참조)
              - ORDER_DATE (TEXT): 주문 날짜 (YYYY-MM-DD 형식)
              - STATUS (TEXT): 주문 상태 (COMPLETE: 완료, PENDING: 대기)
            관계: CUSTOMERS 테이블과 CUSTOMER_ID로 연결, ORDER_ITEMS와 ORDER_ID로 연결
            사용 예: 주문 현황 조회, 월별 주문 수, 주문 상태별 집계
        """,
        "metadata": {"table": "ORDERS", "type": "transaction"}
    },
    {
        "id": "ORDER_ITEMS",
        "document": """
            테이블명: ORDER_ITEMS (주문 상세 테이블)
            설명: 주문별 상품 구매 상세 내역을 관리하는 테이블
            컬럼 (정확한 컬럼명 사용 필수):
              - ITEM_ID (INTEGER): 주문 상세 고유번호, 기본키 (ORDER_ITEM_ID 아님, ITEM_ID 임)
              - ORDER_ID (INTEGER): 주문 번호 (ORDERS 참조)
              - PRODUCT_ID (INTEGER): 상품 번호 (PRODUCTS 참조)
              - QUANTITY (INTEGER): 구매 수량
              - AMOUNT (REAL): 구매 금액 (수량 x 단가, 원 단위)
            주의: 기본키 컬럼명은 반드시 ITEM_ID 사용 (ORDER_ITEM_ID, DETAIL_ID 등 사용 금지)
            관계: ORDERS, PRODUCTS 테이블과 연결됨
            사용 예: 매출 집계, 상품별 판매량, 고객별 구매 금액 합계, 제품별 판매 추이
        """,
        "metadata": {"table": "ORDER_ITEMS", "type": "transaction"}
    },
]

# 테이블 간 관계 요약 (JOIN 시 참고용)
RELATION_INFO = {
    "id": "TABLE_RELATIONS",
    "document": """
        테이블 관계 요약:
        - 고객의 주문 조회: CUSTOMERS JOIN ORDERS ON CUSTOMERS.CUSTOMER_ID = ORDERS.CUSTOMER_ID
        - 주문 상세 조회: ORDERS JOIN ORDER_ITEMS ON ORDERS.ORDER_ID = ORDER_ITEMS.ORDER_ID
        - 상품 정보 포함: ORDER_ITEMS JOIN PRODUCTS ON ORDER_ITEMS.PRODUCT_ID = PRODUCTS.PRODUCT_ID
        - 전체 조회 예시: CUSTOMERS → ORDERS → ORDER_ITEMS → PRODUCTS

        날짜 필터 예시 (SQLite 기준):
        - 이번 달: ORDER_DATE LIKE '2026-03%'
        - 특정 월: strftime('%Y-%m', ORDER_DATE) = '2026-03'
        - 올해: ORDER_DATE LIKE '2026%'

        매출/금액 관련 컬럼: ORDER_ITEMS.AMOUNT (실제 결제 금액)
        수량 관련 컬럼: ORDER_ITEMS.QUANTITY
    """,
    "metadata": {"table": "ALL", "type": "relation"}
}


def load_schema():
    """스키마 정보를 ChromaDB에 저장"""

    # ChromaDB 클라이언트 (로컬 파일 저장)
    client = chromadb.PersistentClient(path="vectordb")

    # 임베딩 함수 설정 (sentence-transformers 다국어 모델)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    # 컬렉션 초기화 (이미 있으면 삭제 후 재생성)
    try:
        client.delete_collection("schema")
    except Exception:
        pass

    collection = client.create_collection(
        name="schema",
        embedding_function=ef
    )

    # 스키마 정보 저장
    all_schemas = SCHEMA_INFO + [RELATION_INFO]
    collection.add(
        ids=[s["id"] for s in all_schemas],
        documents=[s["document"] for s in all_schemas],
        metadatas=[s["metadata"] for s in all_schemas]
    )

    print(f"[OK] {len(all_schemas)}개 스키마 정보 저장 완료")
    return collection


def search_schema(collection, query: str, n_results: int = 2) -> str:
    """자연어 질문과 관련된 스키마 검색"""
    results = collection.query(query_texts=[query], n_results=n_results)
    documents = results["documents"][0]
    return "\n".join(documents)


if __name__ == "__main__":
    print("=" * 40)
    print(" 스키마 Vector DB 저장 시작")
    print("=" * 40)

    collection = load_schema()

    # 검색 테스트
    print("\n[검색 테스트]")
    test_queries = [
        "이번 달 매출 알려줘",
        "고객 목록 보여줘",
        "상품별 판매량",
    ]
    for query in test_queries:
        results = collection.query(query_texts=[query], n_results=2)
        matched = [r["table"] for r in results["metadatas"][0]]
        print(f"  '{query}' → {matched}")

    print("\n[완료] vectordb/ 폴더에 저장됨")
    print("=" * 40)
