# RAG 과정 중 Pipeline 요약

## Overview

`FastAPI -> Retriever -> LLM 요청 -> LLM 응답 검증` 과정에서 통합된 환경을 구축하기 위해 LangChain을 구축하는 과정을 진행한다.

## LangChain 사용 이유

RAG의 전반적인 과정을 별도의 함수로 일일히 관리하는 것이 아닌, LCEL(LangChain Expression Language)로 통합, Chaining을 통해 필요에 따라 단계를 조합하거나 디버깅을 위해 제거할 수 있어 사용한다.

## Retriever 과정에서 LangChain을 사용하는 방법

### 검색 실패 유형에 따라 구분

| 관찰한 현상                                  | 문제가 발생한 단계    | 이번 수업의 대응                                 |
| -------------------------------------------- | --------------------- | ------------------------------------------------ |
| “그거 취소는?”을 검색하니 무관한 자료가 나옴 | 질문 이해: 대상 생략  | Rewrite로 명시적 독립 질문 만들기                |
| “신청 취소”로 찾으면 “예약 철회” 문서 누락   | 검색 표현·용어        | Expansion 또는 Multi-query로 표현 넓히기         |
| 정답 청크가 후보 10개 중 8위                 | 후보 순위             | Cross-Encoder로 상위 후보 재정렬                 |
| 현재 문서 대신 과거 버전 검색                | Version·Metadata 필터 | 검색 전후 동일한 최신 버전·권한 조건 적용        |
| 정답 문서가 후보에 전혀 없음                 | Candidate Recall      | Reranker가 해결할 수 없음: 검색 범위·인덱싱 확인 |

### Rewrite와 Rerank의 차이

- Query Rewrite: 검색에 사용할 질문을 변경. 올바른 대상을 복원하되 사용자의 의도를 새로 만들어서는 안 됨.
- Rerank: 검색된 Document 후보의 순서를 변경. 이미 찾지 못한 문서는 만들 수 없음.
- 시연/실패 원인에 따라 탐색 범위가 달라짐

### 코드 예시

```python
from langchain_core.runnables import RunnableLambda

# 이미 준비한 Day26 Retriever: state를 받아 Document 후보를 반환합니다.
# 실제 검색 함수는 E5 + PostgreSQL을 호출하고 Metadata를 보존합니다.
def retrieve_step(state):
    hits = search_hits(state["search_query"], state["category"], k=10)
    return {**state, "candidate_hits": hits}

# 오늘 추가하는 Reranker는 첫 검색 결과만 재정렬합니다.
def rerank_step(state):
    # rerank는 retrieve_step에서 선택된 후보를 기반으로 top-k를 다시 산정해서 최종 검색 결과를 선정
    ranked = rerank_hits(state["search_query"], state["candidate_hits"])
    return {**state, "ranked_hits": ranked}

# | 는 실행 순서를 정의합니다. 두 단계는 이 시점에 호출되지 않습니다.
retrieval_chain = RunnableLambda(retrieve_step) | RunnableLambda(rerank_step)
# retrieval_chain.invoke({"search_query": "...", "category": "시설"})
```

### Conversational Query Rewrite

- 이전 대화의 내역을 기반으로 문맥을 이해하는 과정
- QueryRewrite 시 이전 대화의 내역을 추적하되 사용자가 새로 입력한 질문의 의도를 바꾸지 않도록 주의

### Expansion & Multi-query

- Query Expansion은 질문의 목적을 유지하면서 검색에 도움이 되는 관련 표현이나 용어를 추가하는 방법
- '회의실 예약 취소' '회의실 예약 철회' '회의실 예약 취소 절차' 등 유사한 문장을 탐색할 수 있도록 쿼리를 확장하는 과정
- 쿼리에 따라 바로 Retrieval를 수행할 수 있는 경우가 있어 무조건 확장하지 않을 것.

### Candidate Retrieval

- Candidate Retrieval은 큰 문서 집합에서 일부 관련 문서를 빠르게 찾아 Reranker에 전달할 후보를 준비하는 단계임
- Candidate-k: 첫 검색에서 가져오는 후보 개수임. 예를 들어 10개 후보를 찾고 Cross-Encoder가 모두 평가하도록 할 수 있음. (검색 후보)
- Context-k / Top-N: Reranking 후 최종적으로 Context에 넣는 문서 개수임. 후보 10개를 전부 입력하지 않고 3개만 선택할 수 있음. (최대 선택할 후보 개수)
- E5·pgvector는 비교 검색을 위해 기존 규칙을 유지 해야함.
- Candidate 수와 Context 수는 같을 필요가 없음
  - 작은 후보 수는 정답 누락 위험이 있고, 너무 큰 후보 수는 Reranking의 시간·자원을 증가시킴

  | 설정 예시                   | Retrieval 단계                     | Rerank/Context 단계                           |
  | --------------------------- | ---------------------------------- | --------------------------------------------- |
  | candidate_k=3, context_k=3  | 3개만 검색                         | 3개에서 순서를 바꿔 3개 사용 → 후보 누락 위험 |
  | candidate_k=10, context_k=3 | 10개 검색                          | 10개를 점수화한 뒤 상위 3개 사용              |
  | candidate_k=20, context_k=3 | 20개 검색                          | 더 넓지만 Cross-Encoder 계산량 증가           |
  | Candidate에 정답 없음       | 어떤 k에서도 정답 후보가 오지 않음 | 재정렬해도 정답 문서는 나타나지 않음          |

### Reranking

- Retrieval 단계에서 나온 검색 후보의 순위(Top-k)를 재지정
- Bi-Encoder: 1차 검색 / 질문 벡터와 미리 저장한 문서 벡터를 비교하므로 대규모 문서에서 빠르게 후보를 탐색 (예시: E5 + pgvector)
- Cross-Encoder: 2차 정렬 / 문서 후보마다 질문과 문서를 함께 읽어 점수를 계산함. 비교 횟수가 늘어나므로 좁힌 후보에 사용함

## LLM 요청 / LLM 응답 검증

11월 24일 기준 해당 단계는 수업에서 다루지 않아 간략하게 작성한다.

우선, RAG 단계에서 탐색했던 pipeline을 기반으로 LLM에 질문을 하고, 응답을 주고 받는다.  
이전 수업 및 Retriever 단계에서 LangChain을 사용한 것 처럼 유사하게 응답을 받고, 검증 처리 하는 단계를 pipeline으로 생성하면 된다.

최종적으로 아래와 같이 코드가 구성될 것이다.

```python
# ... Retriever 단계의 Pipeline 생략

def llm_request_step(state):
    # LLM에 질문을 보내고 응답을 받는 단계
    response = call_llm(state["ranked_hits"], state["user_query"])
    return {**state, "llm_response": response}

def llm_validation_step(state):
    # LLM 응답을 검증하는 단계
    is_valid = validate_response(state["llm_response"])
    return {**state, "is_valid": is_valid}

def llm_pipeline = RunnableLambda(llm_request_step) | RunnableLambda(llm_validation_step)

# fast api에서 호출 시
@app.post("/process_query")
async def process_query(request: Request):
    user_query = await request.json()
    initial_state = {"user_query": user_query}
    # 전체 pipeline 실행
    search_result = retrieval_chain.invoke(initial_state)
    llm_resonse = llm_pipeline.invoke(search_result)

    return llm_resonse
```
