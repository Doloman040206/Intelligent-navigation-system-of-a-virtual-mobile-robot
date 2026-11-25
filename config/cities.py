from dataclasses import dataclass

@dataclass(frozen=True)
class CityScenario:
    key: str
    city: str
    start_name: str
    start_lat: float
    start_lon: float
    target_name: str
    target_lat: float
    target_lon: float

CITIES = [
    CityScenario("kyiv", "Київ", "Майдан Незалежності", 50.4501, 30.5234,
                 "Києво-Печерська лавра", 50.4346, 30.5577),
    CityScenario("lviv", "Львів", "Площа Ринок", 49.8419, 24.0315,
                 "Залізничний вокзал", 49.8397, 23.9933),
    CityScenario("odesa", "Одеса", "Дерибасівська вулиця", 46.4846, 30.7326,
                 "Потьомкінські сходи", 46.4886, 30.7414),
]
