import json
import multiprocessing
from time import sleep
from unittest.mock import MagicMock
import pytest
import carla
import zmq

import random

from pycarlanet import CarlanetManager
from pycarlanet import SimulatorStatus


def test_creation_of_server():
    port = random.randint(5000, 6000)

    p = _start_server(port, None)
    assert p.is_alive()
    _end_server(p)


def _create_init_listener():
    omnet_worl_listener = MagicMock()
    carla_actor = MagicMock()
    carla_actor.get_transform.return_value = carla.Transform(carla.Location(1, 2, 3), carla.Rotation(1, 2, 3))
    carla_actor.get_velocity.return_value = carla.Vector3D(1, 2, 3)
    carla_actor.alive.return_value = True

    omnet_worl_listener.on_finished_creation_omnet_world.return_value = 10, SimulatorStatus.RUNNING
    omnet_worl_listener.on_static_actor_created.return_value = carla_actor
    return omnet_worl_listener


def test_init_with_my_client():
    port = random.randint(5000, 6000)

    omnet_worl_listener = MagicMock()
    carla_timestamp = 0.76

    carla_actor = MagicMock()
    carla_actor.get_transform.return_value = carla.Transform(carla.Location(1, 2, 3), carla.Rotation(1, 2, 3))
    carla_actor.get_velocity.return_value = carla.Vector3D(1, 2, 3)
    # carla_actor.alive.return_value = True
    carla_actor.alive = True
    omnet_worl_listener.on_finished_creation_omnet_world.return_value = carla_timestamp, SimulatorStatus.RUNNING
    omnet_worl_listener.on_static_actor_created.return_value = carla_timestamp, carla_actor

    p = _start_server(port, omnet_worl_listener)
    init_request = _read_request('init')

    s = _connect('localhost', port)
    _send_message(s, init_request)
    msg = _receive_message(s)  # omnet_worl_listener.on_finished_creation_omnet_world.assert_called_once()
    assert msg['initial_timestamp'] == carla_timestamp
    assert msg['actors_positions'][0]['position'][0] == 1
    # assert omnet_worl_listener.on_finished_creation_omnet_world.call_count == 1
    _end_server(p)


# def test_init_with_omnet():
#     omnet_worl_listener = MagicMock()
#     carla_timestamp = 0.76
#
#     carla_actor = MagicMock()
#     carla_actor.get_transform.return_value = carla.Transform(carla.Location(1, 2, 3), carla.Rotation(1, 2, 3))
#     carla_actor.get_velocity.return_value = carla.Vector3D(1, 2, 3)
#     carla_actor.alive = True
#     omnet_worl_listener.on_finished_creation_omnet_world.return_value = carla_timestamp
#     omnet_worl_listener.on_static_actor_created.return_value = carla_actor
#     p = _start_server(5555, omnet_worl_listener)
#     p.join()
#     _end_server(p)


def test_simulation_step_with_my_client():
    port = random.randint(5000, 6000)

    s = _connect('localhost', port)
    carla_timestamp = 0.76

    omnet_worl_listener = _create_init_listener()
    omnet_worl_listener.on_carla_simulation_step.return_value = SimulatorStatus.RUNNING
    # omnet_worl_listener.on_carla_simulation_step.return_value = carla_timestamp, SimulatorStatus.RUNNING
    p = _start_server(port, omnet_worl_listener)
    init_request = _read_request('init')
    init_request['moving_actors'] = []
    _send_message(s, init_request)
    _ = _receive_message(s)  # omnet_worl_listener.on_finished_creation_omnet_world.assert_called_once()

    simulation_step_request = _read_request('simulation_step')
    _send_message(s, simulation_step_request)
    msg = _receive_message(s)
    # omnet_worl_listener.on_carla_simulation_step.assert_called_once()
    _end_server(p)


def _start_server(port, omnet_world_listener):
    carlanet_manager = CarlanetManager(port, omnet_world_listener)
    p = multiprocessing.Process(target=carlanet_manager.start_simulation, args=())
    p.start()
    return p


def _end_server(process):
    process.terminate()


def _read_request(type_request):
    with open(f'tests/communication_models/{type_request}/from_omnet.json') as f:
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
    test_simulation_step_with_my_client()
