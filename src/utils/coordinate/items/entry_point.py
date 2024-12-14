from typing import Tuple
from utils.coordinate.base_item import BaseItem

class EntryPoint(BaseItem):
    """
    Represents an entry point (line) on the FloorMap.
    """

    def __init__(self, name: str, start: Tuple[int, int], end: Tuple[int, int], metadata: dict = None):
        """
        Initialize an entry point with its start and end coordinates.

        :param name: Unique name of the entry point.
        :param start: Start point of the entry (x1, y1).
        :param end: End point of the entry (x2, y2).
        :param metadata: Optional metadata dictionary for additional information.
        """
        super().__init__(name, metadata)
        self.start = start
        self.end = end

    def get_position(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Get the start and end coordinates of the entry point.

        :return: ((x1, y1), (x2, y2)) start and end coordinates of the line.
        """
        return self.start, self.end

    def __str__(self):
        """
        String representation of the entry point.
        """
        return f"EntryPoint(Name={self.name}, Start={self.start}, End={self.end}, Metadata={self.metadata})"