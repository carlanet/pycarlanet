import abc
import enum
from carla.libcarla import World
from utils import InstanceExist
from CarlaClient import CarlaClient

class SimulatorStatus(enum.Enum):
    RUNNING = 0
    FINISHED_OK = 1
    FINISHED_TIME_LIMIT = 2
    FINISHED_ERROR = -1

class WorldManager(abc.ABC):
    # INIT PHASE
    def omnet_init_completed(self, run_id, carla_configuration, user_defined) -> (SimulatorStatus, World):
        """
        After Omnet INIT
        :param run_id: id corresponding to the one in OMNeT++
        :param carla_configuration:
        :param user_defined:
        :return: current carla world, current simulator status
        """
        return SimulatorStatus.RUNNING, self.world
    
    def carla_init_completed(self):
        """Called when the initialization of CARLA World is finished"""
        ...

    # RUN PHASE
    def before_world_tick(self, timestamp) -> None:
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
        return SimulatorStatus.FINISHED_OK

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
    def load_world(self, worldName):
        #CarlaClient.instance._client.load_world("Town05")
        CarlaClient.instance.client.load_world(worldName)
        ...
