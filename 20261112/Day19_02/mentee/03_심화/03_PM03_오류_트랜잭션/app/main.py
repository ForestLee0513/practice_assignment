from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.db import get_engine
from app.errors import DataConflictError, KnowledgeNotFoundError
from app.routers.knowledge import router

# 강사 해설: Day17의 URL·Method·입력·응답 계약을 유지하고 저장소만 PostgreSQL로 교체합니다.
app = FastAPI(title="Knowledge API · PostgreSQL · Advanced")
app.include_router(router)

@app.exception_handler(KnowledgeNotFoundError)
async def not_found_handler(_, exc: KnowledgeNotFoundError):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"detail":"Knowledge not found", "knowledge_id":exc.knowledge_id})

@app.exception_handler(DataConflictError)
async def conflict_handler(_, exc: DataConflictError):
    from fastapi.responses import JSONResponse
    # Service에서 전달된 DataConflictError를 JSON 본문의 HTTP 409 응답으로 변환합니다.
    return JSONResponse(status_code=409, content={"detail":exc.message})

@app.get("/health")
def health():
    try:
        # DB 연결 및 SELECT 1 실행이 성공하면 정상 상태를 반환합니다.
        with get_engine().connect() as conn: conn.execute(text("SELECT 1"))
        return {"status":"ok", "database":"reachable"}
    except OperationalError as exc:
        # DB 연결 실패 등의 OperationalError만 HTTP 503으로 변환합니다.
        # 원래 예외를 원인으로 연결하며, 다른 종류의 예외는 여기서 처리하지 않습니다.
        raise HTTPException(503, "Database unavailable") from exc
