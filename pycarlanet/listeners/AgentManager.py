import abc

class BasicAgentManager():
    #_agents = dict(int, ?actor)

    # INIT PHASE
    def omnet_init_completed(self, message): return
    
    # RUN PHASE
    #def before_world_tick(self, timestamp): ...

class AgentManager(abc.ABC):

    # INIT PHASE
    def omnet_init_completed(self, message):
        """
        After Omnet, WorldManager INIT
        :param run_id: id corresponding to the one in OMNeT++
        :param carla_configuration:
        :param user_defined:
        :return: current carla world, current simulator status
        """
        ...
    
    # RUN PHASE
    def before_world_tick(self, timestamp):
        """
        Method called before a world tick called by OMNeT++
        :param timestamp
        :return: current simulator status
        """
        ...
    
    def after_world_tick(self, timestamp):
        """
        Method called after a world tick called by OMNeT++
        :param timestamp
        :return: current simulator status
        """
        ...
    
    def generic_message(timestamp, message) -> (SimulatorStatus, dict):
        """
        :param timestamp:
        :param message:
        :return: (current simulator status, dict contained custom parameters not None)
        """
        ...