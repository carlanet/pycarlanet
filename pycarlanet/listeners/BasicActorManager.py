class BasicActorManager(abc.ABC):
    #_agents = dict(int, ?actor)

    # INIT PHASE
    def omnet_init_completed(self, message): ...
    
    # RUN PHASE
    #def before_world_tick(self, timestamp): ...

    def _generate_carla_nodes_positions(self): return []