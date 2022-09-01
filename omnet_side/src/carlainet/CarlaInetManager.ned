package carlainet;

simple CarlaInetManager
{
    parameters:
        @class(CarlaInetManager);

        string host = default("localhost");  // server hostname
        string protocol = default("tcp");  // server hostname
        double simulationTimeStep @unit("s") = default(10ms);
        int port = default(5555);  // server port (-1: automatic)
        int seed = default(-1); // seed value to set in launch configuration, if missing (-1: current run number)
        //string carlaConfiguration;
        int communicationTimeoutms = default(1000);
        //bool autoShutdown = default(true);  // Shutdown module as soon as no more vehicles are in the simulation
		object extraInitParams = default(parseJSON("{}"));
		
        @display("i=block/cogwheel");
}

