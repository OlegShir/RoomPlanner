from app.roomplanner import RoomPlanner
from app.visualizer import visualize


room_size = (400, 600)
cell_size = 20
doors = [(0, 200, 20, 90)]
windows = [(100, 0, 180, 20)]

planner = RoomPlanner(room_size, cell_size, doors, windows)
planner.calculate_weights()

# Размеры мебели в сантиметрах
planner.place_furniture("Туалетный столик", 60, 30, prefer_window=True)
planner.place_furniture("Двуспальная кровать", 200, 180, prefer_wall=True)
planner.place_furniture_near("Стул", 20, 20, near_name="Туалетный столик")
planner.place_furniture_around("Прикроватная тумбочка", 30, 30, target_name="Двуспальная кровать")
planner.place_wardrobe("Шкаф 1", 120, 60)
planner.place_wardrobe("Шкаф 2", 120, 60)

# Визуализация
visualize(planner)
