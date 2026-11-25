from time import perf_counter
from config.settings import WEATHER_WEIGHTS


def _clamp(value):
    return max(0.0, min(1.0, float(value)))


def assess_weather(weather, selected_mode):
    started = perf_counter()
    t = weather.temperature_c
    p = max(0.0, weather.precipitation_mm)
    w = max(0.0, weather.wind_kmh)

    if 5 <= t <= 25:
        rt = 0.0
    elif t < 5:
        rt = _clamp((5 - t) / 20)
    else:
        rt = _clamp((t - 25) / 18)

    rp = _clamp(p / 5.0)
    rw = _clamp(w / 70.0)
    score = (WEATHER_WEIGHTS["temperature"] * rt
             + WEATHER_WEIGHTS["precipitation"] * rp
             + WEATHER_WEIGHTS["wind"] * rw)

    if score < 0.20:
        category = "сприятливі"
    elif score < 0.50:
        category = "помірні"
    else:
        category = "несприятливі"

    recommendation = "car" if score >= 0.50 else "walk"
    warnings = []
    if t < -5 or t > 32:
        warnings.append("Температура виходить за межі комфортного діапазону")
    if p >= 1.0:
        warnings.append("Опади можуть ускладнювати пересування")
    if w >= 35:
        warnings.append("Підвищена швидкість вітру")
    if score >= 0.50:
        warnings.append("Висока сумарна модельована оцінка погодного ризику")

    elapsed_ms = (perf_counter() - started) * 1000
    return {
        "temperature_risk": round(rt, 4),
        "precipitation_risk": round(rp, 4),
        "wind_risk": round(rw, 4),
        "overall_risk": round(score, 4),
        "category": category,
        "recommended_mode": recommendation,
        "selected_mode": selected_mode,
        "selected_mode_preserved": True,
        "warnings": warnings,
        "decision_time_ms": round(elapsed_ms, 4),
        "model_weights": WEATHER_WEIGHTS,
    }
