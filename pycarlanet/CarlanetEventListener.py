import abc
import enum

from pycarlanet import CarlanetActor

"""
Listener for OMNeT world, note, every parameters gave as in input is a String, so eventually you need to use cast
"""


class SimulatorStatus(enum.Enum):
    RUNNING = 0
    FINISHED_OK = 1
    FINISHED_TIME_LIMIT = 2
    FINISHED_ERROR = -1


class CarlanetEventListener(abc.ABC):

    def omnet_init_completed(self, run_id, carla_configuration, user_defined) -> (float, SimulatorStatus):
        """
        :param run_id: id corresponding to the one in OMNeT++
        :param carla_configuration:
        :param user_defined:
        :return: current carla world timestamp (see Snapshot class of CarlaAPI), current simulator status
        """
        ...

    def actor_created(self, actor_id: str, actor_type: str, actor_config) -> (float, CarlanetActor):
        """
        Called at the beginning of the simulation, OMNeT says which actors it has and communicate
        with carla to create those actors in the world
        :param actor_id:
        :param actor_type:
        :param actor_config:
        :return: current carla world timestamp (see Snapshot class of CarlaAPI), new actor created from carlaWorld
        """
        ...
        ##return Actor

    def carla_init_completed(self):
        """Called when the initialization of CARLA World is finished"""
        ...

    def carla_simulation_step(self, timestamp) -> SimulatorStatus:
        """
        Method called every time OMNeT call simulation_step of Carla
        :param timestamp
        :return: current simulator status
        """
        ...

    def generic_message(self, timestamp, user_defined_message) -> (SimulatorStatus, dict):
        """
        :param timestamp:
        :param user_defined_message:
        :return: (current simulator status, dict contained custom parameters not None)
        """
        ...

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
