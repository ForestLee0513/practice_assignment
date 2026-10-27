"""새 범주 처리와 필수 입력 열 누락을 검사합니다.

현재 폴더에서 실행: python -m unittest -v test_preprocessing.py
"""
import unittest

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor

from preprocessing import FEATURES, build_model


class PreprocessingTests(unittest.TestCase):
    def setUp(self):
        # 검사용 가상 데이터만 사용하므로 train·valid·test 원본에 영향을 주지 않습니다.
        self.X = pd.DataFrame({
            "input_chars": [100, 200, 300, 400],
            "allowed_tools": [1, 2, 3, 2],
            "task_type": ["qa", "summary", "qa", "summary"],
            "priority": ["low", "normal", "normal", "low"],
        })
        self.model = build_model(DecisionTreeRegressor(random_state=42))
        self.model.fit(self.X, [1000, 2000, 3000, 4000])

    def test_new_category(self):
        """학습에 없던 범주를 해당 원핫 구간의 0으로 처리해야 합니다."""
        pre = self.model["pre"]
        encoder = pre.named_transformers_["cat"]["encoder"]
        category_start = pre.output_indices_["cat"].start
        expected_width = pre.transform(self.X.iloc[[0]]).shape[1]

        for column, categories in zip(FEATURES[2:], encoder.categories_):
            with self.subTest(column=column):
                new = self.X.iloc[[0]].copy()
                new[column] = "unseen_category"
                transformed = pre.transform(new)

                # 새 범주 때문에 출력 열이 늘거나 숫자가 유효하지 않게 되면 실패합니다.
                self.assertEqual(transformed.shape, (1, expected_width))
                self.assertTrue(np.isfinite(transformed).all())
                np.testing.assert_array_equal(
                    transformed[:, category_start:category_start + len(categories)],
                    np.zeros((1, len(categories))),
                )
                prediction = self.model.predict(new)
                self.assertEqual(prediction.shape, (1,))
                self.assertTrue(np.isfinite(prediction).all())
                print(
                    f"\n[통과] 새 범주 | 열={column} | 입력=unseen_category"
                    f" | 변환 크기={transformed.shape}"
                    f" | 해당 원핫 구간={transformed[:, category_start:category_start + len(categories)].tolist()}"
                    f" | 예측(ms)={prediction.tolist()}",
                    flush=True,
                )
            category_start += len(categories)

    def test_missing_required_column(self):
        """필수 입력 열이 하나라도 빠지면 예측을 거부해야 합니다."""
        for column in FEATURES:
            with self.subTest(column=column):
                missing = self.X.drop(columns=[column])
                with self.assertRaises(ValueError) as caught:
                    self.model.predict(missing)
                print(
                    f"\n[통과] 필수열 누락 | 제거한 열={column}"
                    f" | 예상 오류=ValueError | 실제 오류={caught.exception}",
                    flush=True,
                )


if __name__ == "__main__":
    unittest.main()
