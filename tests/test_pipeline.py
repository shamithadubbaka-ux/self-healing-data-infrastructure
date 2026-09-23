import unittest

import pandas as pd

from core.transformer import clean_data
from core.validator import run_validation


class TestSelfHealingPipeline(unittest.TestCase):

    def test_clean_data_removes_duplicates(self):

        dataframe = pd.DataFrame(
            {
                "customer_id": [1, 1],
                "name": ["A", "A"],
                "age": [25, 25],
                "email": [
                    "a@example.com",
                    "a@example.com",
                ],
                "city": [
                    "Hyderabad",
                    "Hyderabad",
                ],
                "purchase_amount": [100, 100],
                "purchase_date": [
                    "2025-01-01",
                    "2025-01-01",
                ],
            }
        )

        cleaned = clean_data(
            dataframe
        )

        self.assertEqual(
            len(cleaned),
            1,
        )

    def test_validator_detects_invalid_age(self):

        dataframe = pd.DataFrame(
            {
                "customer_id": [1],
                "name": ["A"],
                "age": [150],
                "email": [
                    "a@example.com"
                ],
                "city": ["Hyderabad"],
                "purchase_amount": [100],
                "purchase_date": [
                    "2025-01-01"
                ],
            }
        )

        result = run_validation(
            dataframe
        )

        self.assertFalse(
            result.is_valid
        )


if __name__ == "__main__":

    unittest.main()