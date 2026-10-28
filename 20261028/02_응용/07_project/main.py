"""실습 07~08 응용: 06번 계획을 읽어 개발80으로 새 Pipeline을 학습하고 test20을 평가합니다."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from preprocessing import build
from evaluate import summarize

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)
plan = json.loads((OUT / "selection.json").read_text(encoding="utf-8"))
raw = pd.read_csv(HERE / "data/requests.csv").set_index("request_id")
ids = plan["split_ids"]
develop = raw.loc[ids["train"] + ids["valid"]]
test = raw.loc[ids["test"]]
X_develop, X_test = develop[plan["features"]].copy(), test[plan["features"]].copy()
# 파생 특성 생성도 Pipeline에 포함하여 저장·복원 시 같은 공식을 적용합니다.
model = build(
    LogisticRegression(C=plan["C"], max_iter=plan["max_iter"]),
    derived=plan["derived"],
)
model.fit(X_develop, develop["failed"])
positive_column = model.classes_.tolist().index(1)
probability = model.predict_proba(X_test)[:, positive_column]
prediction = (probability > plan["threshold"]).astype(int)
metrics = summarize(test["failed"], prediction, probability)
result = pd.DataFrame({"request_id": test.index, "actual": test["failed"].to_numpy(),
                       "probability_failed": probability, "predicted": prediction})
result.to_csv(OUT / "test_predictions.csv", index=False, encoding="utf-8-sig")
(OUT / "test_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
errors = result.loc[result["actual"] != result["predicted"]]
errors.to_csv(OUT / "error_cases.csv", index=False, encoding="utf-8-sig")
joblib.dump(model, OUT / "pipeline.joblib")
print("확정 모델:", plan["selected"], "/ 학습80·최종20")
print(pd.DataFrame([metrics]).round(4).to_string(index=False))
print("오류 사례")
print(result.loc[result["actual"] != result["predicted"]].head(3).round(3).to_string(index=False))
print("저장: outputs/test_predictions.csv, test_metrics.json, error_cases.csv, pipeline.joblib")
print("다음은 restore.py로 복원합니다. test를 보고 후보를 다시 고르지 않습니다.")
