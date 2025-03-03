import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Mock the custom_logging module
sys.modules['custom_logging'] = MagicMock()

from dags.data_preprocessing.clean_reviews import clean_reviews_data

class TestCleanReviewsData(unittest.TestCase):
    def setUp(self):
        # Create mock data
        self.mock_data = {
            'compensation': ['None', 'None'],
            'user_id': [123, 456],
            'username': [' user1 ', ' user2 '],
            'found_funny': [0, 1],
            'hours': [10.5, 5.0],
            'page_order': [1, 2],
            'page': [1, 2],
            'early_access': [False, True],
            'products': ['["game1"]', '["game2"]'],  # Changed lists to JSON strings
            'date': [1710000000000, 1710500000000],  # Milliseconds timestamp
            'product_id': [1001, None],
            'review': [' Great game! ', ' Not bad ']
        }
        self.mock_df = pd.DataFrame(self.mock_data)
    
    def test_clean_reviews_data(self):
        # Call the function that performs the cleaning
        cleaned_df = clean_reviews_data(self.mock_df)
        
        # Assert the cleaned data is as expected
        self.assertNotIn('compensation', cleaned_df.columns)
        self.assertNotIn('user_id', cleaned_df.columns)
        self.assertNotIn('username', cleaned_df.columns)
        self.assertNotIn('found_funny', cleaned_df.columns)
        self.assertNotIn('hours', cleaned_df.columns)
        self.assertNotIn('page_order', cleaned_df.columns)
        self.assertNotIn('page', cleaned_df.columns)
        self.assertNotIn('early_access', cleaned_df.columns)
        self.assertNotIn('products', cleaned_df.columns)
        self.assertNotIn('date', cleaned_df.columns)
        
        self.assertEqual(cleaned_df['id'].dtype, int)
        self.assertEqual(cleaned_df['review'].dtype, object)
        self.assertEqual(cleaned_df.shape[0], 2)  # Ensure 2 rows after cleaning
        self.assertEqual(cleaned_df['review'].iloc[0], 'Great game!')  # Check whitespace trimming
    
    def test_no_duplicate_rows(self):
        duplicate_df = pd.concat([self.mock_df, self.mock_df], ignore_index=True)
        cleaned_df = clean_reviews_data(duplicate_df)
        self.assertEqual(cleaned_df.shape[0], 2)  # Ensure duplicates are removed
    
    def test_product_id_fillna(self):
        cleaned_df = clean_reviews_data(self.mock_df)
        self.assertTrue((cleaned_df['id'] >= 0).all())  # Ensure NaN values are replaced with 0
    
    def test_review_trimmed(self):
        cleaned_df = clean_reviews_data(self.mock_df)
        self.assertEqual(cleaned_df['review'].iloc[0], 'Great game!')  # Ensure whitespace is trimmed
        self.assertEqual(cleaned_df['review'].iloc[1], 'Not bad')

if __name__ == '__main__':
    unittest.main()
