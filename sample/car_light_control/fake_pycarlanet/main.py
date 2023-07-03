import json
import sys

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
    res['initial_timestamp'] = first_row['timestamp']
    res['actor_positions'] = dict()
    # return json.dumps(res).encode("utf-8")
    return res


def generate_updated_position(row):
    actor = dict()
    actor['actor_id'] = 'car'
    actor['is_net_active'] = True
    actor['position'] = [row['location_x'], row['location_y'], row['location_z']]
    actor['velocity'] = [row['velocity_x'], row['velocity_y'], row['velocity_z']]
    actor['rotation'] = [row['rotation_pitch'], row['rotation_yaw'], row['rotation_roll']]

    return actor


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # infinite iterator which return always the same value
        def constant_data_iterators():
            while True:
                yield { "location_x": 50, "location_y": 325, "location_z": 0.1, "velocity_x": 0.1, "velocity_y": 0.1, "velocity_z": 0.1, "rotation_pitch": 0.1, "rotation_yaw": 0.1, "rotation_roll": 0.1 }
        data_iterators = constant_data_iterators()
    else:
        data = pd.read_csv(sys.argv[1])
        data_iterators = data.iterrows()
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:5555")

    recv_msg = socket.recv()
    json_data = json.loads(recv_msg.decode("utf-8"))
    print("recv:", json_data)
    car_id = json_data['moving_actors'][0]['actor_id']
    msg = read_json('sample/standalone_rensponse_generator/init.json')

    actor_status = generate_updated_position(next(data_iterators))
    msg['actor_positions'][0]['actor_id'] = car_id
    msg['actor_positions'][0]['position'] = actor_status['position']
    msg['actor_positions'][0]['rotation'] = actor_status['rotation']

    print(msg)
    print("\n\n")
    send_info(socket, msg)


    # for _, row in data_iterators:
    while msg['simulation_status'] == 0:
        recv_msg = socket.recv()
        json_data = json.loads(recv_msg.decode("utf-8"))
        if json_data['message_type'] == 'GENERIC_MESSAGE':
            print("recv:", json_data)
            if json_data['user_defined']['msg_type'] == 'LIGHT_UPDATE':
                msg = read_json('sample/standalone_rensponse_generator/light_command.json')
                msg['user_defined']['light_next_state'] = str(int(json_data['user_defined']['light_curr_state']))
            elif json_data['user_defined']['msg_type'] == 'LIGHT_COMMAND':
                msg = read_json('sample/standalone_rensponse_generator/light_update.json')
                msg['user_defined']['light_curr_state'] = str((int(json_data['user_defined']['light_next_state']) + 1) % 4)
            else:
                raise Exception("general message not recognized: " + json_data['user_defined']['user_message_type'])
            print('send:', msg, '\n\n')

        elif json_data['message_type'] == 'SIMULATION_STEP':
            msg = read_json('sample/standalone_rensponse_generator/simulation_step.json')
            msg['actor_positions'] = []

            next_position = next(data_iterators, None)
            if next_position is None:
                msg['simulation_status'] = 1
            else:
                msg['actor_positions'].append(generate_updated_position(next_position))
                msg['actor_positions'][0]['actor_id'] = 'car'
                msg['actor_positions'][0]['actor_id'] = car_id

        else:
            raise Exception("Message not recognized: " + json_data['message_type'])
        
        send_info(socket, msg)

#
