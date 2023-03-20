import abc
import json
import os
import carla
import zmq
from carla.libcarla import World

from pycarlanet import CarlanetEventListener, SimulatorStatus
from pycarlanet import CarlanetActor
from pycarlanet.utils import preconditions


class UnknownMessageCarlanetError(RuntimeError):
    def __init__(self, unknown_msg):
        self.unknown_msg = unknown_msg

    def __repr__(self) -> str:
        return "I don't know how to handle the following msg: " + self.unknown_msg['message_type']


# .get_snapshot().timestamp.elapsed_seconds
class CarlanetManager:
    def __init__(self, listening_port, omnet_world_listener: CarlanetEventListener, save_config_path=None,
                 socket_options=None):
        self._listening_port = listening_port
        self._omnet_world_listener = omnet_world_listener
        self._message_handler: MessageHandlerState = None
        self._carlanet_actors = dict()
        self._save_config_path = save_config_path
        self.socket_options = socket_options if socket_options else {}
        self.carla_world: World = None

    def _start_server(self):
        context = zmq.Context()
        for opt_name, opt_value in self.socket_options.items():
            context.setsockopt(opt_name, opt_value)
        self.socket = context.socket(zmq.REP)
        self.socket.setsockopt(zmq.CONFLATE, 1)
        self.socket.setsockopt(zmq.LINGER, 100)
        self.socket.bind(f"tcp://*:{self._listening_port}")
        print("server running")

    def _receive_data_from_omnet(self):
        message = self.socket.recv()
        json_data = json.loads(message.decode("utf-8"))
        self.timestamp = json_data['timestamp']
        return json_data

    def start_simulation(self):
        self._start_server()
        self.set_message_handler_state(InitMessageHandlerState)
        try:
            while not isinstance(self._message_handler, FinishedMessageHandlerState):
                msg = self._receive_data_from_omnet()
                answer = self._message_handler.handle_message(msg)
                self._send_data_to_omnet(answer)
            self._omnet_world_listener.simulation_finished(self._message_handler.simulator_status_code)
        except Exception as e:
            self._omnet_world_listener.simulation_error(e)
        finally:
            self.socket.close()

    def _send_data_to_omnet(self, answer):
        self.socket.send(json.dumps(answer).encode('utf-8'))

    def set_message_handler_state(self, msg_handler_cls, *args):
        self._message_handler = msg_handler_cls(self, *args)

    def add_dynamic_actor(self, actor_id: str, carlanet_actor: CarlanetActor):
        """
        Used to create dynamically a new actor, both active and passive, and send its position to OMNeT
        :param actor_id:
        :param carlanet_actor:
        :return:
        """
        self._carlanet_actors[actor_id] = carlanet_actor

    def remove_actor(self, actor_id: str):
        """
        Remove actor from OMNeT world
        :param actor_id:
        :return:
        """
        del self._carlanet_actors[actor_id]

    def get_curr_sim_timestamp(self):
        return self.carla_world.get_snapshot().timestamp.elapsed_seconds


class MessageHandlerState(abc.ABC):
    def __init__(self, carlanet_manager: CarlanetManager):
        self._manager = carlanet_manager
        self.omnet_world_listener: CarlanetEventListener = self._manager._omnet_world_listener
        self._carlanet_actors = self._manager._carlanet_actors

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
        for actor_id, actor in self._carlanet_actors.items():
            transform: carla.Transform = actor.get_transform()
            velocity: carla.Vector3D = actor.get_velocity()
            position = dict()
            position['actor_id'] = actor_id
            position['position'] = [transform.location.x, transform.location.y, transform.location.z]
            position['rotation'] = [transform.rotation.pitch, transform.rotation.yaw, transform.rotation.roll]
            position['velocity'] = [velocity.x, velocity.y, velocity.z]
            position['is_net_active'] = actor.alive
            nodes_positions.append(position)
        return nodes_positions


class InitMessageHandlerState(MessageHandlerState):

    def __init__(self, carlanet_manager: CarlanetManager):
        super().__init__(carlanet_manager)
        self._save_config_path = self._manager._save_config_path

    def _save_config(self, message):
        if self._save_config_path:
            if not os.path.exists(self._save_config_path):
                os.makedirs(self._save_config_path)
            with open(os.path.join(self._save_config_path, 'init.json'), 'w') as f:
                json.dump(message, f)

    def INIT(self, message):

        self._save_config(message)
        res = dict()
        res['message_type'] = 'INIT_COMPLETED'

        sim_status, carla_world = self.omnet_world_listener.omnet_init_completed(
            run_id=message['run_id'],
            carla_configuration=message['carla_configuration'],
            user_defined=message['user_defined'])

        self._manager.carla_world = carla_world

        for static_carlanet_actor in message['moving_actors']:
            actor_id = static_carlanet_actor['actor_id']
            self._carlanet_actors[actor_id] = self.omnet_world_listener.actor_created(
                actor_id,
                static_carlanet_actor['actor_type'],
                static_carlanet_actor['actor_configuration']
            )

        res['initial_timestamp'] = self._manager.get_curr_sim_timestamp()
        res['simulation_status'] = sim_status.value
        res['actor_positions'] = self._generate_carla_nodes_positions()

        self.omnet_world_listener.carla_init_completed()

        if sim_status == SimulatorStatus.RUNNING:
            self._manager.set_message_handler_state(RunningMessageHandlerState)

        return res


class RunningMessageHandlerState(MessageHandlerState):
    def SIMULATION_STEP(self, message):
        res = dict()
        self.omnet_world_listener.before_world_tick(message['timestamp'])
        self._manager.carla_world.tick()
        res['message_type'] = 'UPDATED_POSITIONS'
        sim_status = self.omnet_world_listener.carla_simulation_step(message['timestamp'])
        res['simulation_status'] = sim_status.value
        res['actor_positions'] = self._generate_carla_nodes_positions()
        if sim_status != SimulatorStatus.RUNNING:
            self._manager.set_message_handler_state(FinishedMessageHandlerState, sim_status)
        return res

    def GENERIC_MESSAGE(self, message):
        res = dict()
        res['message_type'] = 'GENERIC_RESPONSE'
        sim_status, user_defined_response = self.omnet_world_listener.generic_message(message['timestamp'], message[
            'user_defined'])

        res['simulation_status'] = sim_status.value
        res['user_defined'] = user_defined_response

        if sim_status != SimulatorStatus.RUNNING:
            self._manager.set_message_handler_state(FinishedMessageHandlerState, sim_status)
        return res


class FinishedMessageHandlerState(MessageHandlerState):
    def __init__(self, carlanet_manager: CarlanetManager, simulator_status_code: SimulatorStatus):
        super().__init__(carlanet_manager)
        self.simulator_status_code = simulator_status_code
