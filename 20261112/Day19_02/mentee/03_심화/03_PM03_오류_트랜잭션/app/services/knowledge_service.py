from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.errors import DataConflictError, KnowledgeNotFoundError
from app.db import transaction
from app.repositories import knowledge as repo
from app.schemas import KnowledgeWrite

def _constraint_name(exc: IntegrityError) -> str | None:
    return getattr(getattr(exc.orig, "diag", None), "constraint_name", None)

# 강사 해설: Service가 Transaction 종료 지점을 소유해 여러 DB 작업의 성공/실패를 한곳에서 결정합니다.
def _raise_conflict(exc: IntegrityError) -> None:
    # IntegrityError에서 위반한 DB 제약조건 이름을 추출합니다.
    name = _constraint_name(exc)
    safe = {
        "categories_name_key": "Category conflict",
        "categories_name_length": "Category rule conflict",
        "knowledge_title_length": "Title rule conflict",
        "knowledge_content_length": "Content rule conflict",
        "knowledge_category_fk": "Category reference conflict",
    }.get(name, "Database constraint conflict")
    # 등록된 제약조건이면 해당 메시지를, 없으면 기본 메시지를 사용합니다.
    # DataConflictError를 발생시키고 원래 IntegrityError를 원인 예외로 연결합니다.
    raise DataConflictError(safe) from exc

def list_knowledge(db: Session, category: str | None = None):
    return repo.list_knowledge(db, category)

def get_knowledge(db: Session, knowledge_id: int):
    item = repo.get_knowledge(db, knowledge_id)
    if item is None: raise KnowledgeNotFoundError(knowledge_id)
    return item

def create_knowledge(db: Session, payload: KnowledgeWrite):
    try:
        with transaction(db):
            category = repo.get_or_create_category(db, payload.category)
            item = repo.add_knowledge(db, title=payload.title, content=payload.content, category_id=category.id)
            item.category = category
            db.flush()
            item_id = item.id
        return repo.get_knowledge(db, item_id)
    except IntegrityError as exc:
        _raise_conflict(exc)

def update_knowledge(db: Session, knowledge_id: int, payload: KnowledgeWrite):
    item = get_knowledge(db, knowledge_id)
    try:
        with transaction(db):
            category = repo.get_or_create_category(db, payload.category)
            item.title, item.content, item.category_id = payload.title, payload.content, category.id
            item.category = category
            db.flush()
        return repo.get_knowledge(db, knowledge_id)
    except IntegrityError as exc:
        _raise_conflict(exc)

def delete_knowledge(db: Session, knowledge_id: int):
    item = get_knowledge(db, knowledge_id)
    try:
        with transaction(db):
            repo.delete_knowledge(db, item)
    except IntegrityError as exc:
        _raise_conflict(exc)
