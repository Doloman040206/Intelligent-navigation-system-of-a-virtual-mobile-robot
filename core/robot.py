from dataclasses import dataclass, field
from typing import Optional
from config.cities import CityScenario

@dataclass
class VirtualRobot:
    scenario: CityScenario
    selected_mode: str
    state: str = "initialized"
    route_coordinates: list = field(default_factory=list)
    mission_success: bool = False
    weather_summary: Optional[dict] = None

    @property
    def start(self):
        return (self.scenario.start_lat, self.scenario.start_lon)

    @property
    def target(self):
        return (self.scenario.target_lat, self.scenario.target_lon)

    def set_route(self, coordinates):
        self.route_coordinates = coordinates
        self.state = "route_planned"
        self.mission_success = bool(coordinates)
