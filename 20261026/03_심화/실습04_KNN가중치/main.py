"""실습 04 심화: 이전 응용의 거리 가중치를 표로 설명합니다."""
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

X = np.array([[1], [2], [4], [7], [9]]) # 입력값
y = np.array([10, 20, 40, 70, 90]) # 정답
plain = KNeighborsRegressor(n_neighbors=3).fit(X, y) # 입력값 X와 정답 y를 기반으로 KNN 모델을 학습
distance, indices = plain.kneighbors([[3.2]]) # 거리, 인덱스(각 이웃에 대한 위치)
print(pd.DataFrame({"input": X[indices[0], 0], "distance": distance[0], "target": y[indices[0]]}).round(3).to_string(index=False))
# TODO H04: 가까운 이웃에 큰 가중치를 주도록 변경하세요.
# 힌트: weights="distance"
# uniform은 데이터 분포와 관계없이 선택한 이웃에 같은 가중치를 주는 방식 
# distance가 가까운 이웃에게 가중치를 더 주는 계산 방식 / 단, 가까운 이웃이 이상치나 노이즈가 있을 경우 영향을 크게 받을 수 있음
weighted = KNeighborsRegressor(n_neighbors=3, weights="distance")
# 새 모델을 X와 y로 학습
weighted.fit(X, y)
print("uniform:", plain.predict([[3.2]]).round(2))
print("distance:", weighted.predict([[3.2]]).round(2))
print("역거리 가중 손계산:", round(np.average(y[indices[0]], weights=1 / distance[0]), 2))
