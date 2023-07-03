import random
import carla
from carla import libcarla, ActorBlueprint, World
import traceback
import pygame

from pycarlanet import CarlanetActor
from pycarlanet import CarlanetManager
from pycarlanet import CarlanetEventListener, SimulatorStatus

"""This example demonstrates a car equipped with an automatic pilot, where the state of the car's lights is controlled 
by a remote agent hosted on a remote server. The remote agent is implemented within the RemoteAgent class, 
while OMNeT is used for communication.
The remote agent sends a new light state to the car, which then updates its lights and sends a response 
with the new current status. The agent receives the updated status, calculates the new light state, 
and sends it back to the car. This process is repeated in a loop for 100s.
"""
class MyWorld(CarlanetEventListener):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.carlanet_manager = CarlanetManager(5555, self, log_messages=True)

        self.client = self.sim_world = self.carla_map = None
        self.carlanet_actors = dict()
        self.remote_agent = RemoteAgent()

    def start_simulation(self):
        self.carlanet_manager.start_simulation()

    def omnet_init_completed(self, run_id, carla_configuration, user_defined) -> (SimulatorStatus, World):
        random.seed(carla_configuration['seed'])

        print(f'OMNeT world is completed with the id {run_id}')
        world = user_defined['carla_world']  # Retrieve from user_defined

        client: libcarla.Client = carla.Client(self.host, self.port)
        client.set_timeout(15)
        sim_world = client.load_world(world)

        settings = sim_world.get_settings()
        settings.synchronous_mode = True  # Mandatory
        settings.fixed_delta_seconds = carla_configuration['carla_timestep']
        sim_world.apply_settings(settings)
        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)
        traffic_manager.set_random_device_seed(carla_configuration['seed'])
        sim_world.tick()
        sim_world.tick()

        client.reload_world(False)  # Reload map keeping the world settings
        sim_world.set_weather(carla.WeatherParameters.ClearSunset)

        sim_world.tick()
        self.client, self.sim_world = client, sim_world
        self.carla_map = self.sim_world.get_map()

        return SimulatorStatus.RUNNING, self.sim_world

    def actor_created(self, actor_id: str, actor_type: str, actor_config) -> CarlanetActor:
        if actor_type == 'car':  # and actor_id == 'car_1':
            blueprint: ActorBlueprint = random.choice(self.sim_world.get_blueprint_library().filter("vehicle.tesla.model3"))

            spawn_points = self.sim_world.get_map().get_spawn_points()

            settings = self.sim_world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            settings.no_rendering_mode = False
            self.sim_world.apply_settings(settings)

            traffic_manager = self.client.get_trafficmanager()
            traffic_manager.set_synchronous_mode(False)
            self.client.reload_world(False)  # reload map keeping the world settings
            self.sim_world.tick()

            # Attach sensors
            spawn_point = random.choice(spawn_points)
            print(blueprint)
            response = self.client.apply_batch_sync([carla.command.SpawnActor(blueprint, spawn_point)])[0]
            carla_actor: carla.Vehicle = self.sim_world.get_actor(response.actor_id)
            carla_actor.set_simulate_physics(True)
            carla_actor.set_autopilot(True)
            carlanet_actor = CarlanetActor(carla_actor, True)
            self.carlanet_actors[actor_id] = carlanet_actor

            self.sim_world.tick()
            return carlanet_actor
        else:
            raise RuntimeError(f'I don\'t know this type {actor_type}')

    def carla_init_completed(self):
        super().carla_init_completed()

    def before_world_tick(self, timestamp) -> None:
        super().before_world_tick(timestamp)

    def carla_simulation_step(self, timestamp) -> SimulatorStatus:
        self.sim_world.tick()
        # Do all the things, save actors data
        if timestamp > 100:  # ts_limit
            return SimulatorStatus.FINISHED_OK
        else:
            return SimulatorStatus.RUNNING

    def generic_message(self, timestamp, user_defined_message) -> (SimulatorStatus, dict):
        # Handle the action of the actors in the world (apply_commands, calc_instruction)
        # es: apply_commands with id command_12 to actor with id active_actor_14
        if user_defined_message['msg_type'] == 'change_light':
            actor_id = user_defined_message['actor_id']
            self.carlanet_actors[actor_id].set_light_state(user_defined_message['new_state'])

            msg_to_send = {'msg_type': 'light_state',
                           'state': self.carlanet_actors[actor_id].get_traffic_light_state()}
            return SimulatorStatus.RUNNING, msg_to_send
        elif user_defined_message['msg_type'] == 'LIGHT_COMMAND':
            msg_to_send = {'msg_type': 'change_light',
                           'new_state': self.remote_agent.calc_next_light_state(user_defined_message['light_state'])}
            return SimulatorStatus.RUNNING, msg_to_send
        else:
            raise RuntimeError(f"I don\'t know this type {user_defined_message['msg_type']}")

    def simulation_finished(self, status_code: SimulatorStatus):
        super().simulation_finished(status_code)

    def simulation_error(self, exception):
        traceback.print_exc()
        super().simulation_error(exception)


class RemoteAgent:

    def __init__(self):
        self.light_state = carla.VehicleLightState.NONE

    def calc_next_light_state(self, light_state: carla.VehicleLightState):
        if light_state == carla.VehicleLightState.Position:
            next_state = carla.VehicleLightState.Brake
        elif light_state == carla.VehicleLightState.Brake:
            next_state = carla.VehicleLightState.All
        elif light_state == carla.VehicleLightState.NONE:
            next_state = carla.VehicleLightState.Position
        else:
            next_state = carla.VehicleLightState.NONE
        return next_state



if __name__ == '__main__':
    my_world = MyWorld('marine', 2000)
    my_world.start_simulation()