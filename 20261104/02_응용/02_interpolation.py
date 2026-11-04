from pathlib import Path
import os
import cv2
import numpy as np

# 제공 코드: 어느 작업 폴더에서 실행해도 현재 파일 옆의 입력을 읽습니다.
# OpenCV에는 영문 상대 경로를 전달합니다. 원본 파일은 덮어쓰지 않습니다.
os.chdir(Path(__file__).resolve().parent)

import csv
import json
from time import perf_counter
Path("outputs").mkdir(exist_ok=True)

image = cv2.imread("data/scene.png")
rows = []
methods = (
    { "name": "nearest", "method": cv2.INTER_NEAREST }, # 인접한 기준으로 보간 / 명확하게 분리되어 있는 픽셀단위
    { "name": "linear", "method": cv2.INTER_LINEAR }, # 선형보간 / 수채화 느낌 확대
    { "name": "area", "method": cv2.INTER_AREA }, # 일반적인 확대 / 별도처리 안함
)
for item in methods:
    name = item["name"]
    method = item["method"]
    # >>> TODO A02
    # 현재 method를 사용해 (너비80, 높이60)으로 축소한 small을 만드세요.
    small = cv2.resize(image, (80, 60), interpolation=method)
    # <<< TODO A02
    large = cv2.resize(small, (320, 240), interpolation=method)
    cv2.imwrite(f"outputs/p02_{name}_small.png", small)
    cv2.imwrite(f"outputs/p02_{name}_large.png", large)
    # 동일 원본과 크기일 때만 오차를 비교합니다. float 변환으로 uint8 차이의 순환을 피합니다.
    mse = np.mean((image.astype(np.float32) - large.astype(np.float32)) ** 2)
    rows.append([name, small.shape[1], small.shape[0], round(float(mse), 4)])
with open("outputs/p02_interpolation.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f); w.writerow(["method", "width", "height", "roundtrip_mse"]); w.writerows(rows)
print(rows)
print("왕복 MSE는 이 합성 이미지의 수치 비교이며 모델 성능이 아닙니다.")
