"""제공 모듈: 전처리 구성과 후보 설정만 담습니다. import만으로 학습하지 않습니다."""
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from features import add_features

FEATURES = ["input_chars", "allowed_tools", "task_type", "priority"]
NUM, CAT = FEATURES[:2], FEATURES[2:]
DERIVED = ["log_input_chars", "chars_per_slot"]

def build(estimator, derived=False, scale=True):
    """매번 학습 전 상태의 Pipeline을 만듭니다. 결측·범주 처리는 전날과 같습니다."""
    numbers = NUM + DERIVED if derived else NUM
    numeric = [("imputer", SimpleImputer(strategy="median", keep_empty_features=True))]
    if scale:
        numeric.append(("scaler", StandardScaler()))
    category = Pipeline([("imputer", SimpleImputer(strategy="most_frequent", keep_empty_features=True)),
                         ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))])
    pre = ColumnTransformer([("num", Pipeline(numeric), numbers), ("cat", category, CAT)])
    steps = [("features", FunctionTransformer(add_features, validate=False))] if derived else []
    return Pipeline(steps + [("pre", pre), ("model", clone(estimator))])

