import json
from config.cities import CITIES
from core.robot import VirtualRobot
from core.decision_module import assess_weather
from core.route_planner import plan_route
from services.osm_service import get_graph
from services.weather_service import get_current_weather
from experiments.experiment_runner import run_experiment
from visualization.map_visualization import create_map
from config.settings import OUTPUT_DIR


def choose_city():
    print("\nОберіть тестовий міський сценарій:")
    for i, city in enumerate(CITIES, 1):
        print(f"{i}. {city.city}: {city.start_name} → {city.target_name}")
    while True:
        value = input("Номер сценарію [1-3]: ").strip()
        if value in {"1", "2", "3"}:
            return CITIES[int(value)-1]
        print("Введіть 1, 2 або 3.")


def choose_mode():
    print("\nЯк ви бажаєте дістатися до місця призначення?")
    print("1 — Пішки\n2 — На автомобілі")
    while True:
        value = input("Ваш вибір [1/2]: ").strip()
        if value == "1": return "walk"
        if value == "2": return "drive"
        print("Введіть 1 або 2.")


def main():
    print("=" * 66)
    print("ІНТЕЛЕКТУАЛЬНА СИСТЕМА НАВІГАЦІЇ ВІРТУАЛЬНОГО МОБІЛЬНОГО РОБОТА З УРАХУВАННЯМ ПОГОДНИХ УМОВ")
    print("=" * 66)
    city = choose_city()
    mode = choose_mode()
    robot = VirtualRobot(city, mode)

    try:
        graph = get_graph(city, mode)
        print(f"[OSM] Вузлів: {graph.number_of_nodes()}, ребер: {graph.number_of_edges()}")
    except Exception as exc:
        print(f"Не вдалося отримати дорожній граф: {exc}")
        print("Перевірте інтернет-з'єднання або повторіть запуск пізніше.")
        return

    try:
        _, experiment_summary = run_experiment(graph, city, mode)
    except Exception as exc:
        print(f"Помилка контрольованого експерименту: {exc}")
        return

    print("\n=== ОСНОВНИЙ ЗАПУСК З АКТУАЛЬНОЮ ПОГОДОЮ ===")
    mid_lat = (city.start_lat + city.target_lat) / 2
    mid_lon = (city.start_lon + city.target_lon) / 2
    try:
        weather = get_current_weather(mid_lat, mid_lon)
    except Exception as exc:
        print(f"Не вдалося отримати актуальну погоду Open-Meteo: {exc}")
        print("Основний маршрут не буде побудовано")
        return

    decision = assess_weather(weather, mode)
    robot.weather_summary = decision
    try:
        route = plan_route(graph, robot.start, robot.target, decision, adaptive=True)
    except Exception as exc:
        print(f"Не вдалося побудувати маршрут: {exc}")
        return

    live_result = {
        "city": city.city,
        "selected_mode": mode,
        "weather": weather.to_dict(),
        "decision": decision,
        "route": {k: v for k, v in route.items() if k != "coordinates"},
        "experiment_summary": experiment_summary,
        "comparison_note": "Погодні умови API в нас можуть змінюватися з часом.",
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "live_run.json").write_text(json.dumps(live_result, ensure_ascii=False, indent=2), encoding="utf-8")
    map_path = create_map(city, mode, weather, decision, route, robot)

    print(f"\nМісто: {city.city}; режим: {'пішки' if mode == 'walk' else 'автомобілем'}")
    print(f"Погода: {weather.temperature_c} °C; опади {weather.precipitation_mm} мм; вітер {weather.wind_kmh} км/год")
    print(f"Оцінка умов: {decision['category']} ({decision['overall_risk']:.3f})")
    print(f"Рекомендація модуля: {'пішки' if decision['recommended_mode']=='walk' else 'автомобілем'}; вибір користувача збережено: {decision['selected_mode_preserved']}")
    print(f"Маршрут: {route['length_m']:.0f} м; сегментів: {route['edge_count']}; час планування: {route['planning_time_ms']:.2f} мс")
    print(f"Карта: {map_path}")

if __name__ == "__main__":
    main()
