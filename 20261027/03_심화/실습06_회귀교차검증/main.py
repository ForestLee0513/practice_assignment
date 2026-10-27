"""실습 06 심화: 같은 회귀 KFold에서 음수 RMSE 부호를 되돌립니다."""
from pathlib import Path
import pandas as pd

# 제공: 전날의 분할 소속뿐 아니라 position 순서까지 그대로 읽습니다.
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "data/requests.csv").set_index("request_id")
manifest = pd.read_csv(HERE / "data/split_manifest.csv")
train_ids = manifest.loc[manifest["split"] == "train"].sort_values("position")["request_id"]
valid_ids = manifest.loc[manifest["split"] == "valid"].sort_values("position")["request_id"]
train = raw.loc[train_ids]
valid = raw.loc[valid_ids]
FEATURES = ["input_chars", "allowed_tools", "task_type", "priority"]
X_train, X_valid = train[FEATURES], valid[FEATURES]
# 회귀 정답은 실패 여부가 아니라 실제 처리 시간(ms)이다.
y_train, y_valid = train["elapsed_ms"], valid["elapsed_ms"]
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)
# test 20건의 입력·정답은 아래 모델에 전달하지 않습니다.

from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import KFold, cross_val_score
from preprocessing import build_model

folds = list(KFold(n_splits=5, shuffle=True, random_state=42).split(X_train))
candidates = [("Tree", DecisionTreeRegressor(max_depth=3, min_samples_leaf=3, random_state=42)),
              ("Forest", RandomForestRegressor(n_estimators=100, max_depth=4, min_samples_leaf=2,
                                  max_features=1.0, random_state=42, n_jobs=1)), ("XGB", XGBRegressor(n_estimators=80, max_depth=2, learning_rate=0.05,
                  subsample=0.8, colsample_bytree=1.0, reg_lambda=1.0,
                  objective="reg:squarederror", eval_metric="rmse",
                  tree_method="hist", device="cpu", random_state=42, n_jobs=1))]
rows, detail = [], []
for name, estimator in candidates:
    model = build_model(estimator)
    # TODO C06a: 회귀 정답으로 neg_root_mean_squared_error 점수를 구하세요.
    # 전처리를 포함한 Pipeline으로 범주형 입력과 결측값을 fold마다 처리한다.
    # (파라미터 순서대로)
    # estimator = model : 교차검증에 사용될 모델 - fit은 별도로 하지 않아도 됨. cross_val_score 실행 과정에서 fit을 모두 진행함
    # X = 실제로 학습할 모델의 값
    # y = 실제로 학습할 모델의 정답값 (예측값 산정에 필요)
    # scoring = "neg_root_mean_squared_error" = 음수 제곱 평균값으로 점수 책정
    # scoring이 음수로 진행되는 이유:
    # scikit 내부에서 동작되는 구조적인 문제로 인해 음수로 변환
    # scikit의 기조는 "점수는 높을수록 좋다" 라는 판단 근거로 모델을 학습/검증하기에, RMSE 에러 검증을 위해서는 낮은 값을 비교 해야 하므로 음수로 진행
    negative = cross_val_score(estimator=model, X=X_train, y=y_train, cv=folds, scoring="neg_root_mean_squared_error")
    # TODO 끝
    # TODO C06b: 음수 scorer 값을 양수 RMSE로 되돌리세요.
    rmse = -negative
    # TODO 끝
    rows.append({"model": name, "CV_RMSE_ms": rmse.mean(), "CV_std_ms": rmse.std()})
    for number, value in enumerate(rmse, start=1):
        detail.append({"model": name, "fold": number, "fit_n": 48, "evaluate_n": 12, "RMSE_ms": value})
result = pd.DataFrame(rows)
result.to_csv(OUT / "regression_cv.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(detail).to_csv(OUT / "cv_scores.csv", index=False, encoding="utf-8-sig")
print(result.round(3).to_string(index=False))
print("CV_RMSE는 fold별 RMSE의 단순 평균입니다. 전체 예측을 합친 RMSE와 다를 수 있습니다.")
