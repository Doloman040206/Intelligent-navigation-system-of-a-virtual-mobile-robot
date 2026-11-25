import json, webbrowser
from pathlib import Path
from config.settings import OUTPUT_DIR, ROOT_DIR


def create_map(city, mode, weather, decision, route, robot):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    robot.set_route(route["coordinates"])
    data = {
        "city": city.city,
        "mode": "Пішки" if mode == "walk" else "Автомобілем",
        "start": {"name": city.start_name, "lat": city.start_lat, "lon": city.start_lon},
        "target": {"name": city.target_name, "lat": city.target_lat, "lon": city.target_lon},
        "route": route["coordinates"],
        "length_m": route["length_m"],
        "weather": weather.to_dict(),
        "decision": decision,
        "mission_success": robot.mission_success,
    }
    template_path = ROOT_DIR / "visualization" / "templates" / "map.html"
    html = template_path.read_text(encoding="utf-8").replace("__MAP_DATA__", json.dumps(data, ensure_ascii=False))
    out = OUTPUT_DIR / "route_map.html"
    out.write_text(html, encoding="utf-8")
    return out


def open_map(path: Path):
    webbrowser.open(path.resolve().as_uri())
