from carla.libcarla import World
from pycarlanet.utils import DecoratorSingleton
import carla

@DecoratorSingleton
class CarlaClient():

    _host: str = None
    _port: int = None
    _client: carla.Client = None

    def __init__(self, host, port):
        self._host = host
        self._port = port

        try:
            self._client = carla.Client(self._host, self._port)
            self._client.set_timeout(15)
            #self._world = self._client.get_world()
        except Exception as e:
            CarlaClient._instance = None
            raise Exception("error from CarlaClient class while connecting to carla simulator")
    
    @property
    def world(self):
        return self._client.get_world()

    @property
    def client(self):
        return self._client
