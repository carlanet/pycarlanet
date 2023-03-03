import json

import zmq


def read_json(path):
    with open(path) as f:
        return json.load(f)


def send_info(socket, t):
    print(json.dumps(t).encode('utf-8'))
    socket.send(json.dumps(t).encode("utf-8"))


def generate_init_completed(first_row):
    res = dict()
    res['message_type'] = "INIT_COMPLETED"
    res['payload'] = dict()
    res['payload']['initial_timestamp'] = first_row['timestamp']
    # return json.dumps(res).encode("utf-8")
    return res





def generate_new_position(actor_id, old_position):
    return {
        "actor_id": actor_id,
        "position": [old_position[0] + 0.5, old_position[1] + 0.5, 0],
        "velocity": [0.1, 0.1, 0.1],
        "rotation": [0.1, 0.1, 0.1],
        "is_net_active": True
    }


""" 
OMNeT gives only one static actor
"""
if __name__ == '__main__':
    dynamic_actors = {
        'dynamic_1': {
            'timestamp_start': 10,
            'timestamp_end': -1,  # -1 for infinite, now it doesn't work
            'position_x': 0,
            'position_y': 0,
        }
    }


    active_actors = dict()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:5555")

    recv_msg = socket.recv()

    # Main actor

    json_data = json.loads(recv_msg.decode("utf-8"))
    actor_id = json_data['moving_actors'][0]['actor_id']
    active_actors[actor_id] = {'position': (0, 0, 0)}

    msg = read_json('../api_documentation/init/to_omnet.json')
    print(msg['actors_positions'][0]['position'])
    msg['actors_positions'][0]['position'] = active_actors[actor_id]['position']
    send_info(socket, msg)

    # for _, row in data_iterators:
    while msg['simulation_status'] == 0:
        recv_msg = socket.recv()
        json_data = json.loads(recv_msg.decode("utf-8"))
        print("recv:", json_data)
        if json_data['message_type'] == 'GENERIC_MESSAGE':
            msg = read_json('../api_documentation/message/to_omnet.json')
        elif json_data['message_type'] == 'SIMULATION_STEP':
            current_timestamp = json_data['timestamp']
            dynamic_actors_to_spawn_id = dynamic_actors.keys() - active_actors.keys()

            # Dynamic adding of an actor
            for actor_to_spawn_id in dynamic_actors_to_spawn_id:
                if current_timestamp > dynamic_actors[actor_to_spawn_id]['timestamp_start']:
                    active_actors[actor_to_spawn_id] = {'position': (0, 0, 0)}
            # Dynamic removing of an actor
            keys_to_remove = []
            for active_actor_id in active_actors.keys():
                if active_actor_id in dynamic_actors.keys() and dynamic_actors[active_actor_id][
                    'timestamp_end'] > current_timestamp:
                    keys_to_remove = active_actors[active_actor_id]

            msg = read_json('../api_documentation/simulation_step/to_omnet.json')
            msg['actors_positions'] = list()
            for active_actor_id in active_actors.keys():
                actor_position = generate_new_position(active_actor_id, active_actors[active_actor_id]['position'])
                active_actors[active_actor_id]['position'] = actor_position['position']
                msg['actors_positions'].append(actor_position)
        send_info(socket, msg)
#
