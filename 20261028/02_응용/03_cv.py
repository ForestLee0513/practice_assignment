"""실습 03 응용: Pipeline을 통째로 train 내부 5-fold에 넣어 다중 지표를 계산합니다."""
from pathlib import Path
import pandas as pd
import numpy as np
HERE = Path(__file__).resolve().parent
raw = pd.read_csv(HERE / "data/requests.csv").set_index("request_id")
manifest = pd.read_csv(HERE / "data/split_manifest.csv")
train_ids = manifest.loc[manifest["split"] == "train"].sort_values("position")["request_id"].tolist()
valid_ids = manifest.loc[manifest["split"] == "valid"].sort_values("position")["request_id"].tolist()
train, valid = raw.loc[train_ids].copy(), raw.loc[valid_ids].copy()
FEATURES = ["input_chars", "allowed_tools", "task_type", "priority"]
NUM, CAT = FEATURES[:2], FEATURES[2:]
X_train, X_valid = train[FEATURES].copy(), valid[FEATURES].copy()
y_train, y_valid = train["failed"], valid["failed"]
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
# 제공: 모든 평균·중앙값·범주 목록은 Pipeline.fit의 학습 부분에서만 결정됩니다.
pre = ColumnTransformer([
    ("num", Pipeline([("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
                      ("scaler", StandardScaler())]), NUM),
    ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent", keep_empty_features=True)),
                      ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), CAT),
])

from sklearn.base import clone
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import make_scorer, f1_score
model = Pipeline([("pre", pre), ("model", LogisticRegression(C=1, max_iter=1000))])
folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
# 두 모델이 같은 학습·검증 행을 사용하도록 분할을 고정합니다.
cv_splits = list(folds.split(X_train, y_train))
# TODO A03: train만 넣어 F1과 AUC를 함께 구하세요. 전처리한 배열 대신 model 전체를 전달합니다.
"""
cross_validate 함수로 분류 모델의 교차검증을 수행한다.
model, X_train, y_train: 전처리를 포함한 모델, 학습용 입력, 실패 여부 정답이다.
cv=cv_splits: 미리 만든 5개 분할로 각각 새 모델을 학습·검증한다.
scoring: 각 fold의 F1과 ROC-AUC를 계산한다.
make_scorer의 zero_division=0: F1 계산에서 분모가 0이면 점수를 0으로 처리한다.
return_train_score=True: 검증 점수 외에 학습 데이터의 점수도 반환한다.
error_score='raise': 학습이나 점수 계산에 실패하면 예외를 발생시킨다.
n_jobs=1: fold 작업을 하나씩 순서대로 실행한다. 학습 횟수를 제한하지 않는다.
반환값은 점수와 소요 시간 배열을 담은 딕셔너리이며, 학습된 모델 자체는 반환하지 않는다.
"""
scores = cross_validate(
    model, X_train, y_train,
    cv=cv_splits,
    scoring={"f1": make_scorer(f1_score, zero_division=0), "auc": "roc_auc"},
    return_train_score=True, error_score='raise',
    n_jobs=1
    )
# TODO 끝
# RMSE(ms)는 별도 회귀 모델로 처리 시간을 예측해 계산합니다.
# clone(pre)는 학습되지 않은 별도 전처리기를 만들어 회귀 Pipeline에 넣습니다.
regression_model = Pipeline([("pre", clone(pre)), ("model", LinearRegression())])
# 분할은 failed의 클래스 비율을 기준으로 만들었고, 회귀에도 같은 행 분할을 사용합니다.
# 회귀의 정답은 elapsed_ms이며, F1·AUC를 계산하는 분류 모델과는 별도로 학습합니다.
regression_scores = cross_validate(
    regression_model, X_train, train["elapsed_ms"],
    cv=cv_splits,
    scoring="neg_root_mean_squared_error",
    error_score="raise",
    n_jobs=1,
)
# scorer는 큰 점수가 좋다는 규칙에 맞춰 음수 RMSE를 반환하므로 부호만 되돌립니다.
# 이미 제곱근을 계산한 점수이므로 추가로 제곱근을 구하지 않습니다.
rmse = -regression_scores["test_score"]
result = pd.DataFrame({"fold": range(1, 6), "F1": scores["test_f1"], "ROC_AUC": scores["test_auc"], "RMSE_ms": rmse})
result.to_csv(OUT / "classification_cv.csv", index=False, encoding="utf-8-sig")
print(result.round(3).to_string(index=False))
print("평균F1/표준편차:", round(result["F1"].mean(), 3), round(result["F1"].std(ddof=0), 3))
print("평균RMSE(ms)/표준편차:", round(rmse.mean(), 3), round(rmse.std(ddof=0), 3))
print("각 fold: 학습48·평가12. test_f1의 test는 CV 내부 평가이며 보관 test20이 아닙니다.")

"""
train 60개를 5개 fold로 나누어 모델별로 5번 학습·검증한 결과이다.

 fold    F1  ROC_AUC  RMSE_ms
    1 0.286    0.750  760.316
    2 0.667    0.844  528.144
    3 0.857    0.875  481.277
    4 0.400    0.704  557.910
    5 0.400    0.852  737.376
평균F1/표준편차: 0.522 0.209
평균RMSE(ms)/표준편차: 613.005 113.805
각 fold: 학습48·평가12. test_f1의 test는 CV 내부 평가이며 보관 test20이 아닙니다.

5-fold 교차검증에서는 4개 fold로 학습하고 남은 1개로 검증하며, 검증 대상을 바꾼다.
각 행은 한 번씩 검증에 사용되고, 각 회차의 모델은 새로 학습한다.
각 fold의 학습·검증 데이터가 달라 F1, ROC-AUC, RMSE도 달라질 수 있다.
random_state=42로 분할을 고정했으므로 같은 환경에서 다시 실행해도 분할은 같다.

F1은 정밀도와 재현율의 조화평균이며, 정확도(Accuracy)와는 다른 지표이다.
ROC-AUC는 예측 점수가 양성과 음성을 얼마나 잘 구분하는지 평가하는 지표이다.
F1과 ROC-AUC는 모두 0~1 범위이며, 클수록 좋다. AUC 0.5는 무작위 수준이다.
동일한 정답과 예측 점수에서 분류 임계값만 바꿀 때는 ROC-AUC가 변하지 않는다.

RMSE는 예측 오차를 제곱해 평균한 뒤 제곱근을 구한 값이며, 작을수록 좋다.
정답이 처리 시간(ms)이므로 RMSE의 단위도 ms이고, 1보다 큰 값도 가능하다.
오차를 제곱하므로 큰 오차에 더 민감하며, 단순한 평균 절대 오차와는 다르다.
평균 RMSE 613.005ms는 5개 fold의 RMSE를 평균한 값이다.
각 fold의 RMSE 평균은 전체 검증 예측을 합쳐 계산한 RMSE와 다를 수 있다.
표준편차 113.805ms는 fold별 RMSE의 변동을 나타내며, 개별 예측 오차의 표준편차가 아니다.
std(ddof=0)은 이 5개 점수를 대상으로 표준편차를 계산한다.

F1·ROC-AUC는 실패 여부를 예측한 분류 결과이고, RMSE는 처리 시간을 예측한 회귀 결과이다.
서로 다른 목표와 단위를 평가하므로 F1과 RMSE의 숫자 크기를 직접 비교하지 않는다.
두 모델은 각각 5번씩, 총 10번 학습하며 전처리도 각 fold의 학습 데이터에서만 학습한다.
별도로 보관한 valid와 test 데이터는 이 교차검증에 사용하지 않는다.

*ms는 밀리초 단위가 아닌, 제곱근의 원본 단위로 보면된다.
"""
