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


#ifndef CARLAINETMOBILITY_H_
#define CARLAINETMOBILITY_H_


#include <omnetpp.h>
#include "inet/mobility/base/MobilityBase.h"

using namespace omnetpp;
using namespace std;

/**
 * TODO - Generated class
 */
class CarlaInetMobility : public inet::MobilityBase
{
public:
    /** @brief called by class CarlaCommunicationManager */
    virtual void preInitialize(const inet::Coord& position, const inet::Coord& velocity,  const inet::Quaternion& rotation);
    virtual void initialize(int stage) override;


    /** @brief called by class CarlaCommunicationManager */
    virtual void nextPosition(const inet::Coord& position, const inet::Coord& velocity,  const inet::Quaternion& rotation);


    virtual const inet::Coord& getCurrentPosition() override;
    virtual const inet::Coord& getCurrentVelocity() override;
    virtual const inet::Coord& getCurrentAcceleration() override;

    virtual const inet::Quaternion& getCurrentAngularPosition() override;
    virtual const inet::Quaternion& getCurrentAngularVelocity() override;
    virtual const inet::Quaternion& getCurrentAngularAcceleration() override;


    // access to members
    string getCarlaActorType(){return carlaActorType;}
    cValueMap* getCarlaActorConfiguration(){return carlaActorConfiguration;}

protected:
    /** This must be implemented as described in MobilityBase*/
    virtual void handleSelfMessage(cMessage *msg) override;

    virtual void setInitialPosition() override;

    /** @brief The last velocity that was set by nextPosition(). */
    inet::Coord lastVelocity;
    /** @brief The last angular velocity that was set by nextPosition(). */
    inet::Quaternion lastAngularVelocity;

private:
    string carlaActorType;
    cValueMap* carlaActorConfiguration;
    bool preInitialized = false;  // this field is set during dynamic module creation

//private:
//    CarlaCommunicationManager *manager = nullptr;
};

#endif
