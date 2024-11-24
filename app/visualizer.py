import os
import numpy as np
import matplotlib.pyplot as plt

from app.roomplanner import RoomPlanner

def visualize(room: RoomPlanner, save_to_file: bool = False, filename: str = "План комнаты.png") -> None:
    _, ax = plt.subplots(figsize=(8, 8))

    # Отображение сетки комнаты
    ax.imshow(room.grid, cmap='coolwarm', origin='upper', alpha=0.5)
    ax.set_title("Визуализация комнаты", fontsize=16)
    ax.set_xlabel("Ширина (ячейки)")
    ax.set_ylabel("Высота (ячейки)")
    ax.set_xticks(np.arange(-0.5, room.grid_width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, room.grid_height, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)

    # Функция для добавления элементов на график
    def add_rectangle(x, y, w, h, edge_color, fill_color, label, text_color) -> None:
        rect = plt.Rectangle((x, y), w, h, edgecolor=edge_color, facecolor=fill_color, linewidth=2, alpha=0.8)
        ax.add_patch(rect)
        if label:
            ax.text(
                x + w / 2, y + h / 2, label,
                ha='center', va='center', color=text_color, fontsize=10, fontweight='bold'
            )

    # Отображение мебели
    for name, (x, y, w, h) in room.furniture_positions.items():
        add_rectangle(x, y, w, h, edge_color='black', fill_color='green', label=name, text_color='white')
        print(name, x, y)

    # Отображение дверей
    for door_x, door_y, door_w, door_h in room.doors:
        add_rectangle(door_x - 0.5, door_y - 0.5, door_w, door_h, edge_color='blue', fill_color='blue', label='Дверь', text_color='black')

    # Отображение окон
    for window_x, window_y, window_w, window_h in room.windows:
        add_rectangle(window_x - 0.5, window_y - 0.5, window_w, window_h, edge_color='cyan', fill_color='cyan', label='Окно', text_color='black')

    # Настройки отображения
    ax.set_xlim(-0.5, room.grid_width - 0.5)
    ax.set_ylim(-0.5, room.grid_height - 0.5)
    
    if save_to_file:
        os.makedirs("output", exist_ok=True) 
        plt.savefig(os.path.join("output", filename))
    else:
        plt.show()