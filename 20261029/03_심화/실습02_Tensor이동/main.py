"""실습 02: 모양 변환과 장치 이동 후 같은 장치에서 연산합니다."""
import torch
from torch import nn

torch.manual_seed(42) # 동일한 출력값을 보장하기 위한 랜덤시드 고정
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") # 쿠다 활성 여부에 따라 장치 선택
values = torch.arange(12, dtype=torch.float32) # 1차원 tensor 초기화 (12개의 float32로 구성) - 0에서 12까지 순서대로 채움
# 12개 원소를 (3,4)로 바꾸고 네 열에 [1,2,3,4]를 더하세요.
# 이후 앞의 두 열을 신경망 입력으로 사용합니다.
# >>> H02
# TODO H02: 위 요구사항을 읽고 이 블록을 완성하세요.
# numpy와 비슷하게 연산을 처리하면 됨
# matrix
matrix = values.reshape(3, 4) # 값과 원소의 개수를 유지하면서 3x4 행렬로 변경 (3행 4열)
"""
[[ 0,  1,  2,  3],
 [ 4,  5,  6,  7],
 [ 8,  9, 10, 11]]
"""
shifted = matrix + torch.tensor([1, 2, 3, 4]) # 각 행렬마다 첫번째 행에는 1, 두번째 행에는 2 ... 형식으로 더함
"""
[[0+1, 1+2,  2+3,  3+4],
 [4+1, 5+2,  6+3,  7+4],
 [8+1, 9+2, 10+3, 11+4]]

==

[[1,  3,  5,  7],
 [5,  7,  9, 11],
 [9, 11, 13, 15]]
"""
# <<< H02
X = shifted[:, :2].to(device)
y = torch.tensor([0, 0, 1], dtype=torch.long).to(device)
model = nn.Linear(2, 2).to(device)
logits = model(X)
print("행렬:", matrix.tolist())
print("보정:", shifted.tolist())
print("입력/출력:", tuple(X.shape), tuple(logits.shape))
print("device 일치:", X.device == y.device == next(model.parameters()).device)
