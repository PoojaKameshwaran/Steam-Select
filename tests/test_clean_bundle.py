import unittest
from unittest.mock import patch
import pandas as pd
from your_script import clean_bundle_data  # Update with correct import

class TestDataCleaning(unittest.TestCase):
    
    # Test the cleaning logic directly on a DataFrame
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
        
        # Check that the 'bundle_final_price' and 'bundle_price' columns are converted to float
        self.assertEqual(cleaned_df['bundle_final_price'].dtype, float)
        self.assertEqual(cleaned_df['bundle_price'].dtype, float)
        
        # Check that 'bundle_discount' is a float (after conversion from percentage string)
        self.assertEqual(cleaned_df['bundle_discount'].dtype, float)
        
        # Ensure that 'items' column is now a list (after conversion from JSON-like string)
        self.assertEqual(type(cleaned_df['items'].iloc[0]), list)
        
        # Check that the 'bundle_id' column is of type integer
        self.assertEqual(cleaned_df['bundle_id'].dtype, int)
        
        # Verify that the shape of the cleaned data is correct (should be the same as the input)
        self.assertEqual(cleaned_df.shape[0], 2)  # Ensure 2 rows after cleaning

if __name__ == '__main__':
    unittest.main()
