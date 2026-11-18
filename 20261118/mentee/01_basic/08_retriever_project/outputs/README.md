# Day08 Retriever 검색 결과 보고서

## 1. 환경 구성

- 기록일: 2026년 11월 18일 (한국 표준시, Asia/Seoul)
- 운영체제 및 아키텍처: Linux x86_64
- 셸: Bash
- Python 버전: 3.13.16
- 작업 디렉터리: /home/swchoi/projects/python/practice_assignment/20261118/mentee/01_basic/08_retriever_project

## RDB에 미리 추가한 지식 데이터 목록 (실습 07 기준)

| id  | title               | description                                                 | category      | knowledge_type        |
| --- | ------------------- | ----------------------------------------------------------- | ------------- | --------------------- |
| 101 | "실습 파일 보관"    | "실습 파일은 개인 폴더에 보관합니다."                       | "course"      | "knowledge_v1"        |
| 102 | "서버 실행"         | "프로젝트 폴더에서 서버를 실행합니다."                      | "development" | "knowledge_v1"        |
| 103 | "질문 작성"         | "오류 메시지와 시도한 작업을 함께 적습니다."                | "support"     | "knowledge_v1"        |
| 104 | "수업 녹화"         | "녹화가 제공되는 수업은 강의실 안내 페이지에서 확인합니다." | "course"      | "knowledge_search_v2" |
| 105 | "과제 제출"         | "과제 제출 위치는 해당 과제의 안내 페이지에서 확인합니다."  | "course"      | "knowledge_search_v2" |
| 106 | "데이터베이스 연결" | "PostgreSQL 접속 정보는 로컬 설정 파일에서 읽습니다."       | "development" | "knowledge_search_v2" |
| 107 | "패키지 설치"       | "필요한 Python 패키지는 기존 가상환경에 추가합니다."        | "development" | "knowledge_search_v2" |
| 108 | "문제 해결 안내"    | "문제를 보고할 때 재현한 단계와 오류 메시지를 기록합니다."  | "support"     | "knowledge_search_v2" |
| 109 | "결과 검토"         | "검색된 자료는 원문과 실제 질문의 요구를 대조합니다."       | "support"     | "knowledge_search_v2" |

## 테스트 결과

- 검색 방식: `pgvector_exact`
- 결과 파일: [exercise_08.json](exercise_08.json)
- 검색 조건: Top-3, 카테고리 필터 없음
- 반환 후보: 3건
- 유사도 검증결과: 실습 07의 교재 기준 라벨

| case_id | 질문 내용                     | reference_ids |
| ------- | ----------------------------- | ------------- |
| server  | "서버는 어디에서 실행하나요?" | 102           |

### 최종 요약

- 1위 후보 102의 원문에서 서버 실행 위치가 프로젝트 폴더임을 확인했습니다.
- 후보 103과 107은 교재 기준으로 무관입니다.

### server - "서버는 어디에서 실행하나요?" 질문에 대한 검색 결과

#### Case 1

질문 내용: "서버는 어디에서 실행하나요?"  
검색된 ID: 102  
유사도 검증결과: 관련  
실제 cos거리: 0.11459903543006955  
카테고리: development  
출처 버전: knowledge_v1  
실제 검색된 ID의 내용:

```md
TITLE: 서버 실행
DESCRIPTION: 프로젝트 폴더에서 서버를 실행합니다.
```

#### Case 2

질문 내용: "서버는 어디에서 실행하나요?"  
검색된 ID: 103  
유사도 검증결과: 무관  
실제 cos거리: 0.19596676850516836  
카테고리: support  
출처 버전: knowledge_v1  
실제 검색된 ID의 내용:

```md
TITLE: 질문 작성
DESCRIPTION: 오류 메시지와 시도한 작업을 함께 적습니다.
```

#### Case 3

질문 내용: "서버는 어디에서 실행하나요?"  
검색된 ID: 107  
유사도 검증결과: 무관  
실제 cos거리: 0.1977901936894525  
카테고리: development  
출처 버전: knowledge_search_v2  
실제 검색된 ID의 내용:

```md
TITLE: 패키지 설치
DESCRIPTION: 필요한 Python 패키지는 기존 가상환경에 추가합니다.
```
