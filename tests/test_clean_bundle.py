import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Mock the custom_logging module
sys.modules['custom_logging'] = MagicMock()

from dags.data_preprocessing.clean_bundle import clean_bundle_data

class TestDataCleaning(unittest.TestCase):
    def test_clean_bundle_data(self):
        # Create mock data (simulating what would be read from the JSON file)
        mock_data = {
            'bundle_id': [1, 2],
            'bundle_final_price': ['$10.00', '$20.00'],
            'bundle_price': ['$15.00', '$25.00'],
            'bundle_discount': ['10%', '20%'],
            'items': ['[{"item_id": 1, "item_name": "itemA"}]', '[{"item_id": 2, "item_name": "itemB"}]']
        }
        mock_df = pd.DataFrame(mock_data)

        # Call the function that performs the cleaning
        cleaned_df = clean_bundle_data(mock_df)

        # Assert the cleaned data is as expected
        self.assertEqual(cleaned_df['bundle_final_price'].dtype, float)
        self.assertEqual(cleaned_df['bundle_price'].dtype, float)
        self.assertEqual(cleaned_df['bundle_discount'].dtype, float)
        self.assertEqual(type(cleaned_df['items'].iloc[0]), list)
        self.assertEqual(cleaned_df['bundle_id'].dtype, int)
        self.assertEqual(cleaned_df.shape[0], 2)  # Ensure 2 rows after cleaning

if __name__ == '__main__':
    unittest.main()
