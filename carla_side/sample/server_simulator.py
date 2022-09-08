import json

import pandas as pd
import zmq


def read_json(path):
    with open(path) as f:
        return json.load(f)


def send_info(socket, t):
    socket.send(json.dumps(t).encode("utf-8"))


def generate_init_completed(first_row):
    res = dict()
    res['message_type'] = "INIT_COMPLETED"
    res['payload'] = dict()
    res['payload']['initial_timestamp'] = first_row['timestamp']
    # return json.dumps(res).encode("utf-8")
    return res


def generate_updated_position(row):
    res = dict()
    res['message_type'] = "UPDATED_POSITIONS"
    actor = dict()
    actor['actor_id'] = 'car'
    actor['position'] = [row['location_x'], row['location_y'], row['location_z']]
    actor['velocity'] = [row['velocity_x'], row['velocity_y'], row['velocity_z']]
    actor['rotation'] = [row['rotation_pitch'], row['rotation_yaw'], row['rotation_roll']]
    res['payload'] = dict()
    res['payload']['actors'] = [actor]
    res['simulation_status'] = 0

    # return json.dumps(res).encode("utf-8")
    return res


if __name__ == '__main__':
    data = pd.read_csv('sample/omnet_network/server_simulator/sensors.csv')
    data_iterators = data.iterrows()
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:5555")

    recv_msg = socket.recv()
    print(recv_msg)
    json_data = json.loads(recv_msg.decode("utf-8"))
    print("recv:", json_data)
    msg = read_json('documentation/api_carla_omnet/init/to_omnet.json')
    print(msg)
    print("\n\n")
    send_info(socket, msg)

    # for _, row in data_iterators:
    while msg['simulation_status'] == 0:
        recv_msg = socket.recv()
        json_data = json.loads(recv_msg.decode("utf-8"))
        print("recv:", json_data)
        if json_data['message_type'] == 'COMPUTE_INSTRUCTION':
            msg = read_json('documentation/api_carla_omnet/compute_instruction/to_omnet.json')
        elif json_data['message_type'] == 'APPLY_INSTRUCTION':
            msg = read_json('documentation/api_carla_omnet/apply_instruction/to_omnet.json')
        elif json_data['message_type'] == 'ACTOR_STATUS_UPDATE':
            msg = read_json('documentation/api_carla_omnet/actor_status_update/to_omnet.json')
        elif json_data['message_type'] == 'SIMULATION_STEP':
            next_position = next(data_iterators, None)
            if next_position is None:
                msg = read_json('documentation/api_carla_omnet/simulation_step/to_omnet.json')
                msg['simulation_status'] = 1
            else:
                msg = generate_updated_position(next_position[1])
            msg['payload']['actors'][0]['actor_id'] = 'car'

        else:
            raise Exception("Message not recognized")
        print(msg)
        print("\n\n")
        send_info(socket, msg)

#
