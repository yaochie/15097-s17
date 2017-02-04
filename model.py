#!/usr/bin/env python2

import matplotlib.pyplot as plt
import sys
import numpy as np
import random

VERBOSE = 0

class Brain:
    def __init__(self, num_in, num_out, decay = 0.995):
        mag = 0.01/num_in #xavier init.
        self.weights = np.random.normal(0.0, mag, (num_out, num_in))
        self.num_in = num_in
        self.num_out = num_out
        self.baseline = 0
        self.decay = decay
        self.newgame()

    def newgame(self):
        self.gradient = 0

    def softmax(self, vec):
        maxvec = max(vec)
        vec2 = vec-maxvec
        expvec = np.exp(vec2)
        norm = np.sum(expvec)
        return expvec/norm

    def choose(self, chances):
        return np.random.choice(range(self.num_out), p = chances)

    #use this function to output the index of the action to be taken
    def sample(self, input_):
        input_ = np.array(input_)
        Y = self.softmax(np.matmul(self.weights, input_))

        if VERBOSE:
            print(input_)
            print(self.weights)
            print(np.matmul(self.weights, input_))
            print(Y)
        
        idx = self.choose(Y)
        gradient_rows = []
        for i in range(self.num_out):
            gradient_rows.append(input_*(-Y[i]))
        gradient_rows[idx] += input_
        self.gradient += np.stack(gradient_rows, axis = 0)
        return idx

    #use this function to give the brain a reward and update params
    def give_reward(self, reward, lr = 0.0001):
        delta = self.gradient*(reward-self.baseline)*lr
        if VERBOSE:
            print('rewarding...')
            print(self.gradient)
            print(delta)
        self.weights += delta
        self.baseline = self.decay*self.baseline + (1.0-self.decay)*reward
        self.newgame()

def test():
    data = []
    
    B = Brain(10,4)
    for k in range(100000):
        x = random.randint(1,4)
        y = random.randint(1,4)

        input_ = ([1 if i == x else 0 for i in range(5)] +
                  [1 if i == y else 0 for i in range(5)])
        
        for i in range(50):
            a = B.sample(input_)

            if a == 0:
                x = (x+1)%5
            elif a == 1:
                x = (x+4)%5
            elif a == 2:
                y = (y+1)%5
            elif a == 3:
                y = (y+4)%5
            
            if x == 0 and y == 0:
                rwd = 50-i
                break
        else:
            rwd = -10

        B.give_reward(rwd)
        print(rwd)
        sys.stdout.flush()
        data.append(B.baseline)

    plt.plot(data)
    plt.show()
    
#test()
