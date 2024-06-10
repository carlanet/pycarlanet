import carla
import time

from carla.libcarla import World

import inspect

from pycarlanet.utils import InstanceExist
from pycarlanet.listeners import WorldManager, ActorManager
from pycarlanet.enum import SimulatorStatus, CarlaMaplayers
from pycarlanet import CarlaClient, SocketManager

class wManager(WorldManager):
    def omnet_init_completed(self, message) -> (SimulatorStatus, World):
        super().omnet_init_completed(message=message)
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name}")
        super().load_world("Town05_opt", [CarlaMaplayers.Buildings, CarlaMaplayers.Foliage])
        return SimulatorStatus.RUNNING, self.world

    def after_world_tick(self, timestamp) -> SimulatorStatus:
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name}")
        if timestamp > 20:
           return SimulatorStatus.FINISHED_OK
        else:
           return SimulatorStatus.RUNNING    

class aManager(ActorManager):
    @InstanceExist(CarlaClient)
    def omnet_init_completed(self, message):
        #print(f"{self.__class__.__name__} {inspect.currentframe().f_code.co_name}")
        try:
            spawnPoints = CarlaClient.instance.world.get_map().get_spawn_points()
            if len(spawnPoints) < 1 : raise Exception("error, non sufficient spawn points")
            for i in range(0,1):
                blueprint_library = CarlaClient.instance.world.get_blueprint_library()
                vehicle_bp = blueprint_library.filter("vehicle")[0]
                vehicle = CarlaClient.instance.world.spawn_actor(vehicle_bp, spawnPoints[i])
                vehicle.set_autopilot(True)
                super().add_carla_actor_to_omnet(vehicle)
        except Exception as e:
            print(e)


#SimulationManager(carla_sh_path='/home/stefano/Documents/tesi/CARLA_0.9.15/CarlaUE4.sh')
#SimulationManager.instance.reload_simulator()
#time.sleep(5)
CarlaClient(host='localhost', port=2000)

SocketManager(listening_port=5555, worldManager=wManager(synchronousMode=True), actorManager=aManager(), log_messages=True)
SocketManager.instance.start_socket()