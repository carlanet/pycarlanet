import zmq
import time
import json



simulation_step = 0.01
refresh_status = 0.05
delay = 0  # TODO implements this feature

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
print("connected")

msg = {
        'carla_configuration': {'carla_timestep': 0.05, 'seed': 0, 'sim_time_limit': -1.0},
        'message_type': 'INIT',
        'moving_actors': [
            {
                "actor_id": "car_id_1",
                "actor_type": "car",
                "actor_configuration": {
                    
                }
            }
        ],
        'run_id': 'General-0-20240606-23:42:38-160063',
        'timestamp': 0.0,
        'user_defined': {'config_name': 'c01'}
    }
socket.send(json.dumps(msg).encode('utf-8'))
print(f"send {msg}\n")
message = socket.recv()
json_data = json.loads(message.decode("utf-8"))
print(f"received {json_data}\n")
timestamp = json_data["initial_timestamp"] + simulation_step

while True:
    msg = {
            "message_type": "SIMULATION_STEP",
            "carla_timestep": 0.05,
            "timestamp": timestamp  
        }
    socket.send(json.dumps(msg).encode('utf-8'))
    print(f"send {msg}\n")
    message = socket.recv()
    json_data = json.loads(message.decode("utf-8"))
    print(f"received {json_data}\n")
    
    timestamp += simulation_step

    time.sleep(0.2)