import abc
from typing import Dict
import carla
from pycarlanet import CarlanetActor

class BasicActorManager():
    #_agents = dict(int, ?actor)

    # INIT PHASE
    def omnet_init_completed(self, message): return
    
    # RUN PHASE
    #def before_world_tick(self, timestamp): ...

    def _generate_carla_nodes_positions(self): return []

class ActorManager(abc.ABC):
    _carlanet_actors: Dict[str, CarlanetActor] = dict()

    # INIT PHASE
    def omnet_init_completed(self, message):
        """
        After Omnet, WorldManager INIT
        :param message: init message fro OMNeT++
        """
        #:param run_id: id corresponding to the one in OMNeT++
        #:param carla_configuration:
        #:param user_defined:
        self.create_actors_from_omnet(message['moving_actors'])
        #create carla actors from configuration file
    
    def create_actors_from_omnet(self, actors):
        """
        Called at the beginning of the simulation, OMNeT says which actors it has and communicate
        with carla to create those actors in the world
        :param actor_id:
        :param actor_type:
        :param actor_config:
        :return: new actor created from carlaWorld
        """
        #TODO
        print(len(actors))
        for actor in actors: print(actor)
        #self._carlanet_actors[actor_id] = CarlanetActor(carla.Actor())
    
    # RUN PHASE
    def before_world_tick(self, timestamp) -> None:
        """
        Method called before a world tick called by OMNeT++
        :param timestamp
        :return: current simulator status
        """
        ...

    # UTILITIES
    def add_carla_actor_to_omnet(self, actor:carla.Actor):
        """
        Called to add a carla actor to the list and communicate in next step to omnet
        :param actor:carla.Actor
        """
        print(f"add_carla_actor_to_omnet, id {actor.id} -> {actor}")
        #TODO check if is correct and uncomment
        self._carlanet_actors[actor.id] = CarlanetActor(actor, True) 

        #TODO check if necessary
        #if actor.id in self._carlanet_actors:
        #    print(f"ActorManager -> create_actors_from_carla {actor} with id {actor.id} already exists'")
        #    return

    def remove_actor(self, actor_id: str):
        """
        Remove actor from OMNeT world
        :param actor_id:
        :return:
        """
        del self._carlanet_actors[actor_id]
    
    def _generate_carla_nodes_positions(self):
        nodes_positions = []
        for actor_id, actor in self._carlanet_actors.items():
            transform: carla.Transform = actor.get_transform()
            velocity: carla.Vector3D = actor.get_velocity()
            position = dict()
            position['actor_id'] = actor_id
            position['position'] = [transform.location.x, transform.location.y, transform.location.z]
            position['rotation'] = [transform.rotation.pitch, transform.rotation.yaw, transform.rotation.roll]
            position['velocity'] = [velocity.x, velocity.y, velocity.z]
            position['is_net_active'] = actor.alive
            nodes_positions.append(position)
        return nodes_positions