from datetime import datetime
import json
import random
import sys
import time

import numpy as np
import zmq


def read_json(type_request):
    with open(f'sample/car_light_control/fake_carlanetpp/api/{type_request}.json') as f:
        return json.load(f)


def send_info(socket, t):
    print("Send: ", json.dumps(t).encode("utf-8"))
    socket.send(json.dumps(t).encode("utf-8"))


def receive_info(socket):
    message = socket.recv()
    print("Received: ", message.decode("utf-8"))
    json_data = json.loads(message.decode("utf-8"))
    if json_data['simulation_status'] != 0: sys.exit(0)
    return json_data


if __name__ == '__main__':
    simulation_step = 0.01
    transmission_delay = 0.05
    delay = 0  # TODO implements this feature

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    print("connected")

    limit_sim_time = 15
    req = read_json('init')
    send_info(socket, req)

    message = receive_info(socket)
    timestamp = message['initial_timestamp']

    light_curr_state = 0
    light_next_state = 0
    while True:
        req = read_json('light_update')
        req['user_defined']['light_curr_state'] = light_curr_state
        req['timestamp'] = timestamp
        send_info(socket, req)
        message = receive_info(socket)
        if message['simulation_status'] != 0:
            break
        
        light_next_state = message['user_defined']['light_next_state']
        
        for _ in np.arange(0, transmission_delay, simulation_step):
            timestamp += simulation_step
            req = read_json('simulation_step')

            req['timestamp'] = timestamp
            send_info(socket, req)
            message = receive_info(socket)

        req = read_json('light_command')
        req['user_defined']['light_next_state'] = light_next_state
        req['timestamp'] =  timestamp
        send_info(socket, req)
        message = receive_info(socket)
        light_curr_state = message['user_defined']['light_curr_state']