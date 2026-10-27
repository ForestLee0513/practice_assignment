"""별도 탐색: RandomForest의 잎 최소 크기만 비교하고 보고서용 로그를 남깁니다.

실행: python explore.py
"""
import importlib.metadata as metadata
import json
from pathlib import Path
import platform

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score

from evaluate import classification_metrics, regression_metrics
from preprocessing import FEATURES, build_model


def main():
    here = Path(__file__).resolve().parent
    out = here / "outputs" / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    messages = []

    def log(message):
        print(message, flush=True)
        messages.append(message)

    # 결과 확인 전에 후보와 규칙을 고정합니다. 기존 main.py의 선택을 변경하지 않습니다.
    config = {
        "experiment": "RandomForest min_samples_leaf 비교",
        "candidates": [2, 4],
        "seed": 42,
        "folds": 5,
        "classification_rule": "train CV F1 평균 최대",
        "regression_rule": "train CV RMSE 평균 최소",
        "tie_rule": "후보 순서 우선: 2, 4",
        "valid_role": "선택 후 진단만 수행",
        "test_evaluated": False,
        "features": FEATURES,
        "environment": {
            "python": platform.python_version(),
            **{name: metadata.version(name) for name in ["numpy", "pandas", "scikit-learn"]},
        },
    }
    log("[실험 조건]\n" + json.dumps(config, ensure_ascii=False, indent=2))

    raw = pd.read_csv(here / "data/requests.csv").set_index("request_id")
    manifest = pd.read_csv(here / "data/split_manifest.csv")

    def get_split(name):
        ids = manifest.loc[manifest["split"] == name].sort_values("position")["request_id"]
        return raw.loc[ids]

    train, valid = get_split("train"), get_split("valid")
    X_train, X_valid = train[FEATURES], valid[FEATURES]
    log(f"[데이터] train={len(train)}행, valid={len(valid)}행; test 사용 안 함")
    summary, detail, fold_manifest = [], [], []
    selected = {}
    for task in ["classification", "regression"]:
        is_class = task == "classification"
        target = "failed" if is_class else "elapsed_ms"
        scoring = "f1" if is_class else "neg_root_mean_squared_error"
        metric_name = "F1" if is_class else "RMSE_ms"
        splitter = (StratifiedKFold if is_class else KFold)(
            n_splits=config["folds"], shuffle=True, random_state=config["seed"]
        )
        folds = list(splitter.split(X_train, train[target]))
        task_rows = []
        fitted = {}
        for number, (fit_ids, eval_ids) in enumerate(folds, start=1):
            for role, positions in [("fit", fit_ids), ("evaluate", eval_ids)]:
                for position in positions:
                    fold_manifest.append({
                        "task": task, "fold": number, "role": role,
                        "request_id": X_train.index[position],
                    })

        for leaf in config["candidates"]:
            forest_type = RandomForestClassifier if is_class else RandomForestRegressor
            estimator = forest_type(
                n_estimators=100, max_depth=4, min_samples_leaf=leaf,
                max_features="sqrt" if is_class else 1.0,
                random_state=config["seed"], n_jobs=1,
            )
            log(f"\n[후보] {task} | {estimator.get_params()}")
            model = build_model(estimator, scale=False)
            scores = cross_val_score(
                model, X_train, train[target], cv=folds,
                scoring=scoring, n_jobs=1, error_score="raise",
            )
            if not is_class:
                scores = -scores
            for number, ((fit_ids, eval_ids), score) in enumerate(zip(folds, scores), start=1):
                record = {
                    "task": task, "min_samples_leaf": leaf, "fold": number,
                    "fit_n": len(fit_ids), "evaluate_n": len(eval_ids),
                    "metric": metric_name, "score": float(score),
                }
                detail.append(record)
                log(f"[fold] {number} | 학습={len(fit_ids)} 평가={len(eval_ids)}"
                    f" | {metric_name}={score:.6f}")
            row = {
                "task": task, "min_samples_leaf": leaf, "metric": metric_name,
                "CV_mean": float(scores.mean()), "CV_std": float(scores.std()),
            }
            task_rows.append(row)
            log(f"[CV] 평균={scores.mean():.6f} | 표준편차(ddof=0)={scores.std():.6f}")
            model.fit(X_train, train[target])
            fitted[leaf] = model

        # 같은 점수에서는 앞 후보를 유지합니다. valid를 조회하기 전에 선택합니다.
        choose = max if is_class else min
        best = choose(task_rows, key=lambda row: row["CV_mean"])
        selected[task] = best["min_samples_leaf"]
        log(f"[CV 선택] {task} | min_samples_leaf={selected[task]}")
        evaluate = classification_metrics if is_class else regression_metrics
        for row in task_rows:
            prediction = fitted[row["min_samples_leaf"]].predict(X_valid)
            metrics = evaluate(valid[target], prediction)
            row.update({f"valid_{key}": value for key, value in metrics.items()})
            summary.append(row)
            log(f"[valid 진단] min_samples_leaf={row['min_samples_leaf']} | {metrics}")

    pd.DataFrame(summary).to_csv(out / "summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(detail).to_csv(out / "fold_scores.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(fold_manifest).to_csv(out / "fold_manifest.csv", index=False, encoding="utf-8-sig")
    (out / "config.json").write_text(
        json.dumps({**config, "selected_min_samples_leaf": selected}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log("\n[전체 결과]\n" + pd.DataFrame(summary).round(6).to_string(index=False))
    log("[한계] CV 표준편차는 신뢰구간이 아닙니다. valid 반복 조회와 후보 추가는 선택 편향을 만들 수 있습니다.")
    log("[저장 위치] " + str(out))
    (out / "experiment.log").write_text("\n".join(messages) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
