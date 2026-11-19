# 11월 20일 보고서 처리 Agent · 강사용 운영 안내

## 자료의 책임 분리

- `../common/`: 동일한 ERD·SRS·Postman·SQL·초기 데이터. 학생/강사 공통, 변경하지 않습니다.
- `01_basic/`: API-00~09 구현 정답. 명시적 Action Router이며 자율 LLM Agent와 구분합니다.
- `02_intermediate/`: Basic + API-10/11 + 카테고리별 Pydantic Detail + 구조화 요약·필터.
- `03_advanced/`: 전 단계 + API-12~14 + Revision 잠금·재색인·제한된 Tool Calling·검색 평가·실행 이력.
- 모든 난이도의 최종 디렉터리 역할은 동일하며, 실제 구현 범위가 다릅니다.

## 오전 100분 라이브 코딩을 위한 현실적인 진행 순서

1. **DB 0~25분**: 빈 프로젝트 폴더 생성, PG18.6 `report_agent_lab` DB 확인, `schema.sql`, `seed.sql` 실행, Count 6/180/60 확인.
2. **ORM·Session·E5 준비 25~40분**: 제공 ORM 매핑과 `app/main.py`, `get_db`를 확인하고 `embedding_client.encode`·`report_service.encode_overview`를 연결합니다. POST가 벡터도 생성하므로 이 어댑터는 CRUD보다 먼저 준비합니다.
3. **CRUD 40~62분**: 한 종류(Create 실험 보고서)부터 공통 CRUD 구현. Postman 생성→조회→수정→삭제 시험. ORM 전 종류 선언은 스크립트/기준 코드 활용 가능.
4. **일괄 색인·검색 62~78분**: 초기 개요 180건을 E5로 인덱싱하고 SQL로 ready·revision을 확인합니다. 이어 `query: ` 벡터 → pgvector cosine 검색 → Keyword 결합. '가중치'의 실제 후보를 조회해 관련성을 확인하고 ID를 고정 정답으로 삼지 않습니다.
5. **LLM 78~90분**: `.env`에 있는 키로 실제 요약. 유료 요청 최소 1건, API 실패 시 정해진 오류 응답.
6. **Agent 90~100분**: 명시적 `get_report` / `find_report` / `summarize_report`를 연결합니다. 마지막에는 검색 결과 ID로 조회·요약하고 `report_id/source_revision`을 대조합니다. `not_found`이면 요약하지 않습니다.

180은 초기 시드 기준입니다. CRUD 시연의 생성 데이터는 삭제하거나 추가 건수를 별도로 확인합니다. E5 어댑터 준비와 초기 데이터 일괄 색인을 구분해 설명합니다.

### 사전 준비 (100분 시간을 확보하는 필수 조건)

- Windows 11 PostgreSQL 18.6에 **pgvector extension 설치 완료**; DB 로그인 확인.
- `.venv` 의존 패키지 설치 완료, E5 모델 가중치 로컬 캐시, LLM API 키·모델 미리 확인.
- `sql/seed.sql`은 교사가 직접 타이핑하지 않고 제공본을 실행. 반복 SQL 작성에 시간을 쓰지 않습니다.
- 라이브 코딩 도중 꼬였을 때 Mentor 정답으로 Checkpoint를 복원하되, **직접 작성한 부분과 제공된 부분을 명확히 구분**합니다.

## 검수 절차

1. 선택한 mentor 디렉터리에서 자체 `.env.example`을 `.env`로 복사하고 DB·LLM 값을 설정합니다. `PROJECT_LEVEL`은 basic/intermediate/advanced 중 해당 단계여야 합니다. `python -c "from app.core.config import settings; print(settings.project_level)"`로 확인합니다.
2. `python -m app.main` 실행, `/health` 응답 200, DB/pgvector ready 확인.
3. `python scripts/index_overviews.py` 실행 후 SQL에서 초기 180건의 벡터·ready·최신 revision을 확인합니다. `/health`만으로 색인 완료를 판정하지 않습니다.
4. Postman Collection JSON/Environment JSON 가져오기; **무료 경로 우선** 실행, DB 조회로 저장 결과까지 검증.
5. 유료 요청 5개는 **별도 선택 폴더에서 수동** 실행합니다. Postman `allow_paid_llm=false`가 기본이며, 키·모델·비용 확인 후 필요한 요청을 실행할 때만 `true`로 바꾸고 다시 `false`로 돌립니다. 모델 미설정 503은 실패입니다.
6. `pytest -q`는 오프라인 구조/입력 검증, `RUN_LIVE_TESTS=1 pytest -q -m live`는 실제 DB 준비 후에만 실행(Advanced는 Rollback 포함).
7. Basic은 `common/data/search_cases.json`을 Postman으로 수동 확인하고 query·응답 ID·점수/threshold·관련성 근거를 기록합니다. Advanced는 `python scripts/evaluate_search.py`의 JSON·CSV 결과로 Recall@5와 오탐 사례를 검토합니다. 응용 이상 Keyword 점수는 제목 3 + 개요 2 + 본문 1의 일치 가중합이며 Semantic 점수와 구분합니다. Advanced의 LLM 재시도는 최대 2회이며 호출별 출력 상한과 사용량 집계 범위는 해당 README를 확인합니다. 실패 요청의 미확인 과금을 포함한 전체 비용을 보장하는 기능은 아닙니다.

## 자주 발생하는 오류와 원인

- `extension "vector" is not available`: pgvector Windows용 서버 확장이 아직 설치되지 않았음. Docker 사용하지 않음.
- `password authentication failed`: `.env`의 DATABASE_URL 계정·DB·비밀번호 또는 URL 인코딩 확인.
- `relation "reports" does not exist`: 잘못된 DB에 접속했거나 schema.sql을 실행하지 않았음.
- `ModuleNotFoundError: pgvector`: 현재 선택된 VS Code Python 인터프리터의 `.venv`와 requirements 설치 여부 확인.
- 최초 E5 다운로드가 오래 걸림: 수업 전에 캐시 확인; CPU `torch.set_num_threads(1)` 사용.
- `LLM_UNAVAILABLE`: OPENAI_API_KEY/LLM_MODEL 설정과 실제 네트워크·잔여 사용량을 확인.
- 유사도 검색이 무관한 보고서를 반환: E5 Score 0.75는 교육용 초기값; 테스트셋으로 Threshold 보정.

## 검수 완료/미완료 구분

- 이번 수정본의 검증 범위와 결과는 함께 제공한 재검수 기록을 기준으로 확인합니다. 이전 제작 당시의 테스트 통과 수를 이번 실행 결과로 사용하지 않습니다.
- SQLite 변환 검사와 테스트 더블은 데이터·함수 분기를 확인하는 보조 검증입니다. 실제 PostgreSQL·E5·LLM 통합 성공을 뜻하지 않습니다.
- **실제 Windows PostgreSQL 18.6·pgvector·E5 모델·LLM API 연동 통합 테스트는 미실행.** 강사 PC에서 완료 후 배포하세요.
- Mock 결과를 수강생에게 실제 모델 실행 성공으로 발표하지 않습니다.
