import random
import carla
from carla import libcarla, ActorBlueprint, World
import traceback
import pygame

from pycarlanet import CarlanetActor
from pycarlanet import CarlanetManager
from pycarlanet import CarlanetEventListener, SimulatorStatus

from example.car_light_control.carla_window import HUD, TeleCarlaCameraSensor


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
        self._car = None
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
        
        settings.synchronous_mode = False
        settings.fixed_delta_seconds = None
        settings.no_rendering_mode = False
        settings.fixed_delta_seconds = carla_configuration['carla_timestep']

        sim_world.set_weather(carla.WeatherParameters.ClearNight)

        sim_world.apply_settings(settings)
        sim_world.tick()
        
        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)
        traffic_manager.set_random_device_seed(carla_configuration['seed'])
        sim_world.tick()

        client.reload_world(False)  # Reload map keeping the world settings
        sim_world.set_weather(carla.WeatherParameters.ClearNight)

        sim_world.tick()
        self.client, self.sim_world = client, sim_world
        self.carla_map = self.sim_world.get_map()

        return SimulatorStatus.RUNNING, self.sim_world

    def actor_created(self, actor_id: str, actor_type: str, actor_config) -> CarlanetActor:
        if actor_type == 'car':  # and actor_id == 'car_1':
            blueprint: ActorBlueprint = random.choice(self.sim_world.get_blueprint_library().filter("vehicle.tesla.model3"))

            spawn_points = self.sim_world.get_map().get_spawn_points()
            # Attach sensors
            spawn_point = random.choice(spawn_points)
            print(blueprint)
            response = self.client.apply_batch_sync([carla.command.SpawnActor(blueprint, spawn_point)])[0]
            carla_actor: carla.Vehicle = self.sim_world.get_actor(response.actor_id)
            carla_actor.set_simulate_physics(True)
            carla_actor.set_autopilot(False)
            carlanet_actor = CarlanetActor(carla_actor, True)
            self.carlanet_actors[actor_id] = carlanet_actor
            self._car = carlanet_actor

            self.sim_world.tick()

            camera_sensor = TeleCarlaCameraSensor(2.2)
            self._create_display(carla_actor, 1280, 720, camera_sensor)
            camera_sensor.attach_to_actor(self.sim_world, carla_actor)
            return carlanet_actor
        else:
            raise RuntimeError(f'I don\'t know this type {actor_type}')
        
    def _create_display(self, player, camera_width, camera_height, camera_sensor):
        pygame.init()
        pygame.font.init()
        display = pygame.display.set_mode((camera_width, camera_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        # display.fill((0, 0, 0))
        pygame.display.flip()

        hud = HUD(player, pygame.time.Clock(), display)
        camera_sensor.add_display(display)

        def render(_):
            camera_sensor.render()
            hud.render()
            pygame.display.flip()

        self.sim_world.on_tick(render)
        self.sim_world.on_tick(hud.tick)

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

    # get light control enum from int value
    @staticmethod
    def _str_to_light_control_enum(light_value):
        if light_value == '0':
            return carla.VehicleLightState.NONE
        elif light_value == '1':
            return carla.VehicleLightState.Position
        elif light_value == '2':
            return carla.VehicleLightState.Brake
        else:
            return carla.VehicleLightState.All
        
    # get int value from light control enum
    @staticmethod
    def _light_control_enum_to_str(light_enum):
        if light_enum == carla.VehicleLightState.NONE:
            return '0'
        elif light_enum == carla.VehicleLightState.Position:
            return '1'
        elif light_enum == carla.VehicleLightState.Brake:
            return '2'
        else:
            return '3'
        
    

    
    def generic_message(self, timestamp, user_defined_message) -> (SimulatorStatus, dict):
        # Handle the action of the actors in the world (apply_commands, calc_instruction)
        # es: apply_commands with id command_12 to actor with id active_actor_14
        if user_defined_message['msg_type'] == 'LIGHT_COMMAND':
            #actor_id = user_defined_message['actor_id']
            #self.carlanet_actors[actor_id].set_light_state(user_defined_message['light_next_state'])
            
            #convert enum value to enum
            next_light_state = self._str_to_light_control_enum(user_defined_message['light_next_state'])
            self._car.set_light_state(next_light_state)

            msg_to_send = {'msg_type': 'LIGHT_UPDATE',
                           'light_curr_state': self._light_control_enum_to_str(self._car.get_light_state())}
            
            print("LIGHT CURR STATE: ", self._car.get_light_state(), '\n\n')
            return SimulatorStatus.RUNNING, msg_to_send
        elif user_defined_message['msg_type'] == 'LIGHT_UPDATE':
            curr_light_state = self._str_to_light_control_enum(user_defined_message['light_curr_state'])
            next_light_state = self.remote_agent.calc_next_light_state(curr_light_state)
            print("LIGHT CURR STATE: ", curr_light_state, "LIGHT NEXT STATE: ", next_light_state, '\n')

            msg_to_send = {'msg_type': 'LIGHT_COMMAND',
                           'light_next_state': self._light_control_enum_to_str(next_light_state)}
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
    #my_world = MyWorld('192.168.1.37', 2000)
    my_world = MyWorld('marine', 5000)
    my_world.start_simulation()