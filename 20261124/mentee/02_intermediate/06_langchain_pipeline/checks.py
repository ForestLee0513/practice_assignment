"""단계별 역할 분리: checks.py / 독립 실행은 main.py. """

def validate_trace(result):
    """원 질문·검색용 질문·후보·Context ID를 각각 확인합니다."""
    # BEGIN D27-06-I03
    # TODO D27-06-I03: 원 질문·검색용 질문·후보·Context ID를 각각 확인합니다.
    # 반환값과 예외 조건은 README.md의 수행 기준을 따르세요.
    trace = result["trace"]
    return {
        "questions_separate": bool(trace["original_question"]) and bool(trace["search_query"]),
        "ids_recorded": isinstance(trace["candidate_ids"], list) and isinstance(trace["included_ids"], list),
        "included_from_candidates": set(trace["candidate_ids"]).issubset(set(trace["ranked_ids"]))
    }
    # END D27-06-I03
