import abc

import carla

from pycarlanet.utils import preconditions


# Pattern decorator for carla.Actor
# NOTE: you can call each method of carla.Actor on this class, but if you want to pass an object of type
# CarlanetActor to a methods defined in carla you have to pass the attribute carla_actor
# because carla can't see this class
class CarlanetActor(abc.ABC):

    def __init__(self, carla_actor: carla.Actor, alive: bool):
        self._carla_actor = carla_actor
        self._alive = alive

    @preconditions('_carla_actor')
    def __getattr__(self, *args):
        return self._carla_actor.__getattribute__(*args)

    def apply_command(self, command):
        carla.command.ApplyVehicleControl(self.id, command)

    @property
    def alive(self):
        return self._alive
