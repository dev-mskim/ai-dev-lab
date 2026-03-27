# Text-to-SQL 챗봇 개발 진행률

> 마지막 업데이트: 2026-03-26

---

## 전체 진행률

```
환경 세팅    ████████████████████ 100% ✅
DB 구성      ████████████████████ 100% ✅
Vector DB    ████████████████████ 100% ✅
테스트       ████████░░░░░░░░░░░░  40% (1~3단계 완료)
핵심 로직    ████████████████████ 100% ✅
웹 UI        ████████████████████ 100% ✅
테스트       ░░░░░░░░░░░░░░░░░░░░   0%
Oracle 연동  ░░░░░░░░░░░░░░░░░░░░   0%
```

---

## 1단계. 환경 세팅 ✅ 완료

### 1-1. Python 환경
- [x] Python 3.10.0 설치 확인
- [x] 가상환경 생성 (`.venv/`)
- [x] pip 26.0.1 업그레이드

### 1-2. 패키지 설치
- [x] `anthropic 0.86.0` — Claude API SDK
- [x] `streamlit 1.55.0` — 웹 UI
- [x] `chromadb 1.5.5` — Vector DB
- [x] `SQLAlchemy 2.0.48` — DB 연결 (JPA 역할)
- [x] `sentence-transformers 5.3.0` — 텍스트 벡터 변환
- [x] `cx-Oracle 8.3.0` — Oracle 드라이버 (ERP 확장용)
- [x] `python-dotenv 1.2.2` — .env 파일 읽기

### 1-3. 프로젝트 구조
- [x] 폴더 구조 생성 (`src/`, `data/`, `vectordb/`)
- [x] `requirements.txt` 생성
- [x] `.env.example` 생성
- [x] `.gitignore` 생성
- [x] `GUIDE.md` 생성

### 1-4. API 키 설정
- [x] Claude API 키 발급 (https://console.anthropic.com)
- [x] `.env` 파일 생성 (`.env.example` 복사)
- [x] `.env` 에 API 키 입력

---

## 2단계. 샘플 DB 구성 ✅ 완료

> 파일: `src/db_setup.py`

- [x] SQLite 샘플 DB 생성 (`data/sample.db`)
- [x] `CUSTOMERS` 테이블 생성 및 샘플 데이터 입력
- [x] `PRODUCTS` 테이블 생성 및 샘플 데이터 입력
- [x] `ORDERS` 테이블 생성 및 샘플 데이터 입력
- [x] `ORDER_ITEMS` 테이블 생성 및 샘플 데이터 입력
- [x] DB 연결 및 데이터 조회 테스트

---

## 3단계. Vector DB 구성 ✅ 완료

> 파일: `src/schema_loader.py`

- [x] 테이블 스키마 정보 정의 (테이블명, 컬럼명, 설명)
- [x] 스키마 정보 임베딩 변환 (sentence-transformers)
- [x] ChromaDB에 스키마 저장 (`vectordb/` 폴더)
- [x] 유사 스키마 검색 테스트 ("매출" 검색 시 ORDERS 테이블 반환 확인)

---

## 4단계. 핵심 로직 구현

> 파일: `src/sql_generator.py`

- [ ] Claude API 연결 설정
- [ ] 자연어 → SQL 변환 함수 구현
- [ ] SQL 안전성 검증 (SELECT만 허용)
- [ ] DB 쿼리 실행 함수 구현
- [ ] 쿼리 결과 → 자연어 요약 함수 구현
- [ ] 단위 테스트 (터미널에서 직접 실행)

---

## 5단계. 웹 UI 구현

> 파일: `src/app.py`

- [ ] Streamlit 기본 화면 구성
- [ ] 채팅 입력창 구현
- [ ] 대화 히스토리 표시
- [ ] 생성된 SQL 쿼리 표시 (디버깅용)
- [ ] DB 결과 테이블 표시
- [ ] 자연어 답변 표시
- [ ] 로딩 스피너 (쿼리 생성 중 표시)

---

## 6단계. 통합 테스트

- [ ] 기본 질문 테스트: "전체 고객 목록 보여줘"
- [ ] 집계 질문 테스트: "이번 달 매출 TOP 5 고객 알려줘"
- [ ] 조인 질문 테스트: "홍길동 고객의 주문 내역 보여줘"
- [ ] 잘못된 질문 처리: "날씨 알려줘" (SQL 생성 불가 케이스)
- [ ] 위험 쿼리 차단 테스트: "모든 데이터 삭제해줘" (DELETE 차단 확인)

---

## 7단계. Oracle ERP 연동 (확장)

> 데모 완성 후 진행

- [ ] Oracle DB 접속 정보 확인
- [ ] `.env` 에 Oracle 연결 정보 추가
- [ ] DB 연결 설정 Oracle로 전환 (`sqlalchemy` 연결 문자열 변경)
- [ ] ERP 실제 테이블 스키마 수집
- [ ] 수집한 스키마 ChromaDB 재등록
- [ ] Oracle 환경에서 통합 테스트
- [ ] 보안 설정 (SELECT 전용 계정, 접근 테이블 제한)
- [ ] ERP 시스템에 REST API 형태로 연동

---

## 참고 명령어

```bash
# 가상환경 활성화 (작업 시작 전 항상 실행)
.venv\Scripts\activate

# 샘플 DB 생성 (2단계 완료 후)
python src/db_setup.py

# 스키마 Vector DB 저장 (3단계 완료 후)
python src/schema_loader.py

# 웹앱 실행 (5단계 완료 후)
streamlit run src/app.py
```
