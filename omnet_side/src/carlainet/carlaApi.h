#include "../lib/json.hpp"

using json = nlohmann::json;

#define SIM_STATUS_RUNNING 0
#define SIM_STATUS_FINISHED_OK 1
#define SIM_STATUS_FINISHED_ACCIDENT 2
#define SIM_STATUS_FINISHED_TIME_LIMIT 3
#define SIM_STATUS_ERROR -1



namespace carla_api_base{

    struct init_actor {
        std::string actor_id;
        std::string actor_type;
        json actor_configuration;
        //json agent_configuration;
        //std::string route;
        //std::list<init_agent> agents;
    };
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(init_actor, actor_id, actor_type, actor_configuration)


    struct actor_position {
        std::string actor_id;
        double position[3];  // x,y,z
        double velocity[3];  // x,y,z
        double rotation[3];  // pitch,yaw,roll
        bool is_net_active;
    };
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(actor_position, actor_id, position, velocity, rotation, is_net_active)

//    "carla_configuration": {
//            "seed": 11120,
//            "carla_timestep": 0.01
//        },

    struct carla_configuration {
        int seed;
        double carla_timestep;
        double sim_time_limit;
    };

    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(carla_configuration, seed, carla_timestep, sim_time_limit)


}


namespace carla_api{
    /* MESSAGE DEFINITION*/
    /* OMNET --> CARLA*/
    struct init{
        std::string message_type = "INIT";
        double timestamp;
        std::string run_id;

        std::list<carla_api_base::init_actor> moving_actors;
        carla_api_base::carla_configuration carla_configuration;

        json user_defined;

    };
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(init, message_type, timestamp, run_id, moving_actors,carla_configuration, user_defined)

    /* CARLA --> OMNET */
    struct init_completed {
        std::string message_type = "INIT_COMPLETED";
        double initial_timestamp;
        std::list<carla_api_base::actor_position> actors_positions;
        //carla_api_payload::init_completed payload;
        int simulation_status;
    };
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(init_completed, message_type, initial_timestamp, actors_positions, simulation_status)


    /* OMNET --> CARLA*/
    struct simulation_step {
        std::string message_type = "SIMULATION_STEP";
        double carla_timestep;
        double timestamp;
    };
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(simulation_step, message_type, carla_timestep, timestamp)


    /* CARLA --> OMNET */
    struct updated_postion {
        std::string message_type = "UPDATED_POSITIONS";
        std::list<carla_api_base::actor_position> actors_postions;
        int simulation_status;
    };
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(updated_postion, message_type, actors_postions, simulation_status)


    struct generic_message {
        std::string message_type = "GENERIC_MESSAGE";
        double timestamp;
        json user_defined;
    };
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(generic_message, message_type, timestamp, user_defined)


    struct generic_response {
        std::string message_type = "GENERIC_RESPONSE";
        json user_defined;
        int simulation_status;
    };
    NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(generic_response, message_type, user_defined ,simulation_status)

}
