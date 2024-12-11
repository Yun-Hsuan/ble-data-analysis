from abc import ABC, abstractmethod

class RSSIToDistanceModel(ABC):
    @abstractmethod
    def convert(self, rssi: float) -> float:
        """Convert RSSI to distance."""
        pass