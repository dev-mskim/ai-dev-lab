# API 명세서 (함수 명세)

> 최초 작성: 2026-03-26
> 대상: 내부 모듈 함수 명세 (ERP 연동 시 REST API 명세로 확장 예정)

---

## 모듈 구조

```
src/
├── db_setup.py       DB 초기화 모듈
├── schema_loader.py  Vector DB 모듈
├── sql_generator.py  핵심 로직 모듈  (4단계 예정)
└── app.py            웹 UI 모듈      (5단계 예정)
```

---

## db_setup.py

### `create_tables()`
```
설명   : 테이블이 없을 경우 생성
입력   : 없음
출력   : 없음
부작용 : data/sample.db 에 테이블 생성
```

### `insert_sample_data()`
```
설명   : 샘플 데이터 삽입 (이미 있으면 스킵)
입력   : 없음
출력   : 없음
부작용 : CUSTOMERS, PRODUCTS, ORDERS, ORDER_ITEMS 에 데이터 삽입
```

### `verify_data()`
```
설명   : 테이블별 건수 및 샘플 쿼리 결과 출력
입력   : 없음
출력   : 콘솔 출력
```

---

## schema_loader.py

### `load_schema()`
```
설명   : 테이블 스키마 정보를 ChromaDB에 저장
입력   : 없음
출력   : ChromaDB Collection 객체
부작용 : vectordb/ 폴더에 스키마 저장
주의   : 기존 컬렉션 삭제 후 재생성 (초기화)
```

### `search_schema(collection, query, n_results)`
```
설명   : 자연어 질문과 관련된 스키마 검색
입력
  - collection : ChromaDB Collection 객체
  - query      : 사용자 자연어 질문 (str)
  - n_results  : 반환할 스키마 수 (int, 기본값 2)
출력   : 관련 스키마 텍스트 (str)

사용 예)
  search_schema(col, "이번 달 매출 알려줘", n_results=2)
  → "테이블명: ORDERS ... 테이블명: ORDER_ITEMS ..."
```

---

## sql_generator.py (4단계 작성 예정)

### `generate_sql(question)`
```
설명   : 자연어 질문을 SQL로 변환
입력
  - question : 사용자 자연어 질문 (str)
출력   : 생성된 SQL 문자열 (str)
```

### `execute_query(sql)`
```
설명   : SQL 실행 후 결과 반환
입력
  - sql : 실행할 SQL 문자열 (str)
출력   : 쿼리 결과 (list of dict)
예외   : SELECT 외 쿼리 시 차단
```

### `summarize_result(question, sql, result)`
```
설명   : 쿼리 결과를 자연어로 요약
입력
  - question : 원래 사용자 질문 (str)
  - sql      : 실행된 SQL (str)
  - result   : 쿼리 결과 (list of dict)
출력   : 자연어 요약 문자열 (str)
```

### `ask(question)` ← 통합 함수
```
설명   : 위 3개 함수를 순서대로 실행하는 통합 함수
입력
  - question : 사용자 자연어 질문 (str)
출력   : dict
  {
    "sql"     : 생성된 SQL,
    "result"  : 쿼리 결과,
    "answer"  : 자연어 요약
  }
```

---

## ERP 연동 시 REST API 설계 (7단계 예정)

```
POST /api/chat
Content-Type: application/json

Request Body:
{
  "question": "이번 달 매출 TOP 5 고객 알려줘",
  "user_id": "admin"
}

Response Body:
{
  "answer": "이번 달 매출 1위는 홍길동(150만원)입니다...",
  "sql": "SELECT ...",
  "result": [...]
}
```
