import unittest
from utils.rssi_to_distance.models.lookup_model import LookupTableModel

class TestLookupTableModel(unittest.TestCase):
    def setUp(self):
        self.lookup_table = {-30: 1.0, -40: 3.0, -50: 10.0}
        self.model = LookupTableModel(self.lookup_table)

    def test_convert_exact_match(self):
        self.assertEqual(self.model.convert(-30), 1.0)

    def test_convert_closest_match(self):
        self.assertEqual(self.model.convert(-40), 3.0)

if __name__ == "__main__":
    unittest.main()