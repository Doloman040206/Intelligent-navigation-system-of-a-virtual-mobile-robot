from config.settings import ALPHA


def _first(value, default=""):
    if isinstance(value, (list, tuple)):
        return value[0] if value else default
    return value if value is not None else default


def edge_susceptibility(edge_data, decision):
    surface = str(_first(edge_data.get("surface"), "unknown")).lower()
    highway = str(_first(edge_data.get("highway"), "unknown")).lower()
    bridge = str(_first(edge_data.get("bridge"), "no")).lower() not in ("no", "false", "0", "")

    surface_factor = {
        "asphalt": 0.65, "concrete": 0.65, "paving_stones": 0.85,
        "sett": 0.90, "gravel": 1.20, "fine_gravel": 1.05,
        "ground": 1.35, "dirt": 1.40, "mud": 1.60, "sand": 1.45,
    }.get(surface, 1.0)
    if highway in ("steps",):
        surface_factor *= 1.35
    elif highway in ("footway", "path", "track"):
        surface_factor *= 1.10
    wind_factor = 1.25 if bridge else 1.0

    rain = decision["precipitation_risk"]
    wind = decision["wind_risk"]
    temp = decision["temperature_risk"]
    risk = 0.20 * temp + 0.55 * rain * surface_factor + 0.25 * wind * wind_factor
    return max(0.0, min(1.0, risk))


def edge_weight(length_m, edge_data, decision, adaptive=True):
    length = max(0.01, float(length_m))
    if not adaptive:
        return length
    risk = edge_susceptibility(edge_data, decision)
    return length * (1.0 + ALPHA * risk)
