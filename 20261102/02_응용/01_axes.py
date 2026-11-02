from pathlib import Path
import copy
import csv
import json
import time
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import pandas as pd

torch.manual_seed(42)
torch.set_num_threads(1)
root = Path(__file__).resolve().parent
out = root / "outputs"
out.mkdir(exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

path = sorted((root / "data" / "train" / "horizontal").glob("*.png"))[0]
chw = transforms.ToTensor()(Image.open(path).convert("RGB"))
# BEGIN A01
# TODO A01: 채널 축을 마지막으로 보내 HWC를 만든다.
# permute로 배열 순서를 변경하는데, 변경 순서는 아래와 같다.
# CHW (CHW의 기준 순서: 0, 1, 2) => HWC (CHW의 기준 순서: 1, 2, 0)
hwc = chw.permute(1, 2, 0)
# END A01
nchw = hwc.permute(2, 0, 1).unsqueeze(0)
# matplotlib은 RGB 이미지를 (H, W, C) 순서로 받는다.
fig, ax = plt.subplots(figsize=(4, 4))
ax.imshow(hwc.numpy())
ax.set_title(f"HWC view: horizontal stripes\nshape = {tuple(hwc.shape)}")
ax.set_axis_off()
fig.tight_layout()
# Agg 백엔드에서는 창을 띄우는 대신 파일로 저장한다.
image_path = out / "image_axes.png"
fig.savefig(image_path, dpi=120)
plt.close(fig)
print("CHW / HWC / NCHW:", tuple(chw.shape), tuple(hwc.shape), tuple(nchw.shape))
print("왕복 값 일치:", torch.equal(chw, nchw[0]))
print("이미지 저장:", image_path)
