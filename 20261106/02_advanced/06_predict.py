"""실습 06. 04의 last.pt와 val 입력을 고정하고 confidence만 바꿉니다."""
from pathlib import Path

import pandas as pd
import torch
from torchvision.ops import box_iou
from ultralytics import YOLO

BASE = Path(__file__).resolve().parent


def main():
    out = BASE / "outputs"
    out.mkdir(exist_ok=True)
    torch.set_num_threads(1)
    model = YOLO(str(out / "cli_smoke/weights/last.pt"))
    device = 0 if torch.cuda.is_available() else "cpu"
    records = []

    for conf in [0.15, 0.25, 0.50]:
        tp = fp = fn = images = detections = 0
        # >>> A06
        # 입력·모델·imgsz를 고정하고 confidence만 바꿉니다.
        results = model.predict(
            source=str(BASE / "data/images/val"), conf=conf, stream=True,
            imgsz=160, device=device, save=False, verbose=False
        )
        # <<< A06
        for result in results:
            images += 1  # 검출이 0개인 이미지도 처리 수에 포함합니다.
            height, width = result.orig_shape
            gt, classes = [], []
            label = BASE / "data/labels/val" / (Path(result.path).stem + ".txt")
            for line in label.read_text(encoding="utf-8").splitlines():
                cls, cx, cy, bw, bh = map(float, line.split())
                gt.append([(cx - bw / 2) * width, (cy - bh / 2) * height,
                           (cx + bw / 2) * width, (cy + bh / 2) * height])
                classes.append(int(cls))

            used = set()
            preds = result.boxes.cpu()
            detections += len(preds)
            gt_boxes = torch.tensor(gt, dtype=torch.float32).reshape(-1, 4)
            for i in torch.argsort(preds.conf, descending=True, stable=True).tolist():
                if not gt:
                    continue
                overlaps = box_iou(preds.xyxy[[i]], gt_boxes)[0]
                eligible = [j for j in range(len(gt))
                            if classes[j] == int(preds.cls[i]) and j not in used]
                for j in sorted(eligible, key=lambda j: -float(overlaps[j])):
                    if float(overlaps[j]) >= 0.5:
                        used.add(j)
                        break
            matched = len(used)
            tp += matched
            fp += len(preds) - matched
            fn += len(gt) - matched

        records.append(dict(conf=conf, images=images, detections=detections,
                            tp=tp, fp=fp, fn=fn,
                            precision=tp / (tp + fp) if tp + fp else 0,
                            recall=tp / (tp + fn) if tp + fn else 0))

    result = pd.DataFrame(records)
    result.to_csv(out / "confidence_comparison.csv", index=False)
    print(result.to_string(index=False))
    return result


if __name__ == "__main__":
    main()
