import unittest
import numpy as np

from app.roomplanner import RoomPlanner

class TestRoomPlanner(unittest.TestCase):
    def setUp(self):
        """Метод для подготовки данных перед каждым тестом."""
        room_size = (400, 600)
        cell_size = 20
        doors = [(0, 200, 20, 90)]
        windows = [(100, 0, 180, 20)]
        self.planner = RoomPlanner(room_size, cell_size, doors, windows)

    def test_initial_grid(self):
        """Тест для проверки начальной сетки."""
        self.assertTrue(np.all(self.planner.grid == 1), "Начальная сетка должна быть пустой.")

    def test_calculate_weights(self):
        """Тест для проверки расчетов веса с учетом дверей и окон."""
        self.planner.calculate_weights(influence_radius=8)
        self.assertFalse(np.all(self.planner.grid == 1), "Вес в ячейках должен измениться после расчета.")

    def test_place_furniture(self):
        """Тест для проверки размещения мебели."""
        self.planner.place_furniture("Туалетный столик", 60, 30, prefer_window=True)
        self.assertIn("Туалетный столик", self.planner.furniture_positions)

    def test_place_furniture_near(self):
        """Тест для размещения мебели рядом с другой мебелью."""
        self.planner.place_furniture("Туалетный столик", 60, 30, prefer_window=True)
        self.planner.place_furniture_near("Стул", 20, 20, near_name="Туалетный столик")
        self.assertIn("Стул", self.planner.furniture_positions)
        x_tu, y_tu, w_tu, h_tu = self.planner.furniture_positions["Туалетный столик"]
        x_st, y_st, w_st, h_st = self.planner.furniture_positions["Стул"]
        # Стул должен быть рядом с туалетным столиком
        self.assertTrue(abs(x_tu - x_st) <= w_tu + w_st or abs(y_tu - y_st) <= h_tu + h_st)

    def test_place_furniture_around(self):
        """Тест для размещения мебели вокруг другой."""
        self.planner.place_furniture("Двуспальная кровать", 200, 180, prefer_wall=True)
        self.planner.place_furniture_around("Прикроватная тумбочка", 30, 30, target_name="Двуспальная кровать")
        self.assertIn("Прикроватная тумбочка", self.planner.furniture_positions)
        x_bed, y_bed, w_bed, h_bed = self.planner.furniture_positions["Двуспальная кровать"]
        x_nightstand, y_nightstand, w_nightstand, h_nightstand = self.planner.furniture_positions["Прикроватная тумбочка"]
        self.assertTrue(abs(x_bed - x_nightstand) <= w_bed + w_nightstand or abs(y_bed - y_nightstand) <= h_bed + h_nightstand)

    def test_place_wardrobe(self):
        """Тест для размещения шкафа вдоль стены с учётом пространства для дверей."""
        self.planner.place_wardrobe("Шкаф1", 120, 60)
        self.assertIn("Шкаф1", self.planner.furniture_positions)

    def test_grid_after_furniture(self):
        """Тест для проверки сетки после размещения мебели."""
        self.planner.place_furniture("Туалетный столик", 60, 30, prefer_window=True)
        x, y, w, h = self.planner.furniture_positions["Туалетный столик"]
        self.assertTrue(np.all(self.planner.grid[y:y+h, x:x+w] == 0), "Область, занятая мебелью, должна быть свободной.")

    def test_placement_around_wardrobe(self):
        """Тест для размещения шкафа вокруг другой мебели."""
        self.planner.place_furniture("Туалетный столик", 60, 30, prefer_window=True)
        self.planner.place_wardrobe("Шкаф1", 120, 60)
        self.assertIn("Шкаф1", self.planner.furniture_positions)

if __name__ == "__main__":
    unittest.main()
