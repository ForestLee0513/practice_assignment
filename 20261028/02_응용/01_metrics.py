"""실습 01 응용: 모델 예시와 전부 성공으로 예측하는 기준선을 비교합니다."""
import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
y = [0]*14 + [1]*6
predictions = {"example": [0]*10 + [1]*4 + [0]*4 + [1]*2, "all_success": [0]*20}
rows = []
for name, pred in predictions.items():
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    # TODO A01: 현재 후보의 F1을 계산하세요. 분모 0은 0으로 표시합니다.
    f1 = f1_score(y, pred, zero_division=0)
    # TODO 끝
    rows.append({"model": name, "Accuracy": accuracy_score(y, pred),
                 "Precision": precision_score(y, pred, zero_division=0),
                 "Recall": recall_score(y, pred, zero_division=0), "F1": f1,
                 "FP": fp, "FN": fn, "TP": tp})
print(pd.DataFrame(rows).round(3).to_string(index=False))
print("정확도가 높은 all_success도 실패 6건을 하나도 찾지 못합니다.")

"""
y (결과)값 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1
예측값(원본): 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1
예측값(모두성공): 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
을 가정했을 때 y와 예측값(원본)의 경우 정확도가 60%로, FP, FN, TP가 모두 정상적으로 도출이 되는 것을 확인할 수 있음.
하지만 y와 예측값(모두성공)을 기준으로 했을 때 정확도 70%지만 정상적으로 처리된 FP(False Positive)가 없음에도 0으로 처리해서 유효하지 않는 값으로 도출됨

"""