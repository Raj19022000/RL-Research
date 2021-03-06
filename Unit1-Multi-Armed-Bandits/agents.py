#######################################################################
# Copyright (C)                                                       #
# 2020(rajghugare.vnit@gmail.com)                                     #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
#######################################################################

import random
import numpy as np
from bandits import BernoulliStationaryBandit
from bandits import GaussianStationaryBandit


class epsilon_greedy_agent(BernoulliStationaryBandit):
    def __init__(self, bandit, epsilon, num_iters):
        self.bandit = bandit
        self.epsilon = epsilon
        self.num_iters = num_iters
        self.Q = np.ones(self.bandit.num_arms)

    def EpsilonGreedy_policy(self):
        if random.random()<self.epsilon:
            arm = random.randint(0, self.bandit.num_arms-1)
        else:
            arm = np.argmax(self.Q)
        return arm

    def play(self,decay = True):
        self.bandit.reset()
        self.indicator = np.zeros(self.bandit.num_arms)
        for t in range(self.num_iters):
            arm = self.EpsilonGreedy_policy()
            reward = self.bandit.pull(arm)
            self.indicator[arm] += 1
            self.Q[arm] = (self.Q[arm]*self.indicator[arm] + reward)/(self.indicator[arm] + 1)
            if decay and t>0:
                if t > self.num_iters/50:
                    self.epsilon = 1/t
        arm_history = self.bandit.get_ArmHistory()
        regret = self.bandit.get_regret()
        total_reward = self.bandit.get_total_reward()
        return self.Q, regret, arm_history, total_reward


class softmax_agent(BernoulliStationaryBandit):
    def __init__(self, bandit, beta, num_iters):
        self.bandit = bandit
        self.beta = beta
        self.num_iters = num_iters
        self.Q = np.ones(self.bandit.num_arms)

    def Softmax_policy(self):
        prob = np.copy(np.exp(self.Q/self.beta)/np.sum(np.exp(self.Q/self.beta)))
        arm = np.random.choice(np.arange(self.bandit.num_arms), p = prob)
        return arm

    def play(self):
        self.bandit.reset()
        self.indicator = np.zeros(self.bandit.num_arms)
        for t in range(self.num_iters):
            arm = self.Softmax_policy()
            reward =  self.bandit.pull(arm)
            self.indicator[arm] += 1
            self.Q[arm] = (self.Q[arm]*self.indicator[arm] + reward)/(self.indicator[arm] + 1)
        arm_history = self.bandit.get_ArmHistory()
        regret = self.bandit.get_regret()
        total_reward = self.bandit.get_total_reward()
        return self.Q, regret, arm_history, total_reward


class UCB():
    def __init__(self, bandit, num_iters):
        self.bandit = bandit
        self.time = 0
        self.Q = np.zeros(self.bandit.num_arms)
        self.confidence = np.zeros(self.bandit.num_arms)
        self.num_iters = num_iters

    def UCB_policy(self):
        arm = np.argmax(np.add(self.Q,self.confidence))
        return arm

    def play(self):
        self.bandit.reset()
        for i in range(self.bandit.num_arms):
            self.Q[i] = self.bandit.pull(i)
            self.time +=1
        for i in range(self.num_iters-self.bandit.num_arms):
            a_h = self.bandit.get_ArmHistory()
            self.confidence = np.sqrt(2*np.log(self.time)/a_h)
            arm = self.UCB_policy()
            reward = self.bandit.pull(arm)
            self.Q[arm] = (self.Q[arm]*a_h[arm] + reward)/(a_h[arm] + 1)
        arm_history = self.bandit.get_ArmHistory()
        regret = self.bandit.get_regret()
        total_reward = self.bandit.get_total_reward()
        return self.Q, regret, arm_history, total_reward


class Median_elimination_agent():
    def __init__(self, bandit, epsilon, delta):
        self.bandit = bandit
        self.epsilon = epsilon/4
        self.delta = delta/2
        self.Q = np.ones(self.bandit.num_arms)
        self.S = np.arange(self.bandit.num_arms)
    def play(self):
        self.bandit.reset()
        self.indicator = np.zeros(self.bandit.num_arms)
        while len(self.S) != 1:
            for arm in self.S:
                count = int(2*np.log(3/self.delta)/np.square(self.epsilon))
                for i in range(count):
                    reward = self.bandit.pull(arm)
                    self.indicator[arm] += 1
                    self.Q[arm] = (self.Q[arm]*self.indicator[arm] + reward)/(self.indicator[arm] + 1)
            M = np.median(self.Q[self.S])
            self.S = np.delete(self.S, np.where(self.Q[self.S]<M))
            self.epsilon = self.epsilon*3/4
            self.delta = self.delta/2
            print(self.S)
        arm_history = self.bandit.get_ArmHistory()
        regret =  self.bandit.get_regret()
        total_reward = self.bandit.get_total_reward()
        #self.s will eventually contain arm
        return self.S, regret, arm_history,total_reward
