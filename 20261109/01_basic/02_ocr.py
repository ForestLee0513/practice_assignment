"""실습 02: Tesseract를 실제 호출합니다. 엔진과 eng 언어팩이 필요합니다."""
from pathlib import Path
import os
import pandas as pd
import pytesseract
import cv2

base = Path(__file__).resolve().parent
# Windows에서 PATH 설정이 어려우면 환경변수 TESSERACT_CMD에 exe 경로를 지정합니다.
pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_CMD', 'tesseract')
paths = [str(base / f'doc{i:02d}.png') for i in range(1, 4)]
input_list = base / 'p02_inputs.txt'
input_list.write_text('\n'.join(paths), encoding='utf-8')
# 여러 페이지를 목록으로 전달해 엔진을 한 번 호출합니다.
# TODO B02

# 방법 1: 목록 전체를 전달하여 Tesseract를 한 번 호출합니다.
words = pytesseract.image_to_data(
    str(input_list),
    lang='eng',
    config='--psm 6',
    output_type=pytesseract.Output.DATAFRAME
)

# 방법 2: 이미지별 전처리 후 각각 OCR을 실행합니다.
# 방법 2를 사용하려면 방법 1을 주석 처리하고 아래 블록을 해제합니다.
# ocr_results = []
# with open(input_list, "r", encoding="utf-8") as file:
#     image_paths = [line.strip() for line in file if line.strip()]
#     for page_number, path in enumerate(image_paths, start=1):
#         # cv2 image => binary
#         image = cv2.imread(path)
#         if image is None:
#             raise FileNotFoundError(f"이미지를 읽을 수 없습니다: {path}")
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#         _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
#         # cv2 binary => tesseract ocr => pd2 dataframe
#         ocr = pytesseract.image_to_data(
#             binary, lang="kor+eng", config="--oem 3 --psm 6",
#             output_type=pytesseract.Output.DATAFRAME,
#             pandas_config={
#                 "keep_default_na": False,
#                 "dtype": { "text": str }
#             }
#         )

#         # 단일 이미지 OCR의 page_num은 1이므로 원본 페이지 번호를 지정합니다.
#         ocr['page_num'] = page_number
#         ocr_results.append(ocr)

# # concat all dataframes into single dataframe
# words = pd.concat(ocr_results, ignore_index=True) if ocr_results else pd.DataFrame(
#     columns=['page_num', 'text', 'conf']
# )
# TODO 끝 B02
words = words.dropna(subset=['text'])
words = words[words['text'].astype(str).str.strip().ne('')]
words = words[words['conf'] >= 0]
words.to_csv(base / 'p02_words.csv', index=False, encoding='utf-8-sig')
for page, rows in words.groupby('page_num', sort=True):
    text = ' '.join(rows['text'].astype(str))
    print('page:', page, 'words:', len(rows), 'mean confidence:', round(rows['conf'].mean(), 2))
    print(text)
print('backend: live Tesseract; confidence는 정답 확률이 아닙니다.')
