"""실습 05 Intermediate · 설명용 20자 경계 세트."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]))
from coursekit.io import save_json,show_success
from coursekit.processing import covered_positions


def validate_ranges(length:int,spans:list[tuple[int,int]])->None:
    # BEGIN D24-05-I01
    # TODO D24-05-I01 : 청크별 Span이 기준 본문의 범위 안인지 검증합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.
    for a, b in spans:
        if not 0 <= a < b <= length:
            raise ValueError("invalid range")
    # END D24-05-I01
def coverage(length:int,spans:list[tuple[int,int]])->float|None:
    # BEGIN D24-05-I02
    # TODO D24-05-I02 : 합집합으로 덮은 문자 수와 Coverage를 계산합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.
    if length == 0:
        return None
    validate_ranges(length, spans)
    n, _ = covered_positions(spans, length)
    return n / length
    # END D24-05-I02
def detect_gaps_and_duplicates(length:int,spans:list[tuple[int,int]],ids:list[str])->dict:
    # BEGIN D24-05-I03
    # TODO D24-05-I03 : 빠진 위치의 연속 구간 및 중복 Chunk ID를 구합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.
    _,missing=covered_positions(spans,length)
    gaps=[]
    for pos in missing:
        if gaps and gaps[-1][1]==pos:gaps[-1]=(gaps[-1][0],pos+1)
        else:gaps.append((pos,pos+1))
    seen=set();dups=[]
    for cid in ids:
        if cid in seen:dups.append(cid)
        seen.add(cid)
    return {'gaps':gaps,'duplicate_ids':sorted(set(dups))}

    # END D24-05-I03
def make_report(length:int,spans:list[tuple[int,int]],ids:list[str])->dict:
    # BEGIN D24-05-I04
    # TODO D24-05-I04 : 통과·오류·반복량·Coverage를 구분한 보고서를 작성합니다.
    # 요구: 입력 변수·반환값의 자료형을 유지하고, 완료 기준은 README/expected를 참조하세요.
    # 힌트: 이 함수의 docstring과 상위 실행 함수에 전달되는 값을 확인합니다.
    # TODO를 완성한 뒤 아래 NotImplementedError 줄을 삭제합니다.
    validate_ranges(length,spans)
    covered, _ = covered_positions(spans,length)
    errors = detect_gaps_and_duplicates(length,spans,ids)
    return {
        'coverage': coverage(length,spans),
        'covered_characters': covered,
        'repeat_extra_chars': sum(b-a for a,b in spans)-covered,
        'errors': errors,
        'valid': not errors['gaps'] and not errors['duplicate_ids']
    }
    # END D24-05-I04
def main():
    samples={'overlap':([(0,8),(6,14),(12,20)],['A','B','C']),
             'missing':([(0,8),(10,20)],['A','B']),
             'duplicate':([(0,8),(0,8),(8,20)],['A','A','C'])}
    reports={name:make_report(20,*parts) for name,parts in samples.items()}
    assert [reports[n]['coverage'] for n in samples]==[1.0,.9,1.0]
    out=save_json(HERE,'coverage_report.json',reports)
    show_success('05 Intermediate',out)
