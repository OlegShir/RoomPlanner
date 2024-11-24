import os
from typing import Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt

class RoomPlanner:
    def __init__(self, room_size, cell_size, doors, windows, empty=2) -> None:
        """Инициализация параметров комнаты."""
        self.room_width, self.room_height = room_size
        self.cell_size = cell_size
        self.grid_width = int(self.room_width / self.cell_size)
        self.grid_height = int(self.room_height / self.cell_size)
        self.grid = np.ones((self.grid_height, self.grid_width))
        self.doors = [(x // cell_size, y // cell_size, (w + cell_size - 1) // cell_size, (h + cell_size - 1) // cell_size) for (x, y, w, h) in doors]
        self.windows = [(x // cell_size, y // cell_size, (w + cell_size - 1) // cell_size, (h + cell_size - 1) // cell_size) for (x, y, w, h) in windows]
        self.furniture_positions = {}
        self.empty = empty

    def _update_grid(self, name: str, best_position: Optional[Tuple[int, int]], width: int, height: int):
        """В случае если найдено подходящее место для мебели:
           добавляет ее в План, обновляет сетку, отмечая занятую область.
           Если нет - уведомляет об этом сообщением"""
        if best_position:
            x, y = best_position
            self.furniture_positions[name] = (x, y, width, height)
            x_start = max(0, x - self.empty)
            y_start = max(0, y - self.empty)
            x_end = min(self.grid_width, x + width + self.empty)
            y_end = min(self.grid_height, y + height + self.empty)
            self.grid[y_start:y_end, x_start:x_end] = 0
            return        
        print(f"Не удалось найти подходящее место для {name}.")


    def _can_place_furniture(self, x: int, y: int, width: int, height: int) -> bool:
        """Проверяет, можно ли разместить мебель в указанной области."""
        if x < 0 or y < 0 or x + width > self.grid_width or y + height > self.grid_height:
            return False
        return True      


    def calculate_weights(self, influence_radius=8):
        """Рассчитывает веса для всех клеток сетки с учетом влияния дверей и окон."""
        # Собираем все препятствия (двери и окна) в один список
        obstacles = self.doors + self.windows
        radius_sq = influence_radius**2
        for obj_x, obj_y, obj_w, obj_h in obstacles:
            # Рассчитываем область влияния препятствия
            x_start = max(0, obj_x - influence_radius)
            x_end = min(self.grid_width, obj_x + obj_w + influence_radius)
            y_start = max(0, obj_y - influence_radius)
            y_end = min(self.grid_height, obj_y + obj_h + influence_radius)
            # Создаем сетки координат для области влияния
            y_coords, x_coords = np.meshgrid(
                np.arange(y_start, y_end),
                np.arange(x_start, x_end),
                indexing="ij")
            # Вычисляем расстояние от текущей точки до препятствия
            dist_x = np.maximum(0, np.maximum(obj_x - x_coords, x_coords - (obj_x + obj_w)))
            dist_y = np.maximum(0, np.maximum(obj_y - y_coords, y_coords - (obj_y + obj_h)))
            distances_sq = dist_x**2 + dist_y**2
            # Учет влияния только в пределах радиуса
            influence_mask = distances_sq <= radius_sq
            distances = np.sqrt(distances_sq[influence_mask])
            # Обновляем веса: чем ближе к препятствию, тем меньше вес
            self.grid[y_coords[influence_mask], x_coords[influence_mask]] -= 1.0 / (1.0 + distances)
        self.grid = np.maximum(0, self.grid) # Гарантируем, что веса не будут отрицательными


    def place_furniture(self, name: str, width_cm:int, height_cm:int, prefer_window: bool=False, prefer_wall: bool=False):
        """Размещение мебели с учетом приоритетов."""
        best_score = -np.inf
        best_position = None
        width = int(np.ceil(width_cm / self.cell_size))
        height = int(np.ceil(height_cm / self.cell_size))
        for y in range(self.grid_height - height):
            for x in range(self.grid_width - width):
                total_score = self.grid[y:y+height, x:x+width].sum()  # Общий вес области
                # Увеличиваем приоритет для областей возле окон
                if prefer_window:
                    for window in self.windows:
                        window_x, window_y, window_w, window_h = window
                        dist_x = max(0, max(window_x - x, x - (window_x + window_w)))
                        dist_y = max(0, max(window_y - y, y - (window_y + window_h)))
                        distance = np.sqrt(dist_x**2 + dist_y**2)
                        if distance <= 5:
                            # Чем ближе к окну, тем лучше
                            total_score += 20.0 / (1 + distance)
                # Увеличиваем приоритет для областей возле стен
                if prefer_wall:
                    dist_to_wall = min(
                        x, self.grid_width - (x + width), y, self.grid_height - (y + height))
                    # Чем ближе к стене, тем лучше
                    total_score += 5.0 / (1 + dist_to_wall)
                if total_score > best_score:
                    best_score = total_score
                    best_position = (x, y)
        self._update_grid(name, best_position, width, height)


    def place_furniture_near(self, name: str, width_cm: int, height_cm: int, near_name: str) -> None:
        """Размещение мебели рядом с другой, с учетом примыкания к ней."""
        if near_name not in self.furniture_positions:
            print(f"Мебель '{near_name}' не найдена для размещения рядом.")
            return        
        # Получаем координаты и размеры мебели, рядом с которой нужно разместить
        x_near, y_near, w_near, h_near = self.furniture_positions[near_name]
        width = int(np.ceil(width_cm / self.cell_size))
        height = int(np.ceil(height_cm / self.cell_size))
        best_score = -np.inf
        best_position = None
        # Функция для оценки возможных позиций для мебели
        def evaluate_position(x: int, y:int) -> None:
            nonlocal best_score, best_position
            if self._can_place_furniture(x, y, width, height):
                area_weights = self.grid[y:y + height, x:x + width].sum()
                if area_weights > best_score:
                    best_score = area_weights
                    best_position = (x, y)
        # Примыкание снизу
        for x in range(x_near, x_near + w_near - width + 1):
            for y in range(y_near + h_near, min(self.grid_height, y_near + h_near + height)):
                evaluate_position(x, y)
        # Примыкание сверху
        for x in range(x_near, x_near + w_near - width + 1):
            for y in range(max(0, y_near - height), y_near):
                evaluate_position(x, y)
        # Примыкание справа
        for y in range(y_near, y_near + h_near - height + 1):
            for x in range(x_near + w_near, min(self.grid_width, x_near + w_near + width)):
                evaluate_position(x, y)
        # Примыкание слева
        for y in range(y_near, y_near + h_near - height + 1):
            for x in range(max(0, x_near - width), x_near):
                evaluate_position(x, y)    
        self._update_grid(name, best_position, width, height)


    def place_furniture_around(self, name: str, width_cm: int, height_cm:int, target_name: str) -> None:
        if target_name not in self.furniture_positions:
            print(f"Мебель '{target_name}' не найдена для размещения рядом.")
            return
        width = int(np.ceil(width_cm / self.cell_size))
        height = int(np.ceil(height_cm / self.cell_size))
        # Получаем позицию и размеры целевой мебели
        target_x, target_y, target_w, target_h = self.furniture_positions[target_name]
        # Перебираем все возможные позиции
        for num, y in enumerate([target_y - height, target_y + target_h], start=1):
            best_score = -np.inf
            best_position = None
            name_num = f"{name} {num}"
            for x in [target_x + dx for dx in range(target_w)]:
                if not self._can_place_furniture(x, y, width, height):
                    continue
                #  Расстояние от текущей области до ближайшей стены
                dist_from_walls = min(x, self.grid_width - (x + width), y, self.grid_height - (y + height))
                total_score = self.grid[y:y+height, x:x+width].sum() - dist_from_walls         
                # Если это лучшая позиция, запоминаем её
                if total_score > best_score:
                    best_score = total_score
                    best_position = (x, y)
            self._update_grid(name_num, best_position, width,height)
    
    def place_wardrobe(self, name: str, width_cm: int, height_cm: int):
        """Place a wardrobe along the wall with clearance for doors and preference for distance from occupied cells."""
        width = int(np.ceil(width_cm / self.cell_size))
        height = int(np.ceil(height_cm / self.cell_size))
        door_clearance = width//2
        best_score = -np.inf
        best_position = None
        # Найти занятые клетки
        occupied_cells = np.argwhere(self.grid == 0)
        # Перебираем все возможные клетки размещения шкафа
        for y in range(self.grid_height - height + 1):
            for x in range(self.grid_width - width + 1):
                # Проверяем, умещается ли шкаф в текущую область
                if not self._can_place_furniture(x, y, width, height):
                    continue
                # Убедимся, что перед шкафом есть необходимое пространство для открывания дверей
                clearance_y_start = max(0, y - door_clearance)
                clearance_y_end = min(self.grid_height, y + height + door_clearance)
                clearance_x_start = max(0, x - door_clearance)
                clearance_x_end = min(self.grid_width, x + width + door_clearance)
                clearance_area = self.grid[clearance_y_start:clearance_y_end, clearance_x_start:clearance_x_end]
                if np.any(clearance_area < 0):  # Если область занята
                    continue
                # Рассчитываем общий вес области
                area_weights = self.grid[y:y + height, x:x + width].sum()
                # Преимущество для размещения вдоль стен
                dist_to_wall = min(x, self.grid_width - (x + width), y, self.grid_height - (y + height))
                wall_score = 5.0 / (1 + dist_to_wall)
                # Учет расстояния от занятых ячеек
                if len(occupied_cells) > 0:
                    center_x = x + width / 2
                    center_y = y + height / 2
                    distances = np.sqrt((occupied_cells[:, 1] - center_x) ** 2 + (occupied_cells[:, 0] - center_y) ** 2)
                    distance_score = distances.min()  # Минимальное расстояние до занятой ячейки
                else:
                    distance_score = self.grid_width + self.grid_height  # Максимальный возможный при пустой сетке
                total_score = area_weights + wall_score + distance_score # Итоговый вес
                if total_score > best_score:
                    best_score = total_score
                    best_position = (x, y)

        self._update_grid(name, best_position, width, height)