"""제공 코드. 파일 읽기/쓰기는 호출자가 같은 LOCK 안에서 수행합니다."""
import json
from pathlib import Path
from threading import Lock
from operator import itemgetter

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data" / "knowledge.json"
LOCK = Lock()


def read_data() -> dict:
    # 파일 손상/누락을 빈 데이터로 숨기지 않습니다.
    with DATA.open(encoding="utf-8") as f:
        return json.load(f)


def write_data(data: dict) -> None:
    # 단일 프로세스에서 완성한 임시 파일을 교체합니다. DB 트랜잭션의 대체물이 아닙니다.
    temporary = DATA.with_suffix(".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        temporary.replace(DATA)
    finally:
        temporary.unlink(missing_ok=True)


def list_entries(category: str | None = None) -> list[dict]:
    with LOCK:
        entries = read_data()["entries"]
    # BEGIN H-API-01
    # TODO H-API-01: category가 None이 아닐 때만 entries를 분류 완전 일치로 필터링하고 ID 오름차순 목록을
    # 반환하세요.
    if category is not None:
        entries = [entry for entry in entries if entry["category"] == category]
    # 저장 순서와 관계없이 전체·필터 목록 모두 ID 오름차순으로 반환합니다.
    return sorted(entries, key=itemgetter("id"))
    # END H-API-01
def find_entry(knowledge_id: int) -> dict | None:
    with LOCK:
        data = read_data()
    # BEGIN H-API-02
    # TODO H-API-02: 파일에서 읽은 entries에서 knowledge_id와 같은 id의 항목을 반환하고 없으면 None을
    # 반환하세요.
    entries = data["entries"]

    return next((entry for entry in entries if entry['id'] == knowledge_id), None)
    # END H-API-02
def create(fields: dict) -> dict:
    with LOCK:
        data = read_data()
        next_id = data["next_id"]
        # BEGIN H-API-03
        # TODO H-API-03: fields를 복사해 entry를 만들고 next_id로 ID를 발급하세요. entries에 추가하고
        # next_id를 1 늘리세요. 아직 여기서는 저장하지 않습니다.
        entry = dict(fields)
        entry["id"] = next_id
        # END H-API-03
        # BEGIN H-API-04
        # TODO H-API-04: 변경된 data를 저장하고 entry를 반환하세요. 저장 실패를 성공 결과로 바꾸지 마세요.
        next_id += 1
        data["next_id"] = next_id
        data["entries"].append(entry)
        write_data(data)

        return entry
        # END H-API-04
def update(knowledge_id: int, fields: dict) -> dict | None:
    with LOCK:
        data = read_data()
        # BEGIN H-API-05
        # TODO H-API-05: 해당 ID가 있는 위치만 fields 복사본과 같은 ID로 교체·저장·반환하세요. 없으면 None을
        # 반환하세요.
        entries = data["entries"]
        target_index = next((index for (index, entry) in enumerate(entries) if entry['id'] == knowledge_id), -1)

        if target_index == -1:
            return None

        entry = dict(fields)
        entry_id = entries[target_index]["id"] # 기존 ID 보존
        entry["id"] = entry_id
        entries[target_index] = entry
        write_data(data)

        return entry
        # END H-API-05
def delete(knowledge_id: int) -> bool:
    with LOCK:
        data = read_data()
        # BEGIN H-API-06
        # TODO H-API-06: 같은 ID가 있으면 그 항목만 삭제·저장하고 True, 없으면 False를 반환하세요. HTTP 상태코드는
        # 여기에서 결정하지 않습니다.
        entries = data["entries"]
        if next((entry for entry in entries if entry['id'] == knowledge_id), None) is None:
            return False

        for index, entry in enumerate(entries):
            if entry['id'] == knowledge_id:
                del entries[index]

        write_data(data)
        # END H-API-06
    return True
