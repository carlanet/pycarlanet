import abc
import carla
from enum import Enum

from pycarlanet.utils import preconditions

# Pattern decorator for carla.Actor
# NOTE: you can call each method of carla.Actor on this class, but if you want to pass an object of type
# CarlanetActor to a methods defined in carla you have to pass the attribute carla_actor
# because carla can't see this class

class ActorType(Enum):
    #TODO define module omnet for each type
    Sensor = 'a'
    Spectator = 'b'
    Traffic_sign = 'c'
    Traffic_light = 'd'
    Vehicle = 'e'
    Walkers = 'f'

class CarlanetActor(abc.ABC):

    def __init__(self, carla_actor: carla.Actor, actor_type: ActorType):
        self._carla_actor = carla_actor
        self._actor_type = actor_type

    #@preconditions('_carla_actor')
    #def __getattr__(self, *args):
    #    return self._carla_actor.__getattribute__(*args)

    #def apply_command(self, command):
    #    carla.command.ApplyVehicleControl(self.id, command)

    @property
    def carla_actor(self): return self._carla_actor

    @property
    def actor_type(self): return self._actor_type
