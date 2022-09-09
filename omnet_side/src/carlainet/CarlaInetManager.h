#ifndef __CARLACOMMUNICATIONMANAGER_H_
#define __CARLACOMMUNICATIONMANAGER_H_

#include <string>
#include <list>
#include <zmq.hpp>
#include <iostream>
#include <chrono>
#include <thread>

#include <map>
#include <memory>
#include <list>
#include <queue>
#include <fstream>
#include <nlohmann/json.hpp>

#include "omnetpp.h"
#include "inet/common/INETDefs.h"
#include "carlaApi.h"
#include "CarlaInetMobility.h"

using namespace std;
using namespace omnetpp;
using namespace inet;



class CarlaInetManager: public cSimpleModule {//, public cISimulationLifecycleListener {
public:
    CarlaInetManager();
    ~CarlaInetManager();

    bool isConnected() const
    {
        return true; //static_cast<bool>(connection);
    }

    simtime_t getCarlaInitialCarlaTimestamp() { return initial_timestamp; }


    void registerMobilityModule(CarlaInetMobility *mod);

    //API used by applications
    //    string getActorStatus(string actorId);
    //    string computeInstruction(string actorId, string statusId, string agentId);
    //    void applyInstruction(string actorId, string instructionId);


protected:
    virtual int numInitStages() const override { return inet::NUM_INIT_STAGES; }
    virtual void initialize(int stage) override;
    virtual void handleMessage(cMessage *msg) override;
    virtual void finish() override;

    //virtual json addExtraInitParameters() {}

private:
    void connect();
    void doSimulationTimeStep();
    void initializeCarla();
    void findModulesToTrack();
    void updateNodesPosition(std::list<carla_api_base::actor_position> actor);

    void sendToCarla(json msg);
    template<typename T> void receiveFromCarla(T *v,  double timeoutFactor = 1);


    bool connection;
    string protocol;
    string host;
    double simulationTimeStep;
    simtime_t initial_timestamp = 0;
    int seed;
    int port;
    zmq::context_t context;
    zmq::socket_t socket;
    int timeout_ms;
    cMessage *simulationTimeStepEvent =  new cMessage("simulationTimeStep");
    map<string,CarlaInetMobility*> modulesToTrack = map<string,CarlaInetMobility*>();


    //Handlers for dynamic actor creation/destroying
    void createAndInitializeActor(carla_api_base::actor_position newActor);
    void destroyActor(string actorId);
    const char* networkActiveModuleType;
//    const char* networkActiveModuleName;
    const char* networkPassiveModuleType;
//    const char* networkPassiveModuleName;
};

#endif
