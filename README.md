pyCARLANeT
===============
## Introduction
pyCARLANeT is the carla side of the open source library CARLANeT for the co-simulation between CARLA and OMNeT++.

## Requirements

According to the [CARLA documentation](https://carla.readthedocs.io/en/latest/start_quickstart/), To use pyCARLANeT, your system must meet the following requirements:

- Python 3.8.x
- Pip version greater than 22.x

```shell
pip install --upgrade pip==22.*
```

## Installation
You can install **pyCARLANeT** directly from [pypi](https://pypi.org/project/pycarlanet/). 
```shell
pip install pycarlanet
```

## Usage
To use the library, you must have an instance of CARLA simulator already active.

First, create an instance of the **\`CarlanetManager\`** class:

```
carlanet_manager = CarlanetManager(listening_port, event_listener)
```

In the code above, **\`listening_port\`** is the port number used by ZeroMQ for communication between the two sides of CARLANeT, which must be the same in CARLANeTpp. **\`event_listener\`** is an implementation of the class CarlaEventListener, which contains all the callback methods of the event of CARLANeT. The callbacks are the follow:

- **`omnet_init_completed(run_id, carla_configuration, user_defined) -> (SimulatorStatus, World)`**<br>
  This method is called when the initialization in the OMNeT world is completed. Here, you can insert the initialization code for the CARLA world. This method receives:
  - **\`run_id\`:** the identifier of the current run in the OMNeT++ simulation. This is used to map the results of the two simulators. 
  - **\`carla_configuration\`:**  a dictionary that contains the basic parameters to create the CARLA world:
    - **\`seed\`:** the seed for the random number generator used in OMNeT++.
    - **\`sim_time_limit\`:** the maximum simulation time for the CARLA world.
    - **\`carla_timestep\`:** the time step to use in the CARLA simulation.
  - **\`user_defined\`:** custom parameters defined by the specific application.

    
  This method returns a **SimulatorStatus** and the **World** of the CARLA simulator that was just created.

- **`actor_created(actor_id: str, actor_type: str, actor_config) -> CarlanetActor`**<br>
  This method is called for each actor created in the OMNeT++ simulation during the initialization phase. Here, you have to create the actor defined in OMNeT++ configuration. This method receives:
  - **\`actor_id\`:** the identifier of the actor. 
  - **\`actor_type\`:**  the type of the actor.
  - **\`actor_config\`:** custom parameters for the actor defined by the specific application.
  This method returns an object of CarlanetActor, which is a wrapper of the CarlaActor object contained in the carlalib library. The CarlanetActor object adds the property of activeness of the actor, which is used to control the actor location by CARLANeTpp in OMNeT++.

- **`carla_init_completed()`**<br>
  This method is called when the initialization of the CARLA World is finished.

- **`before_world_tick(timestamp)`**<br>
  This method is called before the world tick of CARLA. This method receives:
    - **\`timestamp\`:** the current timestamp of the CARLA world before the tick, which is approximately the same as the timestamp of OMNeT++. 

- **`carla_simulation_step(timestamp) -> SimulatorStatus`**<br>
  This method is called after the world tick of CARLA. This method receives:
  - **\`timestamp\`:** the current timestamp of the CARLA world after the tick.
  This method return the current SimulatorStatus.
  
- **`generic_message(timestamp, user_defined_message) -> (SimulatorStatus, dict)`**<br>
  This method is called when a generic message is received. This method receives:
  - **\`timestamp\`:** the current timestamp of the CARLA world.
  - **\`user_defined_message\`:** custom parameters for the message defined by the specific application.
  This method returns a tuple containing the current SimulatorStatus and a dictionary of user-defined data, that representes the answer to send to CARLANeTpp.

- **`simulation_finished(status_code: SimulatorStatus)`**<br>
  this method is called when the simulation is finished.
  
- **`simulation_error(exception)`**<br>
  This method is called when an error is encountered.

CARLANeT allows for dynamic addition and removal of actors:
```
carlanet_manager.add_dynamic_actor(actor_id: str, carlanet_actor: CarlanetActor)
carlanet_manager.remove_actor(actor_id: str)
```
Please note that these operations are related to the CARLA world and must be initiated from pyCARLANeT, as it is responsible for handling the actors. pyCARLANeT only notifies CARLANeTpp of any additions or removals, and CARLANeTpp takes appropriate action. Therefore, when adding or removing an actor from the CARLA world, you must first apply these operations using your own code in the CARLA world and then call the corresponding method in CarlanetManager. This method will notify the OMNeT++ world accordingly.


## Sample

The sample code provided in this repository demonstrates a simple application with a car and an application agent that controls the car's lights remotely. The communication network used in this sample can be found in the corresponding sample code in CARLANeTpp.

To access the sample code, please see [sample_car_light.py](https://github.com/carlanet/pycarlanet/blob/main/sample/sample_car_light.py).
