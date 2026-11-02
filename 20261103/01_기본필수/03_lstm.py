import torch
from torch import nn
torch.set_num_threads(1)  # 작은 CPU 실습의 실행 조건을 고정한다.
torch.manual_seed(42)  # LSTM과 Linear의 초기 가중치가 재현되도록 난수 시드를 고정한다.
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent  # 터미널 위치와 관계없이 이 파일 옆의 CSV를 찾는다.
df = pd.read_csv(ROOT / "series.csv")
# 시간 구간을 먼저 분리한다. test 구간은 모델에 넣지 않는다.
# CSV의 기존 행 순서를 유지한 채 value만 float32 텐서로 만든다.
# train=[60], valid=[20]이다. 시간순 분할 뒤 각 구간 안에서 window를 만들어야
# train/valid 경계를 넘는 관측이 섞이지 않는다. 이번 파일은 train만 사용한다.
train = torch.tensor(df.loc[df["split"]=="train","value"].values,dtype=torch.float32)
valid = torch.tensor(df.loc[df["split"]=="valid","value"].values,dtype=torch.float32)

# unfold(0,13,1): 과거 12개+다음 정답 1개인 묶음을 만든다.
# ---- params ----
# train.unfold(0, 13, 1)
# 0 = (dimension) window를 만들 축
# 13 = (size) 한 window의 길이
# 1 = (step) 시작점 간격
# ---- 반환 형태 ----
# 원소 60개에서 길이 13, 간격 1인 window 수는 (60-13)//1+1=48이다.
# window=[48,13]이며 첫 행은 train[0:13], 다음 행은 train[1:14]이다.
# 인접 window는 12개 관측을 공유하지만 각 window 안의 시간 순서는 유지된다.
# unfold는 원본 데이터를 공유하는 뷰를 반환하므로 window를 제자리 수정하지 않는다.
window = train.unfold(0,13,1)
# 과거 12개를 선택하고, LSTM 입력에 필요한 특성 축을 추가한다.
# [B,12] → [B,12,1]. B=48, 시점 수=12, 시점별 입력 특성 수=1이다.
# unsqueeze는 크기 1인 축을 추가하며 값을 지우거나 Padding을 제거하지 않는다.
x = window[:,:12].unsqueeze(-1)
# 각 window의 13번째 값이 다음 시점의 정답이다.
# 12:13 슬라이스는 축을 유지해 [48,1]을 만든다. window[:,12]는 [48]이 된다.
y = window[:,12:13]
# input_size=1: 시점별 관측값 1개, hidden_size=8: 은닉 특성 8개.
# batch_first=True이므로 입력과 output은 [B,T,특성] 순서이다.
# 기본값은 1층·단방향이며, h_n과 c_n의 축 순서는 batch_first와 무관하다.
lstm = nn.LSTM(1,8,batch_first=True)
# 은닉 특성 8개를 다음 값 1개로 변환하는 회귀층이다. 분류 확률이 아니다.
head = nn.Linear(8,1)
# 초기 (h0,c0)를 생략했으므로 둘 다 0에서 시작한다.
# output=[48,12,8]: 마지막 층의 모든 시점 은닉 출력.
# h_n=[1,48,8]: 각 층·방향의 최종 은닉 상태, c_n=[1,48,8]: 최종 셀 상태.
# 셀 상태는 LSTM 내부에서 정보를 전달하며 이번 예측층에는 직접 넣지 않는다.
output, (h_n,c_n) = lstm(x)
# 해설 B03: 12개 관측의 마지막 은닉 출력으로 다음 값 1개를 예측한다.
# [:, -1, :]는 마지막 시점이다. 이 예제의 Window 길이는 모두 12이다.
# BEGIN B03
# output[:,-1,:]는 모든 자료에서 마지막 시점의 은닉 특성을 선택해 [48,8]이 된다.
# 모든 길이가 12인 단방향 설정이므로 h_n[-1]과 같은 값이다.
# Linear(8,1)을 거쳐 [48,1]을 만들고 정답 y와 shape를 맞춘다.
prediction = head(output[:, -1, :])
# END B03
# shape를 출력해 입력·정답·은닉 상태·예측의 축 구성이 맞는지 확인한다.
print("입력 / 정답:", tuple(x.shape), tuple(y.shape))
print("h_n / c_n:", tuple(h_n.shape), tuple(c_n.shape))
print("예측:", tuple(prediction.shape))
# 첫 자료의 예측 텐서에서 스칼라를 꺼내 소수점 6자리로 표시한다.
print("첫 예측:", round(prediction[0].item(),6))
# MSE는 (예측-정답)^2의 평균이다. prediction과 y는 모두 [48,1]이어야 한다.
# 이 파일은 순전파만 수행하며 backward/optimizer.step이 없어 아직 학습 전이다.
# 따라서 아래 값은 초기 모델의 train window 오차이며 검증 성능이 아니다.
print("학습 전 MSE:", round(nn.MSELoss()(prediction,y).item(),6))
