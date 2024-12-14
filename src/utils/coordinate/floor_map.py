from utils.coordinate.items.entry_point import EntryPoint
from utils.coordinate.items.store import Store
from utils.coordinate.items.terminal import Terminal
from utils.coordinate.items.obstacle import Obstacle


class FloorMap:
    def __init__(self, name, bounds):
        """
        Initialize the FloorMap
        :param name: The name of the floor
        :param bounds: (min_x, min_y, max_x, max_y) representing the boundaries
        """
        self.name = name
        self.bounds = bounds
        self.items = {
            "entry_points": [],
            "stores": [],
            "terminals": [],
            "obstacles": [],
        }

    def add_item(self, item_type, item):
        """
        Add an item of any type
        :param item_type: The type of the item (e.g., "entry_points", "stores")
        :param item: The item object to be added
        """
        if item_type not in self.items:
            self.items[item_type] = []  # Dynamically support new types
        self.items[item_type].append(item)

    def get_items(self, item_type):
        """
        Retrieve all items of a given type
        :param item_type: The type of the item
        :return: List of item objects
        """
        if item_type not in self.items:
            raise KeyError(f"{item_type[:-1].capitalize()} type not found.")
        return self.items[item_type]

    def remove_item(self, item_type, item_name):
        """
        Remove an item of any type by name
        :param item_type: The type of the item
        :param item_name: The name of the item to be removed
        """
        if item_type not in self.items:
            raise KeyError(f"{item_type[:-1].capitalize()} type not found.")
        filtered_items = [item for item in self.items[item_type] if item.name != item_name]
        if len(filtered_items) == len(self.items[item_type]):
            raise KeyError(f"{item_type[:-1].capitalize()} '{item_name}' not found.")
        self.items[item_type] = filtered_items

    def __str__(self):
        """
        Return a summary of the FloorMap
        """
        items_summary = {key: [item.name for item in value] for key, value in self.items.items()}
        return f"FloorMap(Name={self.name}, Bounds={self.bounds}, Items={items_summary})"