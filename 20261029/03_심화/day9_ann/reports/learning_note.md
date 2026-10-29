# ANN 학습·평가·저장·복원 구현 보고서

작성일: 2026-10-29

대상: [20261029/03\_심화/day9_ann](../README.md)

## 1. 구현 목적과 조건

입력 특성 두 개로 이진 분류를 수행하는 ANN을 학습하고, 평가 결과를 기록한 뒤 새 프로세스에서 학습한 파라미터를 복원한다. 모델은 2→8→2 구조이며 CrossEntropyLoss, SGD(lr=0.1), batch size 32, 80 epoch를 사용한다.

데이터 200건 중 train 120건으로 학습하고 valid 40건으로 평가한다. 나머지 test 40건은 모델에 전달하지 않는다. 모델 초기화 seed는 42, DataLoader의 shuffle seed는 43이다. 실제 실행은 CUDA 사용이 불가능해 CPU에서 수행했다.

앞선 실습에서 구분한 online loss와 고정 모델 평가 loss의 의미를 이 프로젝트에도 적용한다. 이번 변경 범위는 H07 역전파·갱신, H08 클래스 예측, H09 state_dict 저장, H10 CPU 복원, H11·H12 자동검사다.

## 2. 파일별 역할

| 파일           | 역할                                                         |
| -------------- | ------------------------------------------------------------ |
| `model.py`     | 제공된 SimpleANN 구조 정의                                   |
| `train.py`     | 한 epoch 학습과 고정 모델 평가                               |
| `main.py`      | 데이터 준비, 80 epoch 실행, 학습 기록·예측·파라미터 저장     |
| `check_gpu.py` | 장치 선택과 PyTorch·CUDA 환경 기록                           |
| `restore.py`   | 같은 구조의 모델에 파라미터를 적용하고 저장된 ID·예측과 대조 |

## 3. 기능별 구현

### 3.1 역전파와 SGD 갱신

`train_one_epoch()`는 `model.train()`으로 전환하고 각 배치에서 아래 순서로 학습한다.

```python
optimizer.zero_grad()
loss = loss_fn(model(xb), yb)
loss.backward()
optimizer.step()
```

이번에 추가한 `backward()`는 현재 배치 손실의 기울기를 계산하고, `step()`은 그 기울기로 파라미터를 갱신한다. 매 배치에서 먼저 기울기를 초기화하므로 이전 배치의 기울기가 누적되지 않는다.

기존 손실 집계는 `배치 평균 loss × 실제 배치 표본 수`를 합산한 뒤 전체 표본 수로 나눈다. train 120건은 32·32·32·24건으로 나뉘므로 마지막 배치도 실제 크기만큼 반영한다. 이 값은 배치마다 갱신 중인 모델로 측정한 `train_loss_online`이며, epoch 종료 시 고정한 모델의 전체 train 평가 loss와 구분한다.

### 3.2 평가와 클래스 예측

`evaluate()`는 `model.eval()`과 `torch.no_grad()`를 사용한다. 각 행의 두 logits 중 가장 큰 값의 클래스 인덱스를 `torch.argmax(logits, dim=1)`로 선택하고 `.cpu()`로 옮겨 실제 정답과 비교한다.

`argmax`는 가장 큰 logit 값이 아니라 그 위치인 클래스 인덱스 0 또는 1을 반환한다. 평가에서는 `backward()`나 optimizer 갱신을 수행하지 않는다. 함수는 loss, 정확도, CPU 예측 Tensor를 반환한다.

### 3.3 파라미터 사전 저장

```python
model_state_path = out / "model_state.pt"
torch.save(model.state_dict(), model_state_path)
```

모델 구조는 `SimpleANN()`으로 재생성하므로 학습으로 달라진 가중치·편향과 등록된 버퍼를 담는 `state_dict`를 저장한다. 전체 모델 객체를 저장했던 방식과 `weights_only=True`로 사전을 읽는 방식의 불일치를 해소했다. 파일 이름이 같아도 저장 형식이 바뀌므로 `main.py`를 다시 실행해 파일을 생성했다.

저장 경로를 이미 `model_state_path`에 구성했으므로 `torch.save`에는 해당 경로를 그대로 전달한다. 이 파일은 추론용 파라미터 저장이며, optimizer·epoch·난수 상태를 포함한 학습 재개용 체크포인트는 아니다.

### 3.4 CPU 복원과 결과 대조

```python
model = SimpleANN()
state = torch.load(model_state_path, map_location="cpu", weights_only=True)
model.load_state_dict(state)
```

저장할 때와 같은 모델 구조에 파라미터를 적용한다. `load_state_dict`는 사전을 클래스로 변환하는 함수가 아니라, 이미 생성한 모델에 저장된 파라미터를 적용하는 함수다.

복원 후에는 다시 학습하지 않고 `eval()`·`no_grad()`로 valid를 예측한다. 저장된 CSV와 valid ID 순서 및 클래스 예측의 일치를 확인한다. 서로 다른 장치에서 logits의 마지막 비트까지 일치하는지 검사하는 것은 아니다.

## 4. 직접 실행한 결과

이번 보고서를 작성하며 `main.py`를 실행하고 별도 프로세스로 `restore.py`를 실행했다. 아래 값은 제공된 expected 파일을 복사한 값이 아니라 이번 실행으로 생성한 `outputs` 파일과 콘솔에서 확인한 값이다.

| 항목                         |     결과 |
| ---------------------------- | -------: |
| 실행 장치                    |      cpu |
| epoch 수                     |       80 |
| 학습 전 전체 train 평가 loss | 0.565832 |
| epoch 80 online train loss   | 0.090861 |
| 학습 후 전체 train 평가 loss | 0.089844 |
| 최종 valid loss              | 0.057217 |
| 최종 valid 정확도            |   1.0000 |
| test 사용                    |    False |
| 복원 후 ID 순서 일치         |     True |
| 복원 후 클래스 예측 일치     |     True |

학습 기록은 epoch 1~80의 80행이며 콘솔에는 10 epoch 간격으로 출력한다. online loss와 고정 모델 평가 loss는 측정 시점이 달라 동일할 필요가 없다. 현재 valid 정확도가 100%라는 결과를 새로운 데이터에서도 성능이 보장된다는 의미로 해석하지 않는다.

실제 환경 기록은 PyTorch `2.14.0+cu130`, CUDA build `13.0`, `cuda_available=False`다. CUDA 지원 빌드를 설치했어도 실행 장치는 CPU일 수 있다.

## 5. 검증 결과

| 검증                            | 결과                                                                                                 |
| ------------------------------- | ---------------------------------------------------------------------------------------------------- |
| main.py 학습·기록·저장          | 정상 종료, 80개 epoch 기록 확인                                                                      |
| restore.py 별도 프로세스 실행   | 정상 종료, ID 순서·예측 모두 True                                                                    |
| model_state.pt 형식             | weights_only=True로 로드 가능한 Tensor 사전 확인                                                     |
| 마지막 배치 가중 평균 별도 검사 | 7건을 3·3·1로 나눔. 학습률 0에서 배치 집계 0.49240296과 전체 loss 0.49240294가 소수점 5자리까지 일치 |
| 학습 갱신 별도 검사             | 학습률 0.1에서 파라미터가 실제로 변경됨을 확인                                                       |
| 평가 비학습성 별도 검사         | 평가 전후 파라미터와 기존 gradient 보존, CPU 예측과 requires_grad=False 확인                         |
| 제공 unittest | 최신 코드로 재실행한 결과 H11·H12 테스트 2개 모두 통과 |

별도 검사는 실제 `train_one_epoch()`와 `evaluate()`를 호출하고 assertion으로 확인했다. 이어서 제공 테스트의 H11·H12도 구현했다. H11은 배치 가중 평균과 전체 loss를 소수점 5자리까지 비교하고, H12는 평가 전후 파라미터·기존 gradient의 일치와 예측의 requires_grad=False를 검사한다. 두 테스트 모두 통과했다.

최신 테스트 실행 기록:

```text
test_evaluation_does_not_learn ... ok
test_last_batch_weighting ... ok

Ran 2 tests
OK
```

H12에서는 반환되는 loss와 accuracy를 사용하지 않아 `_`로 받았다. 평가 전후 파라미터끼리, gradient끼리 각각 비교하며 파라미터와 gradient를 서로 비교하는 것은 아니다.

프로젝트 폴더에서 재현할 명령은 다음과 같다.

```bash
python main.py
python restore.py
python -m unittest discover -s tests -v
```

세 명령 모두 정상 종료를 확인했다. 장치·버전이 바뀌면 학습 수치가 달라질 수 있으므로 실행 환경도 함께 확인해야 한다.

## 6. 생성물과 커밋 범위

`outputs/`에는 `training_history.csv`, `final_metrics.json`, `validation_predictions.csv`, `gpu_check.txt`, `model_state.pt`를 생성한다. 이 폴더는 프로젝트의 `.gitignore`로 제외되어 있으며 커밋에는 소스와 이 보고서만 포함한다.

변경은 학습 갱신, 평가 예측, state_dict 저장, CPU 복원, 자동검사, 구현 보고서 단위로 나눈다. 기존에 커밋된 앞선 실습과 이번 변경을 함께 묶어 다시 커밋하지 않는다.
