import sys
sys.path.append('..')

from copy import copy
from copy import deepcopy

import numpy as np
from multiprocessing import Pool

from astar import Astar

from load_data.RLoader import PCBLoader

####    Environment for MCTS    ####

class MCTS_CREnv():
    def __init__(self, pcb_path, resolution):

        self.directions = [(-1, 0, 0), (0, 1, 0), (1, 0, 0), (0, -1, 0), (0, 0, -1), (0, 0, 1)]
        self.state_shape = (6,)
        self.n_actions = len(self.directions)

        self.resolution = resolution
        self.pcb_path = pcb_path
        pcb = PCBLoader(self.pcb_path, self.resolution)
        self.nets = deepcopy(pcb.net_pads)
        self.board = np.zeros(pcb.routing_matrix.shape) 

        self.pin_pair2net = []
        self.start, self.end = [], []
        for nidx, net in self.nets.items():
            print(net, self.board.shape)
            if nidx != -1:
                for pidx in range(len(net)-1):
                    self.board[tuple(net[pidx])] = nidx
                    self.board[tuple(net[pidx + 1])] = nidx
                    self.start.append(net[pidx])
                    self.end.append(net[pidx + 1])
                    self.pin_pair2net.append(nidx)

        if len(self.start)!=len(self.end):
            print("Number of pads in nets is not correct!!!!")
        self.original_board = copy(self.board)

        # compute and store the shortest for each single net
        self.short_net_path = dict()
        for pair_id in range(len(self.start)):
            path_t = self.find_shortest_path(pair_id)
            self.short_net_path[pair_id] = path_t

        self.path_length = 0

    def reset(self, board=None, pin_idx=2):

        if board is None:
            self.board = deepcopy(self.original_board)
        else:
            self.board = board
        
        self.connection = False
        self.collide = False

        # initialize the action node
        self.pairs_idx = pin_idx
        self.max_pair = self.pairs_idx
        # self.max_pair = max(self.start.keys())
        self.head = self.start[self.pairs_idx]

        self.total_reward = 0

    def takeAction(self, action, is_tuple=False):

        newState = deepcopy(self)

        if is_tuple:
            action_tmp = action
        else:
            action_tmp = newState.directions[action]
        newState.connection = False
        newState.collide = False
        newState.pre_head = newState.head

        newState.path_length += 1

        # pre-determine new action node
        newState.head = (newState.head[0]+action_tmp[0], newState.head[1]+action_tmp[1], newState.head[2]+action_tmp[2])
        # check/adjust new action node and set its value
        x = newState.head[0]
        y = newState.head[1]
        z = newState.head[2]

        if 0 <= x < newState.board.shape[0] and 0 <= y < newState.board.shape[1] and 0<= z < newState.board.shape[2]:
            if newState.head == newState.end[newState.pairs_idx]:
                newState.goto_new_net(True)
            elif newState.board[newState.head]!=0:
                newState.collide = True
                newState.goto_new_net(False)
            else:
                newState.board[newState.pre_head] = 1
        else:
            newState.collide = True
            newState.goto_new_net(False, out_range=True)

        newState.total_reward += newState.step_reward()

        return newState

    def goto_new_net(self, connection_sign, out_range=False):
        # print(f"here? {connection_sign} {self.head} {self.start[self.pairs_idx]} {self.end[self.pairs_idx]}")
        self.board[self.pre_head] = 1
        self.connection = connection_sign
        self.pairs_idx += 1
        if not out_range:
            self.board[self.head] = 1
            self.pre_head = self.head
        if self.pairs_idx<=self.max_pair:
            self.head = self.start[self.pairs_idx]

    def isTerminal(self):

        if self.pairs_idx>self.max_pair:
            return True

        return False

    def getReward(self):

        return self.total_reward

    def step_reward(self):

        # compute reward from other nets
        if self.connection or self.collide:
            # blocking other nets
            r_2 = self.reward_other_nets()
            # print("reward_other_nets is {} {}".format(r_2, self.total_reward))
            return r_2

        return -0.1

    def check_direction(self, direction):

        x = self.head[0] + direction[0]
        y = self.head[1] + direction[1]
        z = self.head[2] + direction[2]
        if 0 <= x < self.board.shape[0] and 0 <= y < self.board.shape[1] and 0 <= z < self.board.shape[2]:
            if (x,y,z) == self.end[self.pairs_idx]:
                return 2
            elif self.board[(x,y,z)] == 0:
                return 1
        return 0

    def compute_mask(self):

        mask = np.zeros(self.n_actions)
        for act_i in range(self.n_actions):
            act_d = self.directions[act_i]
            check_sign = self.check_direction(act_d)
            if check_sign==2:
                mask = np.zeros(self.n_actions)
                mask[act_i] = 1
                return mask
            elif check_sign==1:
                mask[act_i] = 1     

        return mask

    def getPossibleActions(self):

        possible_actions = []
        for act_d in self.directions:
            check_sign = self.check_direction(act_d)
            if check_sign==2:
                return [act_d]
            elif check_sign==1:
                possible_actions.append(act_d)
        return possible_actions

    def board_embedding(self):

        if self.pairs_idx<=self.max_pair:
            # dist_to_target = [i-j for i, j in zip(self.head, self.end[self.pairs_idx])]
            target = self.end[self.pairs_idx]
        else:
            # dist_to_target = [i-j for i, j in zip(self.head, self.end[self.pairs_idx-1])]
            target = self.end[self.pairs_idx - 1]
        state = np.array(list(self.head)+list(target))
        # state = np.array(list(self.head)+dist_to_target)
        # state = np.concatenate(( state, np.array(nets_vector.tolist()+obs_vector.tolist()) ), axis=0)

        return state

    def reward_other_nets(self):

        path_diff = 0
        pin_max = int(len(self.start)-1)
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
        t_node = self.end[net_id]
        maze = copy(self.board)
        maze[maze>1] = 1
        maze[s_node] = 0
        maze[t_node] = 0
        astar = Astar(maze)
        path = astar.run(s_node, t_node)

        return path