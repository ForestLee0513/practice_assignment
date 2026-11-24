"""단계별 역할 분리: checks.py / 독립 실행은 main.py. """

def check_conditions(case, before, ranked):
    print(before, ranked)
    """Gold Label은 검색과 Reranker의 입력이 아니라 평가할 때만 사용합니다."""
    # BEGIN D27-07-I03
    # TODO D27-07-I03: Gold Label은 검색과 Reranker의 입력이 아니라 평가할 때만 사용합니다.
    # 반환값과 예외 조건은 README.md의 수행 기준을 따르세요.

    return {
        "question_id": case["id"],
        "category": case["category"],
        "gold_separate": all("gold" not in d.metadata for d in before),
        "same_candidates": set(d.metadata["chunk_id"] for d in ranked).issubset(set(d.metadata["chunk_id"] for d in before))
    }
    # END D27-07-I03
