import unittest
import pandas as pd
from USAggregate.usaggregate import usaggregate

class TestUSAggregate(unittest.TestCase):

    def setUp(self):
        # Create sample data for testing
        self.data_city = pd.DataFrame({
            'city': ['Albany', 'Albany', 'Buffalo', 'Buffalo'],
            'state': ['NY', 'NY', 'NY', 'NY'],
            'value': [1, 2, 3, 4],
            'year': [2017, 2018, 2017, 2018]
        })

        self.data_county = pd.DataFrame({
            'county': ['Albany', 'Albany', 'Erie', 'Erie'],
            'state': ['NY', 'NY', 'NY', 'NY'],
            'value': [5, 6, 7, 8],
            'year': [2017, 2018, 2017, 2018]
        })

    def test_single_dataframe_city(self):
        # Test single DataFrame aggregation at city level
        result = usaggregate([self.data_city], level='city')
        self.assertTrue('GEO_ID' in result.columns)
        self.assertEqual(result[result['year'] == 2017].shape[0], 2)
        self.assertEqual(result[result['year'] == 2018].shape[0], 2)

    def test_single_dataframe_county(self):
        # Test single DataFrame aggregation at county level
        result = usaggregate([self.data_county], level='county')
        self.assertTrue('GEO_ID' in result.columns)
        self.assertEqual(result[result['year'] == 2017].shape[0], 2)
        self.assertEqual(result[result['year'] == 2018].shape[0], 2)

    def test_multiple_dataframes_same_level(self):
        # Test aggregation with multiple DataFrames at the same level
        data1 = self.data_city.copy()
        data1['value'] = [10, 20, 30, 40]
        result = usaggregate([self.data_city, data1], level='city')
        self.assertTrue('GEO_ID' in result.columns)
        self.assertEqual(result[result['year'] == 2017].shape[0], 2)
        self.assertEqual(result[result['year'] == 2018].shape[0], 2)

    def test_multiple_years(self):
        # Test handling multiple years of data
        result = usaggregate([self.data_city, self.data_county], level='state')
        self.assertTrue('year' in result.columns)
        self.assertEqual(result[result['year'] == 2017].shape[0], 1)
        self.assertEqual(result[result['year'] == 2018].shape[0], 1)

    def test_incompatible_levels(self):
        # Test error raising for incompatible levels
        with self.assertRaises(ValueError):
            usaggregate([self.data_city, self.data_county], level='city')

if __name__ == '__main__':
    unittest.main()