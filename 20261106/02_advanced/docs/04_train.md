# 응용 04 · YOLO 학습 문서 안내

자세한 코드 설명과 제공 데이터의 실제 학습 기록은 [Jupyter 학습 문서](04_train.ipynb)에 정리했습니다.

이번 기록은 제공된 square·circle·triangle 데이터로 수행한 2 epoch 학습입니다.

|항목|기록|
|---|---|
|학습 이미지·객체 수|36장·90개|
|검증 이미지·객체 수|12장·30개|
|모델|yolo26n.yaml, 사전학습 사용하지 않음|
|epochs / batch / imgsz|2 / 4 / 160|
|optimizer / lr0 / seed|SGD / 0.01 / 42|
|기존 학습 args의 장치|0|
|두 epoch의 mAP50·mAP50–95|모두 0|
|5·6번에서 사용하는 가중치|outputs/cli_smoke/weights/last.pt|

현재 코드는 CUDA가 없으면 CPU를 선택하며, API와 CLI의 장치 설정과 저장 경로 안내를 일치시켰습니다. CLI 문자열 저장 자체가 별도 학습 실행을 뜻하지는 않습니다.

Jupyter 문서에는 손실 변화, 지표의 의미, 파일별 역할, 관측과 원인 가설을 구분해 설명했습니다. 결과 파일과 체크포인트는 Git에 포함하지 않습니다. 실행·검증 여부와 제출용 판단은 직접 기록하세요.

참고 파일: `04_train.py`, `data/manifest.csv`, `outputs/cli_smoke/args.yaml`, `outputs/cli_smoke/results.csv`.
