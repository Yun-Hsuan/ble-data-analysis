import unittest
from src.utils.coordinate.floor_map import FloorMap
from src.utils.coordinate.items.entry_point import EntryPoint
from src.utils.coordinate.items.store import Store
from src.utils.coordinate.items.terminal import Terminal
from src.utils.coordinate.items.obstacle import Obstacle


class TestFloorMap(unittest.TestCase):
    def setUp(self):
        """
        Set up the FloorMap and test items for each test case.
        """
        self.floor_map = FloorMap(name="Floor 1", bounds=(0, 0, 200, 200))

        # Entry points
        self.entry_point_1 = EntryPoint(name="Main Entrance", start=(10, 20), end=(30, 40))
        self.entry_point_2 = EntryPoint(name="Side Entrance", start=(50, 60), end=(70, 80))

        # Stores
        self.store_1 = Store(name="Store A", top_left=(50, 50), bottom_right=(150, 150), category="Retail")
        self.store_2 = Store(name="Store B", top_left=(160, 50), bottom_right=(200, 100), category="Grocery")

        # Terminals
        self.terminal_1 = Terminal(name="Terminal 1", position=(100, 100), serial_number="T1")
        self.terminal_2 = Terminal(name="Terminal 2", position=(150, 150), serial_number="T2")

        # Obstacles
        self.obstacle_1 = Obstacle(name="Wall 1", top_left=(20, 20), bottom_right=(40, 40))
        self.obstacle_2 = Obstacle(name="Wall 2", top_left=(60, 60), bottom_right=(90, 90))

    def test_add_and_get_entry_points(self):
        self.floor_map.add_item("entry_points", self.entry_point_1)
        self.floor_map.add_item("entry_points", self.entry_point_2)

        entry_points = self.floor_map.get_items("entry_points")
        self.assertEqual(len(entry_points), 2)
        self.assertEqual(entry_points[0].name, "Main Entrance")
        self.assertEqual(entry_points[1].name, "Side Entrance")

    def test_add_and_get_stores(self):
        self.floor_map.add_item("stores", self.store_1)
        self.floor_map.add_item("stores", self.store_2)

        stores = self.floor_map.get_items("stores")
        self.assertEqual(len(stores), 2)
        self.assertEqual(stores[0].name, "Store A")
        self.assertEqual(stores[1].name, "Store B")

    def test_add_and_get_terminals(self):
        self.floor_map.add_item("terminals", self.terminal_1)
        self.floor_map.add_item("terminals", self.terminal_2)

        terminals = self.floor_map.get_items("terminals")
        self.assertEqual(len(terminals), 2)
        self.assertEqual(terminals[0].name, "Terminal 1")
        self.assertEqual(terminals[1].name, "Terminal 2")

    def test_add_and_get_obstacles(self):
        self.floor_map.add_item("obstacles", self.obstacle_1)
        self.floor_map.add_item("obstacles", self.obstacle_2)

        obstacles = self.floor_map.get_items("obstacles")
        self.assertEqual(len(obstacles), 2)
        self.assertEqual(obstacles[0].name, "Wall 1")
        self.assertEqual(obstacles[1].name, "Wall 2")

    def test_remove_entry_point(self):
        self.floor_map.add_item("entry_points", self.entry_point_1)
        self.floor_map.add_item("entry_points", self.entry_point_2)

        self.floor_map.remove_item("entry_points", "Main Entrance")
        entry_points = self.floor_map.get_items("entry_points")
        self.assertEqual(len(entry_points), 1)
        self.assertEqual(entry_points[0].name, "Side Entrance")

    def test_remove_store(self):
        self.floor_map.add_item("stores", self.store_1)
        self.floor_map.add_item("stores", self.store_2)

        self.floor_map.remove_item("stores", "Store A")
        stores = self.floor_map.get_items("stores")
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0].name, "Store B")

    def test_remove_terminal(self):
        self.floor_map.add_item("terminals", self.terminal_1)
        self.floor_map.add_item("terminals", self.terminal_2)

        self.floor_map.remove_item("terminals", "Terminal 1")
        terminals = self.floor_map.get_items("terminals")
        self.assertEqual(len(terminals), 1)
        self.assertEqual(terminals[0].name, "Terminal 2")

    def test_remove_obstacle(self):
        self.floor_map.add_item("obstacles", self.obstacle_1)
        self.floor_map.add_item("obstacles", self.obstacle_2)

        self.floor_map.remove_item("obstacles", "Wall 1")
        obstacles = self.floor_map.get_items("obstacles")
        self.assertEqual(len(obstacles), 1)
        self.assertEqual(obstacles[0].name, "Wall 2")

    def test_floor_map_str(self):
        self.floor_map.add_item("entry_points", self.entry_point_1)
        self.floor_map.add_item("stores", self.store_1)
        self.floor_map.add_item("terminals", self.terminal_1)
        self.floor_map.add_item("obstacles", self.obstacle_1)

        expected_str = (
            "FloorMap(Name=Floor 1, Bounds=(0, 0, 200, 200), "
            "Items={'entry_points': ['Main Entrance'], 'stores': ['Store A'], "
            "'terminals': ['Terminal 1'], 'obstacles': ['Wall 1']})"
        )
        self.assertEqual(str(self.floor_map), expected_str)


if __name__ == "__main__":
    unittest.main()