import unittest
from src.utils.coordinate.items.store import Store

class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = Store(
            name="Store A",
            top_left=(50, 50),
            bottom_right=(150, 150),
            category="Retail",
            metadata={"owner": "John Doe", "floor": 1}
        )

    def test_get_position(self):
        self.assertEqual(
            self.store.get_position(),
            ((50, 50), (150, 150))
        )

    def test_metadata(self):
        self.assertEqual(self.store.metadata["owner"], "John Doe")
        self.assertEqual(self.store.metadata["floor"], 1)

    def test_category(self):
        self.assertEqual(self.store.category, "Retail")

    def test_str_representation(self):
        self.assertEqual(
            str(self.store),
            "Store(Name=Store A, Category=Retail, Bounds=((50, 50), (150, 150)), Metadata={'owner': 'John Doe', 'floor': 1})"
        )

if __name__ == "__main__":
    unittest.main()