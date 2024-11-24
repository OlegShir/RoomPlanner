from app.roomplanner import RoomPlanner
from app.visualizer import visualize


def run_test_case(room_size, doors, windows, furniture_list, test_case_id):
    cell_size = 20
    planner = RoomPlanner(room_size, cell_size, doors, windows)
    planner.calculate_weights()

    for item in furniture_list:
        name, width, height, placement, *extra = item
        
        if placement == "window":
            planner.place_furniture(name, width, height, prefer_window=True)
        elif placement == "wall":
            planner.place_furniture(name, width, height, prefer_wall=True)
        elif placement == "near":
            near_name = extra[0]
            planner.place_furniture_near(name, width, height, near_name=near_name)
        elif placement == "around":
            target_name = extra[0]
            planner.place_furniture_around(name, width, height, target_name=target_name)
        elif placement == "wardrobe":
            planner.place_wardrobe(name, width, height)

    print(f"Запуск теста {test_case_id}...")
    visualize(planner, save_to_file=True, filename=f"Тест_{test_case_id}.png")
    print(f"Тест {test_case_id} завершен.")

test_cases = [
    {
        "room_size": (400, 600),
        "doors": [(0, 200, 20, 90)],
        "windows": [(100, 0, 180, 20)],
        "furniture_list": [
            ("Туалетный столик", 60, 30, "window"),
            ("Двуспальная кровать", 200, 180, "wall"),
            ("Стул", 20, 20, "near", "Туалетный столик"),
            ("Прикроватная тумбочка", 30, 30, "around", "Двуспальная кровать"),
            ("Шкаф 1", 120, 60, "wardrobe"),
            ("Шкаф 2", 120, 60, "wardrobe")
        ]
    },
    {
        "room_size": (500, 700),
        "doors": [(690, 10, 10, 90)],
        "windows": [(150, 0, 200, 30)],
        "furniture_list": [
            ("Книжный шкаф", 100, 40, "window"),
            ("Офисный стол", 120, 80, "wall"),
            ("Кресло", 50, 50, "near", "Офисный стол"),
            ("Шкаф для одежды", 120, 60, "wardrobe")
        ]
    },
    {
        "room_size": (350, 500),
        "doors": [(0, 150, 30, 70)],
        "windows": [(50, 0, 100, 40)],
        "furniture_list": [
            ("Компьютерный стол", 100, 60, "wall"),
            ("Кресло офисное", 50, 50, "near", "Компьютерный стол"),
            ("Шкаф для книг", 80, 40, "wardrobe"),
            ("Кровать", 180, 200, "window"),
            ("Тумбочка", 30, 30, "around", "Кровать")
        ]
    },
    {
        "room_size": (600, 800),
        "doors": [(0, 400, 50, 100)],
        "windows": [(200, 0, 250, 40)],
        "furniture_list": [
            ("Кухонный стол", 120, 80, "wall"),
            ("Диван", 200, 100, "around", "Кухонный стол"),
            ("Шкаф для посуды", 100, 60, "wardrobe"),
            ("Полка", 80, 40, "around", "Шкаф для посуды")
        ]
    },
    {
        "room_size": (450, 650),
        "doors": [(200, 250, 50, 100)],
        "windows": [(150, 0, 150, 30)],
        "furniture_list": [
            ("Трехместный диван", 200, 100, "wall"),
            ("Журнальный столик", 60, 40, "near", "Трехместный диван"),
            ("Полка для книг", 120, 60, "wardrobe")
        ]
    },
    {
        "room_size": (400, 600),
        "doors": [(100, 200, 30, 80)],
        "windows": [(50, 0, 200, 20)],
        "furniture_list": [
            ("Компьютерный стол", 120, 60, "wall"),
            ("Офисный стул", 60, 60, "near", "Компьютерный стол"),
            ("Книжный шкаф", 80, 40, "wardrobe")
        ]
    },
    {
        "room_size": (700, 900),
        "doors": [(0, 300, 60, 120)],
        "windows": [(200, 0, 300, 50)],
        "furniture_list": [
            ("Двуспальная кровать", 200, 180, "window"),
            ("Тумбочка", 30, 30, "around", "Двуспальная кровать"),
            ("Шкаф", 120, 60, "wardrobe")
        ]
    },
    {
        "room_size": (350, 450),
        "doors": [(0, 150, 40, 100)],
        "windows": [(100, 0, 150, 30)],
        "furniture_list": [
            ("Кресло", 80, 50, "wall"),
            ("Полка", 50, 40, "near", "Кресло"),
            ("Тумбочка", 30, 30, "wardrobe"),
            ("Шкаф для одежды", 120, 60, "wardrobe")
        ]
    },
    {
        "room_size": (600, 800),
        "doors": [(100, 500, 40, 80)],
        "windows": [(100, 0, 200, 40)],
        "furniture_list": [
            ("Журнальный столик", 80, 50, "window"),
            ("Диван", 250, 150, "wall"),
            ("Шкаф", 120, 60, "wardrobe"),
            ("Полка для книг", 100, 50, "near", "Диван")
        ]
    },
    {
        "room_size": (550, 750),
        "doors": [(50, 400, 50, 100)],
        "windows": [(200, 0, 200, 40)],
        "furniture_list": [
            ("Стол для компьютера", 100, 60, "wall"),
            ("Офисный стул", 60, 60, "near", "Стол для компьютера"),
            ("Шкаф", 120, 60, "wardrobe")
        ]
    }
]

for idx, test_case in enumerate(test_cases, 1):
    run_test_case(
        room_size=test_case["room_size"],
        doors=test_case["doors"],
        windows=test_case["windows"],
        furniture_list=test_case["furniture_list"],
        test_case_id=idx
    )