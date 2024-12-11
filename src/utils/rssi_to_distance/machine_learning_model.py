from .base_model import RSSIToDistanceModel

class MachineLearningModel(RSSIToDistanceModel):
    def __init__(self, model):
        self.model = model

    def convert(self, rssi: float) -> float:
        return self.model.predict([[rssi]])[0]