# 심화 01. 접속과 첫 SQL

아래 결과는 제공된 초기 데이터(S0)와 실습 SQL 기준 예상값이며 실제 DB 실행 결과는 아닙니다.

## 실행 전 알아둘 점

- 현재 연결한 DB가 개인 학습 DB인지 확인합니다. `SELECT current_database()`는 현재 DB를 조회하며 다른 DB로 연결을 바꾸지는 않습니다.
- `--` 뒤는 주석입니다. `@step`과 `TODO`도 주석 안에서는 실행되지 않습니다. 반면 `__TODO_TABLE__`처럼 SQL 본문에 남은 토큰은 실제 이름으로 바꿔야 합니다.
- 한 `@step` 구간씩 선택 실행합니다.

대상: `queries/01_connect.sql`

### 1. 접속한 DB 확인과 스키마 지정

처음의 `DO $guard$ ... $guard$;`는 이름을 붙인 문자열 안의 PL/pgSQL 블록을 한 번 실행합니다. `$guard$`는 블록 경계를 표시하는 구분자입니다.

```sql
IF current_database() !~ '^knowledge_lab(_[a-z0-9_]+)?$' THEN
  RAISE EXCEPTION '개인 knowledge_lab DB에 다시 접속하세요. 현재 DB: %', current_database();
END IF;
```

`!~`는 정규식과 일치하지 않는다는 뜻입니다. `knowledge_lab` 또는 `knowledge_lab_이름` 형태의 DB가 아니면 예외를 발생시켜 잘못된 연결임을 알립니다. 이름 검사만으로 DB의 용도나 안전성을 보장하지는 않습니다.

```sql
SET search_path TO public;
```

스키마를 생략한 이름을 찾을 때 사용할 검색 경로를 지정합니다. `public.knowledge`는 스키마와 테이블을 둘 다 명시한 이름입니다. 이 설정은 DB 연결을 변경하지 않습니다.

### 2. SQL 실행 가능 여부 확인

```sql
SELECT 1 AS connected;
```

서버가 SQL을 처리할 수 있는지 확인합니다. 테이블을 읽지 않고 숫자 `1`을 반환하며 결과 열의 이름은 `connected`가 됩니다. `AS`는 결과에 별칭을 붙입니다.

### 3. DB·사용자·서버 정보 확인

```sql
SELECT current_database() AS database_name;
SELECT current_user AS user_name, version() AS server_version;
```

첫 문장은 현재 DB, 두 번째는 현재 역할과 PostgreSQL 서버 버전을 반환합니다. DB명과 사용자는 실제 접속 환경에 따라 달라집니다.

### 4. 문자 인코딩 확인

```sql
SHOW client_encoding;
SELECT '한글 연결 확인' AS korean_text;
```

현재 연결의 클라이언트 인코딩을 확인하고 한글 문자열이 정상적으로 표시되는지 봅니다. 이 구간은 테이블에 데이터를 저장하지 않습니다.

흐름: **연결 DB 검사 → 검색 경로 설정 → 간단한 응답 확인 → 연결 정보 확인 → 한글 표시 확인**.
