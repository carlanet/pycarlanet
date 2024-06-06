import abc
import carla

from CarlanetActor import CarlanetActor

class ActorManager(abc.ABC):
    _carlanet_actors = dict()

    # INIT PHASE
    def omnet_init_completed(self, run_id, carla_configuration, user_defined):
        """
        After Omnet, WorldManager INIT
        :param run_id: id corresponding to the one in OMNeT++
        :param carla_configuration:
        :param user_defined:
        """
        ...
    
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
    def create_actors_from_carla(self, actor:carla.Actor):
        """
        Called to add a carla actor to the list and communicate in next step to omnet
        :param actor_id:
        :param actor_type:
        :param actor_config:
        :return: new actor created from carlaWorld
        """
        if actor.id in self._carlanet_actors:
            print(f"ActorManager -> create_actors_from_carla 'aacotr with id {actor.id} already exists'")
            return
        self._carlanet_actors[actor.id] = CarlanetActor(actor, True)

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