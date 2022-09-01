import abc

from CarlaInetActor import CarlaInetActor


class OMNeTWorldListener(abc.ABC):

    def on_static_actor_created(self, actor_id: str, actor_type: str, actor_config) -> CarlaInetActor:
        """
        Callback called at the beginning of the simulation, OMNeT says which actors it has and communicate
        with carla to create these actors in the world
        :param actor_id:
        :param actor_type:
        :param actor_config:
        :return: new actor created from carlaWorld
        """
        ...
        ##return Actor

    def on_finished_creation_omnet_world(self, carla_world_configuration) -> float:
        """

        :param carla_world_configuration: current omnet timestmap
        :return: current carla world timestamp (see Snapshot class of CarlaAPI)
        """
        ...

    def on_tick(self):
        ...
