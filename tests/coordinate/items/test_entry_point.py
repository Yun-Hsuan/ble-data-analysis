import unittest
from src.utils.coordinate.items.entry_point import EntryPoint

class TestEntryPoint(unittest.TestCase):
    def setUp(self):
        self.entry_point = EntryPoint(
            name="Main Entrance",
            start=(10, 20),
            end=(30, 40),
            metadata={"type": "door", "access": "public"}
        )

    def test_get_position(self):
        self.assertEqual(
            self.entry_point.get_position(),
            ((10, 20), (30, 40))
        )

    def test_metadata(self):
        self.assertEqual(self.entry_point.metadata["type"], "door")
        self.assertEqual(self.entry_point.metadata["access"], "public")

    def test_str_representation(self):
        self.assertEqual(
            str(self.entry_point),
            "EntryPoint(Name=Main Entrance, Start=(10, 20), End=(30, 40), Metadata={'type': 'door', 'access': 'public'})"
        )

if __name__ == "__main__":
    unittest.main()