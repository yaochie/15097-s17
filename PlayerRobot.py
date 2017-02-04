from robot import Robot
from constants import Actions, TileType, SetupConstants
import random
import time
import copy
import math

##########################################################################
# One of your team members, Chris Hung, has made a starter bot for you.  #
# Unfortunately, he is busy on vacation so he is unable to aid you with  #
# the development of this bot.                                           #
#                                                                        #
# Make sure to read the README for the documentation he left you         #
#                                                                        #
# @authors: christoh, [TEAM_MEMBER_1], [TEAM_MEMBER_2], [TEAM_MEMBER_3]  #
# @version: 2/4/17                                                       #
#                                                                        #
# README - Introduction                                                  #
#                                                                        #
# Search the README with these titles to see the descriptions.           #
##########################################################################

# !!!!! Make your changes within here !!!!!
class player_robot(Robot):
    def __init__(self, args):
        super(self.__class__, self).__init__(args)
        ##############################################
        # A couple of variables - read what they do! # 
        #                                            #
        # README - My_Robot                          #
        ##############################################
        self.toHome = []             
        self.numturns = 0            
        self.goinghome = False;      
        self.targetPath = None
        self.targetDest = (0,0)
        self.position = (0,0)
        self.randPoint = None
        self.uid = random.random()

    # A couple of helper functions (Implemented at the bottom)
    def OppositeDir(self, direction):
        return # See below

    def ViewScan(self, view):
        return # See below

    def FindRandomPath(self, view):
        return # See below

    def UpdateTargetPath(self):
        return # See below
        
    def UpdatePosition(self, offset):
        self.position = (self.position[0] + offset[0], self.position[1] + offset[1])    
    
    def StateEncoding(self):
        pass
        
    def oneHot(self, idx, num):
        tmp = [0 for x in range(num)]
        tmp[idx] = 1
        return tmp

    ###########################################################################################
    # This function is called every iteration. This method receives the current robot's view  #
    # and returns a tuple of (move_action, marker_action).                                    #
    #                                                                                         #
    # README - Get_Move                                                                       #
    ###########################################################################################
    def get_move(self, view, brain):
        self.numturns += 1
        # Returns home if you have one resource
        if len(self.toHome) + 2 > (SetupConstants.NUM_TURNS - self.numturns) or self.storage_remaining() <= 0:
            self.goinghome = True

        # How to navigate back home
        if self.goinghome:
            # You are at home
            if self.toHome == [] :
                self.goinghome = False
                return (Actions.DROPOFF, Actions.DROP_NONE)
            # Trace your steps back home
            prevAction = self.toHome.pop()
            revAction = self.OppositeDir(prevAction)
            assert isinstance(revAction, int)
            return (revAction, Actions.DROP_NONE)

        # go to resource if can be found.
        self.ViewScan(view)
        if self.targetPath is not None:
            if self.targetPath == []:
                self.targetPath = None
                return (Actions.MINE, Actions.DROP_NONE)
            else:
                actionToTake = self.UpdateTargetPath()
                self.toHome.append(actionToTake)
                return (actionToTake, Actions.DROP_NONE)

        bdim = SetupConstants.BOARD_DIM

        if (self.randPoint is None):
            diag = bdim/4
            angle = random.random()*2*math.pi
            self.randPoint = (math.cos(angle*diag),math.sin(angle*diag))

        viewCopy = copy.deepcopy(view)
        encoding_dict = dict(Plains=0, Mountain=1, Marker=2, Resource=3, Base=4)
        for ix in range(len(viewCopy)):
            for iy in range(len(viewCopy[ix])):
                #print(viewCopy[ix][iy])
                viewCopy[ix][iy] = (self.oneHot(viewCopy[ix][iy][0].GetType(), 5), viewCopy[ix][iy][1], viewCopy[ix][iy][2])
                
        # flatten (len 150)
        flat = [item for l1 in viewCopy for l2 in l1 for item in l2[0]]
        flat += [item[1] for l1 in viewCopy for item in l1]
        
        # len 153
        vect = [self.position[0], self.position[1], self.storage_remaining()] + flat
        
        # distance, angle to base
        distance = math.floor(math.hypot(self.position[0], self.position[1]))
        angle = math.atan2(self.position[0], self.position[1])
        
        # distance, angle to randpoint
        offset_rand = (self.position[0] - self.randPoint[0], self.position[1] - self.randPoint[1])
        distance_rand = math.floor(math.hypot(offset_rand[0], offset_rand[1]))
        angle_rand = math.atan2(offset_rand[0], offset_rand[1])
        
        # len 159
        vect += [distance, angle, distance_rand, angle_rand, self.uid, 1]

        # feed to brain, check that result is allowed (can move to that tile)
        offsets = {Actions.MOVE_E: (0,1), Actions.MOVE_N: (-1,0), Actions.MOVE_S: (1,0),
            Actions.MOVE_W: (0,-1), Actions.MOVE_NE: (-1,1), Actions.MOVE_NW: (-1,-1),
            Actions.MOVE_SW: (1,-1), Actions.MOVE_SE: (1,1)}
        actions = [Actions.MOVE_N, Actions.MOVE_E, Actions.MOVE_S, Actions.MOVE_W, Actions.MOVE_NW,
            Actions.MOVE_NE, Actions.MOVE_SW, Actions.MOVE_SE]
        viewLen = len(view)
        while True:
            actionIdx = brain.sample(vect)
            #print(actions[actionIdx])
            actionToTake = actions[actionIdx]

            viewIndex = (viewLen // 2, viewLen // 2)
            offset = offsets[actionToTake]
            if view[viewIndex[0] + offset[0]][viewIndex[1] + offset[1]][0].CanMove():
                break

        self.toHome.append(actionToTake)
        return (actionToTake, Actions.DROP_BLUE)

    """
    def get_move(self, view):
        bdim = SteupConstants.BOARD_DIM

        if (self.randPoint is None):
            diag = bdim/4
            angle = random.random()*2*math.pi
            self.randPoint = (math.cos(angle*diag),math.sin(angle*diag))

        # Returns home if you have one resource
        if (self.held_value() > 0):
            self.goinghome = True
        if(self.storage_remaining() == 0):
            self.goinghome = True

        # How to navigate back home
        if(self.goinghome):
            # You are t home
            if(self.toHome == []):
                self.goinghome = False
                return (Actions.DROPOFF, Actions.DROP_NONE)
            # Trace your steps back home
            prevAction = self.toHome.pop()
            revAction = self.OppositeDir(prevAction)
            assert(isinstance(revAction, int))
            return (revAction, Actions.DROP_NONE)

        viewLen = len(view)
        score = 0
        # Run BFS to find closest resource

        # Search for resources
        # Updates self.targetPath, sefl.targetDest
        self.ViewScan(view)
        
        # If you can't find any resources...go in a random direction!
        actionToTake = None
        if(self.targetPath == None):
            actionToTake = self.FindRandomPath(view)

        # Congrats! You have found a resource
        elif(self.targetPath == []):
            self.targetPath = None
            return (Actions.MINE, Actions.DROP_NONE)
        else:
            # Use the first coordinate on the path as the destination , and action to move
            actionToTake = self.UpdateTargetPath()
        self.toHome.append(actionToTake)
        #markerDrop = random.choice([Actions.DROP_RED,Actions.DROP_YELLOW,Actions.DROP_GREEN,Actions.DROP_BLUE,Actions.DROP_ORANGE])
        markerDrop = Actions.DROP_NONE
        assert(isinstance(actionToTake, int))
        
        offsets = {Actions.MOVE_E: (0,1), Actions.MOVE_N: (-1,0), Actions.MOVE_S: (1,0),
            Actions.MOVE_W: (0,-1), Actions.MOVE_NE: (-1,1), Actions.MOVE_NW: (-1,-1),
            Actions.MOVE_SW: (1,-1), Actions.MOVE_SE: (1,1)}
        if actionToTake in offsets.keys():
            self.updatePosition(offsets[actionToTake])
        
        viewCopy = copy.deepcopy(views)
        for ix in len(viewCopy):
            for iy in len(viewCopy[ix]):
                viewCopy[ix][iy][0] = self.oneHot(viewCopy[ix][iy][0], 5)
                
        # flatten
        [0 for i in range(len(viewCopy))*len(viewCopy[0])*len(viewCopy[0])
        
        flat = [item for l1 in viewCopy for l2 in l1 for item in l2[0]]
        flat += [item[1] for l1 in viewCopy for item in l1]
        
        vect = [self.position[0], self.position[1], self.storage_remaining()] + flat
        
        # distance, angle to base
        distance = math.floor(math.hypot(self.position[0], self.position[1]))
        angle = math.atan2(self.position[0], self.position[1])
        
        # distance, angle to randpoint
        offset_rand = (self.position[0] - self.randPoint[0], self.position[1] - self.randPoint[1])
        distance_rand = math.floor(math.hypot(offset_rand[0], offset_rand[1]))
        angle_rand = math.atan2(offset_rand[0], offset_rand[1])
        
        vect += [distance, angle, distance_rand, angle_rand]
        
        # fix it to track marker objects
        
        return (actionToTake, markerDrop)
    """

    # Returns opposite direction
    def OppositeDir(self, prevAction):
        if(prevAction == Actions.MOVE_N):
            return Actions.MOVE_S
        elif(prevAction == Actions.MOVE_NE):
            return Actions.MOVE_SW
        elif(prevAction == Actions.MOVE_E):
            return Actions.MOVE_W
        elif(prevAction == Actions.MOVE_SE):
            return Actions.MOVE_NW
        elif(prevAction == Actions.MOVE_S):
            return Actions.MOVE_N
        elif(prevAction == Actions.MOVE_SW):
            return Actions.MOVE_NE
        elif(prevAction == Actions.MOVE_W):
            return Actions.MOVE_E
        elif(prevAction == Actions.MOVE_NW):
            return Actions.MOVE_SE
        else:
            return Actions.MOVE_S

    # Scans the entire view for resource searching
    # REQUIRES: view (see call location)
    def ViewScan(self, view):
        viewLen = len(view)
        queue = [[(0,0)]]
        deltas = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
        visited = set()
        visited.add((0,0))

        targetDepleted = (view[self.targetDest[0]][self.targetDest[1]][0].GetType() == TileType.Resource and
                         view[self.targetDest[0]][self.targetDest[1]][0].AmountRemaining() <= 0)

        # BFS TO find the next resource within your view
        if self.targetPath == None or targetDepleted:
            while(len(queue)>0):
                path = queue[0]
                loc = path[0]
                queue = queue[1:]
                #print("path: {} \t loc {}".format(path, loc))
                viewIndex = (loc[0] + viewLen//2,loc[1]+viewLen//2)
                if (view[viewIndex[0]][viewIndex[1]][0].GetType() == TileType.Resource and
                    view[viewIndex[0]][viewIndex[1]][0].AmountRemaining() > 0):
                    # print(path)
                    self.targetPath = path[1:]
                    self.targetDest = path[0]
                    return
                elif(view[viewIndex[0]][viewIndex[1]][0].CanMove()):
                    for i in range(8):
                        x = loc[0] + deltas[i][0]
                        y = loc[1] + deltas[i][1]
                        if(abs(x) <= viewLen//2 and abs(y) <= viewLen//2):
                            if((x,y) not in visited):
                                queue.append([(x,y)] + path[1:] + [deltas[i]])
                                visited.add((x,y))

        return

    # Picks a random move based on the view - don't crash into mountains!
    # REQUIRES: view (see call location)
    def FindRandomPath(self, view):
        viewLen = len(view)

        while(True):
            actionToTake = random.choice([Actions.MOVE_E,Actions.MOVE_N,
                                          Actions.MOVE_S,Actions.MOVE_W,
                                          Actions.MOVE_NW,Actions.MOVE_NE,
                                          Actions.MOVE_SW,Actions.MOVE_SE])
            if ((actionToTake == Actions.MOVE_N and view[viewLen//2-1][viewLen//2][0].CanMove()) or
               (actionToTake == Actions.MOVE_S and view[viewLen//2+1][viewLen//2][0].CanMove()) or
               (actionToTake == Actions.MOVE_E and view[viewLen//2][viewLen//2+1][0].CanMove()) or
               (actionToTake == Actions.MOVE_W and view[viewLen//2][viewLen//2-1][0].CanMove()) or
               (actionToTake == Actions.MOVE_NW and view[viewLen//2-1][viewLen//2-1][0].CanMove()) or
               (actionToTake == Actions.MOVE_NE and view[viewLen//2-1][viewLen//2+1][0].CanMove()) or
               (actionToTake == Actions.MOVE_SW and view[viewLen//2+1][viewLen//2-1][0].CanMove()) or
               (actionToTake == Actions.MOVE_SE and view[viewLen//2+1][viewLen//2+1][0].CanMove()) ):
               return actionToTake

        return None

    # Returns actionToTake
    # REQUIRES: self.targetPath != []
    def UpdateTargetPath(self):
        actionToTake = None
        (x, y) = self.targetPath[0]

        if(self.targetPath[0] == (1,0)):
            actionToTake = Actions.MOVE_S
            
        elif(self.targetPath[0] == (1,1)):
            actionToTake = Actions.MOVE_SE
        elif(self.targetPath[0] == (0,1)):
            actionToTake = Actions.MOVE_E
        elif(self.targetPath[0] == (-1,1)):
            actionToTake = Actions.MOVE_NE
        elif(self.targetPath[0] == (-1,0)):
            actionToTake = Actions.MOVE_N
        elif(self.targetPath[0] == (-1,-1)):
            actionToTake = Actions.MOVE_NW
        elif(self.targetPath[0] == (0,-1)):
            actionToTake = Actions.MOVE_W
        elif(self.targetPath[0] == (1,-1)):
            actionToTake = Actions.MOVE_SW

        # Update destination using path
        self.targetDest = (self.targetDest[0]-x, self.targetDest[1]-y)
        # We will continue along our path    
        self.targetPath = self.targetPath[1:]

        return actionToTake

