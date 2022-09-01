//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
// 

#ifndef CARLAINETMANAGER_H_
#define CARLAINETMANAGER_H_
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
using namespace std;
using namespace omnetpp;
using namespace inet;

class CarlaInetManager: public cSimpleModule {
public:
    CarlaInetManager();
    virtual ~CarlaInetManager();

protected:
    virtual int numInitStages() const override { return inet::NUM_INIT_STAGES; }
    virtual void initialize(int stage) override;

private:
    string protocol;
    string host;
    double simulationTimeStep;
    simtime_t initial_timestamp = 0;
    int seed;
    int port;
    zmq::context_t context;
    zmq::socket_t socket;
    int timeout_ms;
};

#endif /* CARLAINETMANAGER_H_ */
