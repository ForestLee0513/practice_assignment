"""실습 06: 같은 모델의 train·valid 학습 기록을 남깁니다."""

from pathlib import Path
import csv
import json
import torch
from torch import nn
from torch.utils.data import TensorDataset, DataLoader

base = Path(__file__).resolve().parent
out = base / "outputs"
out.mkdir(exist_ok=True)
with (base / "data" / "points.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
train_rows = [r for r in rows if r["split"] == "train"]
valid_rows = [r for r in rows if r["split"] == "valid"]
X_train = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in train_rows])
y_train = torch.tensor([int(r["label"]) for r in train_rows], dtype=torch.long)
X_valid = torch.tensor([[float(r["x1"]), float(r["x2"])] for r in valid_rows])
y_valid = torch.tensor([int(r["label"]) for r in valid_rows], dtype=torch.long)
# test 40건은 모델에 전달하지 않습니다. 순서를 바꾸거나 다시 분할하지 않습니다.
torch.manual_seed(42)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
loader = DataLoader(TensorDataset(X_train, y_train), batch_size=32, shuffle=True,
                    generator=torch.Generator().manual_seed(43), num_workers=0)
model = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 2)).to(device)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
Xv, yv = X_valid.to(device), y_valid.to(device)
Xt, yt = X_train.to(device), y_train.to(device)
history = []

def train_each_model(model):
    model.train()
    online_loss_sum = 0.0
    sample_count = 0
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        logits = model(xb)
        loss = loss_fn(logits, yb)
        # 갱신 전 배치 평균 loss를 표본 수로 가중해 누적한다.
        # 배치마다 모델이 갱신되므로 하나의 고정 모델을 평가한 값과 다르다.
        online_loss_sum += loss.detach().item() * yb.size(0)
        sample_count += yb.size(0)
        loss.backward()
        optimizer.step()
    return online_loss_sum / sample_count

def evaluate_model(model, epoch, online_loss=None):
    model.eval()
    with torch.no_grad():
        # 해당 epoch의 갱신을 모두 마친 동일한 모델로 전체 데이터를 평가한다.
        train_loss = loss_fn(model(Xt), yt).item()
        logits = model(Xv)
        valid_loss = loss_fn(logits, yv).item()
        accuracy = (logits.argmax(dim=1) == yv).float().mean().item()
    history.append([epoch, online_loss, train_loss, valid_loss, accuracy])
    return {
        "train_loss_online": online_loss,
        "train_loss": train_loss,
        "valid_loss": valid_loss,
        "accuracy": accuracy,
    }

def train_model(model, max):
    for epoch in range(max + 1):
        # epoch 0에는 학습 배치가 없으므로 online loss를 기록하지 않는다.
        online_loss = None
        if epoch > 0:
            online_loss = train_each_model(model)
        if epoch % 10 == 0:
            evaluate_reesult = evaluate_model(model, epoch, online_loss)
            online_text = "N/A" if online_loss is None else f"{online_loss:.6f}"
            print(
                f"epoch={epoch} | train_loss_online={online_text}"
                f" | train_loss_eval={evaluate_reesult['train_loss']:.6f}"
                f" | valid_loss={evaluate_reesult['valid_loss']:.6f}"
                f" | valid_accuracy={evaluate_reesult['accuracy']:.4f}"
            )

    return evaluate_reesult

evaluate_reesult = train_model(model=model, max=80)

with (out / "training_history.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["epoch", "train_loss_online", "train_loss_eval", "valid_loss", "valid_accuracy"])
    writer.writerows(history)
