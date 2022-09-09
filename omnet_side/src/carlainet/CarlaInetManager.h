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



class CarlaInetManager: public cSimpleModule {
public:
    CarlaInetManager();
    ~CarlaInetManager();

    bool isConnected() const
    {
        return true;
    }

    simtime_t getCarlaInitialCarlaTimestamp() { return initial_timestamp; }


    void registerMobilityModule(CarlaInetMobility *mod);

    //API used by applications

    /**
     * This is a generic API that accepts and return json type
     */
    json sendToAndGetFromCarla(json requestMessage);

    /*
     * Variants of the API using templates
     * IMPORTANT the type must implement "to_json" and "from_json" as specified
     * by the "nlohmann/json" library
     */
    template<typename S> json sendToAndGetFromCarla(S requestMessage);
    template<typename T> T sendToAndGetFromCarla(json requestMessage);
    template<typename S, typename T> T sendToAndGetFromCarla(S requestMessage);


protected:
    virtual int numInitStages() const override { return inet::NUM_INIT_STAGES; }
    virtual void initialize(int stage) override;
    virtual void handleMessage(cMessage *msg) override;
    virtual void finish() override;

private:
    void connect();
    void doSimulationTimeStep();
    void initializeCarla();
    void findModulesToTrack();
    void updateNodesPosition(std::list<carla_api_base::actor_position> actor);

    void sendToCarla(json msg);

    json receiveFromCarla(double timeoutFactor = 1);
    template<typename T> T receiveFromCarla(double timeoutFactor = 1);


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
    const char* networkPassiveModuleType;
};

#endif
