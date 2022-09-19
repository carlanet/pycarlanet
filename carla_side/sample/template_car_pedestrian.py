import random
import carla
from carla import libcarla, ActorBlueprint

from CarlaInetActor import CarlaInetActor
from CarlaInetManager import CarlaInetManager
from OMNeTWorldListener import OMNeTWorldListener, SimulatorStatus


class MyWorld(OMNeTWorldListener):
    def __init__(self):
        self.carla_inet_manager = CarlaInetManager(5555, self)

        self.client = self.sim_world = self.carla_map = None
        self.carla_inet_actors = dict()
        self.general_status = dict()

    def on_finished_creation_omnet_world(self, run_id, seed, carla_timestep, sim_time_limit, custom_params) -> (float, SimulatorStatus):
        random.seed(seed)

        host = ...
        port = ...
        timeout = ...
        world = ...  # Retrieve for example from custom_params

        client: libcarla.Client = carla.Client(host, port)
        client.set_timeout(timeout)
        sim_world = client.load_world(world)

        settings = sim_world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = carla_timestep
        settings.no_rendering_mode = ...  # Retrieve for example from custom_params
        sim_world.apply_settings(settings)
        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)
        traffic_manager.set_random_device_seed(seed)

        client.reload_world(False)  # Reload map keeping the world settings
        sim_world.set_weather(carla.WeatherParameters.ClearSunset)

        sim_world.tick()
        self.client, self.sim_world = client, sim_world
        self.carla_map = self.sim_world.get_map()

    def on_static_actor_created(self, actor_id: str, actor_type: str, actor_config: dict) -> CarlaInetActor:
        if actor_type == 'car':  # and actor_id == 'car_1':
            blueprint: ActorBlueprint = random.choice(
                self.sim_world.get_blueprint_library().filter("vehicle.tesla.model3"))
            blueprint.set_attribute(..., ...)  # Retrieve for example from actor_config
            blueprint.set_attribute(..., ...)  # Retrieve for example from actor_config

            spawn_point = ...  # Retrieve for example from actor_config

            # Attach sensors

            response = self.client.apply_batch_sync(carla.command.SpawnActor(blueprint, spawn_point))
            carla_actor = self.sim_world.get_actor(response.actor_id)
        elif actor_type == 'pedestrian':
            carla_actor = ...
        else:
            raise RuntimeError(f'I don\'t know this type {actor_type}')

        carla_inet_actor = CarlaInetActor(carla_actor, True)
        self.carla_inet_actors[actor_id] = carla_inet_actor
        return carla_inet_actor

    def on_carla_simulation_step(self, timestamp) -> SimulatorStatus:
        self.sim_world.tick()
        # Do all the things, save actors data
        if timestamp > 100:  # ts_limit
            return SimulatorStatus.FINISHED_OK
        else:
            return SimulatorStatus.RUNNING

    def on_generic_message(self, timestamp, user_defined_message) -> (SimulatorStatus, dict):
        # Handle the action of the actors in the world (apply_commands, calc_instruction)
        # es: apply_commands with id command_12 to actor with id active_actor_14
        if user_defined_message['msg_type'] == 'car_action':
            msg_to_send = dict()
            specific_action = user_defined_message['action']  # apply_commands
            command_id = user_defined_message['command_id']
            actor_id = user_defined_message['actor_id']

            status = self.general_status[command_id]
            action_to_call = getattr(self.carla_inet_actors[user_defined_message[actor_id]], specific_action)(*status)
            action_to_call()
            msg_to_send['agent_id'] = ...
            return SimulatorStatus.RUNNING, msg_to_send
        return ...
