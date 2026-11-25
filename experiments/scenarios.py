from core.environment import WeatherData

TEST_WEATHER_SCENARIOS = [
    ("favorable", "Сприятливі", WeatherData(18.0, 0.0, 8.0, "controlled_test", "fixed")),
    ("moderate", "Помірні", WeatherData(7.0, 1.2, 28.0, "controlled_test", "fixed")),
    ("unfavorable", "Несприятливі", WeatherData(-3.0, 4.0, 52.0, "controlled_test", "fixed")),
]
