from enum import Enum
import carla

class SimulatorStatus(Enum):
    RUNNING = 0
    FINISHED_OK = 1
    FINISHED_TIME_LIMIT = 2
    FINISHED_ERROR = -1

class CarlaMaplayers(Enum):
    Buildings = carla.MapLayer.Buildings
    Decals = carla.MapLayer.Decals
    Foliage = carla.MapLayer.Foliage
    Ground = carla.MapLayer.Ground
    ParkedVehicles = carla.MapLayer.ParkedVehicles
    Particles = carla.MapLayer.Particles
    Props = carla.MapLayer.Props
    StreetLights = carla.MapLayer.StreetLights
    Walls = carla.MapLayer.Walls