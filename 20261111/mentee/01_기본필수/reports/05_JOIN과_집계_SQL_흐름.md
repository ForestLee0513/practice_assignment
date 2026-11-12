# 기본필수 05. JOIN과 집계 SQL 흐름

대상: `05_join.sql`. 사용자가 작성한 기본필수 05의 JOIN과 집계를 설명합니다. 실제 DB 실행 결과는 아니며, 결과는 초기 데이터 S0 기준입니다. 현재 사용자 SQL의 JOIN은 `k.id = c.id`이므로 분류 연결이 잘못될 수 있습니다. 원본은 사용자 작성 상태로 보존했고, 아래에는 올바른 관계인 `k.category_id = c.id`를 비교 예시로 기록합니다.

## 1. 연결과 관계 확인

처음의 안전 확인 블록은 개인 학습 DB인지 검사하고 `search_path`를 public으로 설정합니다. 본 실습은 기존 `public.categories`와 `public.knowledge`를 조회합니다.

분류의 기본 키는 `categories.id`, 지식이 분류를 가리키는 외래 키는 `knowledge.category_id`입니다. 지식 자신의 번호 `knowledge.id`와 분류 번호를 연결하면 안 됩니다.

## 2. JOIN: 각 지식에 분류명 붙이기

```sql
SELECT k.id, k.title, c.name AS category
FROM public.knowledge AS k
JOIN public.categories AS c ON k.category_id = c.id
ORDER BY k.id;
```

`k`, `c`는 테이블 별칭입니다. `ON`은 두 표에서 연결할 행의 조건을 정합니다. 이 JOIN은 INNER JOIN이므로 조건에 맞는 쌍만 남깁니다. 결과 한 행은 지식 한 건이며 S0에서는 3행입니다.

S0의 지식 id 3도 category_id는 1이므로 learning에 속합니다. `k.id = c.id`로 연결하면 이를 reference로 잘못 붙일 수 있습니다. 결과 행 수만 보고 올바른 JOIN이라고 판단하지 않습니다.

## 3. LEFT JOIN과 GROUP BY: 빈 분류도 포함해 개수 세기

```sql
SELECT c.name AS category, COUNT(k.id) AS knowledge_count
FROM public.categories AS c
LEFT JOIN public.knowledge AS k ON k.category_id = c.id
GROUP BY c.id, c.name
ORDER BY c.id;
```

논리적 흐름은 분류를 기준으로 연결 → 분류별 그룹 구성 → 각 그룹의 지식 개수 계산 → 정렬입니다. 결과 한 행의 단위가 지식에서 분류로 바뀝니다.

`LEFT JOIN`은 연결된 지식이 없는 분류도 유지하며, 그 행의 지식 열은 NULL로 채웁니다. 여기서는 **COUNT(k.id)**를 써야 그 NULL을 제외하고 실제 지식만 셉니다. `COUNT(*)`는 연결 결과의 행을 세므로 빈 분류도 1로 집계할 수 있습니다.

| 분류 | S0 예상 지식 수 |
|---|---|
| learning | 2 |
| environment | 1 |
| reference | 0 |

4번의 전체 행 수 확인은 `COUNT(*)`, 이 단계의 자식 행 수 확인은 `COUNT(k.id)`가 목적에 맞습니다.

## 4. 본문 길이 집계

```sql
SELECT COUNT(*) AS knowledge_count,
       SUM(char_length(content)) AS total_chars,
       MIN(char_length(content)) AS min_chars,
       MAX(char_length(content)) AS max_chars
FROM public.knowledge;
```

`char_length`는 본문의 문자 수입니다. GROUP BY가 없으므로 전체 지식을 하나의 집계 대상으로 삼아 한 행을 반환합니다. COUNT는 전체 행 수, SUM은 총 문자 수, MIN/MAX는 가장 짧고 긴 본문의 문자 수입니다.

새 S0에서는 3건·64자·최소 20자·최대 24자입니다. 7번에서 본문을 커밋한 뒤에는 길이가 달라질 수 있으므로 현재 데이터로 판단합니다. 빈 표에서는 COUNT는 0, 나머지 세 집계는 NULL입니다.

## 5. 검토 범위

기본필수 05의 JOIN, LEFT JOIN·GROUP BY와 본문 길이 집계를 다뤘습니다. HAVING은 응용 확장에 해당하므로 이 문서 범위에서 제외합니다. SQL은 사용자 작성 상태로 보존했으며 DB 실행 검증은 하지 않았습니다.
