from typing import Tuple
from utils.coordinate.base_item import BaseItem

class Store(BaseItem):
    """
    Represents a store area on the FloorMap.
    """

    def __init__(self, name: str, top_left: Tuple[int, int], bottom_right: Tuple[int, int], category: str, metadata: dict = None):
        """
        Initialize a store with its bounds and category.

        :param name: Unique name of the store.
        :param top_left: Top-left corner of the store.
        :param bottom_right: Bottom-right corner of the store.
        :param category: Category of the store (e.g., "Retail", "Food").
        :param metadata: Optional metadata dictionary.
        """
        super().__init__(name, metadata)
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.category = category

    def get_position(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Get the bounds of the store.

        :return: ((x1, y1), (x2, y2)) bounds of the store.
        """
        return self.top_left, self.bottom_right

    def __str__(self):
        """
        String representation of the store.
        """
        return f"Store(Name={self.name}, Category={self.category}, Bounds=({self.top_left}, {self.bottom_right}), Metadata={self.metadata})"