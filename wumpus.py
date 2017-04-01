import logic2
import copy
import random

# -----------------------------------------------------------------------------

def playGame(world, useLogic):

    agent = Agent(world.boardSize, useLogic)

    loc = (1, 1)
    moveID = 0
    moveStatement = "Safe"
    agent.markCellAsVisited(loc)

    while(True):
        # Get sensor data at the current location

        x = loc[0]
        y = loc[1]

        moveID += 1

        #print("********** Sensor Data at (%d, %d) **********" % (x, y))

        breeze, stench, glitter, pit, wumpus, gold = world.getSensorData(loc, agent)

        # Update the knowledge base

        agent.B[x][y]  = breeze
        agent.S[x][y]  = stench
        agent.GL[x][y] = glitter

        if (not pit):
            agent.KB.tell('~P%d_%d' % (x, y))
            agent.P[x][y] = 0

        if (not wumpus):
            agent.KB.tell('~W%d_%d' % (x, y))
            agent.W[x][y] = 0

        if (not gold):
            agent.KB.tell('~G%d_%d' % (x, y))
            agent.G[x][y] = 0

        if (not pit and not wumpus and not gold):
            # Event: A breeze is detected or not -- related to a pit
            agent.setLogicForEvent(breeze, "breeze", "B", "P", (x, y))

            # Event: stench is detected or not -- related to a wumpus
            agent.setLogicForEvent(stench, "stench", "S", "W", (x, y))

            # Event: glitter is detected or not -- related to gold
            agent.setLogicForEvent(glitter, "glitter", "GL", "G", (x, y))

        #agent.displayKnowledge(x, y, world)
        agent.updateKnowledge()
        #agent.displayKnowledge(x, y, world)

        # Display information about the sensor data

        sensorData = ""

        if (breeze): sensorData  = "breeze"

        if (stench):
            if (len(sensorData) > 0):
                sensorData  += " & stench"
            else:
                sensorData = "stench"

        if (glitter):
            if (len(sensorData) > 0):
                sensorData  += " & glitter"
            else:
                sensorData = "glitter"

        if (len(sensorData) > 0):
            print 'Move # %d -- to (%d, %d): %s, detect %s' % (moveID, x, y, moveStatement, sensorData)
        else:
            print 'Move # %d -- to (%d, %d): %s' % (moveID, x, y, moveStatement)

        # Indicate if the game was won or lost

        if (pit):
            print("Fell into a pit - Game Over")
        elif (wumpus):
            print("The wumpus got you - Game Over")
        elif (gold):
            print("Game Won!")

        if (gold or pit or wumpus):
            agent.displayKnowledge(x, y, world)
            break

        agent.displayKnowledge(x, y, world)

        # Make the next move -- to a safe spot if possible, otherwise to a risky one.

        moveStatement, loc = agent.getNextMove(loc)
        
        if (moveStatement == "Can't Move"):
            print(moveStatement)
            print
            agent.displayKnowledge(x, y, world)
            break
        else:
            #statement = 'Move to %s - %s' % (loc, moveStatement)
            #print(statement)
            agent.markCellAsVisited(loc)
            
    print
    print

# -----------------------------------------------------------------------------

class Agent():
    def __init__(self, boardSize, useLogic):
        self.KB             = logic2.KB()
        self.boardSize      = boardSize
        self.useLogic       = useLogic
        self.visitedCells   = []
        self.unvisitedCells = []
        self.moves          = {}

        self.B  = [[False for i in range(self.boardSize+1)] for j in range(self.boardSize+1)]
        self.S  = [[False for i in range(self.boardSize+1)] for j in range(self.boardSize+1)]
        self.GL = [[False for i in range(self.boardSize+1)] for j in range(self.boardSize+1)]

        self.P  = [[1 for i in range(self.boardSize+1)] for j in range(self.boardSize+1)]
        self.W  = [[1 for i in range(self.boardSize+1)] for j in range(self.boardSize+1)]
        self.G  = [[1 for i in range(self.boardSize+1)] for j in range(self.boardSize+1)]

        for i in range(1, self.boardSize+1):
            for j in range(1, self.boardSize+1):
                self.unvisitedCells.append((i, j))
                self.moves[(i, j)] = 0

    def getNeighbors(self, x, y):    
        neighbors = [(x-1, y), (x+1, y), (x, y+1), (x, y-1)]
        return [(i, j) for i, j in neighbors if 1 <= i <= self.boardSize and 1 <= j <= self.boardSize] 

    def markCellAsVisited(self, loc):
        if (not loc in self.visitedCells): self.visitedCells.append(loc)
        if (loc in self.unvisitedCells):   self.unvisitedCells.remove(loc)

        maxMoveID = max([v for v in self.moves.values()])
        self.moves[loc] = maxMoveID+1

    def getNextMove(self, loc):
        safeCells = self.getSafeCells()
        safeCells = self.getSafeCells().intersection(self.unvisitedCells)
        #print("Safe cells: %s" % safeCells)

        goldCells = self.getGoldCells()

        statement = ""
        location  = ()

        if (len(goldCells) > 0):
            location = min(goldCells)
            statement = "gold"
        elif (len(safeCells) > 0):
            location = min(safeCells)
            statement = "safe"
        else:
            riskyCells = self.getRiskyCells().intersection(self.unvisitedCells)

            neighborsOfVisitedCells = self.getNeighborsOfVisitedCells()
            riskyCells = riskyCells.intersection(neighborsOfVisitedCells)
            #print("Risky cells: %s" % riskyCells)

            if (len(riskyCells) > 0):
                location = min(riskyCells)
                statement = "risky"
            else:
                statement = "Can't Move"

        return statement, location

    def getSafeCells(self):
        "Use logic to determine the set of safe locations"

        safeCells = set()

        if (self.useLogic):
            for i in range(1, self.boardSize + 1):
                for j in range(1, self.boardSize + 1):
                    loc = "" + str(i) + "_" + str(j)

                    # Add location to the safe_spots if it has been visited
                    if ((i, j) in self.visitedCells): safeCells.add((i, j))

                    # Not a pit and not a wumpus at location
                    if self.KB.resolution(logic2.expr("~P"+loc)) and self.KB.resolution(logic2.expr("~W"+loc)):
                        safeCells.add((i, j))

                    # If no smell, and no breeze, then all neighbors are safe locations.
                    no_smell  = self.KB.resolution(logic2.expr("~S"+loc))
                    no_breeze = self.KB.resolution(logic2.expr("~B"+loc))

                    if (no_smell and no_breeze):
                        for n in self.getNeighbors(i, j): safeCells.add(n)
        else:
            for i in range(1, self.boardSize + 1):
                for j in range(1, self.boardSize + 1):
                    if ((self.P[i][j] == 0) and (self.W[i][j] == 0)): safeCells.add((i, j))

        return safeCells

    def getGoldCells(self):
        "Use logic to determine the set of locations that contain gold"

        goldCells = set()

        if (self.useLogic):
            for i in range(1, self.boardSize + 1):
                for j in range(1, self.boardSize + 1):
                    loc = "" + str(i) + "_" + str(j)

                    # Locations with gold
                    if self.KB.resolution(logic2.expr("G"+loc)):
                        goldCells.add((i, j))

            neighborsOfVisitedCells = self.getNeighborsOfVisitedCells()
            goldCells = goldCells.intersection(neighborsOfVisitedCells)
        else:
            for i in range(1, self.boardSize + 1):
                for j in range(1, self.boardSize + 1):
                    if (self.G[i][j] == 2): goldCells.add((i, j))

        return goldCells

    def getRiskyCells(self):
        # Risky cells may have a pit or a wumpus
        # Not enough information is know to make an accurate determination

        riskyCells = set()

        if (self.useLogic):
            for i in range(1, self.boardSize + 1):
                for j in range(1, self.boardSize + 1):
                    loc = "" + str(i) + "_" + str(j)

                    if (not (i, j) in self.visitedCells): riskyCells.add((i, j))

                    if self.KB.resolution(logic2.expr("P" + loc)) or self.KB.resolution(logic2.expr("W" + loc)):
                        if ((i, j) in riskyCells): riskyCells.remove((i, j))

                    # If no smell and no breeze, then all neighbors are safe.
                    noSmell  = self.KB.resolution(logic2.expr("~S" + loc))
                    noBreeze = self.KB.resolution(logic2.expr("~B" + loc))

                    if (noSmell and noBreeze):
                        for n in self.getNeighbors(i, j): riskyCells.add(n)
        else:
            for i in range(1, self.boardSize + 1):
                for j in range(1, self.boardSize + 1):
                    if ((self.P[i][j] == 1) or (self.W[i][j] == 1)): riskyCells.add((i, j))

        return riskyCells

    def getNeighborsOfVisitedCells(self):
        neighborCells = copy.deepcopy(self.visitedCells)

        for i in range(1, self.boardSize + 1):
            for j in range(1, self.boardSize + 1):
                if (i, j) in self.visitedCells:
                    for n in self.getNeighbors(i, j):
                        if (not n in neighborCells): neighborCells.append(n)

        return neighborCells

    def setLogicForEvent(self, eventTrue, eventName, eventCode, objectCode, (x, y)):
        #Account for the fact that an event did or did not happen,
        # and relate the event to the objects on which it depends.

        neighbors = self.getNeighbors(x, y)
        nSet      = set(neighbors)
        xNV       = nSet.intersection(self.visitedCells)
        nNotV     = list(nSet.difference(xNV))
       
        var = '%s%d_%d' % (eventCode, x, y)

        if (eventTrue):
            self.KB.tell(var)

            if (len(nNotV) > 0):
                s = '%s <=> ' % var
                n = 0
                for i, j in nNotV:
                    n += 1
                    if (n > 1): s += " | "
                    seg = '%s%d_%d' % (objectCode, i, j)
                    s += seg

                self.KB.tell(s)
        else:
            self.KB.tell('~%s' % var)

            if (len(nNotV) > 0):
                s = '~%s <=> ' % var
                n = 0
                for i, j in nNotV:
                    n += 1
                    if (n > 1): s += " & "
                    seg = '~%s%d_%d' % (objectCode, i, j)
                    s += seg

                    if   (eventCode == "B"):  self.P[i][j] = 0
                    elif (eventCode == "S"):  self.W[i][j] = 0
                    elif (eventCode == "GL"): self.G[i][j] = 0

                self.KB.tell(s)

    def updateKnowledge(self):
        # Identify cells that definitely have a pit or a wumpus.
        # Assume that a cell can have only one of the following: [pit, wumpus, gold, nothing]

        for i in range(1, self.boardSize+1):
            for j in range(1, self.boardSize+1):
                if ((not self.B[i][j]) and (self.S[i][j]) and (self.GL[i][j])): continue

                neighbors = self.getNeighbors(i, j)

                # If cell has a breeze, try to isolate the pit cell
                if (self.B[i][j]):
                    nn = [(x, y) for (x, y) in neighbors if (self.P[x][y] > 0)]
                    #print("B - (%d, %d): %s" % (i, j, nn))
                    if (len(nn) == 1):
                        (p,q) = nn[0]
                        self.P[p][q] = 2

                # If cell has a stench, try to isolate the wumpus cell
                if (self.S[i][j]):
                    nn = [(x, y) for (x, y) in neighbors if (self.W[x][y] > 0)]
                    #print("W - (%d, %d): %s" % (i, j, nn))
                    if (len(nn) == 1):
                        (p,q) = nn[0]
                        self.W[p][q] = 2

                # If cell has a glitter, try to isolate the gold cell
                if (self.GL[i][j]):
                    nn = [(x, y) for (x, y) in neighbors if (self.G[x][y] > 0)]
                    #print("G - (%d, %d): %s" % (i, j, nn))
                    if (len(nn) == 1):
                        (p,q) = nn[0]
                        self.G[p][q] = 2

    def displayKnowledge(self, x, y, world):
        # Block 1: Known pits, wumpii, and gold
        # Block 2: Detected breezes, stenches, and glitter
        # Block 3: The initial world, and the agent's location

        print("------------------------------------------------------------------------")
        print("  Determinations           Sensor Data         Move Order    Hidden View")

        senses = [["-", "B"], ["-", "S"], ["-", "G"]]

        for i in range(self.boardSize, 0, -1):
            s = ""

            for j in range(1, self.boardSize+1):
                seg = "%d%d%d  " % (self.P[j][i], self.W[j][i], self.G[j][i])
                s += seg
            s += "   "

            for j in range(1, self.boardSize+1):
                seg = "%s%s%s  " % (senses[0][self.B[j][i]], senses[1][self.S[j][i]], senses[2][self.GL[j][i]])
                s += seg
            s += "   "

            for j in range(1, self.boardSize+1):
                seg = "%2d " % self.moves[(j, i)]
                s += seg
            s += "   "

            for j in range(1, self.boardSize+1):
                if   ((j, i) in world.pits):   seg = " P "
                elif ((j, i) in world.wumpus): seg = " W "
                elif ((j, i) in world.gold):   seg = " G "
                else:                          seg = " - "
                if ((j == x) and (i == y)): seg = " A "
                s += seg

            print(s)
        print("------------------------------------------------------------------------")

# -----------------------------------------------------------------------------

class World:
    def __init__(self, boardSize, gold, pits, wumpus):
        self.boardSize = boardSize
        self.gold      = gold
        self.pits      = pits
        self.wumpus    = wumpus

    def getNeighbors(self, x, y):
        neighbors = [(x-1, y), (x+1, y), (x, y+1), (x, y-1)]
        return [(i, j) for i, j in neighbors if 1 <= i <= self.boardSize and 1 <= j <= self.boardSize] 

    def getSensorData(self, (x, y), agent):

        neighbors = self.getNeighbors(x, y)

        breeze  = any((i, j) in self.pits   for i, j in neighbors)
        stench  = any((i, j) in self.wumpus for i, j in neighbors)
        glitter = any((i, j) in self.gold   for i, j in neighbors)

        pit    = (x, y) in self.pits
        wumpus = (x, y) in self.wumpus
        gold   = (x, y) in self.gold

        return breeze, stench, glitter, pit, wumpus, gold

# -----------------------------------------------------------------------------

def createRandomGame(boardSize, nGold, nPits, nWumpii):

    startCell = (1, 1)

    nCells = boardSize*boardSize

    # Set gold locations

    if ((nGold < 0) or (nGold > nCells-1)): return

    gold = set()

    n = 0

    while(n < nGold):
        x = random.randint(1, boardSize)
        y = random.randint(1, boardSize)
        if ((not (x, y) in gold) and (not (x, y) == startCell)):
            gold.add((x, y))
            n += 1

    # Set pit locations

    if ((nPits < 0) or (nPits+nGold > nCells-1)): return

    pits = set()

    n = 0

    while(n < nPits):
        x = random.randint(1, boardSize)
        y = random.randint(1, boardSize)
        if (((not (x, y) in pits) and (not (x, y) in gold) and (not (x, y) == startCell))):
            pits.add((x, y))
            n += 1

    # Set wumpii locations

    if ((nWumpii < 0) or (nWumpii+nGold > nCells-1)): return

    wumpii = set()

    n = 0

    while(n < nWumpii):
        x = random.randint(1, boardSize)
        y = random.randint(1, boardSize)
        if (((not (x, y) in wumpii) and (not (x, y) in gold) and (not (x, y) == startCell))):
            wumpii.add((x, y))
            n += 1

    return gold, pits, wumpii

# -----------------------------------------------------------------------------

def main():
    genRandomGame = False

    if (genRandomGame):
        boardSize = random.randint(4, 8)
        #boardSize = 4
        print("Board size = %d" % boardSize)
    
        #gold, pits, wumpii = createRandomGame(boardSize, 1, 3, 1)
        #gold, pits, wumpii = createRandomGame(boardSize, 2, 8, 3)
        gold, pits, wumpii = createRandomGame(boardSize, 1, int(round(0.15*boardSize**2)), 1)

        playGame(World(boardSize, gold, pits, wumpii), False)
        #playGame(World(boardSize, gold, pits, wumpii), True)
    else:
        # Uses my method
        #playGame(World(4, {(3, 4)}, {(3, 1), (3, 3), (4, 4)}, {(1, 3)}), False)
         # Uses propositional logic
        playGame(World(4, {(3, 4)}, {(3, 1), (3, 3), (4, 4)}, {(1, 3)}), True)

if __name__ == '__main__':
  main()
