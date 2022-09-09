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

package carlainet.simulations;

import carlainet.CarlaInetManager;
import carlainet.CarlaInetMobility;
import inet.node.contract.INetworkNode;
import inet.node.base.NodeBase;
import inet.node.inet.WirelessHost;
import inet.visualizer.contract.IIntegratedVisualizer;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.physicallayer.wireless.common.contract.packetlevel.IRadioMedium;

network CarlaInetNetworkTest
{
    @display("bgb=250,134");
    submodules:
        carlaInetManager: CarlaInetManager {
            @display("p=122,75");
        }
        visualizer: <default(firstAvailableOrEmpty("IntegratedVisualizer"))> like IIntegratedVisualizer if typename != "" {
            @display("p=580,125");
        }
        configurator: Ipv4NetworkConfigurator {
            @display("p=580,200");
        }
        radioMedium: <default("UnitDiskRadioMedium")> like IRadioMedium {
            @display("p=580,275");
        }
        
        
        car: NodeBase {
            mobility.typename = "CarlaInetMobility";
            @display("p=55.89,39.329998");
        }
        
}
