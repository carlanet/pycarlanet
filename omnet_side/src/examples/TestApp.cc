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

#include "TestApp.h"

using json = nlohmann::json;

Define_Module(TestApp);

void TestApp::initialize(int stage)
{
    if (stage == inet::INITSTAGE_LOCAL){
        carlaInetManager = check_and_cast<CarlaInetManager*>(getModuleByPath("<root>.carlaInetManager"));
    }

    if (stage == inet::INITSTAGE_LAST){
        json msg;
        msg["message_type"] = "hello";
        carlaInetManager->sendToAndGetFromCarla(msg);
    }
}

void TestApp::handleMessage(cMessage *msg)
{
    // TODO - Generated method body
}
