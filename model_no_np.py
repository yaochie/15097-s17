#!/usr/bin/env python3

import matplotlib.pyplot as plt
import sys
import numpy as np
import math
import random
import copy

VERBOSE = 0

class Brain:
    def __init__(self, num_in, num_out, decay = 0.995):
        mag = 0.01/num_in #xavier init.
        self.weights = np.random.normal(0.0, mag, (num_out, num_in))
        self.num_in = num_in
        self.num_out = num_out
        self.baseline = 35
        self.decay = decay

    def loadweights(self, filename = 'weights'):
        with open(filename, 'r') as f:
            data = f.readlines()
        rows = []
        for line in data:
            line_ = list(map(float,line.strip().split(',')[:-1]))
            rows.append(line_)
        self.weights = rows
        print(np.array(self.weights))
        
    def softmax(self, vec):
        maxvec = max(vec)
        vec2 = [x-maxvec for x in vec]
        expvec = [math.exp(x) for x in vec2]
        norm = sum(expvec)
        return [x/norm for x in expvec]

    def choose(self, chances):
        return random.choices(range(self.num_out), weights=chances)

    def sample(self, input_):
        Y = [0 for i in range(self.num_out)]
        for j in range(self.num_out):
            for i in range(self.num_in):
                Y[j] += self.weights[j][i] + input_[i]
        Y = self.softmax(Y)
        
        idx = self.choose(Y)[0]
        return idx

    def give_reward(self, reward, lr = 0.0001):
        self.baseline = self.decay*self.baseline + (1.0-self.decay)*reward

def test():
    data = []
    
    B = Brain(10,4)
    B.loadweights()
    for k in range(10000):
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
    plt.savefig('graph.png')
    
test()
