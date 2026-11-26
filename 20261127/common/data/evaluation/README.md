# Day30 Gold (평가 전용)
11/20 seed_catalog.json의 제목·본문을 직접 대조하여 고정한 교육용 부분 판정입니다. 전체 180건의 완전한 관련성 판정이 아닙니다. 6개 positive + 1개 no-answer. 6번째 positive는 T-14의 최소 6건을 만족하도록 CNN 학습률 질문을 추가했습니다.
- grades: 2 직접 관련, 1 보조 관련. 미판정 ID는 unjudged이며 이번 제한적 metric 계산에서는 0으로 처리합니다(실제 무관련이라고 단정하지 않음).
- Recall@k/MRR/nDCG의 no-answer는 null(N/A); 전체 평균 제외. No-answer의 생성 결과는 사람이 별도로 검토합니다.
- seed revision/hash와 현재 DB가 다르면 해당 질문을 `dataset_changed`로 표시하고 집계에서 제외합니다. DB는 절대 수정하지 않습니다.
- 애플리케이션/Tool/Prompt에 Gold ID를 전달하지 않습니다. 평가 스크립트만 접근합니다. 자료는 실측 출력이 아닙니다.
