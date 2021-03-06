########################################
# MARUADER TRAINS TO DEFEAT 11 ZERGLINGS
########################################

from absl import app
from absl import flags
from collections import namedtuple
import datetime
import time
import sys
import numpy as np
import pandas as pd
import csv
import json

import numpy as np
import pysc2
from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
from pysc2 import maps
import sys

class FourTowerSequentialMultiUnit():
    """
    This environement can be used to teach an agent to learn how to choose to fight zerglings over banelings.
    The agent has two actions that it can take in the environment and the enviornment's state is a feature
    map of the different agent IDs which have been scaled from 0-1 to act as input to a convolutional neural
    network.
    """
    def __init__(self):
        self.register_map('/maps/','FourTowerSequentialDecomposedFourUnitsRandomComp')
        self.sc2_env = sc2_env.SC2Env(
          map_name="FourTowerSequentialDecomposedFourUnitsRandomComp",
          players=[sc2_env.Agent(sc2_env.Race.terran)],
          agent_interface_format=features.AgentInterfaceFormat(
              feature_dimensions=features.Dimensions(screen=40, minimap=30),
              # rgb_dimensions=features.Dimensions(screen=640, minimap=640),
              action_space=actions.ActionSpace.FEATURES,
              ),
          step_mul=16,
          game_steps_per_episode=0,
          score_index=0,
          visualize=True)
        self.current_obs = None
        self.actions_taken = 0
        self.last_mineral_count = 0
        self.reward = 0
        self.zergling_count = 0
        self.roach_count = 0
        self.last_reward = 0
        self.last2_reward = 0
        self.rewards = []
        self.decomposed_rewards = [0,0]
        self.last_losses = 0

    def action_space():
        return Discrete(2)

    def observation_space():
        return (84, 84, 1)

    def print_current_alerts(self):
        return self.current_obs[3]

    def store_last_reward(self, reward):
        self.last_reward = reward

    def reset(self):
        # Move the camera in any direction
        # This runs the ResetEpisode trigger built into the map
        self.decomposed_rewards = []
        self.rewards = []
        self.last_timestep = self.sc2_env.reset()
        action = actions.FUNCTIONS.move_camera([0, 0])
        self.last_timestep = self.sc2_env.step([action])[0]
        observation, state, reward, done, info = self.unpack_timestep(self.last_timestep)
        self.current_obs = observation
        state = self.int_map_to_onehot(state)
        state = np.array(state)
 #       print(state.shape)
        self.actions_taken = 0
        from s2clientprotocol import sc2api_pb2 as sc_pb



        data = self.sc2_env._controllers[0]._client.send(observation=sc_pb.RequestObservation())
        self.sc2_env._controllers[0]._client.send(action=sc_pb.RequestAction())


        data = data.observation.raw_data.units



        damageByZealot = 0
        damageToZealot = 0
        damageByZergling = 0
        damageToZergling = 0
        damageByRoach = 0
        damageToRoach = 0
        damageByStalker = 0
        damageToStalker = 0
        damageByMarine = 0
        damageToMarine = 0
        damageByHydralisk = 0
        damageToHydralisk = 0
        wins = 0
        losses = 0
        rewards = []
        unit_types = []

        state = []

        # print("#################")
        for x in data:
            # print(x.unit_type)
            if x.unit_type < 1922 and x.unit_type != 51:
                state.append(x.unit_type)
                state.append(x.pos.x)
                state.append(x.pos.y)
            if x.unit_type == 1922:
                damageByZealot = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1923:
                damageToZealot = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1924:
                damageByZergling = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1925:
                damageToZergling = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1926:
                damageByRoach = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1927:
                damageToRoach = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1928:
                damageByStalker = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1929:
                damageToStalker = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1930:
                damageByMarine = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1931:
                damageToMarine = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1932:
                damageByHydralisk = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1933:
                damageToHydralisk = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1934:
                wins = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1935:
                # print("LOSSSSSSSESSSSSSSS")
                losses = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
        state = observation[3]['feature_screen']
        state = np.reshape(state, (1, -1))
        return state

    def noop(self):
        return actions.FUNCTIONS.no_op()

    def step(self, action):
        done = False
        dead = False

        ### ACTION TAKING ###

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

        ####################

        ### STATE PREPARATION ###

        self.last_timestep = self.sc2_env.step([action])[0]

        observation, state, reward, done_null, info = self.unpack_timestep(self.last_timestep)
        self.current_obs = observation

        state = self.int_map_to_onehot(state)
        state = np.array(state)

        #########################

        ### REWARD PREPARATION AND TERMINATION ###

        from s2clientprotocol import sc2api_pb2 as sc_pb
        data = self.sc2_env._controllers[0]._client.send(observation=sc_pb.RequestObservation())
        data = data.observation.raw_data.units

        damageByZealot = 0
        damageToZealot = 0
        damageByZergling = 0
        damageToZergling = 0
        damageByRoach = 0
        damageToRoach = 0
        damageByStalker = 0
        damageToStalker = 0
        damageByMarine = 0
        damageToMarine = 0
        damageByHydralisk = 0
        damageToHydralisk = 0
        wins = 0
        losses = 0
        rewards = []
        unit_types = []

        state = []

        # print("#################")
        for x in data:
            # print(x.unit_type)
            if x.unit_type < 1922 and x.unit_type != 51:
                state.append(x.unit_type)
                state.append(x.pos.x)
                state.append(x.pos.y)
            if x.unit_type == 1922:
                damageByZealot = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1923:
                damageToZealot = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1924:
                damageByZergling = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1925:
                damageToZergling = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1926:
                damageByRoach = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1927:
                damageToRoach = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1928:
                damageByStalker = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1929:
                damageToStalker = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1930:
                damageByMarine = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1931:
                damageToMarine = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1932:
                damageByHydralisk = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1933:
                damageToHydralisk = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1934:
                wins = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
            if x.unit_type == 1935:
                # print("LOSSSSSSSESSSSSSSS")
                losses = x.health
                rewards.append(x.health)
                unit_types.append(x.unit_type)
        # print("#################")
        # print(rewards)
        # unit_types.sort()
        # print(wins)
        # print(losses)
        # print(damageToHydralisk)
        # print(unit_types)
        # print(len(unit_types))
        # print("#################")


        # print("Damage by roach: {}".format(damageByRoach))
        # print("Damage by zergling: {}".format(damageByZergling))
        # print("Damage to roach: {}".format(damageToRoach))
        # print("Damage to zergling: {}".format(damageToZergling))

        # total_reward = roach_reward + zergling_reward - 4
        # reward = total_reward
        # self.reward = total_reward
        self.reward = wins + losses
        self.losses = losses
        # self.rewards.append(reward)

        if self.last_reward != self.reward:
            done = True
            if self.last_losses < self.losses:
                dead = True
            else:
                dead = False

        self.last_reward = self.reward
        self.last_losses = self.losses

        self.decomposed_rewards.append([damageToZealot - 2, damageToZergling - 2, damageToRoach - 2, damageToStalker - 2, damageToMarine - 2, damageToHydralisk - 2])

        # damageToZealot
        # damageToZergling
        # damageToRoach
        # damageToStalker
        # damageToMarine
        # damageToHydralisk

        ###########################################
        # print(len(state))
        if len(state) < 36:
            current_len_state = len(state)
            for x in range(current_len_state, 36):
                state.append(0.0)
        # print(len(state))
        state = observation[3]['feature_screen']
        state = np.reshape(state, (1, -1))
        #print('STATE SHAPE')
        #print(state.shape)
        return state, reward, done, dead, info

    def register_map(self, map_dir, map_name):
        from pysc2.maps import lib
        map_filename = map_name + '.SC2Map'
        class_definition = dict(prefix=map_dir, filename=map_filename, players=1)
        constructed_class = type(map_name, (lib.Map,), class_definition)
        globals()[map_name] = constructed_class

    def get_mineral_count(self, obs):
        return 0

    def get_vespene_gas_count(self, obs):
        return 0

    def unpack_timestep(self, timestep):
        observation = timestep
        state = timestep.observation.feature_screen[6]
        reward = timestep.observation.score_cumulative[0]
        done = timestep.last()
        info = {}
        return observation, state, reward, done, info

    def get_available_actions(self, obs):
        return obs.observation.available_actions

    def check_action(self, obs, action):
        return action in self.get_available_actions(obs)

    def get_health_of_unit_type(self, unit_id):
        total_health = 0
        feature_units = self.current_obs[3]['feature_units']
        for unit in feature_units:
            if unit[0] == unit_id:
                total_health += unit[2]
        return total_health

    def get_unit_count_of_type(self, unit_id):
        count = 0
        feature_units = self.current_obs[3]['feature_units']
        for unit in feature_units:
            if unit[0] == unit_id:
                count += 1
        return count

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
