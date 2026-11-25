from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "outputs"
CACHE_DIR = ROOT_DIR / ".cache" / "graphs"
ALPHA = 2.0
WEATHER_WEIGHTS = {"temperature": 0.25, "precipitation": 0.45, "wind": 0.30}
OPEN_METEO_TIMEOUT = 15
GRAPH_PADDING_DEGREES = 0.018
