# 심화 03. 키·DDL 흐름과 수정 기록

아래 결과는 제공된 초기 데이터(S0)와 실습 SQL 기준 예상값이며 실제 DB 실행 결과는 아닙니다.

## 실행 전 알아둘 점

- 현재 연결한 DB가 개인 학습 DB인지 확인합니다. `SELECT current_database()`는 현재 DB를 조회하며 다른 DB로 연결을 바꾸지는 않습니다.
- `--` 뒤는 주석입니다. `@step`과 `TODO`도 주석 안에서는 실행되지 않습니다. 반면 `__TODO_TABLE__`처럼 SQL 본문에 남은 토큰은 실제 이름으로 바꿔야 합니다.
- 한 `@step` 구간씩 선택 실행합니다.

schema → seed → checks는 같은 DB 세션에서 이어 실행합니다.

실행 순서: `schema/03_try_ddl.sql` → `seed/03_try_seed.sql` → `checks/03_try_verify.sql`.

### 1. 트랜잭션 시작

schema 파일은 연결 DB를 검사하고 `BEGIN;`으로 트랜잭션을 시작합니다. 이후 생성과 입력을 한 묶음으로 진행하고 마지막에 취소합니다. 이 예제의 `CREATE TABLE`과 `INSERT`는 PostgreSQL에서 롤백할 수 있습니다.

### 2. 부모 테이블 생성

```sql
CREATE TABLE public.categories_try (
  id INTEGER PRIMARY KEY,
  name VARCHAR(30) NOT NULL UNIQUE
    CHECK (char_length(name) BETWEEN 1 AND 30)
);
```

- `id`: 분류 한 행을 식별하는 정수 기본 키. 중복과 NULL을 허용하지 않습니다.
- `VARCHAR(30)`: 분류명을 최대 30자로 제한합니다.
- `NOT NULL`: 분류명 누락을 막습니다.
- `UNIQUE`: 분류명 중복을 막습니다.
- `CHECK`: 글자 수가 1~30인지 확인하여 빈 문자열을 막습니다. 공백만 있는 문자열을 자동 제거하거나 금지하지는 않습니다.

먼저 부모 테이블을 만드는 이유는 다음 자식 테이블이 부모의 키를 참조하기 때문입니다.

### 3. 자식 테이블 생성과 외래 키

```sql
CREATE TABLE public.knowledge_try (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  category_id INTEGER NOT NULL
    REFERENCES public.categories_try(id)
    ON DELETE RESTRICT
);
```

`category_id` 열을 선언한 뒤 `REFERENCES`로 참조 대상을 지정하는 열 수준 외래 키 문법입니다. 줄바꿈은 문장을 끝내지 않으며 `ON DELETE RESTRICT`까지 같은 열의 선언에 포함됩니다.

`category_id = 1`을 저장하려면 부모 테이블에 `id = 1`이 있어야 합니다. `NOT NULL`까지 있으므로 각 지식은 반드시 하나의 분류를 참조합니다. 여러 지식이 같은 분류를 참조할 수 있으므로 관계는 **분류 1 : 지식 N**입니다. 지식이 하나도 없는 분류도 가능합니다.

`ON DELETE RESTRICT`는 해당 분류를 참조하는 지식이 있을 때 부모 분류의 삭제를 거부합니다. 부모를 지우면서 자식도 함께 지우는 동작은 아닙니다.

### 4. 부모부터 데이터 입력

```sql
INSERT INTO public.categories_try VALUES (1, '연습');
INSERT INTO public.knowledge_try VALUES (1, '안내', 1);
```

seed 파일은 같은 트랜잭션 안에서 부모를 먼저 입력하고 자식을 입력합니다. 첫 문장은 부모의 `(id, name)`, 두 번째는 자식의 `(id, title, category_id)` 순서입니다. 자식의 마지막 `1`이 부모의 `id = 1`과 연결됩니다. 이 실습에서는 ID를 직접 입력합니다.

### 5. 입력 결과 조회

```sql
SELECT * FROM public.knowledge_try ORDER BY id;
```

checks 파일에서 같은 세션의 아직 확정하지 않은 데이터를 조회합니다. 예상 결과는 `(1, '안내', 1)` 한 행입니다. 다른 세션에서는 커밋 전 생성한 테이블을 볼 수 없으므로 연결을 유지해야 합니다.

### 6. 생성과 입력 취소

```sql
ROLLBACK;
```

`BEGIN` 이후의 테이블 생성과 데이터 입력을 취소합니다. 이번 트랜잭션에서 새로 만든 두 `_try` 테이블은 사라집니다. 준비 단계에서 이미 커밋한 본 테이블 `categories`, `knowledge`는 이 취소 대상이 아닙니다.

### 7. 테이블이 사라졌는지 확인

```sql
SELECT to_regclass('public.categories_try') IS NULL AS parent_gone,
       to_regclass('public.knowledge_try') IS NULL AS child_gone;
```

`to_regclass()`는 해당 이름의 관계 객체를 찾고 없으면 NULL을 반환합니다. 정상적으로 취소됐다면 두 결과 모두 true입니다. `SELECT * FROM ...`로 없는 테이블을 직접 읽는 방식과 달리 존재 여부를 확인할 수 있습니다.

흐름: **BEGIN → 부모 생성 → 자식과 FK 생성 → 부모 입력 → 자식 입력 → 조회 → ROLLBACK → 두 테이블 부재 확인**.

## 3번 SQL 오류와 수정 기록

### 이번에 수정한 부분: IDENTITY만 있고 기본 키가 없었음

수정 전:

```sql
id INTEGER GENERATED ALWAYS AS IDENTITY,
```

수정 후:

```sql
id INTEGER PRIMARY KEY,
```

문제는 두 가지였습니다.

1. `IDENTITY`는 자동 번호 생성 기능이고 기본 키나 유일성 제약을 자동으로 추가하지 않습니다. 따라서 이 정의만으로는 자식 외래 키가 참조할 유일한 키가 마련되지 않습니다. 자식 테이블 생성 시 참조 대상의 유일성 제약이 없다는 오류가 발생할 수 있습니다.
2. seed 파일은 부모 ID를 `1`로 직접 입력합니다. `GENERATED ALWAYS AS IDENTITY`는 일반 INSERT에서 명시적 ID 입력을 거부하므로 seed 방식과도 맞지 않습니다. 과제 역시 자동 발급을 쓰지 않도록 안내합니다.

이 실습에서는 `INTEGER PRIMARY KEY`로 바꾸면 참조 가능한 기본 키가 생기고 seed의 직접 ID 입력도 가능합니다. 자동 번호가 필요한 별도 설계에서는 `IDENTITY PRIMARY KEY`를 사용할 수 있지만, 현재 seed와 과제 조건에는 해당하지 않습니다.

### 앞서 작성 중이던 외래 키 문법 오류

앞서 확인한 코드에는 다음 구문이 있었습니다.

```sql
category_id INTEGER NOT NULL
  category_id public.categories_try(id)
```

두 번째 `category_id`는 참조 관계를 선언하는 키워드가 아닙니다. 올바른 구문은 다음과 같습니다.

```sql
category_id INTEGER NOT NULL
  REFERENCES public.categories_try(id)
  ON DELETE RESTRICT
```

이번 수정 직전 파일에서는 이미 이 외래 키 구문과 삭제 정책이 올바르게 작성되어 있어 그대로 유지했습니다. 이번에 실제 변경한 SQL은 부모 `id` 정의 한 줄입니다.

### 오류 후 다시 실행하는 방법

`BEGIN` 이후 오류가 났다면 같은 세션에서 먼저 `ROLLBACK;`만 따로 실행합니다. 오류가 난 트랜잭션에서 나머지 SQL을 계속 실행하면 트랜잭션이 중단됐다는 후속 오류가 날 수 있습니다.

그다음 schema 파일의 연결 확인과 `BEGIN`부터 시작하여 schema → seed → checks를 순서대로 실행합니다. `_try` 테이블이 이전에 커밋되어 남아 있다면 이 흐름으로 없어지지 않으므로 기존 상태를 먼저 확인합니다. 이를 해결하려고 공통 테이블을 DROP하거나 준비 데이터를 초기화하지 않습니다.
