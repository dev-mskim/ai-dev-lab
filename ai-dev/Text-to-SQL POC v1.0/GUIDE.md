# Text-to-SQL 챗봇 개발 가이드

> Java/Spring Boot 개발자를 위한 단계별 안내서
> 작성일: 2026-03-26

---

## 목차

1. [프로젝트 구조](#1-프로젝트-구조)
2. [환경 요구사항](#2-환경-요구사항)
3. [환경 세팅](#3-환경-세팅)
4. [핵심 개념 정리](#4-핵심-개념-정리)
5. [단계별 구현](#5-단계별-구현)
6. [실행 방법](#6-실행-방법)
7. [Oracle ERP 연동 방법](#7-oracle-erp-연동-방법)
8. [자주 묻는 질문](#8-자주-묻는-질문)

---

## 1. 프로젝트 구조

```
ai-dev/
├── .venv/                  # Python 가상환경 (건드리지 않음)
├── src/
│   ├── db_setup.py         # 샘플 DB 생성 (SQLite)
│   ├── schema_loader.py    # 스키마 → Vector DB 저장
│   ├── sql_generator.py    # 자연어 → SQL 변환 (Claude API)
│   └── app.py              # Streamlit 웹앱 (메인)
├── data/
│   └── sample.db           # SQLite 샘플 DB 파일
├── vectordb/               # ChromaDB 저장 폴더
├── .env                    # API 키 설정 (Git에 올리면 안됨!)
├── requirements.txt        # 설치 패키지 목록
└── GUIDE.md                # 이 파일
```

---

## 2. 환경 요구사항

| 항목 | 버전 | 확인 명령어 |
|------|------|------------|
| Python | 3.10 이상 | `python --version` |
| pip | 최신 버전 | `pip --version` |
| VS Code | 최신 버전 | - |
| Claude API Key | - | https://console.anthropic.com |

---

## 3. 환경 세팅

### Step 1 - VS Code 설치

1. https://code.visualstudio.com 접속
2. Download for Windows 클릭 후 설치
3. VS Code 실행 후 왼쪽 Extensions 탭(Ctrl+Shift+X) 클릭
4. 아래 Extension 검색 후 설치:
   - `Python` (Microsoft 공식)
   - `Pylance`

### Step 2 - 프로젝트 폴더 열기

1. VS Code에서 `파일 > 폴더 열기`
2. `C:\Users\사용자명\Desktop\ai-dev-lab\ai-dev` 선택

### Step 3 - 가상환경 활성화

VS Code 하단 터미널(Ctrl+`) 열고 아래 명령어 입력:

```bash
# Windows
.venv\Scripts\activate

# 활성화 성공 시 터미널 앞에 (.venv) 표시됨
(.venv) C:\...\ai-dev>
```

> **Spring Boot 비유:** Maven/Gradle의 로컬 repository처럼,
> 가상환경은 이 프로젝트만의 독립된 패키지 설치 공간입니다.

### Step 4 - 패키지 설치 확인

```bash
pip list
```

아래 패키지가 보이면 성공:
- `anthropic`
- `streamlit`
- `chromadb`
- `sqlalchemy`
- `sentence-transformers`

### Step 5 - API 키 설정

프로젝트 루트에 `.env` 파일 생성 후 아래 내용 입력:

```
ANTHROPIC_API_KEY=sk-ant-여기에_발급받은_키_입력
```

> **API 키 발급:** https://console.anthropic.com 접속 > API Keys > Create Key

> **주의:** `.env` 파일은 절대 Git에 올리지 마세요! (비밀번호와 동일)

---

## 4. 핵심 개념 정리

### Spring Boot 개념과 비교

| AI 개발 개념 | Spring Boot 비유 |
|-------------|----------------|
| Claude API | 외부 REST API (WebClient로 호출) |
| 프롬프트(Prompt) | API 요청 Body |
| 토큰(Token) | API 요청 글자수 (비용과 직결) |
| Vector DB | 의미 기반 검색용 특수 DB |
| 임베딩(Embedding) | 텍스트를 숫자 배열로 변환한 것 |
| Streamlit | Thymeleaf 없이 Python만으로 만드는 웹 UI |
| SQLAlchemy | JPA/MyBatis (Python용 ORM) |
| `.env` 파일 | `application.properties` |

### 전체 동작 흐름

```
[사용자 입력] "이번 달 TOP 5 고객 알려줘"
       ↓
[ChromaDB] 관련 테이블/컬럼 검색
       → ORDERS(ORDER_DATE, AMOUNT), CUSTOMERS(CUSTOMER_ID, NAME)
       ↓
[Claude API] SQL 생성
       → SELECT c.name, SUM(o.amount)
         FROM customers c JOIN orders o ON c.id = o.customer_id
         WHERE DATE_FORMAT(o.order_date, '%Y-%m') = '2026-03'
         GROUP BY c.name ORDER BY SUM(o.amount) DESC LIMIT 5
       ↓
[Oracle/SQLite] SQL 실행 → 결과 반환
       ↓
[Claude API] 결과를 자연어로 요약
       ↓
[사용자] "이번 달 매출 TOP 5 고객은 홍길동(500만원), ..."
```

---

## 5. 단계별 구현

### Step 1 - 샘플 DB 생성 (`src/db_setup.py`)

```python
# 실행: python src/db_setup.py
# 결과: data/sample.db 파일 생성됨
```

- SQLite로 샘플 ERP 데이터 생성
- 테이블: CUSTOMERS, ORDERS, PRODUCTS, ORDER_ITEMS

### Step 2 - 스키마를 Vector DB에 저장 (`src/schema_loader.py`)

```python
# 실행: python src/schema_loader.py
# 결과: vectordb/ 폴더에 스키마 정보 저장됨
```

- 각 테이블/컬럼 설명을 ChromaDB에 저장
- 사용자 질문과 관련된 테이블을 빠르게 찾기 위한 사전 작업

### Step 3 - 웹앱 실행 (`src/app.py`)

```bash
# 실행
streamlit run src/app.py

# 브라우저 자동 오픈: http://localhost:8501
```

---

## 6. 실행 방법

```bash
# 1. 가상환경 활성화
.venv\Scripts\activate

# 2. 샘플 DB 생성 (최초 1회)
python src/db_setup.py

# 3. 스키마 Vector DB 저장 (최초 1회)
python src/schema_loader.py

# 4. 웹앱 실행
streamlit run src/app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 7. Oracle ERP 연동 방법

데모가 완성된 후 Oracle로 전환 시 변경할 부분:

### 7-1. Oracle 드라이버 설치

```bash
pip install cx_Oracle
# 또는 최신 버전
pip install oracledb
```

### 7-2. DB 연결 설정 변경

```python
# 현재 (SQLite)
engine = create_engine("sqlite:///data/sample.db")

# Oracle 전환 시
engine = create_engine(
    "oracle+cx_oracle://사용자:비밀번호@호스트:1521/서비스명"
)
```

### 7-3. 스키마 재등록

Oracle 테이블 목록을 ChromaDB에 다시 저장:

```python
python src/schema_loader.py
```

### 7-4. 보안 고려사항

ERP 연동 시 반드시 적용해야 할 사항:

- SELECT 쿼리만 허용 (INSERT/UPDATE/DELETE 차단)
- 사용자 권한별 접근 가능 테이블 제한
- 민감 컬럼 마스킹 (주민번호, 급여 등)
- API 키 환경변수 관리 (`.env` 파일 또는 Vault)

---

## 8. 자주 묻는 질문

**Q. Vector DB에는 어떤 데이터가 들어가나요?**
A. 실제 ERP 데이터(고객명, 금액 등)가 아닌, 테이블/컬럼 메타정보만 들어갑니다.
예: `"ORDERS 테이블: 주문 정보를 저장. 컬럼: ORDER_ID(주문번호), AMOUNT(금액)..."`

**Q. API 비용은 얼마나 드나요?**
A. Claude Sonnet 기준 질문 1회당 약 $0.001~0.003 (약 1~4원) 수준입니다.

**Q. 인터넷이 안되는 환경(폐쇄망)에서도 사용 가능한가요?**
A. Claude API는 인터넷 필요. 폐쇄망 환경은 온프레미스 LLM(Ollama 등) 검토 필요.

**Q. SQL이 잘못 생성되면 어떻게 되나요?**
A. DB 실행 오류 발생 시 에러 메시지를 사용자에게 보여줍니다.
향후 에러 발생 시 자동 재시도 기능(Agentic) 추가 가능.

---

## 참고 자료

- [Anthropic 공식 문서](https://docs.anthropic.com)
- [Streamlit 공식 문서](https://docs.streamlit.io)
- [ChromaDB 공식 문서](https://docs.trychroma.com)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org)
