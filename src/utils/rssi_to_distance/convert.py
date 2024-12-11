from .base_model import RSSIToDistanceModel

class RSSIToDistanceConverter:
    def __init__(self, model: RSSIToDistanceModel):
        self.model = model

    def convert(self, rssi: float) -> float:
        return self.model.convert(rssi)