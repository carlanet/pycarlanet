import abc
from typing import List

from carla.libcarla import World

from pycarlanet.enum import CarlaMaplayers, SimulatorStatus
from pycarlanet.utils import InstanceExist
from pycarlanet import CarlaClient


class WorldManager(abc.ABC):

    _synchronousMode: bool
    _fixed_delta_seconds = 0.01

    def __init__(self, synchronousMode: bool):
        self._synchronousMode = synchronousMode

    # INIT PHASE
    def omnet_init_completed(self, message) -> SimulatorStatus:
        """
        After Omnet INIT
        :param message: init message fro OMNeT++
        :return: current carla world, current simulator status
        """
        #run_id=message['run_id'],
        #carla_configuration=message['carla_configuration'],
        #user_defined=message['user_defined']

        try: self._fixed_delta_seconds = message['carla_configuration']['carla_timestep']
        except: ...

        if self._synchronousMode: self.setSynchronous_fixed_delta_seconds()

        return SimulatorStatus.RUNNING

    # RUN PHASE
    def before_world_tick(self, timestamp):
        """
        Method called before a world tick called by OMNeT++
        :param timestamp
        :return: current simulator status
        """
        ...

    def after_world_tick(self, timestamp) -> SimulatorStatus:
        """
        Method called after a world tick called by OMNeT++
        :param timestamp
        :return: current simulator status
        """
        ...

    def generic_message(self, timestamp, message) -> (SimulatorStatus, dict):
        """
        :param timestamp:
        :param message:
        :return: (current simulator status, dict contained custom parameters not None)
        """
        ...

    # FINISH/ERROR PHASE
    def simulation_finished(self, status_code: SimulatorStatus):
        """
        Callback called upon successful completion of the simulation
        :return:
        """
        ...

    def simulation_error(self, exception):
        """

        :param exception:
        :return:
        """
        ...
    
    # UTILITIES
    @property
    @InstanceExist(CarlaClient)
    def world(self):
        return CarlaClient.instance.world

    def get_elapsed_seconds(self):
        return self.world.get_snapshot().timestamp.elapsed_seconds
    
    def tick(self):
        self.world.tick()

    @InstanceExist(CarlaClient)
    def load_world(self, worldName, layer_to_unload: List[CarlaMaplayers] =[]):
        CarlaClient.instance.client.load_world(worldName)
        for layer in layer_to_unload: self.world.unload_map_layer(layer.value)
        if self._synchronousMode: self.setSynchronous_fixed_delta_seconds()

    def setSynchronous_fixed_delta_seconds(self):
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = True
        #settings.no_rendering_mode = False
        settings.fixed_delta_seconds = self._fixed_delta_seconds
        self.world.apply_settings(settings)
