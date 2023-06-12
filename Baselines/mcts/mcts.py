from __future__ import division

import time
import math
import random
import numpy as np
import os

from functools import reduce

def randomPolicy(state, model):
    while not state.isTerminal():
        try:
            action = random.choice(state.getPossibleActions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action, is_tuple=True)
    return state.getReward()


class treeNode():
    def __init__(self, state, parent, rewardType):
        self.state = state
        self.isTerminal = state.isTerminal()
        self.isFullyExpanded = self.isTerminal
        self.parent = parent
        self.numVisits = 0
        if rewardType=="best":
            self.totalReward = float("-inf")
        else:
            self.totalReward = 0
        self.children = {}


class mcts():
    def __init__(self, timeLimit=None, iterationLimit=None, explorationConstant=1 / math.sqrt(2),
                 rolloutPolicy=randomPolicy, nn_model=None, rewardType="best", nodeSelect="best"):
        if timeLimit != None:
            if iterationLimit != None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy

        self.rewardType = rewardType
        self.nodeSelect = nodeSelect

        self.policy_model = nn_model

        self.route_paths_saved = []

    def search(self, initialState):
        self.root = treeNode(initialState, None, self.rewardType)

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeRound()
        else:
            for i in range(self.searchLimit):
                self.executeRoundByIters(i)

        # bestChild = self.getBestChildBasedonReward(self.root)
        # return self.getAction(self.root, bestChild), bestChild.totalReward
        return self.route_paths_saved

    def executeRound(self):
        node = self.selectNode(self.root)
        reward, _ = self.rollout(node.state)
        self.backpropogate(node, reward)

    def executeRoundByIters(self, rollout_idx):
        # selection and expansion
        node, select_by_node = self.selectNode(self.root)
        # print("path in selection part: {}".format(select_by_node))
        # rollout
        time1 = time.time()
        reward_total, route_paths = self.rollout(node.state, self.policy_model)
        print(f"rollout run time {time.time() - time1}")
        # update the best paths

        # from simulation import visualize_path
        # visualize_path(route_paths, node.state.start, rollout_idx)
        # print(rollout_idx, reward_total)
        
        route_paths.pop(0)
        route_paths = select_by_node + route_paths

        if reward_total>self.root.totalReward:
            self.route_paths_saved = route_paths
            
            
        # print(self.root.totalReward, reward_total)
        # backpropagation
        self.backpropogate(node, reward_total)

    def selectNode(self, node):
        route_by_select = []
        while not node.isTerminal:
            if node.isFullyExpanded:
                if self.nodeSelect == "best":
                    node = self.getBestChild(node, self.explorationConstant)
                    # node = self.getBestChildBasedonReward(node)
                else:
                    node = random.choice( list(node.children.values()) )
                if node.state.connection:
                    route_by_select.append(node.state.pre_head)
                route_by_select.append(node.state.head)
            else:
                ret_node = self.expand(node)
                if ret_node.state.connection:
                    route_by_select.append(ret_node.state.pre_head)
                route_by_select.append(ret_node.state.head)
                return ret_node, route_by_select
        return node, route_by_select

    def expand(self, node):
        actions = node.state.getPossibleActions()
        if len(actions)==0:
            # just take action 0
            action = 0
            newNode = treeNode(node.state.takeAction(action), node, self.rewardType)
            node.children[action] = newNode
            node.isFullyExpanded = True
            return newNode
        for action in actions:
            if action not in node.children.keys():
                newNode = treeNode(node.state.takeAction(action, is_tuple=True), node, self.rewardType)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode
        raise Exception("Should never reach here")

    def backpropogate(self, node, reward):
        while node is not None:
            # the backpropagation for the node on the tree is revised,
            # the path length from root to the selected node is counted
            node.numVisits += 1

            if self.rewardType == "ave":
                node.totalReward += reward
            else:
                node.totalReward = max(reward, node.totalReward)
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():

            if self.rewardType == "ave":
                nodeValue = child.totalReward / child.numVisits + explorationValue * math.sqrt(
                    2 * math.log(node.numVisits) / child.numVisits)
            else:
                nodeValue = child.totalReward + explorationValue * math.sqrt(
                    2 * math.log(node.numVisits) / child.numVisits)
                # print(child.totalReward, explorationValue * math.sqrt(2 * math.log(node.numVisits) / child.numVisits))

            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)

    # def getBestChildBasedonReward(self, node):

    #     bestValue = float("-inf")
    #     bestNodes = []
    #     for child in node.children.values():

    #         nodeValue = child.totalReward

    #         if nodeValue > bestValue:
    #             bestValue = nodeValue
    #             bestNodes = [child]
    #         elif nodeValue == bestValue:
    #             bestNodes.append(child)
    #     return random.choice(bestNodes)

    # def getAction(self, root, bestChild):
    #     for action, node in root.children.items():
    #         if node is bestChild:
    #             return action