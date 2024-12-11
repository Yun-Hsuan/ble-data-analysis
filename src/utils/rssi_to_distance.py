from abc import ABC, abstractmethod

class RSSIToDistanceModel(ABC):
    @abstractmethod
    def convert(self, rssi: float) -> float:
        """Convert RSSI to distance."""
        pass

class LookupTableModel(RSSIToDistanceModel):
    def __init__(self, lookup_table: dict):
        """
        Initialize with a lookup table.
        :param lookup_table: {rssi: distance, ...}
        """
        self.lookup_table = lookup_table

    def convert(self, rssi: float) -> float:
        """Find the closest RSSI value in the table."""
        closest_rssi = min(self.lookup_table.keys(), key=lambda x: abs(x - rssi))
        return self.lookup_table[closest_rssi]
    
class FreeSpaceModel(RSSIToDistanceModel):
    def __init__(self, rssi_at_1m: float = -40, path_loss_exponent: float = 2.0):
        self.rssi_at_1m = rssi_at_1m
        self.path_loss_exponent = path_loss_exponent

    def convert(self, rssi: float) -> float:
        """Apply the Free Space Path Loss Model."""
        return 10 ** ((self.rssi_at_1m - rssi) / (10 * self.path_loss_exponent))
    
class LogDistanceModel(RSSIToDistanceModel):
    def __init__(self, rssi_at_1m: float = -40, path_loss_exponent: float = 3.0):
        self.rssi_at_1m = rssi_at_1m
        self.path_loss_exponent = path_loss_exponent

    def convert(self, rssi: float) -> float:
        """Apply the Log-distance Path Loss Model."""
        return 10 ** ((self.rssi_at_1m - rssi) / (10 * self.path_loss_exponent))
    
class MachineLearningModel(RSSIToDistanceModel):
    def __init__(self, model):
        """
        Initialize with a pre-trained machine learning model.
        :param model: A scikit-learn or similar regressor model
        """
        self.model = model

    def convert(self, rssi: float) -> float:
        """Use the ML model to predict distance."""
        return self.model.predict([[rssi]])[0]