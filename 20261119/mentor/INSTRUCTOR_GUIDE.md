# 강사용 운영·해설 가이드 · 11월 19일

## 공통 운영 방침

- **수업 목표:** 실제 Document Ingestion Pipeline에서 원문을 검색 가능한 Chunk와 출처·버전으로 처리하는 능력입니다.
- **난이도 선택:** Basic / Intermediate / Advanced 중 하나만 수행합니다. 단원별 TODO는 2 / 4 / 6개입니다.
- **실습 간 독립성:** 각 폴더에 실행 가능한 Main Entry가 있으며, 앞선 과제가 미완성이더라도 coursekit Checkpoint를 사용합니다.
- **교사 설명:** 실행 전 입력·출력, 정상/실패 경로, 원문 보존 이유를 확인합니다.
- **난이도 통제:** Advanced는 테스트·보안 범위·버전 관리·Transaction처럼 실무 기능이 늘어나는 것이지 임의의 복잡한 파일 수를 요구하지 않습니다.
- **DB/모델:** Day23의 E5-small / pgvector 계약을 재사용합니다. 실제로 실행하지 않은 E5 토큰·벡터·검색 점수를 예상값처럼 표시하지 않습니다.
- **복습 연결:** 11/16의 `KnowledgeAnswer.source_ids: list[int]`와 11/20의 RAG를 이어줍니다. `chunk_id: str`과 `citation_id: int` 매핑을 설명합니다.
- **비밀 보호:** `.env`·DB 비밀번호를 공유하지 않습니다. 오류를 재현하려고 운영 DB를 강제로 중단하지 않습니다.

## 8교시 학습 및 확인 목표

| 교시 | 개념 질문 | Basic 필수 | Intermediate 확장 | Advanced 현업 확인 |
|---|---|---|---|---|
| 01 Collection | 왜 `read_bytes`와 raw hash를 구분할까? | 바이트 수·ID·SHA-256 | 다중 파일·unsupported | 변경 탐지·Manifest 불변성 |
| 02 Parsing | PDF에 텍스트가 없으면 곧 OCR인가? | UTF-8·ParsedUnit | 형식별 Parser | 페이지·HTML 표·오류 격리 |
| 03 Cleaning | NFC/NFKC가 무엇을 바꿀까? | LF·공백 보존 | Unicode·Audit | 구조별 정제·멱등·회귀 |
| 04 Chunking | Overlap과 384차원은 무슨 관계인가? | 문자 창 71자 | 문서별 Span·E5 길이 | 구조 경계·Token 한도·재분할 |
| 05 Validation | Coverage 100%면 완전한 파싱인가? | Span·본문 대응 | 누락·반복·Duplicate | Gate·Quarantine·회귀 |
| 06 Metadata | 왜 버전과 출처를 별도로 둘까? | category 선택 | 공개 버전·Locator | 권한·정수 Citation Mapping |
| 07 Indexing | UPSERT만으로 오래된 Chunk가 지워지나? | 저장·검색 Contract | Stage→Publish→Top-k | Transaction Rollback·새 판 전환 |
| 08 Integration | 무엇이 실제로 완료됐는가? | TXT 한 건 준비 | 6개 입력 상태 보고 | E5·pgvector·실패 복구 Report |

## 자료와 기대 조건

- 가상 출석·과제·시설·상담 4건의 텍스트 파싱 정상 결과, 스캔 PDF `needs_ocr`, 미지원 `.xyz`를 반드시 분리합니다.
- `career.pdf`는 실제 2페이지 텍스트 PDF, `scan.pdf`는 이미지 1페이지로 만들어졌습니다. OCR은 실행하지 않았습니다.
- `expected/offline_reference_*.json`은 동일한 **DB 미접속 기본 실행**의 mentor 기준 자료입니다.
- `tools/check_environment.py`는 모듈의 설치 여부만 조회하며, 모델 다운로드/DB 연결 성공이라고 말하지 않습니다.
- 07·Advanced 08의 `--live-db`는 수강생 개인 PC에서 확인합니다. 이 패키지 제작 환경에서는 PostgreSQL 연결 및 E5 실제 실행은 수행하지 못했습니다.

## 단계별 실무 관점

**1. 원문 보존:** file URI와 doc_id를 분리하고 raw_sha256로 바이트 변경을 추적합니다. 해시가 맞는다고 사실·권한까지 검증된 것은 아닙니다.

**2. Parsing 검수:** HTML은 지정한 main 아래에서 script/nav를 제외합니다. 표는 헤더-셀 대응을 유지합니다. PDF는 페이지마다 raw_text·page_number·locator를 보존하고 사람이 원문을 확인합니다.

**3. Cleaning 정책:** 일반 본문에만 가로 공백/CRLF/NFC 정리를 적용합니다. 코드와 표의 원래 구조를 함부로 바꾸지 않습니다. NFKC는 문서 기호 정보를 바꿀 수 있으므로 Default를 NFC로 둡니다.

**4. Chunking:** Character Window는 원리 설명에 유용하지만 문장과 표를 자를 수 있습니다. Advanced는 구조 경계를 우선한 다음 긴 부분을 재분할합니다. 실제 E5의 Tokenizer로 전체 `passage: ` 입력을 검사합니다.

**5. Validation:** Span의 문자열 일치와 Coverage 합집합은 다른 검증입니다. overlap으로 저장량이 늘어나는 것과 같은 chunk_id의 중복 저장을 구별합니다.

**6. Metadata:** Category만으로 접근 권한을 보호하지 않습니다. 실제 권한은 서버가 인증한 allowed_doc_ids와 결합해야 합니다. 현재 포인터는 원문 판과 처리 판 쌍을 가리킵니다.

**7. Indexing:** 로컬 E5는 CPU로 한 번만 로드해 사용하고 벡터를 미리 검증합니다. 짧은 DB Transaction으로 Stage/Publish합니다. 07 실습끼리 데이터가 섞이지 않도록 서로 다른 Schema를 사용합니다.

**8. Daily Project:** 11/19 완료 산출물은 검증된 Chunk·Embedding·Locator이며, 11/20에서 그 결과를 Retriever·Context Builder·OpenAI API에 연결합니다. 오늘은 LLM 답변을 만들지 않습니다.

## 검수 방법

```bash
python tools/check_environment.py
python tools/run_offline_all.py
# 24개 모든 실습 폴더 각각:
python -m pytest -q tests
```

실제 모델/DB 경로는 별도로 07과 Advanced 08을 선택하여 `python main.py --live-db`를 실행하고, DB의 포인터·Chunk 본문·원문 버전을 직접 대조합니다. 실행 전후에 운영/기존 수업용 테이블을 삭제하지 않습니다.

## 수강생 질문에 답하는 방법

- **“Coverage가 100%인데 왜 답을 못하죠?”** → Coverage의 기준은 이미 정제된 텍스트입니다. 파싱 전 누락, 검색 후보, 질문에 필요한 조건 분리 여부를 확인합니다.
- **“384차원이면 384토큰인가요?”** → 아니요. 차원은 출력 벡터의 좌표 수이며 입력 한도는 모델의 실제 Tokenizer 설정으로 확인합니다.
- **“PDF 문자열이 비어 있으면 무조건 OCR인가요?”** → 아니요. 빈 페이지, 이미지, 암호화, 파서 오류 등 원인을 구분합니다.
- **“`pip install pgvector`만 하면 SQL이 실행되나요?”** → 아니요. PostgreSQL 서버 확장 설치와 현재 DB의 `CREATE EXTENSION`이 별개입니다.
- **“왜 Stage와 Publish를 분리하나요?”** → 긴 처리 중 실패해도 이전 정상 버전이 검색되도록 하고, 검증된 새 판만 원자적으로 공개하기 위함입니다.
- **“다음 날 RAG가 문자열 Chunk ID를 JSON의 source_ids에 넣어도 되나요?”** → 이 수업의 `source_ids`는 양의 정수 목록이므로 DB의 `citation_id`를 사용하고 원래 Chunk ID와 Mapping을 유지합니다.
