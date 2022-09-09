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

#include "CarlaInetMobility.h"

#include "CarlaInetManager.h"

Define_Module(CarlaInetMobility);

void CarlaInetMobility::initialize(int stage)
{
    MobilityBase::initialize(stage);
    if (stage == inet::INITSTAGE_LOCAL){
        carlaActorType = par("carlaActorType").stdstringValue();
        carlaActorConfiguration = check_and_cast<cValueMap*>(par("carlaActorConfiguration").objectValue()); //.cValueMap(); // .objectValue();
        auto carlaManager = check_and_cast<CarlaInetManager*>(getModuleByPath("<root>.carlaInetManager"));
        // register to carlaManager
        carlaManager->registerMobilityModule(this);
    }
}

void CarlaInetMobility::setInitialPosition(){
    if (!preInitialized){
        MobilityBase::setInitialPosition();
    }
}

void CarlaInetMobility::preInitialize(const inet::Coord& position, const inet::Coord& velocity,  const inet::Quaternion& rotation){
    preInitialized = true;
    lastPosition = position;
    lastVelocity = velocity;
    lastOrientation = rotation;
}


void CarlaInetMobility::nextPosition(const inet::Coord& position, const inet::Coord& velocity,  const inet::Quaternion& rotation){
    lastPosition = position;
    lastVelocity = velocity;
    lastOrientation = rotation;

    emitMobilityStateChangedSignal();
}


const inet::Coord& CarlaInetMobility::getCurrentPosition()
{
    return lastPosition;
}

const inet::Coord& CarlaInetMobility::getCurrentVelocity()
{
    return lastVelocity;
}

const inet::Coord& CarlaInetMobility::getCurrentAcceleration()
{
    throw cRuntimeError("Invalid operation");
}

const inet::Quaternion& CarlaInetMobility::getCurrentAngularPosition()
{
    return lastOrientation;
}

const inet::Quaternion& CarlaInetMobility::getCurrentAngularVelocity()
{
    return lastAngularVelocity;
}

const inet::Quaternion& CarlaInetMobility::getCurrentAngularAcceleration()
{
    throw cRuntimeError("Invalid operation");
}


void CarlaInetMobility::handleSelfMessage(cMessage* msg){
}
