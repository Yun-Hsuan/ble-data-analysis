from typing import Tuple
from utils.coordinate.base_item import BaseItem

class Terminal(BaseItem):
    """
    Represents a BLE terminal on the FloorMap.
    """

    def __init__(self, name: str, position: Tuple[int, int], serial_number: str = None, metadata: dict = None):
        """
        Initialize a terminal with its position and optional serial number.

        :param name: Unique name of the terminal.
        :param position: (x, y) position of the terminal.
        :param serial_number: Serial number of the terminal.
        :param metadata: Optional metadata dictionary.
        """
        super().__init__(name, metadata)
        self.position = position
        self.serial_number = serial_number

    def get_position(self) -> Tuple[int, int]:
        """
        Get the position of the terminal.

        :return: (x, y) position of the terminal.
        """
        return self.position

    def __str__(self):
        """
        String representation of the terminal.
        """
        return f"Terminal(Name={self.name}, Position={self.position}, Serial={self.serial_number}, Metadata={self.metadata})"