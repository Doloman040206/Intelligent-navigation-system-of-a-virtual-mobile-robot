from core.environment import WeatherData
from core.decision_module import assess_weather


def test_weather_score_is_bounded_and_mode_is_preserved():
    weather = WeatherData(-10, 8, 80)

    result = assess_weather(weather, "walk")

    assert 0 <= result["overall_risk"] <= 1
    assert result["selected_mode"] == "walk"
    assert result["selected_mode_preserved"] is True


def test_favorable_weather_has_low_risk():
    result = assess_weather(
        WeatherData(18, 0, 5),
        "drive",
    )

    assert result["overall_risk"] < 0.2


def test_edge_susceptibility_is_available_for_baseline_risk_measurement():
    from core.risk_model import edge_susceptibility

    decision = {
        "temperature_risk": 0.2,
        "precipitation_risk": 0.3,
        "wind_risk": 0.1,
    }

    risk = edge_susceptibility(
        {
            "surface": "asphalt",
            "highway": "residential",
            "bridge": "no",
        },
        decision,
    )

    assert 0 <= risk <= 1
    assert risk > 0