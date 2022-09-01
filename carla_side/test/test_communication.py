import json
import multiprocessing
from time import sleep
from unittest.mock import MagicMock

import carla
import pytest
import zmq

from CarlaInetManager import CarlaInetManager
from OMNeTWorldListener import OMNeTWorldListener


def test_creation_of_server():
    p = _start_server(5555, None)
    assert p.is_alive()
    _end_server(p)


def test_init_with_my_client():
    s = _connect('localhost', 5555)
    omnet_worl_listener = MagicMock()
    carla_timestamp = 0.76

    carla_actor = MagicMock()
    carla_actor.get_transform.return_value = carla.Transform(carla.Location(1, 2, 3), carla.Rotation(1, 2, 3))
    carla_actor.get_velocity.return_value = carla.Vector3D(1, 2, 3)
    carla_actor.alive.return_value = True
    omnet_worl_listener.on_finished_creation_omnet_world.return_value = carla_timestamp
    omnet_worl_listener.on_static_actor_created.return_value = carla_actor
    p = _start_server(5555, omnet_worl_listener)
    init_request = _read_request('init')
    _send_message(s, init_request)
    msg = _receive_message(s)
    assert msg['carla_timestamp'] == carla_timestamp
    assert msg['positions'][0]['position'][0] == 1
    _end_server(p)


def test_init_with_omnet():
    omnet_worl_listener = MagicMock()
    carla_timestamp = 0.76

    carla_actor = MagicMock()
    carla_actor.get_transform.return_value = carla.Transform(carla.Location(1, 2, 3), carla.Rotation(1, 2, 3))
    carla_actor.get_velocity.return_value = carla.Vector3D(1, 2, 3)
    carla_actor.alive.return_value = True
    omnet_worl_listener.on_finished_creation_omnet_world.return_value = carla_timestamp
    omnet_worl_listener.on_static_actor_created.return_value = carla_actor
    p = _start_server(5555, omnet_worl_listener)
    p.join()
    _end_server(p)


def _start_server(port, omnet_world_listener):
    carla_inet_manager = CarlaInetManager(port, omnet_world_listener)
    p = multiprocessing.Process(target=carla_inet_manager.start_simulation, args=())
    p.start()
    return p


def _end_server(process):
    process.terminate()


def _read_request(type_request):
    with open(f'../api_documentation/{type_request}/from_omnet.json') as f:
        return json.load(f)


def _send_message(socket, t):
    socket.send(json.dumps(t).encode("utf-8"))


def _receive_message(s):
    message = s.recv()
    json_data = json.loads(message.decode("utf-8"))
    return json_data


def _connect(host, port):
    context = zmq.Context()

    socket = context.socket(zmq.REQ)
    socket.connect(f'tcp://{host}:{port}')
    return socket


if __name__ == '__main__':
    test_init_with_omnet()
