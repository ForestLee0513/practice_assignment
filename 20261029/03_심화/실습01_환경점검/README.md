# 환경 기록과 장치 연산

해당 폴더를 VS Code로 열어 `main.py`의 TODO를 완성합니다. 함수를 처음부터 재설계하지 않고 제공된 흐름을 사용합니다.

**H01** — CUDA 사용 가능 여부를 보고 실행할 장치를 선택하세요. 드라이버가 있다는 사실만으로 CUDA를 선택하지 마세요.

```powershell
python main.py
```

## 예상 출력

```text
{
  "torch": "2.10.0+cpu",
  "cuda_build": null,
  "cuda_available": false,
  "selected_device": "cpu",
  "calculation": [
    [
      5.0,
      11.0
    ],
    [
      11.0,
      25.0
    ]
  ]
}
```

CPU 검수 결과이며 device·버전과 학습 수치는 환경에 따라 달라질 수 있습니다. 상세 출력은 `expected/console.txt`에도 있습니다.

## 완료 조건

TODO의 계산을 코드로 확인하고 예상 결과와 비교합니다. 자신의 말로 입력 shape, 처리한 단계, 출력의 의미를 설명하세요. 단순히 실행 종료 코드가0인 것만으로 완료하지 않습니다.

## 내 기록

### 확인 과정

해당 과제의 조건은 nvidia GPU가 있고 드라이버가 설치 되어 있다고 해서 바로 pyTorch에 cuda로 지정하는 것이 아닌, 실제로 CUDA가 사용 가능한지 검증하는 과정을 확인하기 위함임.
확인한 결과는 아래와 같다.

#### CUDA 확인 여부 검증

```python

if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

```

`torch.cuda.is_available()`를 통해 CUDA가 실제로 사용 가능한지 확인하고 GPU에 문제가 발생하거나 CUDA가 인식이 안되는 경우 예외처리를 통해 CPU로 fallback하도록 구성했다.

#### 검증 결과

```json
{
  "torch": "2.14.0+cu130",
  "cuda_build": "13.0",
  "cuda_available": true,
  "selected_device": "cuda",
  "calculation": [
    [5.0, 11.0],
    [11.0, 25.0]
  ],
  "gpu_name": "NVIDIA GeForce RTX 5080 Laptop GPU",
  "vram_gib": 15.92047119140625
}
```

pyTorch 버전: 2.14.0+cu130
CUDA 빌드 버전: 13.0
CUDA 활성 여부: true
선택 장치: cuda - 여기서 GPU 여부를 검증
calculation 결과: [[5.0, 11.0], [11.0, 25.0]] - 입력값에 대한 연산 결과
gpu_name: NVIDIA GeForce RTX 5080 Laptop GPU - 사용 가능한 GPU 이름
vram_gib: 15.92047119140625 - 사용 가능한 GPU VRAM
