from typing import Tuple
from utils.coordinate.base_item import BaseItem

class Obstacle(BaseItem):
    """
    Represents a rectangular obstacle on the FloorMap.
    """

    def __init__(self, name: str, top_left: Tuple[int, int], bottom_right: Tuple[int, int], metadata: dict = None):
        """
        Initialize an obstacle with its bounds.

        :param name: Unique name of the obstacle.
        :param top_left: Top-left corner of the rectangle (x, y).
        :param bottom_right: Bottom-right corner of the rectangle (x, y).
        :param metadata: Optional metadata dictionary for additional information.
        """
        super().__init__(name, metadata)
        if (
            top_left[0] >= bottom_right[0]
            or top_left[1] >= bottom_right[1]
        ):
            raise ValueError("Invalid rectangle coordinates: top-left must be above and to the left of bottom-right.")
        
        self.top_left = top_left
        self.bottom_right = bottom_right

    def get_position(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Get the top-left and bottom-right coordinates of the obstacle.

        :return: ((x1, y1), (x2, y2)) bounds of the obstacle.
        """
        return self.top_left, self.bottom_right

    def __str__(self):
        """
        String representation of the obstacle.
        """
        return f"Obstacle(Name={self.name}, TopLeft={self.top_left}, BottomRight={self.bottom_right}, Metadata={self.metadata})"