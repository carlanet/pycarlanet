import abc
import carla
from enum import Enum, auto

from pycarlanet.utils import DecoratorSingleton, InstanceExist

# Pattern decorator for carla.Actor
# NOTE: you can call each method of carla.Actor on this class, but if you want to pass an object of type
# CarlanetActor to a methods defined in carla you have to pass the attribute carla_actor
# because carla can't see this class

@DecoratorSingleton
class ActorType:
    _types = ["Vehicle"]
    def get_available_types(self): return self._types
    def add_new_type(self, name: str):
        if name not in self._types: self._types.append(name)

class CarlanetActor(abc.ABC):

    @InstanceExist(ActorType)
    def __init__(self, carla_actor: carla.Actor, actor_type: str):
        if actor_type not in ActorType.instance.get_available_types(): raise ValueError(f'cannot instantiate a CarlanetActor with type {actor_type} because is not present in ActorType list, choose an available type between {ActorType.instance.get_available_types()}')
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
