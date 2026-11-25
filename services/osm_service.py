import time
import osmnx as ox

from config.settings import CACHE_DIR, GRAPH_PADDING_DEGREES

ox.settings.requests_timeout = 300
ox.settings.use_cache = True
ox.settings.overpass_rate_limit = True


def is_temporary_overpass_error(exc):

    message = str(exc).lower()

    temporary_errors = (
        "502",
        "503",
        "504",
        "429",
        "currently at capacity",
        "request queue is full",
        "gateway timeout",
        "too many requests",
    )

    return any(error in message for error in temporary_errors)


def get_graph(city, mode):

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    network_type = "walk" if mode == "walk" else "drive"

    cache_path = CACHE_DIR / f"{city.key}_{network_type}.graphml"

    if cache_path.exists():
        print(f"[OSM] Використовую кеш графа: {cache_path.name}")
        return ox.load_graphml(cache_path)

    lat_min = min(city.start_lat, city.target_lat) - GRAPH_PADDING_DEGREES
    lat_max = max(city.start_lat, city.target_lat) + GRAPH_PADDING_DEGREES

    lon_min = min(city.start_lon, city.target_lon) - GRAPH_PADDING_DEGREES
    lon_max = max(city.start_lon, city.target_lon) + GRAPH_PADDING_DEGREES

    bbox = (lon_min, lat_min, lon_max, lat_max)

    print(
        f"[OSM] Завантажую мережу {network_type}; "
        "перше завантаження може тривати довше..."
    )

    max_attempts = 4
    graph = None

    for attempt in range(max_attempts):
        try:
            graph = ox.graph_from_bbox(
                bbox=bbox,
                network_type=network_type,
                simplify=True
            )

            break

        except Exception as exc:
            if not is_temporary_overpass_error(exc):
                raise

            if attempt == max_attempts - 1:
                raise

            wait_seconds = 30 * (2 ** attempt)

            print(
                f"[OSM] Сервер Overpass тимчасово перевантажений. "
                f"Спроба {attempt + 1}/{max_attempts} не вдалася."
            )

            print(
                f"[OSM] Повторна спроба через {wait_seconds} секунд..."
            )

            time.sleep(wait_seconds)

    if graph is None or graph.number_of_nodes() == 0:
        raise RuntimeError(
            "OpenStreetMap не повернув дорожню мережу для заданої області."
        )

    ox.save_graphml(graph, cache_path)

    print(f"[OSM] Граф успішно збережено: {cache_path.name}")
    print(
        f"[OSM] Вузлів: {graph.number_of_nodes()}, "
        f"ребер: {graph.number_of_edges()}"
    )

    return graph