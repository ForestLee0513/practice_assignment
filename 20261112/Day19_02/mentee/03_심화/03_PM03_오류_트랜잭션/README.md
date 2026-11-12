# PM03 · 실패한 요청에서도 데이터 보호

IntegrityError·rollback·503을 구분하고 실패 뒤 데이터 보존을 확인합니다.

## 시작
- DB: `day19_crud_h`
- `.env.example` → `.env`, `DB_PASSWORD` 수정
- 서버: `python -m uvicorn app.main:app --reload`
- 문서: `http://127.0.0.1:8000/docs`

## TODO
- 코드 TODO 없음. 실제 데이터로 시나리오를 수행합니다.

## 완료 기준
1. 422 요청에서 DB가 바뀌지 않습니다.
2. DB 제약 실패 뒤 rollback되어 Session이 복구됩니다.
3. DB 연결 실패와 일반 API 오류를 구분합니다.

## DB 제약 위반과 409 응답 흐름

```text
DB 제약 위반으로 IntegrityError 발생
→ transaction(db)가 rollback 후 예외를 다시 전달
→ Service의 except IntegrityError에서 _raise_conflict(exc) 호출
→ 제약조건 이름으로 응답 메시지 선택
→ DataConflictError 발생
→ main.py의 conflict_handler가 JSON 본문과 HTTP 409 반환
```

- `_constraint_name()`은 일반 속성명이 아니라 위반한 DB 제약조건 이름을 추출합니다. 예를 들어 `categories_name_key`는 분류 이름의 유일성 제약조건입니다.
- 딕셔너리의 `.get(name, "Database constraint conflict")`는 등록된 이름에 대응하는 메시지를 선택합니다. 이름을 추출하지 못하거나 등록되지 않은 이름이면 기본 메시지를 사용합니다.
- `raise DataConflictError(safe) from exc`는 선택한 메시지로 예외를 발생시키면서 원래 `IntegrityError`를 원인 예외로 연결합니다. 이 줄 자체가 HTTP 응답을 만드는 것은 아닙니다.
- HTTP 응답 변환은 `@app.exception_handler(DataConflictError)`로 등록한 처리기가 담당합니다.
- `transaction(db)`는 블록 정상 종료 시 commit하고, 예외 발생 시 현재 트랜잭션의 미확정 변경을 rollback합니다. 오류 응답을 확인할 때 실제 데이터가 보존되는지도 함께 확인합니다.

## /health가 확인하는 범위

`GET /health`는 DB 연결을 얻고 `SELECT 1`을 실행합니다. 두 작업이 성공하면 다음 JSON을 반환합니다.

```json
{"status": "ok", "database": "reachable"}
```

DB 연결 실패 등의 `OperationalError`는 `HTTPException(503, "Database unavailable")`로 변환합니다. `from exc`는 원래 예외를 원인으로 연결합니다. 모든 예외를 503으로 변환하는 처리는 아니며, 다른 API 경로에 자동으로 적용되는 처리도 아닙니다.

| 상황 | 응답 |
| --- | --- |
| 요청 데이터가 입력 스키마를 만족하지 않음 | 422 |
| 조회한 지식이 없음 (`KnowledgeNotFoundError`) | 404 |
| CRUD에서 DB 제약 위반을 `DataConflictError`로 변환 | 409 |
| `/health`에서 `OperationalError` 발생 | 503 |

`SELECT 1` 성공은 기본 연결과 SQL 실행 가능 여부를 뜻합니다. 테이블 구조, CRUD 권한, 모든 API의 정상 동작까지 보장하지는 않습니다.
