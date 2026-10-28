"""실습 02 응용: 가상 확률로 임계값만 바꿉니다. 최종 모델의 임계값을 탐색하는 코드가 아닙니다."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score, roc_auc_score
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)
y = np.array([0, 0, 1, 1])
score = np.array([0.10, 0.40, 0.35, 0.80])
rows = []
for threshold in [0.5, 0.3]:
    # TODO A02: 확률이 threshold보다 클 때만 실패1로 바꾸세요. 같은 값은 성공0입니다.
    prediction = (score > threshold).astype(int)
    # TODO 끝
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    rows.append({"threshold": threshold, "FP": fp, "FN": fn, "F1": f1_score(y, prediction),
                 "assumed_cost": fp + 5*fn, "AUC": roc_auc_score(y, score)})
result = pd.DataFrame(rows)
print(result.round(3).to_string(index=False))
result.to_csv(OUT / "threshold_comparison.csv", index=False, encoding="utf-8-sig")
print("cost는 FP 비용1, FN 비용5라는 가정입니다. 최종 평가 임계값은 사전에 0.5로 고정합니다.")

"""
임계값을 바꾸면 예측 클래스가 달라지므로 정밀도, 재현율, F1은 달라질 수 있다.
반면 ROC-AUC는 특정 임계값에서의 예측 클래스가 아니라,
예측 점수 전반의 임계값을 변화시켜 얻는 ROC 곡선 아래의 면적이다.
따라서 동일한 정답(y)과 예측 점수(score)를 사용하는 이 코드에서는
분류 임계값을 바꾸어도 AUC는 0.75로 동일하다.
"""