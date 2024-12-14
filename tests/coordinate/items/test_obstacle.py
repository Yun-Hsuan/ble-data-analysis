import unittest
from src.utils.coordinate.items.obstacle import Obstacle

class TestObstacle(unittest.TestCase):
    def setUp(self):
        self.obstacle = Obstacle(
            name="Wall 1",
            top_left=(10, 20),
            bottom_right=(50, 60),
            metadata={"type": "wall", "material": "concrete"}
        )

    def test_get_position(self):
        self.assertEqual(
            self.obstacle.get_position(),
            ((10, 20), (50, 60))
        )

    def test_metadata(self):
        self.assertEqual(self.obstacle.metadata["type"], "wall")
        self.assertEqual(self.obstacle.metadata["material"], "concrete")

    def test_invalid_obstacle(self):
        with self.assertRaises(ValueError):
            Obstacle(name="Invalid Wall", top_left=(50, 60), bottom_right=(10, 20))

if __name__ == "__main__":
    unittest.main()