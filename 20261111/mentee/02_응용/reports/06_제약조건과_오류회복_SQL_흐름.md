# 응용 06. 제약조건과 오류 회복 SQL 흐름

대상: `sql/06_constraints.sql`. 현재 작성된 `ROLLBACK`과 `DELETE ... WHERE id = 1`은 실습 의도에 맞습니다. 아래는 파일과 제공 스키마에 따른 예상이며 실제 DB 오류 메시지를 확인한 기록은 아닙니다.

## 1. 목표와 시작 상태

이 실습은 의도적으로 잘못된 데이터를 입력하거나 참조 중인 부모를 삭제하여 제약조건이 동작하는지 확인합니다. 잘못된 SQL 문법이 아니라 **올바른 SQL이 데이터 규칙 위반으로 거부되는 것**을 확인합니다.

연결 검사 후 knowledge와 categories의 기존 행을 기록합니다. categories에 id -1이 없는지, learning이 존재하는지, id 1을 참조하는 지식이 있는지 확인합니다. 실제 상태가 다르면 아래 오류가 그대로 발생하지 않을 수 있습니다.

## 2. 각 실험의 공통 실행 순서

```text
BEGIN → 실패 SQL 한 건 실행 → 오류 코드·메시지 확인
→ ROLLBACK을 별도로 실행 → 다음 실험의 BEGIN
```

명시적 트랜잭션에서 오류가 나면 그 트랜잭션은 중단 상태가 됩니다. ROLLBACK 전 다른 일반 SQL을 실행하면 원래 오류 대신 `25P02`가 나타날 수 있습니다. 따라서 전체 파일을 한 번에 실행하지 않습니다.

## 3. 빈 본문: CHECK 위반

```sql
BEGIN;
INSERT INTO public.knowledge(title, content, category_id)
VALUES ('오류 확인', '', 1);
-- 오류를 확인한 뒤 별도 실행
ROLLBACK;
```

빈 문자열은 NULL이 아니므로 NOT NULL 검사를 통과하지만 길이는 0입니다. 본문 길이 1~2000 조건을 위반하여 `23514`를 기대합니다. 관련 제약 이름은 `knowledge_content_length`입니다.

## 4. 없는 분류: FOREIGN KEY 위반

```sql
BEGIN;
INSERT INTO public.knowledge(title, content, category_id)
VALUES ('오류 확인', '정상 본문', -1);
-- 오류 확인 후 별도 실행
ROLLBACK;
```

부모 categories에 id -1이 없다면 지식이 그 분류를 참조할 수 없습니다. `knowledge_category_fk` 위반으로 `23503`을 기대합니다.

## 5. 제목 누락: NOT NULL 위반

```sql
BEGIN;
INSERT INTO public.knowledge(title, content, category_id)
VALUES (NULL, '정상 본문', 1);
-- 오류 확인 후 별도 실행
ROLLBACK;
```

title은 필수이므로 NULL 입력이 거부됩니다. 예상 코드는 `23502`입니다. NULL과 빈 문자열은 별개의 값입니다.

## 6. 중복 분류명: UNIQUE 위반

```sql
BEGIN;
INSERT INTO public.categories(name) VALUES ('learning');
-- 오류 확인 후 별도 실행
ROLLBACK;
```

learning이 이미 있다면 분류명 중복 금지 규칙에 걸려 `23505`가 발생합니다.

## 7. 참조 중인 부모 삭제: RESTRICT 확인

```sql
BEGIN;
DELETE FROM public.categories
WHERE id = 1;
-- 오류 확인 후 별도 실행
ROLLBACK;
```

여기의 id는 삭제 대상인 **categories의 id**입니다. knowledge.id를 뜻하지 않습니다. `knowledge.category_id = 1`인 자식이 있으면 `ON DELETE RESTRICT` 때문에 부모 삭제가 거부되어 `23503`이 발생합니다. 자식이 없는 분류에서는 같은 오류를 기대할 수 없습니다.

## 8. 최종 확인

마지막 두 SELECT로 지식과 분류의 ID·내용·개수가 시작 전과 같은지 비교합니다. 오류 코드만 맞아도 데이터 검증을 생략하지 않습니다. 입력 실패로 시퀀스 번호가 소비될 수 있으며 ID가 건너뛰는 것은 데이터가 남았다는 뜻이 아닙니다.

| 위반 대상 | 예상 SQLSTATE |
|---|---|
| 본문 길이 CHECK | 23514 |
| 없는 분류 참조 | 23503 |
| 제목 NOT NULL | 23502 |
| 분류명 UNIQUE | 23505 |
| 참조 중인 부모 삭제 제한 | 23503 |

문법 오류 `42601`은 위 제약 실험의 성공으로 인정하지 않습니다.
