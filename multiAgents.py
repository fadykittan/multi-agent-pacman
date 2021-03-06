# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random
import util

from game import Agent


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(
            gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(
            len(scores)) if scores[index] == bestScore]
        # Pick randomly among the best
        chosenIndex = random.choice(bestIndices)

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [
            ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        # Food - Calculate foodDistance and closestFood
        sumFoodDistance = 0
        closestFood = 10000000
        distanceForEachFoodItem = [manhattanDistance(
            newPos, food) for food in newFood.asList()]
        if distanceForEachFoodItem:
            sumFoodDistance = sum(distanceForEachFoodItem)
            closestFood = min(distanceForEachFoodItem)

        # Ghosts - Calculate ghostDistance
        ghostDistance = 0
        for ghost in newGhostStates:
            ghostDistance += manhattanDistance(newPos, ghost.getPosition())

        # Result - Calculate Result
        if ghostDistance < 2:
            return -100000000000
        if sumFoodDistance < 2:
            return 100000000000
        return (- sumFoodDistance - 10*closestFood**2 - 10/(ghostDistance)**2 + successorGameState.getScore()**3)


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        def searchValue(state, depth):
            if state.isWin() or state.isLose() or (depth == self.depth*state.getNumAgents()):
                return self.evaluationFunction(state)
            if depth % state.getNumAgents() == 0:  # check if the agent is pacman (man agent)
                return maxValue(state, depth, depth % state.getNumAgents())
            else:
                return minValue(state, depth, depth % state.getNumAgents())

        def maxValue(state, depth, agentIndex):
            return max(list(map(lambda x: searchValue(state.generateSuccessor(agentIndex, x), depth+1), state.getLegalActions(agentIndex))))

        def minValue(state, depth, agentIndex):
            return min(list(map(lambda x: searchValue(state.generateSuccessor(agentIndex, x), depth+1), state.getLegalActions(agentIndex))))

        maxV = -float('inf')
        minimaxAction = 0
        if gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        for action in gameState.getLegalActions(0):
            value = searchValue(gameState.generateSuccessor(0, action), 1)
            if value > maxV:
                minimaxAction = action
                maxV = value
        return minimaxAction


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        # add -inf for pacman at index 0
        alphaBetas = [-float('inf')]
        # add inf for ghosts
        for b in range(1, gameState.getNumAgents()):
            alphaBetas.append(float('inf'))

        def searchValue(state, depth, alphaBetas):
            if state.isWin() or state.isLose() or (depth == self.depth*state.getNumAgents()):
                return self.evaluationFunction(state)
            if depth % state.getNumAgents() == 0:
                return maxValue(state, depth, depth % state.getNumAgents(), alphaBetas)
            else:
                return minValue(state, depth, depth % state.getNumAgents(), alphaBetas)

        def maxValue(state, depth, agentIndex, alphaBetas):
            # copy alphaBetas to new list
            alphaBetas = alphaBetas[:]
            v = -float('inf')
            for action in state.getLegalActions(agentIndex):
                v = max(v, searchValue(state.generateSuccessor(
                    agentIndex, action), depth+1, alphaBetas))
                if v > min(alphaBetas[1:]):
                    return v
                alphaBetas[agentIndex] = max(alphaBetas[agentIndex], v)
            return v

        def minValue(state, depth, agentIndex, alphaBetas):
            # copy alphaBetas to new list
            alphaBetas = alphaBetas[:]
            v = float('inf')
            for action in state.getLegalActions(agentIndex):
                v = min(v, searchValue(state.generateSuccessor(
                    agentIndex, action), depth+1, alphaBetas))
                if v < alphaBetas[0]:
                    return v
                alphaBetas[agentIndex] = min(alphaBetas[agentIndex], v)
            return v

        maxV = -float('inf')
        minimaxAction = 0
        if gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        for action in gameState.getLegalActions(0):
            value = searchValue(
                gameState.generateSuccessor(0, action), 1, alphaBetas)
            if value > maxV:
                minimaxAction = action
                maxV = value
            alphaBetas[0] = max(alphaBetas[0], maxV)
        return minimaxAction


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        def searchValue(state, depth):
            if state.isWin() or state.isLose() or (depth == self.depth*state.getNumAgents()):
                return self.evaluationFunction(state)
            if depth % state.getNumAgents() == 0:
                return maxValue(state, depth, depth % state.getNumAgents())
            else:
                return minValue(state, depth, depth % state.getNumAgents())

        def maxValue(state, depth, agentIndex):
            return max(list(map(lambda x: searchValue(state.generateSuccessor(agentIndex, x), depth+1), state.getLegalActions(agentIndex))))

        def minValue(state, depth, agentIndex):
            actions = state.getLegalActions(agentIndex)
            return sum(list(map(lambda x: searchValue(state.generateSuccessor(agentIndex, x), depth+1), actions))) / len(actions)

        maxV = -float('inf')
        minimaxAction = 0
        if gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        for action in gameState.getLegalActions(0):
            value = searchValue(gameState.generateSuccessor(0, action), 1)
            if value > maxV:
                minimaxAction = action
                maxV = value
        return minimaxAction


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: 
    The same logic as question 1, but added into account 
    the newScaredTimes and capsules 
    """
    "*** YOUR CODE HERE ***"
    newPos = currentGameState.getPacmanPosition()
    newFood = currentGameState.getFood()
    newGhostStates = currentGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
    score = currentGameState.getScore()
    capsules = currentGameState.getCapsules()

    # Calculate Ghost Distance
    ghostDistance = 0
    for ghost in newGhostStates:
        ghostDistance += manhattanDistance(newPos, ghost.getPosition())

    # Calculate capsule distance
    capsuleDistance = 0
    if len(capsules) > 0 and max(newScaredTimes) > 25:
        if ghostDistance < 2:
            return -1000000000
        else:
            closestCapsule = 10000
            for capsule in capsules:
                capsuleDistance += manhattanDistance(capsule, newPos)
                if capsuleDistance < closestCapsule:
                    closestCapsule = capsuleDistance
    else:
        capsuleDistance = 10000000000000000

    # Calculate food Distance and closest food
    foodDistance = 0
    closestFood = (1234, 5678)
    for x in range(newFood.width):
        for y in range(newFood.height):
            if newFood[x][y]:
                distance = manhattanDistance(newPos, (x, y))
                foodDistance += distance
                if distance < manhattanDistance(closestFood, newPos):
                    closestFood = (x, y)
    if closestFood != (1234, 5678):
        closestFood = manhattanDistance(closestFood, newPos)

    # Check and adjust variables
    if ghostDistance < 2:
        return -100000000000
    elif foodDistance == 0:
        return 100000000 * score
    if foodDistance == 2:
        return 1000000 * score
    elif foodDistance == 1:
        return 10000000 * score

    # Result
    value = 0
    value += - foodDistance
    value += - 10*closestFood**2
    value += - 10/ghostDistance**2
    value += score**3
    value += 100000000 / (1 + capsuleDistance)
    return value


# Abbreviation
better = betterEvaluationFunction
