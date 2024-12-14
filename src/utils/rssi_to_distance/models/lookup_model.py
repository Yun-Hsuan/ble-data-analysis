from utils.rssi_to_distance.base_model import RSSIToDistanceModel

class LookupTableModel(RSSIToDistanceModel):
    def __init__(self, lookup_table: dict):
        self.lookup_table = lookup_table

    def convert(self, rssi: float) -> float:
        closest_rssi = min(self.lookup_table.keys(), key=lambda x: abs(x - rssi))
        return self.lookup_table[closest_rssi]