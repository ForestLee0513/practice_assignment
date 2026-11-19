"""실습 03 Intermediate · 정제 계약과 보고서."""
from pathlib import Path
import sys, re,unicodedata,hashlib
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]))
from coursekit.io import DATA,save_json,show_success
from coursekit.documents import by_doc,parse_one


def apply_nfc(text:str)->str:
    # BEGIN D24-03-I01
    # TODO D24-03-I01 : 원문을 Unicode NFC로 정규화합니다. NFKC로 동그라미 번호를 무조건 지우지 않습니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.
    return unicodedata.normalize("NFC", text)
    # END D24-03-I01
def normalize_prose(text:str)->str:
    # BEGIN D24-03-I02
    # TODO D24-03-I02 : CRLF·CR·가로 공백만 정리하며 문단 경계를 보존합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.
    lf_text = apply_nfc(text.replace('\r\n', '\n').replace('\r', '\n'))
    return '\n'.join(re.sub(r'[ \t]+',' ',line).strip()
                     for line in lf_text.split('\n')).strip()
    # END D24-03-I02
def check_phrases(text:str,phrases:list[str])->dict:
    # BEGIN D24-03-I03
    # TODO D24-03-I03 : 핵심 구절 목록을 받아 부정어·숫자·예외의 존재 여부를 검사합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.
    return {
        "present": [p for p in phrases if p in text],
        "missing": [p for p in phrases if p not in text]
    }
    # END D24-03-I03
def make_audit(original:str,cleaned:str,phrases:list[str])->dict:
    # BEGIN D24-03-I04
    # TODO D24-03-I04 : 정제 규칙 버전·전후 길이·해시·검사 결과를 출력합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.
    return {
        "cleaner_version": "nfc-prose-v1",
        "chars_before": len(original),
        "chars_after": len(cleaned),
        "clean_hash": hashlib.sha256(cleaned.encode("utf-8")).hexdigest(),
        "phrase_check": check_phrases(cleaned, phrases),
        "idempotent": normalize_prose(cleaned)==cleaned
    }
    # END D24-03-I04
def main():
    doc=by_doc('DOC-ATTEND');unit=parse_one(doc)['units'][0]
    original=unit['raw_text'];cleaned=normalize_prose(original)
    audit=make_audit(original,cleaned,['10분','결석','사전 승인'])
    out=save_json(HERE,'clean_report.json',{'doc_id':doc['doc_id'],
        'unit_id':unit['unit_id'],'clean_text':cleaned,'audit':audit})
    show_success('03 Intermediate',out)
