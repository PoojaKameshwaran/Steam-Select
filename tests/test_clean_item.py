import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Add the project root directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Mock the custom_logging module
sys.modules['custom_logging'] = MagicMock()

# from dags.data_preprocessing.clean_reviews import clean_reviews_data
from dags.data_preprocessing.clean_item import clean_item_data

class TestCleanItemData(unittest.TestCase):
    def setUp(self):
        self.mock_data = {
            'id': [1, 2],
            'app_name': ['Game A ', ' Game B'],
            'genres': [['Action', 'Adventure'], ['RPG']],
            'sentiment': ['Overwhelmingly Positive', '100 user reviews'],
            'tags': ['tag1', 'tag2'],
            'reviews_url': ['url1', 'url2']
        }
        self.mock_df = pd.DataFrame(self.mock_data)
    
    def test_clean_item_data(self):
        cleaned_df = clean_item_data(self.mock_df)
        self.assertNotIn('tags', cleaned_df.columns)
        self.assertNotIn('reviews_url', cleaned_df.columns)
        self.assertEqual(cleaned_df.shape[0], 2)
        self.assertEqual(cleaned_df.columns.tolist(), ['Game_ID', 'Game', 'genres', 'sentiment'])
        self.assertEqual(cleaned_df['sentiment'].iloc[1], 'Mixed')
    
    # def test_no_duplicate_rows(self):
    #     duplicate_df = pd.concat([self.mock_df, self.mock_df], ignore_index=True)
    #     cleaned_df = clean_item_data(duplicate_df)
    #     self.assertEqual(cleaned_df.shape[0], 2)
    
    def test_genres_tuple_conversion(self):
        cleaned_df = clean_item_data(self.mock_df)
        self.assertIsInstance(cleaned_df['genres'].iloc[0], tuple)
    
    def test_game_id_type(self):
        cleaned_df = clean_item_data(self.mock_df)
        self.assertEqual(cleaned_df['Game_ID'].dtype, 'Int64')

if __name__ == '__main__':
    unittest.main()