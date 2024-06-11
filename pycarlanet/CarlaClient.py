from carla.libcarla import World
import carla

from pycarlanet.utils import DecoratorSingleton

@DecoratorSingleton
class CarlaClient():

    _host: str = None
    _port: int = None
    _client: carla.Client = None

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

        try:
            self._client = carla.Client(self._host, self._port)
            self._client.set_timeout(15)
        except Exception as e:
            CarlaClient._instance = None
            raise Exception("error from CarlaClient class while connecting to carla simulator")
    
    @property
    def world(self):
        return self._client.get_world()

    @property
    def client(self):
        return self._client
