from collections import defaultdict
import numpy as np
from copy import copy
from copy import deepcopy
import os

from scipy.spatial import distance

from astar import Astar
import random
import torch
import math

def draw_board(paths_x, paths_y, board, save_name):
    
    import matplotlib.pyplot as plt
    width, height = board.shape

    if board.shape==(30,30):
        fig = plt.figure(figsize=[8, 8])
    else:
    # create a 8" x 8" board
        fig = plt.figure(figsize=[width/4, height/4])

    ax = fig.add_subplot(111)

    # draw the grid
    for x in range(width):
        ax.plot([x, x], [0,height-1], color=(0.5,0.5,0.5,1))
    for y in range(height):
        ax.plot([0, width-1], [y,y], color=(0.5,0.5,0.5,1))

    # draw paths
    for p in range(len(paths_x)):

        ph = plt.subplot()
        ph.plot(paths_x[p], paths_y[p], linewidth=5, color='black')

    # draw obstacles
    x_axis = []
    y_axis = []
    nets = dict()
    for x in range(width):
        for y in range(height):
            if board[x, y]!=0:
                x_axis.append(y)
                y_axis.append(x)
                if board[x, y]!=1:
                    nets[(x,y)] = board[x, y]
    # print(nets)
    ax.scatter(y_axis, x_axis, marker='s', s=250, c='k')

    for xy in nets:
        ax.text(xy[0], xy[1], str(int(nets[xy])-1), fontsize=18, color='w',
                horizontalalignment='center', verticalalignment='center')

    # scale the axis area to fill the whole figure
    ax.set_position([0,0,1,1])

    # get rid of axes and everything (the figure background will show through)
    ax.set_axis_off()

    # scale the plot area conveniently (the board is in 0,0..18,18)
    ax.set_xlim(0,width-1)
    ax.set_ylim(0,height-1)
    
    fig.savefig(save_name)


def visualize_path(board, path, starts, rollout_idx):

    paths_x, paths_y = separate_paths(starts, path)

    res_folder_name = "route_results"
    if not os.path.isdir(res_folder_name):
        os.mkdir(res_folder_name)

    saved_fig_name = os.path.join(res_folder_name, "oneNet_board_{}.png".format(rollout_idx))

    draw_board(paths_x, paths_y, board, saved_fig_name)


def mcts_DFS_rollout(state, model):

    '''
    This function is DFS based rollout for MCTS, now it just rollout for one net
    '''
    paths = []
    ini_state = deepcopy(state)
    while not ini_state.isTerminal():

        # Following 3 line is to deal with the case where the selection of MCTS reaches the target
        possible_actions = ini_state.getPossibleActions()
        if len(possible_actions)>0:
            if possible_actions[0]==ini_state.end[state.pairs_idx]:
                ini_state = ini_state.takeAction(possible_actions[0], is_tuple=True)
                paths += [ini_state.head, ini_state.end[state.pairs_idx]]
                continue
        
        path = prob_DFS(ini_state, model)
        # checking if the path exists, non-existence can be caused be a bad selection of mcts
        if path is None:
            print("DFS doesn't find a path!!!")
            return -100, [ini_state.head]

        path.append(ini_state.end[ini_state.pairs_idx])
        # print(path)
        # print(ini_state.head, ini_state.end[ini_state.pairs_idx], path)
        paths += path
        for node in path[1:]:
            action = tuple(np.array(node)-np.array(ini_state.head))
            ini_state = ini_state.takeAction(action, is_tuple=True)
    # print("total reward is: {}".format(ini_state.getReward()))

    if len(paths)==0:
        paths=[state.head]
    rew = ini_state.getReward()
    del ini_state
    return rew, paths

def block_other_nets(check_state, path):

    state = deepcopy(check_state)
    starts = state.start
    finishs = state.end
    maze = state.board
    for p in path:
        maze[p] = 1
    pin_max = len(state.start) - 1
    for i in range(state.pairs_idx+1, pin_max+1):
        maze[maze>1]=1
        maze[starts[i]] = 0
        maze[finishs[i]] = 0
        astar = Astar(maze)
        path_t = astar.run(starts[i], finishs[i])
        if path_t is None:
            return True        
    return False

def prob_DFS(state, model=None, deterministic=False):
    
    DFS_state = deepcopy(state)
    pair_index = state.pairs_idx
    
    states_queue = [DFS_state]
    path = [DFS_state.head]
    
    while DFS_state.pairs_idx==pair_index:
        
        obs_vec = np.expand_dims(DFS_state.board_embedding(), axis=0)
        mask = DFS_state.compute_mask()
        # print(mask, len(states_queue))
        if not all(mask==0):
            if model is not None:
                dist = model.get_distribution(torch.tensor(obs_vec))
                probs = np.array([math.exp(dist.log_prob(torch.tensor(i)).tolist()[0]) for i in range(len(state.directions))])
                new_dist = probs * mask
                # print(new_dist)
                if sum(new_dist)==0:
                    new_dist = mask
                new_dist = new_dist/sum(new_dist)
                if deterministic:
                    action = DFS_state.directions[np.argmax(new_dist)]
                else:
                    action = random.choices(DFS_state.directions, weights=new_dist, k=1)[0]
            else:
                action = random.choice(DFS_state.getPossibleActions())
                # let's try random action
                # actions = DFS.state.getPossibleActions()

            DFS_state = DFS_state.takeAction(action, True)
            states_queue.append(DFS_state)
            path.append(DFS_state.head)
        elif len(states_queue)>1:
            pop_state = states_queue.pop()
            pop_state.board[pop_state.head] = 1
            DFS_state = states_queue[-1]
            DFS_state.board = copy(pop_state.board)
            path.pop()
        else:
            return None

    # if path[-1]!=state.finish[state.pairs_idx]:
    #     print("mask is: {}".format(mask))
    #     draw_board([], [], DFS_state.board, "DFS_vis.png")
    # for connecting multi-net
    path.pop()
    return path

def MCTS_search(env, model, fig_idx=0, board_ID='II4', rollout_times=50):

    from mcts import mcts

    state = deepcopy(env)
    state.reset()
    # print(state.finish)
    pin_indices = list(range(len(state.start)))
    pin_indices.sort()
    # board = copy(state.board)

    reward_type = 'best'
    node_select = 'best'
    # rollout_times = 20

    routed_paths = defaultdict(list)

    MCTS = mcts(iterationLimit=rollout_times, rolloutPolicy=mcts_DFS_rollout, nn_model=model,
            rewardType=reward_type, nodeSelect=node_select, explorationConstant=5)


    path_length = []
    nets_distance = []
    for pin_idx in pin_indices:
    # for pin_idx in [2]:
        pin_idx = int(pin_idx)
        state.reset(state.board, pin_idx)
        print(np.count_nonzero(state.board == 1))
        net_path = [state.start[pin_idx]]
        net_path += MCTS.search(initialState=state)

        routed_paths[state.pin_pair2net[pin_idx]].append(net_path)
        # checking if the path of this net block any other nets
        # if block_other_nets(state, net_path):
        #     print("MCTS did not find a good path to connect net {}".format(pin_idx))
            # break

        nets_distance.append(distance.cityblock(state.start[pin_idx], state.end[pin_idx]))
        if net_path[-1] == state.end[pin_idx]:
            path_length.append(len(net_path))
        else:
            path_length.append(0)

        for node in net_path[1:]:
            try:
                action = tuple(np.array(node)-np.array(state.head))
                state = state.takeAction(action, is_tuple=True)
            except:
                print("Duplicate path nodes in paths!")

    # paths_x, paths_y = separate_paths(env.start, routed_paths)

    # board = env.original_board

    # visual_folder_name = "visual_results_{}".format(rollout_times)
    # if not os.path.isdir(visual_folder_name):
    #     os.mkdir(visual_folder_name)
    
    # len_folder_name = "path_length_results_{}".format(rollout_times)
    # if not os.path.isdir(len_folder_name):
    #     os.mkdir(len_folder_name)
    # # saving path length and distance
    # len_save_folder = os.path.join(len_folder_name, "length_{}.csv".format(board_ID))
    # np.savetxt(len_save_folder, [path_length, nets_distance], delimiter=",")
    
    # saved_fig_name = os.path.join(visual_folder_name, "{}.eps".format(board_ID))

    # draw_board(paths_x, paths_y, board, saved_fig_name)

    return routed_paths

def separate_paths(starts, routed_paths):
    
    ret_paths_x = []
    ret_paths_y = []
    single_path = []

    start_pins = list(starts.values())

    for v in routed_paths:
        if v in start_pins:
            ret_paths_x.append([node[0] for node in single_path])
            ret_paths_y.append([node[1] for node in single_path])
            single_path = [v]
        single_path.append(v)

    ret_paths_x.append([node[0] for node in single_path])
    ret_paths_y.append([node[1] for node in single_path])

    return ret_paths_x, ret_paths_y


# board_path = "../test_boards/benchmarks-1bitsy-hardware-1bitsy-v1.0b-1bitsy.kicad_pcb.json-B-twoify.csv"
# board = np.genfromtxt(board_path, delimiter=',')
# print(board.shape)
# draw_board([], [], board, "test.png")