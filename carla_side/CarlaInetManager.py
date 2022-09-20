import abc
import json

import carla
import zmq

from OMNeTWorldListener import OMNeTWorldListener, SimulatorStatus
from CarlaInetActor import CarlaInetActor
from utils.decorators import preconditions


class UnknownMessageCarlaInetError(RuntimeError):
    def __init__(self, unknown_msg):
        self.unknown_msg = unknown_msg

    def __repr__(self) -> str:
        return "I don't know how to handle the following msg: " + self.unknown_msg['message_type']


class CarlaInetManager:
    def __init__(self, listening_port, omnet_world_listener: OMNeTWorldListener):
        self._listening_port = listening_port
        self._omnet_world_listener = omnet_world_listener
        self._message_handler: MessageHandlerState = None
        self._carla_inet_actors = dict()

    def _start_server(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.setsockopt(zmq.CONFLATE, 1)
        self.socket.setsockopt(zmq.LINGER, 100)
        self.socket.bind(f"tcp://*:{self._listening_port}")
        print("server running")

    def _receive_data_from_omnet(self):
        message = self.socket.recv()
        json_data = json.loads(message.decode("utf-8"))
        print(json_data)
        self.timestamp = json_data['timestamp']
        return json_data

    def start_simulation(self):
        self._start_server()
        self.set_message_handler_state(InitMessageHandlerState)
        while not isinstance(self._message_handler, FinishedMessageHandlerState):
            msg = self._receive_data_from_omnet()
            answer = self._message_handler.handle_message(msg)
            self._send_data_to_omnet(answer)

        self.socket.close()

    def _send_data_to_omnet(self, answer):
        print(answer)

        self.socket.send(json.dumps(answer).encode('utf-8'))

    def set_message_handler_state(self, msg_handler_cls):
        self._message_handler = msg_handler_cls(self)

    def add_dynamic_actor(self, actor_id: str, carla_inet_actor: CarlaInetActor):
        """
        Used to create dynamically a new actor, both active and passive, and send its position to OMNeT
        :param actor_id:
        :param carla_inet_actor:
        :return:
        """
        self._carla_inet_actors[actor_id] = carla_inet_actor

    def remove_actor(self, actor_id: str):
        """
        Remove actor from OMNeT world
        :param actor_id:
        :return:
        """
        del self._carla_inet_actors[actor_id]


class MessageHandlerState(abc.ABC):
    def __init__(self, carla_inet_manager: CarlaInetManager):
        self._manager = carla_inet_manager
        self.omnet_world_listener: OMNeTWorldListener = self._manager._omnet_world_listener
        self._carla_inet_actors = self._manager._carla_inet_actors

    def handle_message(self, message):
        message_type = message['message_type']
        if hasattr(self, message_type):
            meth = getattr(self, message_type)
            return meth(message)
        raise RuntimeError(f"""I'm in the following state: {self.__class__.__name__} and 
                                    I don't know how to handle {message['message_type']} message""")

    @preconditions('_manager')
    def _generate_carla_nodes_positions(self):
        nodes_positions = []
        for actor_id, actor in self._carla_inet_actors.items():
            transform: carla.Transform = actor.get_transform()
            velocity: carla.Vector3D = actor.get_velocity()
            position = dict()
            position['actor_id'] = actor_id
            position['position'] = [transform.location.x, transform.location.y, transform.location.z]
            position['rotation'] = [transform.rotation.pitch, transform.rotation.yaw, transform.rotation.roll]
            position['velocity'] = [velocity.x, velocity.y, velocity.z]
            position['is_net_active'] = actor.alive()
            nodes_positions.append(position)
        return nodes_positions


class InitMessageHandlerState(MessageHandlerState):

    def __init__(self, carla_inet_manager: CarlaInetManager):
        super().__init__(carla_inet_manager)

    def INIT(self, message):
        res = dict()
        res['message_type'] = 'INIT_COMPLETED'
        carla_timestamp, sim_status = self.omnet_world_listener.on_finished_creation_omnet_world(
            run_id=message['run_id'],
            seed = message['carla_configuration']['seed'],
            carla_timestep = message['carla_configuration']['carla_timestep'],
            sim_time_limit = message['carla_configuration']['sim_time_limit'],
            custom_params=message['user_defined'])
        for static_inet_actor in message['moving_actors']:
            actor_id = static_inet_actor['actor_id']
            carla_timestamp, self._carla_inet_actors[actor_id] = self.omnet_world_listener.on_static_actor_created(
                actor_id,
                static_inet_actor['actor_type'],
                static_inet_actor['actor_configuration']
            )
        res['initial_timestamp'] = carla_timestamp
        res['simulation_status'] = sim_status.value
        res['actors_positions'] = self._generate_carla_nodes_positions()
        if sim_status == SimulatorStatus.RUNNING:
            self._manager.set_message_handler_state(RunningMessageHandlerState)
        return res


class RunningMessageHandlerState(MessageHandlerState):
    def SIMULATION_STEP(self, message):
        res = dict()
        res['message_type'] = 'UPDATED_POSITIONS'
        sim_status = self.omnet_world_listener.on_carla_simulation_step(message['timestamp'])
        res['simulation_status'] = sim_status.value
        res['actors_positions'] = self._generate_carla_nodes_positions()
        if sim_status != SimulatorStatus.RUNNING:
            self._manager.set_message_handler_state(FinishedMessageHandlerState)
        return res

    def GENERIC_MESSAGE(self, message):
        res = dict()
        res['message_type'] = 'GENERIC_RESPONSE'
        sim_status, user_defined_response = self.omnet_world_listener.on_generic_message(message['timestamp'], message[
            'user_defined_message'])

        res['simulation_status'] = sim_status.value
        res['user_defined_response'] = user_defined_response

        if sim_status != SimulatorStatus.RUNNING:
            self._manager.set_message_handler_state(FinishedMessageHandlerState)
        return res


class FinishedMessageHandlerState(MessageHandlerState):
    ...


if __name__ == '__main__':
    CarlaInetManager(5555, None)
