from robot import Robot
from constants import Actions, TileType
import random
import time

################################################################################
# Do not make any API calls not listed below
# The following API is available from the Robot Class
# self.get_fov()                     - \return(int): Range of vision that robot can see. Vision/2 to the left and Vision/2 to the right.
# self.get_max_capacity()            - \return(int): Max amount of resources that the robot can hold.
# self.get_pickup_amount()           - \return(int): Amount of resources the robot can pick up every turn
# self.held_value()                  - \return(int): Value of resources currently held
# self.storage_remaining()           - \return(int): Amount of resources the robot can still pick up
# self.get_turn()                    - \return(int): Current turn number

# The following API is available from the Tile Class
# Tile.CanMove()                     - \return(bool): Determines whether or not robot is able to move to that tile
# Tile.GetType()                     - \return(TileType): Enum in constants.py that determines what type of tile it is

# The following API is available from the Resource Class, subclass of Tile
# Resource.Value()                   - \return(int): Value of 1 unit of resource
# Resource.AmountRemaining()         - \return(int): Number of units of resource remaining

# The following API is available from the Marker Class
# Marker.GetColor()                  - \return(MarkerType): Enum in constants.py that determines color of marker
# Marker.GetTurns()                  - \return(int) : Number of turns until this marker decays
################################################################################

def OppositeDir(direction):
    if(direction == Actions.MOVE_N):
        return Actions.MOVE_S
    elif(direction == Actions.MOVE_S):
        return Actions.MOVE_N
    elif(direction == Actions.MOVE_E):
        return Actions.MOVE_W
    elif(direction == Actions.MOVE_W):
        return Actions.MOVE_E

class player_robot(Robot):
    def __init__(self, args):
        super(self.__class__, self).__init__(args)
        self.toHome = []
        self.numturns = 0
        self.goinghome = False;
        self.targetPath = None
        self.targetDest = (0,0)
        self.directionBias = None

    # This method is called every iteration to determine what action to take
    # \param view = A nxnx3 array of the board centered on the robot
    #    - view[x][y][0] = Tile object for location (x,y)
    #    - view[x][y][1] = Number of robots at position (x,y)
    #    - view[x][y][2] = List of Marker objects at location (x,y)
    #    - x = [0, Vision], y = [0, Vision]
    #    - RobotLocation = (Vision/2, Vision/2) - Note: This is a relative location
    # This function needs to return a tuple ({Action}, {Marker, None}) where
    # {Action} is one of the actions defined in constants.py, and {Marker, None} is
    # one of the markers defined in constants.py or None
    # e.g. Returning (Actions.MOVE_N, Actions.DROP_RED) means an action of moving North and dropping a red marker
    # e.g. Returning (Actions.MINE, Actions.DROP_NONE) means an action of mining a resource and not dropping a marker
    def get_move(self, view):
        if (self.held_value() > 0):
            self.goinghome = True
        if(self.storage_remaining() == 0):
            self.goinghome = True
        if(self.goinghome):
            if(self.toHome == []):
                self.goinghome = False
                return (Actions.DROPOFF, Actions.DROP_NONE)
            prevAction = self.toHome.pop()
            if(prevAction == Actions.MOVE_N):
                revAction = Actions.MOVE_S
            elif(prevAction == Actions.MOVE_NE):
                revAction = Actions.MOVE_SW
            elif(prevAction == Actions.MOVE_E):
                revAction = Actions.MOVE_W
            elif(prevAction == Actions.MOVE_SE):
                revAction = Actions.MOVE_NW
            elif(prevAction == Actions.MOVE_S):
                revAction = Actions.MOVE_N
            elif(prevAction == Actions.MOVE_SW):
                revAction = Actions.MOVE_NE
            elif(prevAction == Actions.MOVE_W):
                revAction = Actions.MOVE_E
            elif(prevAction == Actions.MOVE_NW):
                revAction = Actions.MOVE_SE
            return (revAction, Actions.DROP_NONE)

        viewLen = len(view)
        score = 0
        #run bfs to find closest resource
        queue = [[(0,0)]]
        deltas = [(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
        visited = set()
        visited.add((0,0))

        targetDepleted = (view[self.targetDest[0]][self.targetDest[1]][0].GetType() == TileType.Resource and
                         view[self.targetDest[0]][self.targetDest[1]][0].AmountRemaining() <= 0)

        if(self.targetPath == None or targetDepleted):
            while(len(queue)>0):
                path = queue[0]
                loc = path[0]
                queue = queue[1:]
                viewIndex = (loc[0] + viewLen//2,loc[1]+viewLen//2)
                if (view[viewIndex[0]][viewIndex[1]][0].GetType() == TileType.Resource and
                    view[viewIndex[0]][viewIndex[1]][0].AmountRemaining() > 0):
                    # print(path)
                    self.targetPath = path[1:]
                    self.targetDest = path[0]
                    break
                elif(view[viewIndex[0]][viewIndex[1]][0].CanMove()):
                    for i in range(8):
                        x = loc[0] + deltas[i][0]
                        y = loc[1] + deltas[i][1]
                        if(abs(x) <= viewLen//2 and abs(y) <= viewLen//2):
                            if((x,y) not in visited):
                                queue.append([(x,y)] + path[1:] + [deltas[i]])
                                visited.add((x,y))
        actionToTake = None
        if(self.targetPath == None):
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
                   break

        elif(self.targetPath == []):
            self.targetPath = None
            return (Actions.MINE, Actions.DROP_NONE)
        elif(self.targetPath[0] == (1,0)):
            self.targetDest = (self.targetDest[0]-1, self.targetDest[1])
            self.targetPath = self.targetPath[1:]
            actionToTake = Actions.MOVE_S
        elif(self.targetPath[0] == (1,1)):
            self.targetDest = (self.targetDest[0]-1, self.targetDest[1]-1)
            self.targetPath = self.targetPath[1:]
            actionToTake = Actions.MOVE_SE
        elif(self.targetPath[0] == (0,1)):
            self.targetDest = (self.targetDest[0], self.targetDest[1]-1)
            self.targetPath = self.targetPath[1:]
            actionToTake = Actions.MOVE_E
        elif(self.targetPath[0] == (-1,1)):
            self.targetDest = (self.targetDest[0]+1, self.targetDest[1]-1)
            self.targetPath = self.targetPath[1:]
            actionToTake = Actions.MOVE_NE
        elif(self.targetPath[0] == (-1,0)):
            self.targetDest = (self.targetDest[0]+1, self.targetDest[1])
            self.targetPath = self.targetPath[1:]
            actionToTake = Actions.MOVE_N
        elif(self.targetPath[0] == (-1,-1)):
            self.targetDest = (self.targetDest[0]+1, self.targetDest[1]+1)
            self.targetPath = self.targetPath[1:]
            actionToTake = Actions.MOVE_NW
        elif(self.targetPath[0] == (0,-1)):
            self.targetDest = (self.targetDest[0], self.targetDest[1]+1)
            self.targetPath = self.targetPath[1:]
            actionToTake = Actions.MOVE_W
        elif(self.targetPath[0] == (1,-1)):
            self.targetDest = (self.targetDest[0]-1, self.targetDest[1]+1)
            self.targetPath = self.targetPath[1:]
            actionToTake = Actions.MOVE_SW
        self.toHome.append(actionToTake)
        markerDrop = random.choice([Actions.DROP_RED,Actions.DROP_YELLOW,Actions.DROP_GREEN,Actions.DROP_BLUE,Actions.DROP_ORANGE])
        if(random.randint(0,100) != 1):
            markerDrop = Actions.DROP_NONE
        return (actionToTake, markerDrop)




