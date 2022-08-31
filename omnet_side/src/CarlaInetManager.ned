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

package carla_inet;

simple CarlaInetManager
{
    parameters:
        @class(CarlaCommunicationManager);

        string host = default("localhost");  // server hostname
        string protocol = default("tcp");  // server hostname
        double simulationTimeStep @unit("s") = default(5ms);
        int port = default(5555);  // server port (-1: automatic)
        int seed = default(-1); // seed value to set in launch configuration, if missing (-1: current run number)
        string carlaConfiguration;
        int communicationTimeoutms = default(1000);
        //bool autoShutdown = default(true);  // Shutdown module as soon as no more vehicles are in the simulation

        @display("i=block/cogwheel");
}

