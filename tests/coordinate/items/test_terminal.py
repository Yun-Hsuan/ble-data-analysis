import unittest
from src.utils.coordinate.items.terminal import Terminal

class TestTerminal(unittest.TestCase):
    def setUp(self):
        self.terminal = Terminal(
            name="Terminal 1",
            position=(100, 200),
            serial_number="SN12345",
            metadata={"status": "active", "type": "BLE"}
        )

    def test_get_position(self):
        self.assertEqual(
            self.terminal.get_position(),
            (100, 200)
        )

    def test_metadata(self):
        self.assertEqual(self.terminal.metadata["status"], "active")
        self.assertEqual(self.terminal.metadata["type"], "BLE")

    def test_serial_number(self):
        self.assertEqual(self.terminal.serial_number, "SN12345")

    def test_str_representation(self):
        self.assertEqual(
            str(self.terminal),
            "Terminal(Name=Terminal 1, Position=(100, 200), Serial=SN12345, Metadata={'status': 'active', 'type': 'BLE'})"
        )

if __name__ == "__main__":
    unittest.main()