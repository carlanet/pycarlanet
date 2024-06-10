import abc
from typing import Dict
import carla

from pycarlanet.enum import SimulatorStatus
from pycarlanet import CarlanetActor, ActorType


class ActorManager(abc.ABC):
    _carlanet_actors: Dict[str, CarlanetActor] = dict()

    # INIT PHASE
    def omnet_init_completed(self, message):
        """
        After Omnet, WorldManager INIT
        :param message: init message from OMNeT++
        """
        #:param run_id: id corresponding to the one in OMNeT++
        #:param carla_configuration:
        #:param user_defined:
        self.create_actors_from_omnet(message['moving_actors'])
        #create carla actors from configuration file

    # RUN PHASE
    def before_world_tick(self, timestamp):
        """
        Method called before a world tick called by OMNeT++
        :param timestamp
        :return: 
        """
        ...
    
    def after_world_tick(self, timestamp):
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

    # UTILITIES
    def create_actors_from_omnet(self, actors):
        """
        Called at the beginning of the simulation, OMNeT says which actors it has and communicate
        with carla to create those actors in the world
        :param actor_id:
        :param actor_type:
        :param actor_config:
        :return: new actor created from carlaWorld
        """
        ...
    
    def add_carla_actor_to_omnet(self, actor:carla.Actor, actor_type: ActorType):
        """
        Called to add a carla actor to the list and communicate in next step to omnet
        :param actor:carla.Actor
        :param actor_type: ActorType
        """
        self._carlanet_actors[f'{actor.id}'] = CarlanetActor(actor, actor_type) 

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
            transform: carla.Transform = actor.carla_actor.get_transform()
            velocity: carla.Vector3D = actor.carla_actor.get_velocity()
            position = dict()
            position['actor_id'] = actor_id
            position['position'] = [transform.location.x, transform.location.y, transform.location.z]
            position['rotation'] = [transform.rotation.pitch, transform.rotation.yaw, transform.rotation.roll]
            position['velocity'] = [velocity.x, velocity.y, velocity.z]
            #position['is_net_active'] = actor.alive
            position['actor_type'] = actor.actor_type
            nodes_positions.append(position)
        return nodes_positions

class BasicActorManager(ActorManager):
    #_agents = dict(int, ?actor)

    # INIT PHASE
    def omnet_init_completed(self, message): return
    
    # RUN PHASE
    def before_world_tick(self, timestamp): return
    def _generate_carla_nodes_positions(self): return []