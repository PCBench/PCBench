# The env in this script has 3 candudate actions: 0 degree, and 45 and -45 degree while expending paths
# so it doesn't allow 90-degree bend and also the agent connect one net in one episode.
from __future__ import division

from copy import copy
from copy import deepcopy
from scipy.spatial import distance

import numpy as np
import gym
from gym import spaces
import os, random

from astar import Astar

####    Environment for MCTS    ####

class MCTS_CREnv():
    def __init__(self, board_path="./board.csv"):

        self.directions = [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]
        self.board_path = board_path
        self.state_shape = (6,)
        self.n_actions = 3

        self.board = np.genfromtxt(self.board_path, delimiter=',')
        
        # parse the board and get the starts and ends
        self.start = {}
        self.finish = {}
        for i in range(self.board.shape[0]):
            for j in range(self.board.shape[1]):
                if self.board[i,j]>=2:
                    if self.board[i,j] in self.start.keys():
                        self.finish[self.board[i,j]] = (i,j)
                    else:
                        self.start[self.board[i,j]] = (i,j)

        if len(self.start)!=len(self.finish):
            print("Number of pads in nets is not correct!!!!")

        self.original_board = copy(self.board)

        self.paths45 = dict()
        # compute and store the shortest for each single net
        self.short_net_path = dict()
        for net_id in self.start.keys():
            path_t = self.find_shortest_path(net_id)
            self.short_net_path[net_id] = path_t

    def reset(self, board=None, pin_idx=2):

        if board is None:
            self.board = np.genfromtxt(self.board_path, delimiter=',')
        else:
            self.board = board

        self.head_value = 30
        self.path_length = 0
        self.connection = False
        self.collide = False

        # initialize the action node
        self.pairs_idx = pin_idx
        self.max_pair = self.pairs_idx

        self.head = self.start[self.pairs_idx]

        self.pre_head = self.head

        self.board[self.head] = self.head_value

        self.total_reward = 0


    def takeAction(self, action, is_tuple=False):

        newState = deepcopy(self)

        if is_tuple:
            action_tmp = action
        else:
            action_tmp = newState.get_directions_from_action(action)

        newState.connection = False
        newState.collide = False
        newState.pre_head = newState.head

        newState.path_length += 1

        # pre-determine new action node
        newState.head = (newState.head[0]+action_tmp[0], newState.head[1]+action_tmp[1])
        # check/adjust new action node and set its value
        x = newState.head[0]
        y = newState.head[1]

        mid_node = (np.array(newState.head)+np.array(newState.pre_head))/2
        mid_node = tuple(mid_node)

        if 0 <= x < newState.board.shape[0] and 0 <= y < newState.board.shape[1]:
            if newState.paths45.get(mid_node):
                newState.collide = True
                newState.goto_new_net(False)
            else:
                if newState.head == newState.finish[newState.pairs_idx]:
                    newState.goto_new_net(True)
                    newState.paths45[mid_node] = True
                elif newState.board[newState.head]!=0:
                    newState.collide = True
                    newState.goto_new_net(False)
                else:
                    newState.board[newState.pre_head] = 1
                    newState.board[newState.head] = newState.head_value
                    newState.paths45[mid_node] = True
        else:
            newState.collide = True
            newState.goto_new_net(False, out_range=True)

        newState.total_reward += newState.step_reward()

        return newState

    def goto_new_net(self, connection_sign, out_range=False):

        self.board[self.pre_head] = 1
        self.connection = connection_sign
        self.pairs_idx += 1
        if not out_range:
            self.board[self.head] = 1
        if self.pairs_idx<=self.max_pair:
            self.head = self.start[self.pairs_idx]
            self.board[self.head] = self.head_value
            self.pre_head = self.head

    def get_directions_from_action(self, act_idx):

        path_d = np.array(self.head)-np.array(self.pre_head)

        d_idx = (self.directions.index(tuple(path_d))+act_idx-1)%len(self.directions)

        return self.directions[d_idx]

    def isTerminal(self):

        if self.pairs_idx>self.max_pair:
            return True

        return False

    def getReward(self):

        return self.total_reward

    def step_reward(self):

        # compute reward from other nets
        if self.connection or self.collide:
            r_1 = 0
            if self.collide:
                r_1 = -5*distance.cityblock(self.pre_head, self.finish[self.pairs_idx-1])
            # blocking other nets
            r_2 = self.reward_other_nets()
            # print("reward_other_nets is {} {}".format(r_2, self.total_reward))
            return r_2+r_1/10

        if distance.cityblock(self.pre_head, self.head)==2:
            return -0.14
        return -0.1

    def check_direction(self, direction):

        x = self.head[0] + direction[0]
        y = self.head[1] + direction[1]
        mid_node = np.array(self.head)+np.array(direction)/2
        mid_node = tuple(mid_node)
        if 0 <= x < self.board.shape[0] and 0 <= y < self.board.shape[1]:
            if not self.paths45.get(mid_node):
                if (x,y) == self.finish[self.pairs_idx]:
                    return 2
                elif self.board[(x,y)] == 0:
                    return 1
        return 0

    def compute_mask(self):

        if self.head in self.start.values():
            return np.ones(self.n_actions)

        mask = np.zeros(self.n_actions)
        for act_i in range(self.n_actions):
            act_d = self.get_directions_from_action(act_i)
            check_sign = self.check_direction(act_d)
            if check_sign==2:
                mask[act_i] = 1
                return mask
            elif check_sign==1:
                mask[act_i] = 1     

        return mask

    def getPossibleActions(self):

        possible_actions = []
        if self.head in self.start.values():
            for act_d in self.directions:
                check_sign = self.check_direction(act_d)
                if check_sign != 0:
                    possible_actions.append(act_d)
            return possible_actions
        
        for act_i in range(self.n_actions):
            act_d = self.get_directions_from_action(act_i)
            check_sign = self.check_direction(act_d)
            if check_sign==2:
                return [act_d]
            elif check_sign==1:
                possible_actions.append(act_d)
        return possible_actions

    def board_embedding(self):

        if self.pairs_idx<=self.max_pair:
            dist_to_target = [i-j for i, j in zip(self.head, self.finish[self.pairs_idx])]
        else:
            dist_to_target = [i-j for i, j in zip(self.head, self.finish[self.pairs_idx-1])]
        # state = np.array(list(self.action_node)+list(self.finish[self.pairs_idx]))
        state = np.array(list(self.head)+dist_to_target+list(self.pre_head))
        # state = np.concatenate(( state, np.array(nets_vector.tolist()+obs_vector.tolist()) ), axis=0)

        return state

    def reward_other_nets(self):

        path_diff = 0
        pin_max = int(max(self.start.keys()))
        for i in range(self.pairs_idx, pin_max+1):
            path_t = self.find_shortest_path(i)
            if path_t is None:
                return -20
            # if len(path_t)<len(self.short_net_path[i]):
            #     print(i, path_t, self.short_net_path[i])
            path_diff += (len(path_t)-len(self.short_net_path[i]))
        return -path_diff/10

    def find_shortest_path(self, net_id):

        s_node = self.start[net_id]
        t_node = self.finish[net_id]
        maze = copy(self.board)
        maze[maze>1] = 1
        maze[s_node] = 0
        maze[t_node] = 0
        astar = Astar(maze)
        path = astar.run(s_node, t_node)
        return path
