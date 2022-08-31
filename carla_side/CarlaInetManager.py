import abc

import carla

import OMNeTWorldListener
from CarlaInetActor import CarlaInetActor
from decorators import preconditions


class UnknownMessageCarlaInetError(RuntimeError):
    def __init__(self, unknown_msg):
        self.unknown_msg = unknown_msg

    def __repr__(self) -> str:
        return "I don't know how to handle the following msg: " + self.unknown_msg


class CarlaInetManager:
    def __init__(self, omnet_world_listener: OMNeTWorldListener):
        self._omnet_world_listener = omnet_world_listener
        self._message_handler = None
        self._carla_inet_actors = dict()

    def set_message_handler_state(self, msg_handler_cls):
        self._message_handler = msg_handler_cls(self)

    def subscribe_actor(self, actor_id: int, carla_inet_actor: CarlaInetActor):
        self._carla_inet_actors[actor_id] = carla_inet_actor


class MessageHandlerState(abc.ABC):
    def __init__(self, carla_inet_manager: CarlaInetManager):
        self._manager = carla_inet_manager

    def handle_message(self, message):
        msg = self._handle_message(message)
        msg['positions'] = self._generate_carla_nodes_positions

    @preconditions('_manager')
    def _generate_carla_nodes_positions(self):
        nodes_positions = []
        for actor_id, actor in self._manager._carla_inet_actors.items():
            transform: carla.Transform = actor.get_transform()
            velocity: carla.Vector3D = actor.get_velocity()
            position = dict()
            position['actor_id'] = actor_id
            position['position'] = [transform.location.x, transform.location.y, transform.location.z]
            position['rotation'] = [transform.rotation.pitch, transform.rotation.yaw, transform.rotation.roll]
            position['velocity'] = [velocity.x, velocity.y, velocity.z]
            nodes_positions.append(position)
        return nodes_positions

    def _handle_message(self, message):
        raise RuntimeError(f"""I'm in the following state: {self.__class__.__name__} and 
                            I don't know how to handle {message.__class__.__name__} message""")


class InitMessageHandlerState(MessageHandlerState):
    INIT_MESSAGE_TYPE = 'INIT'

    def _handle_message(self, message):
        if message['message_type'] == self.INIT_MESSAGE_TYPE:
            res = dict()
            res['message_type'] = 'INIT_COMPLETED'
            carla_timestamp = self._manager._omnet_world_listener.on_finished_creation_omnet_world(
                message['carla_world_configuration'])
            res['carla_timestamp'] = carla_timestamp
            return res
        else:
            return super().handle_message(message)
