# ERD (Entity Relationship Diagram)

> 최초 작성: 2026-03-26
> 대상 DB: SQLite (데모) → Oracle (ERP 확장 예정)

---

## 테이블 관계도

```
CUSTOMERS
│  CUSTOMER_ID (PK)
│  NAME
│  EMAIL
│  REGION
│  CREATED_AT
│
└──< ORDERS
       │  ORDER_ID (PK)
       │  CUSTOMER_ID (FK → CUSTOMERS)
       │  ORDER_DATE
       │  STATUS
       │
       └──< ORDER_ITEMS
              │  ITEM_ID (PK)
              │  ORDER_ID (FK → ORDERS)
              │  PRODUCT_ID (FK → PRODUCTS)
              │  QUANTITY
              │  AMOUNT
              │
              >── PRODUCTS
                     PRODUCT_ID (PK)
                     PRODUCT_NAME
                     CATEGORY
                     UNIT_PRICE
```

---

## 테이블 상세 정의

### CUSTOMERS (고객 테이블)

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| CUSTOMER_ID | INTEGER | PK, AUTO | 고객 고유번호 |
| NAME | TEXT | NOT NULL | 고객 이름 |
| EMAIL | TEXT | - | 이메일 주소 |
| REGION | TEXT | - | 지역 (서울, 부산, 대구 등) |
| CREATED_AT | TEXT | DEFAULT now | 등록일 (YYYY-MM-DD) |

---

### PRODUCTS (상품 테이블)

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| PRODUCT_ID | INTEGER | PK, AUTO | 상품 고유번호 |
| PRODUCT_NAME | TEXT | NOT NULL | 상품명 |
| CATEGORY | TEXT | - | 카테고리 (전자기기, 가구 등) |
| UNIT_PRICE | REAL | NOT NULL | 단가 (원 단위) |

---

### ORDERS (주문 테이블)

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| ORDER_ID | INTEGER | PK, AUTO | 주문 고유번호 |
| CUSTOMER_ID | INTEGER | FK | 고객번호 (CUSTOMERS 참조) |
| ORDER_DATE | TEXT | NOT NULL | 주문일 (YYYY-MM-DD) |
| STATUS | TEXT | DEFAULT 'COMPLETE' | 주문상태 (COMPLETE / PENDING) |

---

### ORDER_ITEMS (주문 상세 테이블)

| 컬럼명 | 타입 | 제약 | 설명 |
|--------|------|------|------|
| ITEM_ID | INTEGER | PK, AUTO | 주문상세 고유번호 |
| ORDER_ID | INTEGER | FK | 주문번호 (ORDERS 참조) |
| PRODUCT_ID | INTEGER | FK | 상품번호 (PRODUCTS 참조) |
| QUANTITY | INTEGER | NOT NULL | 구매 수량 |
| AMOUNT | REAL | NOT NULL | 구매 금액 (수량 × 단가) |

---

## 테이블 간 관계 요약

| 관계 | 설명 |
|------|------|
| CUSTOMERS : ORDERS | 1 : N (한 고객이 여러 주문 가능) |
| ORDERS : ORDER_ITEMS | 1 : N (한 주문에 여러 상품 포함 가능) |
| PRODUCTS : ORDER_ITEMS | 1 : N (한 상품이 여러 주문에 포함 가능) |

---

## 자주 쓰는 JOIN 패턴

```sql
-- 고객별 총 구매금액
SELECT c.NAME, SUM(oi.AMOUNT) AS 총구매금액
FROM CUSTOMERS c
JOIN ORDERS o      ON c.CUSTOMER_ID = o.CUSTOMER_ID
JOIN ORDER_ITEMS oi ON o.ORDER_ID = oi.ORDER_ID
GROUP BY c.NAME;

-- 상품별 판매량
SELECT p.PRODUCT_NAME, SUM(oi.QUANTITY) AS 총판매량
FROM PRODUCTS p
JOIN ORDER_ITEMS oi ON p.PRODUCT_ID = oi.PRODUCT_ID
GROUP BY p.PRODUCT_NAME;

-- 월별 매출
SELECT strftime('%Y-%m', o.ORDER_DATE) AS 월,
       SUM(oi.AMOUNT) AS 월매출
FROM ORDERS o
JOIN ORDER_ITEMS oi ON o.ORDER_ID = oi.ORDER_ID
GROUP BY 월
ORDER BY 월;
```

---

## Oracle 전환 시 변경 사항

| 항목 | SQLite | Oracle |
|------|--------|--------|
| AUTO INCREMENT | AUTOINCREMENT | SEQUENCE + TRIGGER |
| 날짜 형식 | TEXT (YYYY-MM-DD) | DATE 타입 |
| 날짜 필터 | `ORDER_DATE LIKE '2026-03%'` | `TO_CHAR(ORDER_DATE,'YYYY-MM') = '2026-03'` |
| 현재 날짜 | `DATE('now')` | `SYSDATE` |
