from abc import ABC, abstractmethod
from typing import Any

class BaseItem(ABC):
    """
    Abstract base class for items that can be marked on the FloorMap.
    """

    def __init__(self, name: str, metadata: dict = None):
        """
        Initialize the item with a name and optional metadata.

        :param name: Unique name of the item.
        :param metadata: Optional dictionary to store additional information.
        """
        self.name = name
        self.metadata = metadata or {}

    @abstractmethod
    def get_position(self) -> Any:
        """
        Abstract method to get the position or bounds of the item.
        Must be implemented by subclasses.
        """
        pass

    def __str__(self):
        """
        String representation of the item.
        """
        return f"{self.__class__.__name__}(Name={self.name}, Metadata={self.metadata})"