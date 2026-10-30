from pathlib import Path
import pandas as pd
import torch
from torch import nn

torch.set_num_threads(1)
base = Path(__file__).resolve().parent
from torch.utils.data import TensorDataset, DataLoader
import copy
import matplotlib
matplotlib.use("Agg")  # 창을 띄우지 않고 PNG에 저장합니다.
import matplotlib.pyplot as plt

out = base / "outputs"
out.mkdir(exist_ok=True)
# CUDA 활성화 가능하다면 GPU, 불가하다면 CPU로 진행
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
df = pd.read_csv(base / "data" / "points.csv")
train = df[df["split"] == "train"]
valid = df[df["split"] == "valid"]
X_train = torch.tensor(train[["x1", "x2"]].values, dtype=torch.float32)
y_train = torch.tensor(train["label"].values, dtype=torch.long)
X_valid = torch.tensor(valid[["x1", "x2"]].values, dtype=torch.float32).to(device)
y_valid = torch.tensor(valid["label"].values, dtype=torch.long).to(device)
loss_fn = nn.CrossEntropyLoss()
configs = [{'name': 'sgd', 'optimizer': 'SGD', 'lr': 0.01}, {'name': 'adamw', 'lr': 0.01}, {'name': 'adamw_dropout', 'lr': 0.01, 'dropout': 0.3}]
# 종료 epoch별로 처음부터 새로 학습하며, 결과를 별도 폴더에 보관합니다.
epoch_options = [40, 80, 120]
all_results = []
for total_epochs in epoch_options:
    out = base / "outputs" / f"07_{total_epochs}"
    out.mkdir(exist_ok=True)
    print(f"\n=== {total_epochs} epochs ===")
    summary = []

    for config in configs:
        torch.manual_seed(42)
        width = config.get("width", 32)
        layers = [nn.Linear(2, width)]
        if config.get("bn", False):
            layers.append(nn.BatchNorm1d(width))
        layers.extend([nn.ReLU(), nn.Dropout(config.get("dropout", 0.0)), nn.Linear(width, width)])
        if config.get("bn", False):
            layers.append(nn.BatchNorm1d(width))
        layers.extend([nn.ReLU(), nn.Dropout(config.get("dropout", 0.0)), nn.Linear(width, 2)])
        model = nn.Sequential(*layers).to(device)
        # shuffle용 Generator를 후보마다 같은 seed로 다시 만듭니다.
        loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True,
                            generator=torch.Generator().manual_seed(43), num_workers=0)
        if config.get("optimizer", "AdamW") == "SGD":
            optimizer = torch.optim.SGD(model.parameters(), lr=config["lr"],
                                        momentum=config.get("momentum", 0.0), weight_decay=0.0)
        else:
            optimizer = torch.optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=0.0)
        history = []
        best_loss = float("inf")  # 비교 기준을 무한대로 시작해 첫 유효한 검증 손실을 최솟값으로 보관합니다.
        best_state = None  # 아직 선택한 모델 상태가 없으며, 검증 손실이 개선되면 복사본을 넣습니다.
        best_epoch = 0  # 아직 최적 epoch를 선택하지 않았다는 초기값입니다. 실제 epoch는 1부터 시작합니다.
        for epoch in range(1, total_epochs + 1):
            model.train()
            for xb, yb in loader:
                xb, yb = xb.to(device), yb.to(device)
                optimizer.zero_grad()
                loss = loss_fn(model(xb), yb)
                # loss.backward() 다음 optimizer.step()을 호출하세요.
                # 같은 초기화·동일 shuffle 순서를 사용하며 세 후보의 변경 조건을 읽어 구분합니다.
                # >>> A07
                # 해설 A07: loss.backward() 처리 후 optimizer.step() 처리를 순차적으로 진행
                loss.backward()
                optimizer.step()
                # <<< A07
            # 같은 epoch 말 모델을 eval 모드로 비교합니다. 학습 중 Dropout loss와 구분합니다.
            # epoch 종료 후 model.eval()을 호출하세요.
            # 그 아래 no_grad 블록은 gradient 추적을 끄지만, Dropout 모드를 바꾸지는 않습니다.
            # >>> A08
            # 해설 A08: model.eval()을 호출함으로써 같은 epoch에 속한 model에 대해 평가를 위한 상태 변경
            model.eval()
            # <<< A08
            with torch.no_grad():
                train_loss = loss_fn(model(X_train.to(device)), y_train.to(device)).item()
                logits = model(X_valid)
                valid_loss = loss_fn(logits, y_valid).item()
                valid_acc = (logits.argmax(1) == y_valid).float().mean().item()
                # 최저 valid loss를 관측하면 값·epoch·가중치 복사본을 함께 보관합니다.
                # A09 요구: 동률은 먼저 발견한 epoch 유지. copy.deepcopy(model.state_dict()) 사용.
                # model.state_dict()만 대입하면 이후 학습이 같은 Tensor를 바꾸므로 안 됩니다.
                # >>> A09
                # 해설 A09: 현재 모델의 검증 손실이 지금까지의 최솟값보다 낮을 때만 세 값을 함께 갱신합니다.
                # valid 데이터는 모델 선택에 사용하며, 이 블록에서 역전파나 가중치 학습을 수행하지 않습니다.
                if valid_loss < best_loss:  # 엄격한 < 비교이므로 손실이 같으면 먼저 발견한 epoch를 유지합니다.
                    best_loss = valid_loss  # 새 최소 검증 손실을 저장해 다음 epoch의 비교 기준으로 사용합니다.
                    best_epoch = epoch  # 최소 손실을 기록한 현재 epoch 번호도 함께 보관합니다.
                    # state_dict()에는 가중치·편향 등 파라미터와 BN running 통계 같은 버퍼가 들어갑니다.
                    # state_dict()만 대입하면 내부 Tensor가 현재 모델과 저장소를 공유할 수 있어,
                    # 이후 optimizer.step() 등으로 모델이 바뀔 때 보관한 최적 상태도 바뀔 수 있습니다.
                    best_state = copy.deepcopy(model.state_dict())  # Tensor까지 독립적으로 복사해 이 시점의 상태를 고정합니다.
                    # 학습 종료 후 model.load_state_dict(best_state)로 이 상태를 복원합니다.
                    # 메모리에 보관하는 복사본이며, 모델 파일로 저장하려면 별도의 torch.save()가 필요합니다.
                # <<< A09
            history.append([epoch, train_loss, valid_loss, valid_acc])
        table = pd.DataFrame(history, columns=["epoch", "train_loss_eval", "valid_loss", "valid_acc"])
        best = table.loc[table["valid_loss"].idxmin()]
        name = config["name"]
        table.to_csv(out / f"07_{name}_history.csv", index=False)
        summary.append({"epochs": total_epochs, **config, "best_epoch": int(best["epoch"]),
                        "best_valid_loss": float(best["valid_loss"]),
                        "valid_acc_at_best": float(best["valid_acc"]),
                        "last_train_loss_eval": train_loss, "last_valid_loss": valid_loss})
        # 제공 코드: 학습이 끝난 뒤 최적 상태로 복원하고 그 모델로 다시 평가합니다.
        model.load_state_dict(best_state)
        model.eval()
        with torch.no_grad():
            best_pred = model(X_valid).argmax(1).cpu()
            restored_loss = loss_fn(model(X_valid), y_valid).item()
        labels = y_valid.cpu()  # 검증 정답을 CPU로 옮겨 CPU에 있는 best_pred와 비교합니다.
        class_rows = []  # 클래스별 계산 결과를 저장할 빈 리스트입니다.
        for label in (0, 1):  # 클래스 0과 1을 각각 한 번씩 선택합니다.
            # A10 요구: 실제 정답이 label인 행을 먼저 고른 뒤 support·correct·recall 계산.
            # 전체 accuracy나 '예측 label의 수'로 나누지 않습니다. 0건이면 recall=None.
            # >>> A10
            # TODO A10: 클래스별 실제 표본 수·정답 수·Recall을 기록하세요.
            mask = labels == label  # 실제 정답이 현재 클래스인 위치를 True로 표시합니다.
            support = mask.sum().item()  # True 개수를 세고 Python 숫자로 변환해 실제 표본 수를 구합니다.
            correct = (best_pred[mask] == label).sum().item()  # 해당 표본 중 예측도 현재 클래스와 일치하는 개수입니다.
            recall = correct / support if support > 0 else None  # 실제 클래스 표본 중 맞힌 비율이며, 표본이 없으면 None입니다.
            class_rows.append({  # 현재 클래스의 결과를 딕셔너리 한 행으로 추가합니다.
                "label": label,  # 클래스 번호
                "support": support,  # 해당 클래스의 실제 표본 수
                "correct": correct,  # 해당 클래스에서 맞힌 표본 수
                "recall": recall,  # 해당 클래스의 재현율
            })
            # <<< A10
        pd.DataFrame(class_rows).to_csv(out / f"07_{name}_class_metrics.csv", index=False)
        pd.DataFrame({"id":valid["id"].tolist(),"actual":labels.tolist(),
                      "predicted":best_pred.tolist()}).to_csv(out / f"07_{name}_predictions.csv", index=False)
        summary[-1]["restored_valid_loss"] = restored_loss
        summary[-1]["restored_matches_best"] = abs(restored_loss-best_loss) < 1e-6
        plt.figure(figsize=(8, 5))
        plt.plot(table["epoch"], table["train_loss_eval"], label="train (eval)")
        plt.plot(table["epoch"], table["valid_loss"], label="valid")
        plt.axvline(best["epoch"], linestyle="--", label="best epoch")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.legend()
        plt.tight_layout()
        plt.savefig(out / f"07_{name}_curves.png", dpi=150)
        plt.close()
        print(name, "best epoch:", int(best["epoch"]), "best valid loss:", round(best["valid_loss"], 6))
    result = pd.DataFrame(summary)
    result.to_csv(out / "07_comparison.csv", index=False)
    print(f"생성: outputs/07_{total_epochs}/07_*.csv, *.png / test 미사용")
    all_results.append(result)

# 3개 종료 시점 × 3개 후보의 비교표입니다. 기존 40 epoch 파일은 유지합니다.
epoch_comparison = pd.concat(all_results, ignore_index=True)
epoch_comparison.to_csv(base / "outputs" / "07_epoch_comparison.csv", index=False)
for total_epochs in epoch_options:
    print(f"\n=== {total_epochs} epochs 결과표 ===")
    print(epoch_comparison.loc[epoch_comparison["epochs"] == total_epochs,
          ["name", "best_epoch", "best_valid_loss", "valid_acc_at_best",
           "restored_valid_loss", "restored_matches_best"]]
          .to_string(index=False, float_format=lambda x: f"{x:.6f}"))
