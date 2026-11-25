from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class WeatherData:
    temperature_c: float
    precipitation_mm: float
    wind_kmh: float
    source: str = "controlled_test"
    observed_at: str = "not specified"

    def to_dict(self):
        return asdict(self)
