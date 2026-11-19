# 외부 파일에서 RAG를 위한 Vector화 과정

## 전체 흐름

```
원본 파일 -> Parse -> Chunk (+ Validation) -> E5 -> pgvector -> Retrieval
```

## Document Collection (순서도 상 `원본 파일`)

- 외부 데이터를 Chunking 후 Vector DB에 넣는 과정
- Client (Front-end) 를 통해서 넣는게 아닌 데이터 사이언티스트가 별도의 경로를 통해 데이터 추가

## Document Parsing (순서도 상 `Parse`)

### Parsing과 Text Extraction의 차이

- Parsing: PDF/HTML 등 임의의 파일의 형식을 읽고 구조와 내용을 처리 가능한 객체로 변환
- Text Extraction: Parsing된 객체에서 텍스트만 추출
- PDF의 경우 화면 배치가 텍스트 순서를 보장하지 않음 (주로 논문 / 계약서 등)
- PDF 파싱 시 스캔본인지, OCR이 적용된 결과물인지 확인
- 파일별 결과(PDF, HTML, DOCX 등)가 다르더라도 DB에는 동일한 Column 형식에 맞춰 저장

### 정규화

정규화는 문자를 줄이는 과정이 아닌 검색에 방해되는 형식 상의 요소를 줄이면서 제목, 본문 등의 내용을 유지하는 과정

#### CRLF / LF / CR

각 운영체제 별 줄바꿈을 제어하는 표현 문자

- CRLF: Windows에서 사용되는 줄바꿈 문자
- LF: Unix/Linux에서 사용되는 줄바꿈 문자
- CR: Mac에서 사용되는 줄바꿈 문자

#### NFC와 NFKC

- NFC (Normalization Form C / Canonical Decomposition Canonical Composition): Unicode에서 동등한 표현을 분해 후 가능하면 다시 조합하는 방식 - 특수 문자 유지
- NFKC (Normalization Form KC / Compatibility Decomposition + Canonical Composition): 정준 등가 뿐만이 아닌 호환 문자의 문자도 분해 후 다시 조합하는 방식 - 특수 문자 치환
- 요약: NFC는 느슨한 정규화 NFKC는 엄격한 정규화
  - 일반적으로 수식은 NFC, 본문은 NFKC를 적용하지만 상황에 따라 유동적으로 적용해야 함.

#### Offset / Span

- Clean 이후 Offset은 원본 파일 바이트 위치가 아님
- Offset: 기준 문자열에서 문자 위치
- Span 시작과 끝을 표시한 연속 구간

### 정제 규칙 / 해시 / 길이 변화 기록

- Idempotency: 같은 입력에 같은 함수를 다시 적용해도 결과가 달라지지 않는 성질
- Clean_hash: 정제된 문자열을 UTF-8로 변환 후 계산한 해시 / Raw(원본)에서 해시로 변환한 값과 다름

## Chunking Strategies (순서도 상 `Chunk`)

- Chunk: 검색과 출처의 기본 단위
- 주요 Chunking Strategies를 비교

### Structure-aware vs Token-based

- Structured-aware: Heading / 문단 / 목록 / 표 경계를 우선하는 분할
- Token based: 모델 Tokenizer가 세는 길이로 상한을 정함

### Sementic Chunking

- Semantic Chunking: 문장 / 문단 임베딩 등의 임의 변환 정보를 이용해 경계를 정하는 접근
- 추가 모델 계산, 검증 필요

### Overlap

- Overlap을 하는 이유: LLM이 잘린 문장 단위에서 문맥을 파악하기 위함
  - 예시: 100자 기준 Chunk size = 40 중 10 ~ 20% 내외를 Overlap으로 지정
- Overlap 적용 시 +- 단위로 padding 적용할 것
- Overlap의 수와 중복량 / 필요 조건의 연결을 함께 비교
- yield를 통해 Generator(aka Iterator)롤 변환해 함수 종료에 조건을 붙여 Character Chunker 생성
  - 재귀함수 + 조건으로 이해하면 편할 듯 함.
  - 해당 개념에 대해서 추가적으로 비동기, 코루틴을 알고 있으면 이해하기 편할 듯 함.
- Chunk 이후 E5 적용 시 Chunking Window, Structured-aware Chunking 기준으로 모델 가동
  - 모델에 따라 다르지만 제목과 본문을 같이 넣을 때와 본문만 넣었을 때 vector가 완전히 달라짐

## Chunking Validation (순서도 상 `Chunk`)

- 검색 가능한 Chunk가 되려면 검증 통과 할 것 (if문 제어, try except 까진 잘 사용 안함)
- 중간 span(text)을 clean unit과 대조 (문자 구간 검증)

### Coverage vs Duplicate

- Coverage
  - 고유한 문자 위치 계산
  - Clean unit이 덮인 위치의 합집합 비율
  - 구간 병합으로 계산
- Duplicate
  - 같은 chunk_id / 같은 구간이 잘못 반복 생성되는 문제
  - 해당 문제를 제거하는 것을 집중해야 함.
- 검증 실패를 원인 별로 분석
- 인덱싱 전 검증 결과표를 만들고 검증 완료 시 Vector DB에 추가
- 조건과 결과가 같은 Chunk에 있어야 함 - 구조 검사 통과 만으로 검색 질문에 필요한 의미가 모두 남은게 아님

## Embedding (순서도 상 `E5`)

### Sementic Search의 필요성

- 기존 Context / LLM Client의 계약 유지, 지식 선택을 Embedding 검색으로 확장

### Embedding의 표현 방식

- 학습된 모델(이 문서에선 E5)이 텍스트를 정해진 차원의 실수 배열로 전환
- 쿼리가 같아도 passage가 다르면 완전히 다른 벡터로 반환
- 입력토큰과 임베딩 shape는 구분
- vector DB 저장 전 차원 개수, vector 값 유효한지 검증 (nan, inf 등 제거)
- **shape가 같다고 원문과 잘 연결 되었다는 보장은 없음**

## pgvector indexing pipeline (순서도 상 `pgvector`)

- indexing pipeline: 문서 수집부터 검증 / embedding / 저장 공개의 일련의 과정
- db index: 저장된 행을 빠르게 찾도록 돕는 자료구조
- 문서 / 버전 / chunk를 postgreSQL(RDB)에 저장함
  - 단, 파일이 클 경우 별도의 스토리지 서버 구축 후 경로를 RDB에 저장 (예시: 논문)
- 검증 통과된 chunk 만 E5를 통해 임베딩
- pipeline 버전 변경 시 기존 offset / vector는 변경됨 (기존 내용은 별도로 보관)
- 반영할 데이터가 최종적으로 COMMIT 돼야 이후 사용 가능 - 그 전에는 아무리 불러오려 해도 못 부름
- 버전 변경 = 임베딩 값 갱신
- 위 내용을 기반으로 Rretrieval 시 Top-k 수치를 내서 최종적으로 연관도 반환

## E2E(End-to-End) Test

간단하다. 위 내용을 모두 처음부터 끝까지 돌려보는거다.  
단, 문서 처리와 인프라 연결 실패만 구분하자.
