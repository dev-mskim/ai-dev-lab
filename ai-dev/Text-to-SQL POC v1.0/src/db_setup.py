"""
샘플 ERP DB 생성 스크립트
실행: python src/db_setup.py
결과: data/sample.db 파일 생성
"""

from sqlalchemy import create_engine, text

# ─────────────────────────────────────────
# DB 연결 (Spring의 DataSource 설정과 동일)
# ─────────────────────────────────────────
engine = create_engine("sqlite:///data/sample.db", echo=False)


def create_tables():
    """테이블 생성 (Spring의 schema.sql 역할)"""
    with engine.begin() as conn:

        # 고객 테이블
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS CUSTOMERS (
                CUSTOMER_ID   INTEGER PRIMARY KEY AUTOINCREMENT,
                NAME          TEXT    NOT NULL,
                EMAIL         TEXT,
                REGION        TEXT,
                CREATED_AT    TEXT    DEFAULT (DATE('now'))
            )
        """))

        # 상품 테이블
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS PRODUCTS (
                PRODUCT_ID    INTEGER PRIMARY KEY AUTOINCREMENT,
                PRODUCT_NAME  TEXT    NOT NULL,
                CATEGORY      TEXT,
                UNIT_PRICE    REAL    NOT NULL
            )
        """))

        # 주문 테이블
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ORDERS (
                ORDER_ID      INTEGER PRIMARY KEY AUTOINCREMENT,
                CUSTOMER_ID   INTEGER NOT NULL,
                ORDER_DATE    TEXT    NOT NULL,
                STATUS        TEXT    DEFAULT 'COMPLETE',
                FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMERS(CUSTOMER_ID)
            )
        """))

        # 주문 상세 테이블
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
                ITEM_ID       INTEGER PRIMARY KEY AUTOINCREMENT,
                ORDER_ID      INTEGER NOT NULL,
                PRODUCT_ID    INTEGER NOT NULL,
                QUANTITY      INTEGER NOT NULL,
                AMOUNT        REAL    NOT NULL,
                FOREIGN KEY (ORDER_ID)   REFERENCES ORDERS(ORDER_ID),
                FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID)
            )
        """))

    print("[OK] 테이블 생성 완료")


def insert_sample_data():
    """샘플 데이터 입력 (Spring의 data.sql 역할)"""
    with engine.begin() as conn:

        # 이미 데이터가 있으면 중복 삽입 방지
        count = conn.execute(text("SELECT COUNT(*) FROM CUSTOMERS")).scalar()
        if count > 0:
            print("[SKIP] 샘플 데이터 이미 존재함")
            return

        # 고객 데이터
        conn.execute(text("""
            INSERT INTO CUSTOMERS (NAME, EMAIL, REGION) VALUES
            ('홍길동', 'hong@example.com', '서울'),
            ('김철수', 'kim@example.com',  '부산'),
            ('이영희', 'lee@example.com',  '서울'),
            ('박민준', 'park@example.com', '대구'),
            ('최지은', 'choi@example.com', '서울'),
            ('정수현', 'jung@example.com', '인천'),
            ('강동원', 'kang@example.com', '서울'),
            ('윤아름', 'yoon@example.com', '광주')
        """))

        # 상품 데이터
        conn.execute(text("""
            INSERT INTO PRODUCTS (PRODUCT_NAME, CATEGORY, UNIT_PRICE) VALUES
            ('노트북 Pro',   '전자기기', 1500000),
            ('무선 마우스',  '전자기기',   35000),
            ('기계식 키보드','전자기기',   89000),
            ('모니터 27인치','전자기기',  450000),
            ('USB 허브',     '전자기기',   25000),
            ('사무용 의자',  '가구',      350000),
            ('책상',         '가구',      280000),
            ('스탠딩 책상',  '가구',      520000)
        """))

        # 주문 데이터 (2025년 12월 ~ 2026년 3월)
        conn.execute(text("""
            INSERT INTO ORDERS (CUSTOMER_ID, ORDER_DATE, STATUS) VALUES
            (1, '2026-03-01', 'COMPLETE'),
            (2, '2026-03-05', 'COMPLETE'),
            (3, '2026-03-10', 'COMPLETE'),
            (1, '2026-03-15', 'COMPLETE'),
            (4, '2026-03-18', 'COMPLETE'),
            (5, '2026-03-20', 'PENDING'),
            (6, '2026-02-10', 'COMPLETE'),
            (7, '2026-02-15', 'COMPLETE'),
            (8, '2026-02-20', 'COMPLETE'),
            (2, '2026-01-05', 'COMPLETE'),
            (3, '2026-01-12', 'COMPLETE'),
            (1, '2025-12-24', 'COMPLETE')
        """))

        # 주문 상세 데이터
        conn.execute(text("""
            INSERT INTO ORDER_ITEMS (ORDER_ID, PRODUCT_ID, QUANTITY, AMOUNT) VALUES
            (1,  1, 1, 1500000),
            (1,  2, 2,   70000),
            (2,  3, 1,   89000),
            (3,  4, 1,  450000),
            (3,  5, 2,   50000),
            (4,  6, 1,  350000),
            (5,  7, 1,  280000),
            (5,  2, 1,   35000),
            (6,  8, 1,  520000),
            (7,  1, 1, 1500000),
            (7,  3, 1,   89000),
            (8,  4, 1,  450000),
            (9,  5, 3,   75000),
            (10, 1, 1, 1500000),
            (11, 6, 1,  350000),
            (12, 7, 1,  280000)
        """))

    print("[OK] 샘플 데이터 입력 완료")


def verify_data():
    """데이터 확인 (정상 입력 여부 검증)"""
    with engine.connect() as conn:
        tables = ["CUSTOMERS", "PRODUCTS", "ORDERS", "ORDER_ITEMS"]
        print("\n[데이터 확인]")
        for table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table}: {count}건")

        # 샘플 쿼리: 이번 달 매출 합계
        result = conn.execute(text("""
            SELECT SUM(oi.AMOUNT) AS 총매출
            FROM ORDER_ITEMS oi
            JOIN ORDERS o ON oi.ORDER_ID = o.ORDER_ID
            WHERE o.ORDER_DATE LIKE '2026-03%'
        """)).scalar()
        print(f"\n  [샘플 쿼리] 2026년 3월 총매출: {result:,.0f}원")


if __name__ == "__main__":
    print("=" * 40)
    print(" 샘플 DB 생성 시작")
    print("=" * 40)
    create_tables()
    insert_sample_data()
    verify_data()
    print("\n[완료] data/sample.db 생성됨")
    print("=" * 40)
