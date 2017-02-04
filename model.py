#!/usr/bin/env python2

import matplotlib.pyplot as plt
import sys
import numpy as np
import random

VERBOSE = 0

class Brain:
    def __init__(self, num_in, num_out, decay = 0.99):
        mag = 0.01/num_in #xavier init.
        self.weights = np.random.normal(0.0, mag, (num_out, num_in))
        self.num_in = num_in
        self.num_out = num_out
        self.baseline = 0.0
        self.decay = decay
        self.newgame()

    def saveweights(self, filename = 'weights'):
        f = open(filename, 'w')
        for row in self.weights:
            for num in row:
                f.write(str(num))
                f.write(',')
            f.write('\n')
        f.close()
        
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
    def give_reward(self, reward, lr = 0.001):
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

    s = 20
    B = Brain(s*2,4)
    
    for k in range(50000):
        x = random.randint(1,s-1)
        y = random.randint(1,s-1)

        for t in range(100):
            input_ = ([1 if i == x else 0 for i in range(s)] +
                      [1 if i == y else 0 for i in range(s)])
            
            a = B.sample(input_)

            if a == 0:
                x = (x+1)%s
            elif a == 1:
                x = (x+s-1)%s
            elif a == 2:
                y = (y+1)%s
            elif a == 3:
                y = (y+s-1)%s
            
            if x == 0 and y == 0:
                rwd = 100-t
                break
        else:
            rwd = -10

        B.give_reward(rwd)
        print(rwd)
        sys.stdout.flush()
        data.append(B.baseline)

    plt.plot(data)
    plt.show()
    B.saveweights()
    
#test()
