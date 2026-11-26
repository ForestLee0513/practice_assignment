# Day31 · FastAPI & LangChain Integration 실습자료 (2026-11-30)
기존 Agent Workflow & State 실습자료와 다른 v3 커리큘럼용 자료입니다. 01_basic, 02_intermediate, 03_advanced 중 **한 난이도**의 report-agent-service 폴더만 열고 README 순서대로 실습하세요. mentor는 정답, mentee는 TODO입니다. 수강생에게는 mentee 전용 ZIP만 제공합니다.

실습 01~08에서 같은 프로젝트를 수정합니다. 최종 API 두 종류: Direct RAG `/api/v1/rag/ask`, Agent `/api/v1/agent/ask`. 실제 CUDA E5·Cross-Encoder, 기존 report_agent_lab, 실제 LLM API를 사용합니다. 새로운 DB/재인덱싱/CPU 자동 전환/직접 LangGraph/MCP 구현은 없습니다. 실제 통합 실행과 Fixture 테스트의 구분은 각 프로젝트 README를 참고하세요.
