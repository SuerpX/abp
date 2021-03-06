import numpy as np
import pysc2
from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from pysc2 import maps, lib
from s2clientprotocol import sc2api_pb2 as sc_pb

class FourTowerSequentialFriendlyUnits():
    def __init__(self):
 #       mapName = 'FoutTowersWithFridenlyUnits'
 #       mapName = 'FoutTowersWithFridenlyUnitsFixedEnemies'
        mapName = 'FoutTowersWithFridenlyUnitsFixedEnemiesFixedPosition'
        self.register_map('/maps/',mapName)
        self.sc2_env = sc2_env.SC2Env(
          map_name = mapName,
          players = [sc2_env.Agent(sc2_env.Race.protoss)],
          agent_interface_format = features.AgentInterfaceFormat(
              feature_dimensions = features.Dimensions(screen = 40, minimap = 30),
              action_space = actions.ActionSpace.FEATURES,
              camera_width_world_units = 28
              ),
          step_mul = 16,
          game_steps_per_episode = 0,
          score_index = 0,
          visualize = False,)
 #       lib.renderer_human.zoom(1.5)

        
        self.current_obs = None
        self.actions_taken = 0
        self.decomposed_rewards_all = []
        self.decomposed_rewards = []
        self.decomposed_rewards_mark = 0
        self.signal_of_finished = 1
        self.last_state = None

        '''
        self.enemy_type_number_dict = {
            101 : 'damageToMarine',
            102 : 'damageByMarine',
            103 : 'damageToZergling',
            104 : 'damageByZergling',
            105 : 'damageToMarauder',
            106 : 'damageByMarauder',
            107 : 'damageToHydralisk',
            108 : 'damageByHydralisk',
            109 : 'damageToThor',
            110 : 'damageByThor',
            111 : 'damageToUltralisk',
            112 : 'damageByUltralisk',
            113 : 'penalty'
            }
        '''
        self.decomposed_reward_dict = {
            'damageToMarine' : 0,
            'damageByMarine' : 0,
            'damageToZergling' : 0,
            'damageByZergling' : 0,
            'damageToMarauder' : 0,
            'damageByMarauder' : 0,
            'damageToHydralisk' : 0,
            'damageByHydralisk' : 0,
            'damageToThor' : 0,
            'damageByThor' : 0,
            'damageToUltralisk' : 0,
            'damageByUltralisk' : 0,
            'penalty' : 0
            }
        
    
    def action_space():
        return Discrete(2)

    def observation_space():
        return (84, 84, 1)

    def print_current_alerts(self):
        return self.current_obs[3]

    def reset(self):
        # Move the camera in any direction
        # This runs the ResetEpisode trigger built into the map
        self.decomposed_rewards_all = []
        self.decomposed_rewards = []
        self.decomposed_rewards_mark = 0
        action = actions.FUNCTIONS.move_camera([0, 0])
        self.last_timestep = self.sc2_env.step([action])[0]
        observation = self.unpack_timestep(self.last_timestep)
        self.current_obs = observation
        self.actions_taken = 0
        np.set_printoptions(threshold=np.nan,linewidth=np.nan)
 #       print(observation)
        state = observation[3]['feature_screen']
        player_id = np.array(state[4])
        player_id[np.array(state[6]) == 73] = 3
        state[4] = player_id.tolist()
        #print(state)
        state = np.reshape(state, (1, -1))
        self.last_state = None


        data = self.sc2_env._controllers[0]._client.send(observation = sc_pb.RequestObservation())
        self.sc2_env._controllers[0]._client.send(action = sc_pb.RequestAction())


        
        data = data.observation.raw_data.units

        rewards, sof = self.getRewards(data)

        self.signal_of_finished = sof
        
        for key in self.decomposed_reward_dict:
            self.decomposed_reward_dict[key] = 0

        return state


    def getRewards(self, data):
        
        rewards = []
 #       state = [0.0,0.0]

        for x in data:
#            print(x.shield, x.health)
 #           print(x.alliance)
            '''
            if x.unit_type != 45 and x.unit_type != 83:
                state.append(x.unit_type)
                state.append(x.pos.x)
                state.append(x.pos.y)
            
            elif x.unit_type == 83:
                state[0] += x.health
                state[1] += 1
            '''
            if x.shield == 101:
                self.decomposed_reward_dict['damageToMarine'] = x.health - 1
                rewards.append(x.health - 1)
            elif x.shield == 102:
                self.decomposed_reward_dict['damageByMarine'] = (x.health - 1) * -1
                rewards.append((x.health - 1) * -1)   
            elif x.shield == 103:
                self.decomposed_reward_dict['damageToZergling'] = x.health - 1
                rewards.append(x.health - 1)
            elif x.shield == 104:
                self.decomposed_reward_dict['damageByZergling'] = (x.health - 1) * -1
                rewards.append((x.health - 1) * -1)
            elif x.shield == 105:
                self.decomposed_reward_dict['damageToMarauder'] = x.health - 1
                rewards.append(x.health - 1)
            elif x.shield == 106:
                self.decomposed_reward_dict['damageByMarauder'] = (x.health - 1) * -1
                rewards.append((x.health - 1) * -1)
            elif x.shield == 107:
                self.decomposed_reward_dict['damageToHydralisk'] = x.health - 1
                rewards.append(x.health - 1)
            elif x.shield == 108:
                self.decomposed_reward_dict['damageByHydralisk'] = (x.health - 1) * -1
                rewards.append((x.health - 1) * -1)
            elif x.shield == 109:
                self.decomposed_reward_dict['damageToThor'] = x.health - 1
                rewards.append(x.health - 1)
            elif x.shield == 110:
                self.decomposed_reward_dict['damageByThor'] = (x.health - 1)* -1
                rewards.append((x.health - 1) * -1)
            elif x.shield == 111:
                self.decomposed_reward_dict['damageToUltralisk'] = x.health - 1
                rewards.append(x.health - 1)
            elif x.shield == 112:
                self.decomposed_reward_dict['damageByUltralisk'] = (x.health - 1)* -1
                rewards.append((x.health - 1) * -1)
            elif x.shield == 113:
                self.decomposed_reward_dict['penalty'] = (x.health - 1) * -1
                rewards.append((x.health - 1) * -1)
            elif x.shield == 114:
                sof = x.health
            
        return rewards, sof

        
    def noop(self):
        return actions.FUNCTIONS.no_op()

    def step(self, action):
        done = False
        dead = False

        ### ACTION TAKING ###
    #    print(action)
        if self.actions_taken == 0 and self.check_action(self.current_obs, 12):
            if action == 0:
                action = actions.FUNCTIONS.Attack_screen("now", [0,0])
            elif action == 1:
                action = actions.FUNCTIONS.Attack_screen("now", [39,0])
            elif action == 2:
                action = actions.FUNCTIONS.Attack_screen("now", [0,39])
            elif action == 3:
                action = actions.FUNCTIONS.Attack_screen("now", [39,39])
            elif action == 4:
                action = actions.FUNCTIONS.no_op()
            else:
                print("Invalid action: check final layer of network")
                action = actions.FUNCTIONS.no_op()
        else:
            action = actions.FUNCTIONS.no_op()
 #           print(self.actions_taken == 0, self.check_action(self.current_obs, 12))
   #     print(action)
        ####################

        ### STATE PREPARATION ###

        self.last_timestep = self.sc2_env.step([action])[0]

        observation = self.unpack_timestep(self.last_timestep)
        self.current_obs = observation
        #########################

        ### REWARD PREPARATION AND TERMINATION ###

        data = self.sc2_env._controllers[0]._client.send(observation=sc_pb.RequestObservation())
        data = data.observation.raw_data.units

        rewards, sof = self.getRewards(data)

        state = observation[3]['feature_screen']
        player_id = np.array(state[4])
        player_id[np.array(state[6]) == 73] = 3
        state[4] = player_id.tolist()
        state = np.reshape(state, (1, -1))

        #print(state.shape)
        self.decomposed_rewards_all.append([])
        for key in self.decomposed_reward_dict:
            la = len(self.decomposed_rewards_all)
            self.decomposed_rewards_all[la - 1].append(self.decomposed_reward_dict[key])
 #       print(self.signal_of_finished,sof)
        if self.signal_of_finished != sof:
            done = True
            
            if sof == 1:
                dead = True
            else:
                dead = False
            self.decomposed_rewards.append([])
            
            
            for i, key in enumerate(self.decomposed_reward_dict):
                l = len(self.decomposed_rewards)
                la = len(self.decomposed_rewards_all)
                if not dead:
                    self.decomposed_rewards[l - 1].append(
                        self.decomposed_rewards_all[la - 1][i] - self.decomposed_rewards_all[self.decomposed_rewards_mark][i]
                        )
                else:
                    self.decomposed_rewards[l - 1].append(
                        self.decomposed_rewards_all[la - 2][i] - self.decomposed_rewards_all[self.decomposed_rewards_mark][i]
                        )
            self.decomposed_rewards_mark = la - 1
            
        self.signal_of_finished = sof
        '''                                                                                       
        if len(state) < 41:
            current_len_state = len(state)
            for x in range(current_len_state, 41):
                state.append(0.0)
#        print(done,dead)
        '''
        if not dead:
            self.last_state = state
        return state, done, dead

    def register_map(self, map_dir, map_name):
        map_filename = map_name + '.SC2Map'
        class_definition = dict(prefix = map_dir, filename = map_filename, players = 1)
        constructed_class = type(map_name, (pysc2.maps.lib.Map,), class_definition)
        globals()[map_name] = constructed_class


    def unpack_timestep(self, timestep):  
        observation = timestep
 #       print(timestep.observation.feature_minimap[3])
 #       state = timestep.observation.feature_screen[6]
 #       reward = timestep.observation.score_cumulative[0]
 #       done = timestep.last()
#        info = {}
        return observation#, state, reward, done, info

    def get_available_actions(self, obs):
        return obs.observation.available_actions

    def check_action(self, obs, action):
 #       print(action, self.get_available_actions)
        return action in self.get_available_actions(obs)



    
    
    def int_map_to_onehot(self, x, vocabulary=None):
        location_zergling = np.argwhere(x == 105.)
        location_roach = np.argwhere(x == 110.)

        if location_zergling.shape[0] == 0 or location_roach.shape[0] == 0:
            onehot = [0,0,0,0,0,0,0,0]
        else:
            onehot = [location_zergling[0][0], location_zergling[0][1], location_roach[0][0], location_roach[0][1], location_roach[1][0], location_roach[1][1], location_roach[2][0], location_roach[2][1]]

        onehot = np.reshape(onehot, [1, 8])
        # print(len(x.ravel()))
        # sys.exit()
        return x.ravel()
    


#FourTowerSequentialMultiUnit()
