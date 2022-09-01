#include "CarlaInetManager.h"

#include <stdexcept>

#include "inet/applications/base/ApplicationPacket_m.h"
#include "inet/common/ModuleAccess.h"
#include "inet/common/TagBase_m.h"
#include "inet/common/TimeTag_m.h"
#include "inet/common/lifecycle/ModuleOperations.h"
#include "inet/common/packet/Packet.h"
#include "inet/networklayer/common/FragmentationTag_m.h"
#include "inet/networklayer/common/L3AddressResolver.h"
#include "inet/transportlayer/contract/udp/UdpControlInfo_m.h"


using namespace inet;
using namespace std;

Define_Module(CarlaInetManager);

CarlaInetManager::CarlaInetManager(){

}
CarlaInetManager::~CarlaInetManager(){
    cancelAndDelete(simulationTimeStepEvent);
}


void CarlaInetManager::finish(){

}


void CarlaInetManager::sendToCarla(json jsonMsg){
    std::stringstream msg;
    //    msg << jsonMsg.dump();
    socket.send(zmq::buffer(jsonMsg.dump()), zmq::send_flags::none);
}

template <typename T> void CarlaInetManager::receiveFromCarla(T *v, double timeoutFactor){
    // set actual timeout
    int recv_timeout_ms =  max(4000, int(timeout_ms * timeoutFactor));
    this->socket.setsockopt(ZMQ_RCVTIMEO, recv_timeout_ms);

    zmq::message_t reply{};

    //assert(!socket.recv(reply, zmq::recv_flags::none));
    if (!socket.recv(reply, zmq::recv_flags::none)){
        throw runtime_error("CALRA Timeout");
        //EV_ERROR << "receive error"<<endl;
    }
    json j = json::parse(reply.to_string());

    switch (j["simulation_status"].get<int>()){
    case SIM_STATUS_FINISHED_OK:
    case SIM_STATUS_FINISHED_ACCIDENT:
    case SIM_STATUS_FINISHED_TIME_LIMIT:
        endSimulation();
        break;
    case SIM_STATUS_ERROR:
        throw runtime_error("Communication error. Wrong message sequence!");
        break;
    default:
        *v = j.get<T>();

    }
    //return j.get<T>();
}


void CarlaInetManager::initialize(int stage)
{
    cSimpleModule::initialize(stage);
    if (stage == INITSTAGE_LOCAL){
        protocol = par("protocol").stdstringValue();
        host = par("host").stdstringValue();
        port = par("port");
        timeout_ms = par("communicationTimeoutms");
        simulationTimeStep = par("simulationTimeStep");
        //findModulesToTrack();
        connect();
    }

    if (stage == INITSTAGE_SINGLE_MOBILITY){
        initializeCarla();
    }
}


void CarlaInetManager::registerMobilityModule(CarlaInetMobility *mod){
    const char* mobileNodeName = mod->getParentModule()->getFullName();
    modulesToTrack.insert(pair<string,CarlaInetMobility*>(string(mobileNodeName), mod));
}


//void CarlaCommunicationManager::findModulesToTrack(){
//    auto rootModule = getModuleByPath("<root>");
//    auto mobilityModList = getSubmodulesOfType<CarlaInetMobility>(rootModule, true);
//    for (auto mobilityMod : mobilityModList) {
//        string nodeModuleName = mobilityMod->getParentModule()->getFullName();
//        modulesToTrack.insert(pair<string, CarlaInetMobility*>(nodeModuleName, mobilityMod));
//    }
//}


void CarlaInetManager::initializeCarla(){
    // conversion
    auto movingActorList = list<carla_api_base::init_actor>();
    for(auto elem: modulesToTrack){
        carla_api_base::init_actor actor;
        actor.actor_id = elem.first;
        actor.actor_type = elem.second->getCarlaActorType();
        actor.actor_configuration = elem.second->getCarlaActorConfiguration()->getFields();
        movingActorList.push_back(actor);
    }

    auto simTimeLimit = getEnvir()->getConfigEx()->getConfigValue("sim-time-limit");


    // compose the message
    carla_api::init msg;
    msg.run_id = getEnvir()->getConfigEx()->getVariable(CFGVAR_RUNID);

    msg.carla_configuration.seed = stoi(getEnvir()->getConfigEx()->getVariable(CFGVAR_SEEDSET));
    msg.carla_configuration.carla_timestep = simulationTimeStep;
    msg.carla_configuration.sim_time_limit = simTimeLimit != nullptr ? stod(simTimeLimit) : -1.0 ;
    msg.moving_actors = movingActorList;
    msg.user_defined = check_and_cast<cValueMap*>(par("extraInitParams").objectValue())->getFields();
    msg.timestamp = simTime().dbl();

    json jsonMsg = msg;

    EV << jsonMsg.dump() << endl;
    sendToCarla(jsonMsg);
    // I expect to receive INIT_COMPLETE message
    carla_api::init_completed response;
    receiveFromCarla<carla_api::init_completed>(&response, 100.0);
    // Carla informs about the intial timestamp, so I schedule the first similation step at that timestamp
    EV << "Initialization completed" << response.initial_timestamp <<  endl;
    updateNodesPosition(response.actors_positions);
    //
    initial_timestamp = simTime() + response.initial_timestamp;
    // schedule
    scheduleAt(simTime() + response.initial_timestamp, simulationTimeStepEvent);
}

void CarlaInetManager::doSimulationTimeStep(){
    carla_api::simulation_step msg;
    msg.carla_timestep = simulationTimeStep;
    msg.timestamp = simTime().dbl();
    json jsonMsg = msg;
    sendToCarla(jsonMsg);
    // I expect updated_postion message
    carla_api::updated_postion response;
    receiveFromCarla<carla_api::updated_postion>(& response);

    //Update position of all nodes in response

    updateNodesPosition(response.actors_postions);
}

void CarlaInetManager::updateNodesPosition(std::list<carla_api_base::actor_position> actors){
    for(auto actor : actors){
        EV << "Position" << actor.position <<endl;
        Coord position = Coord(actor.position[0], actor.position[1], actor.position[2]);
        Coord velocity = Coord(actor.velocity[0],actor.velocity[1],actor.velocity[2]);
        Quaternion rotation = Quaternion(EulerAngles(rad(actor.rotation[0]),rad(actor.rotation[1]),rad(actor.rotation[2])));
        modulesToTrack[actor.actor_id]->nextPosition(position, velocity, rotation);
    }
}



void CarlaInetManager::connect(){
    this->context = zmq::context_t {1};
    this->socket = zmq::socket_t{context, zmq::socket_type::req};

    this->socket.setsockopt(ZMQ_RCVTIMEO, timeout_ms); // set timeout to value of timeout_ms
    this->socket.setsockopt(ZMQ_SNDTIMEO, timeout_ms); // set timeout to value of timeout_ms
    EV_INFO << "CarlaCommunicationManagerLog " << "Finish initialize" << endl;
    string addr = protocol + "://" + host + ":" + std::to_string(port);
    EV << "Trying connecting to: " << addr << endl;
    socket.connect(addr);
}

void CarlaInetManager::handleMessage(cMessage *msg)
{
    if (msg->isSelfMessage()){
        if (msg == simulationTimeStepEvent){
            doSimulationTimeStep();
            EV_INFO << "Simulation step: " << this->simulationTimeStep << endl;
            scheduleAt(simTime() + this->simulationTimeStep, msg);
        }
    }
}


///*
// * PUBLIC APIs
// * */
//
//string CarlaCommunicationManager::getActorStatus(string actorId){
//    EV_INFO << "Contact Carla for getting the status id" << endl;
//    carla_api::vehicle_status_update msg;
//    msg.payload.actor_id = actorId;
//    msg.timestamp = simTime().dbl();
//    json jsonMsg = msg;
//    sendToCarla(jsonMsg);
//    // I expect VEHICLE_STATUS
//    carla_api::vehicle_status response;
//    receiveFromCarla<carla_api::vehicle_status>(& response);
//
//    return response.payload.status_id;
//}
//
//string CarlaCommunicationManager::computeInstruction(string actorId, string statusId, string agentId){
//    EV_INFO << "Contact Carla for getting the instruction id" << endl;
//    carla_api::compute_instruction msg;
//    msg.payload.actor_id = actorId;
//    msg.payload.agent_id = agentId;
//    msg.payload.status_id = statusId;
//    msg.timestamp = simTime().dbl();
//
//    json jsonMsg = msg;
//    sendToCarla(jsonMsg);
//    // I expect INSTRUCTION
//    carla_api::instruction response;
//    //10x is for safety, because CARLA before stops the simulation and then sends the response
//    receiveFromCarla<carla_api::instruction>(&response, 10);
//
//    return response.payload.instruction_id;
//}
//
//void CarlaCommunicationManager::applyInstruction(string actorId, string instructionId){
//    EV_INFO << "Contact Carla for applying the instruction id" << endl;
//    carla_api::apply_instruction msg;
//    msg.payload.actor_id = actorId;
//    msg.payload.instruction_id = instructionId;
//    msg.timestamp = simTime().dbl();
//
//    json jsonMsg = msg;
//    sendToCarla(jsonMsg);
//    // I expect OK
//    carla_api::ok response;
//    receiveFromCarla<carla_api::ok>(&response);
//
//
//}


