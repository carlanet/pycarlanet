from pycarlanet.utils import DecoratorSingleton
from pycarlanet import SimulatorStatus
from listeners import WorldManager, ActorManager, AgentManager
import abc
import json
import os
import zmq

from utils import InstanceExist

class ImmutableMessage:
    _message: bytes
    def __init__(self, msg): self._message = json.dumps(msg).encode('utf-8')
    @property
    def message(self): return json.loads(self._message.decode("utf-8"))

@DecoratorSingleton
class SocketManager:
    
    _listening_port: int
    _worldManager: WorldManager
    _actorManager: ActorManager = BasicActorManager()
    _agentManager: AgentManager = BasicAgentManager()

    def __init__(
        self,
        listening_port,
        worldManager: WorldManager,
        actorManager: ActorManager = None,
        agentManager: AgentManager = None,
        save_config_path=None,
        socket_options=None,
        log_messages=False
    ):
        if listening_port is None or worldManager is None: raise Exception(f"Error initializing SocketManager listening_port and worldManager can't be None, listening_port={listening_port}, worldManager={worldManager}")
        self._listening_port = listening_port
        self._worldManager = worldManager

        if actorManager is not None: self._actorManager = actorManager
        if agentManager is not None: self._agentManager = agentManager

        self._message_handler: MessageHandlerState = None
        self._log_messages = log_messages
        self._save_config_path = save_config_path
        self.socket_options = socket_options if socket_options else {}
    
    def start_socket(self):
        self._start_server()
        self.set_message_handler_state(InitMessageHandlerState)
        try:
            while not isinstance(self._message_handler, FinishedMessageHandlerState):
                msg = self._receive_data_from_omnet()
                answer = self._message_handler.handle_message(msg)
                self._send_data_to_omnet(answer)
            self._worldManager.simulation_finished(self._message_handler.simulator_status_code)
        except Exception as e:
            self._worldManager.simulation_error(e)
        finally:
            self.socket.close()
    
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
        if self._log_messages: print(f'Received msg: {json_data}\n')
        return json_data

    def _send_data_to_omnet(self, answer):
        if self._log_messages: print(f'Sending msg: {answer}\n')
        self.socket.send(json.dumps(answer).encode('utf-8'))

    def set_message_handler_state(self, msg_handler_cls, *args):
        self._message_handler = msg_handler_cls(*args)
    
class MessageHandlerState(abc.ABC):
    @InstanceExist(SocketManager)
    def __init__(self):
        #self.SocketManager = carlanet_manager
        #self.omnet_world_listener: CarlanetEventListener = self._manager._omnet_world_listener
        #self._carlanet_actors = self._manager._carlanet_actors
        ...

    def handle_message(self, message):
        message_type = message['message_type']
        if hasattr(self, message_type):
            meth = getattr(self, message_type)
            print(f"handle_message {message_type}")
            return meth(message)
        raise RuntimeError(f"""I'm in the following state: {self.__class__.__name__} and I don't know how to handle {message['message_type']} message""")

    # def _generate_carla_nodes_positions(self):
    #     nodes_positions = []
    #     # for actor_id, actor in self._carlanet_actors.items():
    #     #     transform: carla.Transform = actor.get_transform()
    #     #     velocity: carla.Vector3D = actor.get_velocity()
    #     #     position = dict()
    #     #     position['actor_id'] = actor_id
    #     #     position['position'] = [transform.location.x, transform.location.y, transform.location.z]
    #     #     position['rotation'] = [transform.rotation.pitch, transform.rotation.yaw, transform.rotation.roll]
    #     #     position['velocity'] = [velocity.x, velocity.y, velocity.z]
    #     #     position['is_net_active'] = actor.alive
    #     #     nodes_positions.append(position)
    #     return nodes_positions


class InitMessageHandlerState(MessageHandlerState):
    @InstanceExist(SocketManager)
    def __init__(self):
        super().__init__()
        #self._save_config_path = SocketManager.instance._save_config_path

    @InstanceExist(SocketManager)
    def _save_config(self, message):
        if SocketManager.instance._save_config_path is None: return
        _path = SocketManager.instance._save_config_path
        if not os.path.exists(_path): os.makedirs(_path)
        with open(os.path.join(_path, 'init.json'), 'w') as f: json.dump(message, f)


    @InstanceExist(SocketManager)
    def INIT(self, message):
        immutableMessage = ImmutableMessage(message)

        self._save_config(immutableMessage.message)
        res = dict()
        res['message_type'] = 'INIT_COMPLETED'

        sim_status, carla_world = SocketManager.instance._worldManager.omnet_init_completed(message=immutableMessage.message)
        SocketManager.instance._actorManager.omnet_init_completed(message=immutableMessage.message)
        SocketManager.instance._agentManager.omnet_init_completed(message=immutableMessage.message)

        res['initial_timestamp'] = SocketManager.instance._worldManager.get_elapsed_seconds()
        res['simulation_status'] = sim_status.value
        res['actor_positions'] = SocketManager.instance._actorManager._generate_carla_nodes_positions()

        SocketManager.instance._worldManager.carla_init_completed()

        if sim_status == SimulatorStatus.RUNNING: SocketManager.instance.set_message_handler_state(RunningMessageHandlerState)

        return res


class RunningMessageHandlerState(MessageHandlerState):
    @InstanceExist(SocketManager)
    def SIMULATION_STEP(self, message):
        res = dict()
        
        SocketManager.instance._worldManager.before_world_tick(message['timestamp'])
        #TODO check if necessary _actorManager.before_world_tick, _agentManager.before_world_tick
            #SocketManager.instance._actorManager.before_world_tick(message['timestamp'])
            #SocketManager.instance._agentManager.before_world_tick(message['timestamp'])

        SocketManager.instance._worldManager.tick()

        res['message_type'] = 'UPDATED_POSITIONS'
        #sim_status = self.omnet_world_listener.carla_simulation_step(message['timestamp'])
        sim_status = SocketManager.instance._worldManager.after_world_tick(message['timestamp'])

        #TODO check if necessary _actorManager.after_world_tick, _agentManager.after_world_tick
            #SocketManager.instance._actorManager.after_world_tick(message['timestamp'])
            #SocketManager.instance._agentManager.after_world_tick(message['timestamp'])
        
        res['simulation_status'] = sim_status.value
        #res['actor_positions'] = self._generate_carla_nodes_positions()
        res['actor_positions'] = SocketManager.instance._actorManager._generate_carla_nodes_positions()
        if sim_status != SimulatorStatus.RUNNING: SocketManager.instance.set_message_handler_state(FinishedMessageHandlerState, sim_status)
        return res

    def GENERIC_MESSAGE(self, message):
        res = dict()
        print(f"generic message handle {message}")
        # res['message_type'] = 'GENERIC_RESPONSE'
        # sim_status, user_defined_response = self.omnet_world_listener.generic_message(message['timestamp'], message[
        #     'user_defined'])

        # res['simulation_status'] = sim_status.value
        # res['user_defined'] = user_defined_response

        # if sim_status != SimulatorStatus.RUNNING:
        #     self._manager.set_message_handler_state(FinishedMessageHandlerState, sim_status)
        return res


class FinishedMessageHandlerState(MessageHandlerState):
    def __init__(self, simulator_status_code: SimulatorStatus):
        super().__init__()
        self.simulator_status_code = simulator_status_code

