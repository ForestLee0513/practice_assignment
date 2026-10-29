# 클래스로 ANN 표현

해당 폴더를 VS Code로 열어 `main.py`의 TODO를 완성합니다. 함수를 처음부터 재설계하지 않고 제공된 흐름을 사용합니다.

**H04** — 입력 x를 self.net에 넣은 결과를 반환하세요. 출력은 (N,2) logits이며 softmax를 추가하지 않습니다.

```powershell
python main.py
```

## 예상 출력

```text
Module 출력: [[-1.204215407371521, 0.9152553677558899], [-0.5985832810401917, 0.3605276942253113], [-0.10027067363262177, 0.021551646292209625]]
Sequential 출력: [[-1.204215407371521, 0.9152553677558899], [-0.5985832810401917, 0.3605276942253113], [-0.10027067363262177, 0.021551646292209625]]
출력 shape: (3, 2) (3, 2)
동일 출력: True
파라미터: 42
```

CPU 검수 결과이며 device·버전과 학습 수치는 환경에 따라 달라질 수 있습니다. 상세 출력은 `expected/console.txt`에도 있습니다.

## 완료 조건

TODO의 계산을 코드로 확인하고 예상 결과와 비교합니다. 자신의 말로 입력 shape, 처리한 단계, 출력의 의미를 설명하세요. 단순히 실행 종료 코드가0인 것만으로 완료하지 않습니다.

## 내 기록

- 확인한 입력 / 출력:
  - 입력 `X`는 `[[1., 2.], [0., 1.], [-1., 0.]]`이며 shape은 `(3, 2)`이다. 샘플 3개가 각각 특징 2개를 가진다.
  - `forward`에서 `return self.net(x)`로 이미 정의한 `Linear(2, 8) → ReLU → Linear(8, 2)`의 연산 결과를 반환했다.
  - 별도로 만든 `Sequential`에 `custom.net.state_dict()`를 복사한 뒤 같은 입력을 전달했다. 두 출력의 shape은 모두 `(3, 2)`, `torch.allclose(a, b)`는 `True`, 파라미터 수는 42개로 확인했다.
- 결과의 의미:
  - `custom(X)`를 호출하면 PyTorch의 Module 호출 과정을 통해 `forward(X)`가 실행되고, 그 안에서 `self.net(X)`가 각 층을 순서대로 실행한다.
  - 중간 shape은 `(3, 2) → (3, 8) → (3, 8) → (3, 2)`이다. 최종 출력은 각 샘플에 대한 클래스 2개의 점수인 logits이다. softmax를 적용하지 않았으므로 확률은 아니다.
  - 같은 구조라도 모델을 두 번 생성하면 초기 가중치가 달라질 수 있다. `sequential.load_state_dict(custom.net.state_dict())`로 가중치와 편향을 모두 맞춰야 구조와 forward 동작을 같은 조건에서 비교할 수 있다.
  - `a = custom(X)`, `b = sequential(X)`의 실제 출력값을 나란히 출력하고 `torch.allclose(a, b)`로 허용오차 내에서 같은지 확인했다. 이번 실행에서는 출력값도 동일했다.
  - 파라미터 수는 첫 Linear의 `2×8+8=24`개와 두 번째 Linear의 `8×2+2=18`개를 합쳐 42개이다. ReLU에는 학습할 파라미터가 없다.
- 잘못 이해했던 내용 또는 질문:
  - `forward`에서 층을 다시 만들 필요가 없다. `__init__`에서 만든 `self.net`을 그대로 활용해 입력을 처리하면 된다.
  - `self.net(x)`는 원본 입력 자체를 변경하는 것이 아니라 모델의 연산 결과를 반환한다.
  - 출력 shape이 같다는 사실만으로 출력값까지 같다고 판단할 수 없다. 같은 입력과 파라미터를 사용한 뒤 실제 값도 비교해야 한다.

### 같은 가중치의 Sequential과 대조한 코드

```python
sequential.load_state_dict(custom.net.state_dict())
a, b = custom(X), sequential(X)
print("Module 출력:", a.detach().tolist())
print("Sequential 출력:", b.detach().tolist())
print("동일 출력:", torch.allclose(a, b))
```

`detach().tolist()`는 출력값을 확인하기 위해 계산 그래프에서 분리해 Python 리스트로 표시하는 과정이다. 모델의 파라미터를 바꾸지는 않는다. 위 비교로 이번 입력에서 직접 정의한 Module의 forward가 동일한 구조와 파라미터의 Sequential과 같은 결과를 내는 것을 확인했다.
