import random
import carla

import time

from carla.libcarla import ActorBlueprint, World

import inspect

from pycarlanet.utils import InstanceExist
from pycarlanet.listeners import WorldManager, ActorManager, AgentManager
from pycarlanet.enum import SimulatorStatus, CarlaMaplayers
from pycarlanet import CarlaClient, SocketManager, ActorType, CarlanetActor

# get light control enum from int value
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
def _light_control_enum_to_str(light_enum):
    if light_enum == carla.VehicleLightState.NONE:
        return '0'
    elif light_enum == carla.VehicleLightState.Position:
        return '1'
    elif light_enum == carla.VehicleLightState.Brake:
        return '2'
    else:
        return '3'

class worldManager(WorldManager):
    def omnet_init_completed(self, message) -> (SimulatorStatus, World):
        super().omnet_init_completed(message=message)
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name}")
        super().load_world("Town05_opt", [CarlaMaplayers.Buildings, CarlaMaplayers.Foliage])
        self.world.set_weather(carla.WeatherParameters.ClearNight)
        self.tick()
        traffic_manager = CarlaClient.instance.client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)
        traffic_manager.set_random_device_seed(message['carla_configuration']['seed'])
        self.tick()
        return SimulatorStatus.RUNNING, self.world

    def after_world_tick(self, timestamp) -> SimulatorStatus:
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name}")
        if timestamp > 20:
           return SimulatorStatus.FINISHED_OK
        else:
           return SimulatorStatus.RUNNING    

    def generic_message(self, timestamp, message) -> (SimulatorStatus, dict):
        print("world generic_message")
        return SimulatorStatus.RUNNING, {}

class actorManager(ActorManager):

    def omnet_init_completed(self, message):
        super().omnet_init_completed(message=message)
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name}")
        # try:
        #     spawnPoints = CarlaClient.instance.world.get_map().get_spawn_points()
        #     if len(spawnPoints) < 1 : raise Exception("error, non sufficient spawn points")
        #     for i in range(0,1):
        #         blueprint_library = CarlaClient.instance.world.get_blueprint_library()
        #         vehicle_bp = blueprint_library.filter("vehicle")[0]
        #         vehicle = CarlaClient.instance.world.spawn_actor(vehicle_bp, spawnPoints[i])
        #         vehicle.set_autopilot(True)
        #         super().add_carla_actor_to_omnet(vehicle)
        # except Exception as e:
        #     print(e)

    @InstanceExist(CarlaClient)
    def create_actors_from_omnet(self, actors):
        for actor in actors:
            if actor['actor_type'] == 'car':  # and actor_id == 'car_1':
                blueprint: ActorBlueprint = random.choice(CarlaClient.instance.world.get_blueprint_library().filter("vehicle.tesla.model3"))

                spawn_points = CarlaClient.instance.world.get_map().get_spawn_points()
                # Attach sensors
                spawn_point = random.choice(spawn_points)
                print(blueprint)
                response = CarlaClient.instance.client.apply_batch_sync([carla.command.SpawnActor(blueprint, spawn_point)])[0]
                carla_actor: carla.Vehicle = CarlaClient.instance.world.get_actor(response.actor_id)
                carla_actor.set_simulate_physics(True)
                carla_actor.set_autopilot(False)
                carlanet_actor = CarlanetActor(carla_actor, ActorType.instance.get_available_types()[0])
                #self.carlanet_actors[actor_id] = carlanet_actor
                self._carlanet_actors[actor['actor_id']] = carlanet_actor
                #self._car = carlanet_actor

                #self.sim_world.tick()

                #camera_sensor = TeleCarlaCameraSensor(2.2)
                #self._create_display(carla_actor, 1280, 720, camera_sensor)
                #camera_sensor.attach_to_actor(self.sim_world, carla_actor)
                return carlanet_actor
            else:
                raise RuntimeError(f"I don\'t know this type {actor['actor_type']}")

    def generic_message(self, timestamp, message) -> (SimulatorStatus, dict):
        print("actor generic_message")
        if message['msg_type'] == 'LIGHT_COMMAND':
            next_light_state = _str_to_light_control_enum(message['light_next_state'])
            key = next(iter(self._carlanet_actors))
            car: carla.Actor = self._carlanet_actors[k].carla_actor
            car.set_light_state(next_light_state)
            msg_to_send = {
                'msg_type': 'LIGHT_UPDATE',
                'light_curr_state': _light_control_enum_to_str(car.get_light_state())
            }
            
            print("LIGHT CURR STATE: ", car.get_light_state(), '\n\n')
            return SimulatorStatus.RUNNING, msg_to_send
        else:
            raise RuntimeError(f"I don\'t know this type {message['msg_type']}")


class agentManager(AgentManager):    
    def generic_message(self, timestamp, message) -> (SimulatorStatus, dict):
        print("agent generic_message")
        if message['msg_type'] == 'LIGHT_UPDATE':
            curr_light_state = _str_to_light_control_enum(message['light_curr_state'])
            next_light_state = self.calc_next_light_state(curr_light_state)
            print("LIGHT CURR STATE: ", curr_light_state, "LIGHT NEXT STATE: ", next_light_state, '\n')

            msg_to_send = {
                'msg_type': 'LIGHT_COMMAND',
                'light_next_state': _light_control_enum_to_str(next_light_state)
            }

            return SimulatorStatus.RUNNING, msg_to_send
        else:
            raise RuntimeError(f"I don\'t know this type {message['msg_type']}")

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

#SimulationManager(carla_sh_path='/home/stefano/Documents/tesi/CARLA_0.9.15/CarlaUE4.sh')
#SimulationManager.instance.reload_simulator()
#time.sleep(5)
CarlaClient(host='localhost', port=2000)

SocketManager(
    listening_port=5555,
    worldManager=worldManager(synchronousMode=False, renderingMode=True),
    actorManager=actorManager(),
    agentManager=agentManager()
    log_messages=True
)

SocketManager.instance.start_socket()