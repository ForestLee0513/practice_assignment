import torch
from torch import nn
torch.set_num_threads(1)  # 작은 CPU 실습의 실행 조건을 고정한다.
torch.manual_seed(42)
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)

from torch.nn.utils.rnn import pad_sequence
# 각 텐서는 [실제 시점 수 L, 시점별 특성 수 F]이며, 리스트의 원소 하나가 자료 하나다.
# 아래 세 자료는 길이가 4,2,5이고 특성 수는 모두 3이다. 원소 수 3이 배치 크기 B가 된다.
sequences=[torch.ones(4,3),torch.ones(2,3)*2,torch.ones(5,3)*3]
# lengths는 Padding 전 실제 길이를 sequences와 같은 순서로 보관한다.
lengths=torch.tensor([4,2,5])
# pad_sequence는 가장 긴 길이 T=5에 맞춰 짧은 자료 뒤를 기본값 0으로 채운다.
# batch_first=True이면 [B,T,F]=[3,5,3], 기본값 False이면 [T,B,F]=[5,3,3]이다.
# batch_first는 축 순서만 정하며 자료나 자료 안의 시점을 섞지 않는다.
# 시간 이외의 차원(F 등)과 dtype은 자료 사이에서 맞춰야 한다.
padded=pad_sequence(sequences,batch_first=True)
# 오른쪽 Padding을 전제로 시점 번호 t가 실제 길이 이상이면 True로 표시한다.
# batch_first=True이므로 size(1)이 시간 T이고, 이후 합산도 dim=1을 사용한다.
mask=torch.arange(padded.size(1)).unsqueeze(0)>=lengths.unsqueeze(1)
# TODO A01: Padding이 아닌 실제 시점만 합산하고 각 자료의 실제 길이로 나눈다.
# mask=True는 Padding이다. 0도 정상 관측값일 수 있으므로 값이 0인지로 판정하지 않는다.
# BEGIN A01
# padded는 [B,T,F]=[3,5,3], mask는 [B,T]=[3,5]이며 True가 Padding이다.
# unsqueeze(-1)로 mask를 [B,T,1]로 만들어 모든 특성 F에 같은 마스크를 적용한다.
# ~mask는 실제 시점=True(1), Padding=False(0)이므로 곱하면 Padding만 0이 된다.
# 곱셈 결과 전체를 괄호로 묶고 sum(dim=1)로 시점 T를 합산한다.
# 실제 관측값이 0이어도 길이 기반 mask가 False이므로 정상 시점으로 포함된다.
mean = (padded * (~mask).unsqueeze(-1)).sum(dim=1) / lengths.unsqueeze(-1)
# lengths를 [B,1]로 만들어 각 자료의 모든 특성을 해당 실제 길이로 나눈다.
# mean(dim=1)은 Padding까지 포함한 최대 길이 5로 나누므로 여기서는 사용하지 않는다.
# 이 예제의 실제 길이는 모두 1 이상이며, Tensor.mean()에는 mask 인자가 없다.
# END A01
print("Padding mask:\n",mask)
print("실제 값 평균:\n",mean)
pd.DataFrame(mask.int().numpy()).to_csv(OUT/"padding_mask.csv",index=False)
