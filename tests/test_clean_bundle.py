import unittest
import pandas as pd
from dags.data_preprocessing.clean_bundle import clean_bundle_data

class TestCleanBundle(unittest.TestCase):
    def setUp(self):
        # Create a sample DataFrame for testing
        self.test_df = pd.DataFrame({
            'bundle_id': ['1', '2'],
            'bundle_final_price': ['$10.99', '$20.50'],
            'bundle_price': ['$15.99', '$25.00'],
            'bundle_discount': ['30%', '18%'],
            'items': ['[{"id": 1}]', '[{"id": 2}]']
        })

    def test_clean_bundle_data(self):
        cleaned_df = clean_bundle_data(self.test_df)
        
        # Check if data types are correct
        self.assertEqual(cleaned_df['bundle_id'].dtype, 'int64')
        self.assertEqual(cleaned_df['bundle_final_price'].dtype, 'float64')
        self.assertEqual(cleaned_df['bundle_price'].dtype, 'float64')
        self.assertEqual(cleaned_df['bundle_discount'].dtype, 'float64')
        
        # Check if values are correctly converted
        self.assertEqual(cleaned_df['bundle_final_price'].iloc[0], 10.99)
        self.assertEqual(cleaned_df['bundle_discount'].iloc[1], 18.0)
        
        # Check if items column is converted to list of dictionaries
        self.assertIsInstance(cleaned_df['items'].iloc[0], list)
        self.assertIsInstance(cleaned_df['items'].iloc[0][0], dict)

if __name__ == '__main__':
    unittest.main()
