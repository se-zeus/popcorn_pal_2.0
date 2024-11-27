import unittest
from unittest.mock import patch, MagicMock
from main import ConfigManager, Utility
from datetime import date, datetime
import pandas as pd


class TestUtility(unittest.TestCase):

    def test_convert_to_list(self):
        input_str = '["action","comedy","drama"]'
        expected_output = ["action", "comedy", "drama"]
        self.assertEqual(Utility.convert_to_list(input_str), expected_output)

    def test_convert_to_list_num(self):
        input_str = "[1,2,3,4]"
        expected_output = ["1", "2", "3", "4"]
        self.assertEqual(Utility.convert_to_list_num(input_str), expected_output)



if __name__ == "__main__":
    unittest.main()
