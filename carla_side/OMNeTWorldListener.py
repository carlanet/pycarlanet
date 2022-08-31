import abc


class OMNeTWorldListener(abc.ABC):

    def on_finished_creation_omnet_world(self, carla_world_configuration) -> float:
        """

        :param omnet_timestamp: current omnet timestmap
        :return: current carla world timestamp (see Snapshot class of CarlaAPI)
        """
        ...

    def on_tick(self):
        ...
