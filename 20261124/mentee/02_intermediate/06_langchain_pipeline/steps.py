"""단계별 역할 분리: steps.py / 독립 실행은 main.py. """

def prepare_pipeline_request(case):
    """원 질문과 History를 함께 보존하고 검색용 질문은 Chain 내부에서 만듭니다."""
    # BEGIN D27-06-I01
    # TODO D27-06-I01: 원 질문과 History를 함께 보존하고 검색용 질문은 Chain 내부에서 만듭니다.
    # 반환값과 예외 조건은 README.md의 수행 기준을 따르세요.
    return {
        "query": case["question"],
        "history": case["history"],
        "category": case["category"],
        "candidate_k": 5,
        "context_k": 2,
        "use_rewrite": True,
        "use_multiquery": False,
        "use_rerank": True
    }
    # END D27-06-I01


def wire_langchain_pipeline(dependencies, offline):
    """LCEL는 Runnable을 준비할 뿐이고 .invoke()가 실행 시작점입니다."""
    # BEGIN D27-06-I02
    # TODO D27-06-I02: LCEL는 Runnable을 준비할 뿐이고 .invoke()가 실행 시작점입니다.
    # 반환값과 예외 조건은 README.md의 수행 기준을 따르세요.
    from coursekit.pipeline import create_rag_pipeline
    return create_rag_pipeline(*dependencies, offline=offline)
    # END D27-06-I02
