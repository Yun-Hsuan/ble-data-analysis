from utils.rssi_to_distance.base_model import RSSIToDistanceModel

class FreeSpaceModel(RSSIToDistanceModel):
    def __init__(self, rssi_at_1m: float = -40, path_loss_exponent: float = 2.0):
        self.rssi_at_1m = rssi_at_1m
        self.path_loss_exponent = path_loss_exponent

    def convert(self, rssi: float) -> float:
        return 10 ** ((self.rssi_at_1m - rssi) / (10 * self.path_loss_exponent))