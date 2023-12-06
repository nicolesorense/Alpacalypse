from cmu_graphics import *
import random
from PIL import Image
import os, pathlib
import copy
import tkinter as tk
from tkinter import font
import math
from node_class import Node

# map class - create subclass of shrubs
class Map:
    def __init__(self):
        self.shrubs = []
        self.trees = []
        self.time = 'day'
        self.projectiles = []
        self.mountains = []
        self.numMountains = 3
        self.wings = []
        self.food = []
        self.pacaMasks = []
        self.caves = []
        self.cavesToDraw = []
        self.caveBorders = []
        self.separateCaves = []
        self.walls = []
        self.tunnels = []
        self.shortestPath = []
    
    def drawShrubs(self, numShrubs, canvasWidth, canvasHeight):
        image = '/Users/nicolesorensen/Downloads/15112/shrubs.png'
        # draw previous shrubs
        for shrub in self.shrubs:
            drawImage(image, shrub.x, shrub.y, width=40, height=40)

        # draw shrubs on app start
        if len(self.shrubs) < numShrubs:
            for newShrub in range(numShrubs):
                x = random.randint(0, canvasWidth)
                y = random.randint(120, 280)
                self.shrubs.append(Shrub(x,y))
                drawImage(image, x, y, width=40, height=40)

    # draw new shrubs when player moves at border
    def drawAtBorder(self, char, canvasWidth, canvasHeight):
        image = '/Users/nicolesorensen/Downloads/15112/shrubs.png'
        # draw a shrub 10% of the time
        z = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        if char.dirMoving == 'left' and char.isAtLeftBorder == True and z == 1:
            x = random.randint(0, 10)
            y = random.randint(120, 280)

            # check if there are already shrubs in the area
            for shrub in self.shrubs:
                if ((x-10) <= shrub.x <= (x+10)):
                    return
            self.shrubs.append(Shrub(x,y))
            drawImage(image, x, y, width=40, height=40)
        if char.dirMoving == 'right' and char.isAtRightBorder == True and z == 1:
            x = random.randint(canvasWidth-5, canvasWidth)
            y = random.randint(120, 280)
            for shrub in self.shrubs:
                if ((x-10) <= shrub.x <= (x+10)):
                    return
            self.shrubs.append(Shrub(x,y))
            drawImage(image, x, y, width=40, height=40)
    
    # draw mountains using midpoint displacement
    # inspiration from this video: https://www.youtube.com/watch?v=xSX1pN_dQQA 
    def generateMountains(self, mStart=0, mEnd=1450, pastMountains=None):
        for i in range (self.numMountains):
            mountain = Mountain()
            self.mountains.append(mountain)
            mountain.generate(mStart, mEnd, i, self.mountains, pastMountains)

    def addMountainPoint(self):
        for mountain in self.mountains:
            mountain.addPoint()

    def drawMountains(self, start, end):
        for mountain in self.mountains:
            index = self.mountains.index(mountain) % 3
            mountain.draw(start, end, index)

    def scroll(self, direction):
        if direction == 'right':
            for shrub in self.shrubs:
                shrub.x -= 10
            for projectile in self.projectiles:
                projectile.x -= 10
            for wing in self.wings:
                wing.x -= 10
            # mountains scroll slower than everything else
            for mountain in self.mountains:
                for point in mountain.mPoints:
                    point[0] -= 2
        if direction == 'left':
            for shrub in self.shrubs:
                shrub.x += 10
            for projectile in self.projectiles:
                projectile.x += 10
            for wing in self.wings:
                wing.x += 10
            for mountain in self.mountains:
                for point in mountain.mPoints:
                    point[0] += 2

    def drawMoreMountains(self, side, canvasWidth, playerX):
        # check if there aren't already mountains there
        currMPoints = self.mountains[0].mPoints
        farthestMountainPoint = currMPoints[len(currMPoints)-1][0]
        if side == 'right' and (farthestMountainPoint%(playerX+30) == 0):
            self.generateMountains(canvasWidth, canvasWidth*2, 'right')
            for mountain in self.mountains:
                mountain.addPoint()
                index = self.mountains.index(mountain) % 3
                mountain.draw(canvasWidth, canvasWidth*2, index)

    def generateWings(self, appWidth, appHeight):
        numWings = 2
        for wing in range(numWings):
            x = random.randint(0, appWidth)
            y = random.randint(120, 200)
            self.wings.append(Wing(x, y))

    def generateFood(self, appWidth, appHeight):
        numFood = 5-len(self.food)
        for food in range(numFood):
            x = random.randint(0, appWidth)
            y = random.randint(120, 270)
            self.food.append(Food(x, y))
    
    def generatePacaMask(self, caves):
        cave = random.choice(caves)
        if len(cave) >= 20 and len(self.pacaMasks) == 0:
            (x,y) = random.choice(cave)
            self.pacaMasks.append(PacaMask(x*20, y*20+300))

    # use Cellular Automata algorithm for cave generation
    # used TP Guide on terrain:
        # https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf
    def generateCaves(self, appWidth, appHeight):
        rows, cols = appWidth//20, appHeight//20-16 # excluding sky and surface

        # initialize with 0, then randomize 1s and 0s
        grid = [[0]*cols for row in range(rows)]
        for row in range(rows):
            for col in range(cols):
                grid[row][col] = random.choice([1, 0])
        self.caves = grid

        # 8 iterations of  cellular automata algorithm
        for i in range(8):
            for row in range(rows):
                for col in range(cols):
                    # if the cell is a passage and 4 neighbors are passages, stay the same
                    neighbors = neighPassagesAndWalls(grid, rows, cols, row, col)
                    if (grid[row][col] == 1 and 
                        neighbors[0] >= 3):
                        grid[row][col] = 1
                    # if the cell is a wall and 5 neighs are passages -> passage
                    elif (grid[row][col] == 0 and 
                        neighbors[0] >= 6):
                        grid[row][col] = 1
                    else:
                        grid[row][col] = 0

    def getCavesToDraw(self):
        for row in range(len(self.caves)):
            for col in range(len(self.caves[0])):
                # if it is a passage add it to the list of squares to draw
                if self.caves[row][col] == 1:
                    self.cavesToDraw.append((row, col))
                elif self.caves[row][col] == 0:
                    self.walls.append((row, col))

    def drawCaves(self):
        for row in range(len(self.caves)-1):
            for col in range(len(self.caves[0])-1):
                if self.caves[row][col] == 1:
                    drawRect(row*20, col*20 + 300, 20, 20, fill='darkgrey')
    
    # idea from https://www.kodeco.com/3016-introduction-to-a-pathfinding?page=2
        # and https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf

    # find shortest path from char to mask using A* algorithm
    def findShortestPath(self, player, appWidth, appHeight):

        # start is char end is mask
        startPoint = Node((player.x, player.y))
        goalPoint = Node((self.pacaMasks[0].x, self.pacaMasks[0].y))

        open = [] # nodes that need to be checked
        closed = [] # nodes already evaluated
        open.append(startPoint) # F, G, H scores, and parent

        while len(open) > 0:
            # print(len(open))
            # node in open with lowest F-cost
            curr = getLowestFcost(open)
            open.remove(curr)
            closed.append(curr)
            input()
            print(f'curr: {curr.position}, goalPoint: {goalPoint.position}')
            if curr == goalPoint:
                # backtrack to start to find path
                path = []
                while curr != None:
                    print('here')
                    path.append(curr.position)
                    curr = curr.parent # set curr = parent
                self.shortestPath.append(path[::-1]) # add reversed path

            neighbors = getNeighbors(curr, appWidth, appHeight)
            for neighbor in neighbors:
                # check if it is walkable
                neighX = neighbor.position[0]
                neighY = neighbor.position[1]
                # check if neighbor is in range
                if (not (0 < neighX < appWidth) or not (100 < neighY < appHeight)):
                    continue
                for closedNeighbor in closed:
                    if neighbor == closedNeighbor:
                        continue
                # G-score -> curr + distance from neigh to curr
                # print(f"open: {open}")
                # print(f"curr: {curr}")
                neighbor.g = (curr.g + 
                    distance(neighX, neighY, curr.position[0], curr.position[1]))
                # H-score -> distance from neigh to end
                neighbor.h = distance(neighX, neighY, goalPoint.position[0], goalPoint.position[1])
                neighbor.f = neighbor.g + neighbor.h

                # check if neighbor is already in open list
                for openNode in open:
                    # if g-score is better
                    if neighbor == openNode and neighbor.g < openNode.g:
                        continue
                open.append(neighbor)

    def getCaveBorders(self):
        caves = self.cavesToDraw
        for cave in caves:
            x = cave[0]
            y = cave[1]
            if ((x+1, y) in caves) and ((x-1, y) not in caves):
                self.caveBorders.append((x-1, y))
            elif ((x+1, y) not in caves) and ((x-1, y) in caves):
                self.caveBorders.append((x+1, y))
            elif ((x, y-1) in caves) and ((x, y+1) not in caves):
                self.caveBorders.append((x, y+1))
            elif ((x, y-1) not in caves) and ((x, y+1) in caves):
                self.caveBorders.append((x-1, y))

    def pathsFromGrassToCaves(self):
        grassStart = 190
        for cave in self.separateCaves:
            # check if cave is close enough to surface
            if cave[0][1] <= 30 and len(cave) > 30:
                # if it is --> create tunnel straight down to it
                self.tunnels.append((cave[0][0], cave[0][1], 400))
                    # append the x coord and the height of the rect
    
    def drawTunnels(self):
        for tunnel in self.tunnels:
            x = tunnel[0]*20
            y = 190
            height = tunnel[2]
            drawRect(x, y, 30, height, fill='darkgrey')
    
    # Identify caves using floodfill algorithm
    # https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf
    # https://www.educative.io/answers/what-is-the-flood-fill-algorithm
        # got idea for algorithm, did not copy code
    def identifyCaves(self, canvasWidth, canvasHeight):
        # keep checking random caves until the list of caves is at least 4
        while len(self.separateCaves) < 6:
            distinctCave = []
            # first identify a random point in the list of all cave points 
            randomCave = random.choice(self.cavesToDraw)
            x = randomCave[0]
            y = randomCave[1]
            identifyCavesHelper(self, canvasWidth, canvasHeight, x, y, distinctCave, set())
            # check if the cave is already in the list
            if distinctCave[0] not in self.separateCaves:
                self.separateCaves.append(distinctCave)

def identifyCavesHelper(self, width, height, x, y, cave, visited):
    # check if the coords are off screen
    if not (0 <= x <= width and 0 <= y <= height):
        return
    # return if its a wall
    if self.caves[x][y] != 1 or (x,y) in visited:
        return
    # add to cave
    cave.append((x,y))
    visited.add((x,y))
    # call for each of the 4 directions
    # input()
    identifyCavesHelper(self, width, height, x-1, y, cave, visited) # left
    identifyCavesHelper(self, width, height, x+1, y, cave, visited) # right
    identifyCavesHelper(self, width, height, x, y-1, cave, visited) # up
    identifyCavesHelper(self, width, height, x, y+1, cave, visited) # down

def getNeighbors(curr, appWidth, appHeight):
    neighbors = []
    indices = [-1, 0, 1]
    for i in indices:
        for j in indices:
            if not (i == j == 0): # if not curr
                neighborPos = (curr.position[0]+i, curr.position[1]+j)
                if (not (0 < neighborPos[0] < appWidth) or not
                    (100 < neighborPos[1] < appHeight)):
                    neighbors.append(Node(neighborPos, curr)) # track neighbor and parent
    return neighbors

def getLowestFcost(open):
    minFcost = None
    minNode = None
    for node in open:
        fCost = node.f
        if minFcost == None or fCost < minFcost:
            minFcost = fCost
            minNode = node
    return minNode

def neighPassagesAndWalls(grid, rows, cols, currRow, currCol):
        numPassages = 0  
        numWalls = 0
        # loop over neightbors
        check = [-1, 0, 1]
        for i in check:
            for j in check:
                # exclude the curr cell and check if in bounds
                if (not (i == 0 and j == 0)) and ((0 < currRow < rows-1) 
                    and (0 < currCol < cols-1)):
                    if grid[currRow+i][currCol+j] == 1:
                        numPassages += 1
                    else:
                        numWalls += 1
        return (numPassages, numWalls)

class Mountain(Map):
    def __init__(self):
        super().__init__()
        self.mPoints = []
        self.mSmooth = 1.3
        self.mDisplacement = 40
        self.maxHeight = 110

    def generate(self, mStart, mEnd, i, mountains, pastMountains=None):
        maxHeight = self.maxHeight + i*15
        if pastMountains == 'right':
            start = [mStart, mountains[-(i+2)].mPoints[-1][1]]
        else:
            start = [mStart, random.randint(self.maxHeight-self.mDisplacement, 
                                        self.maxHeight+self.mDisplacement)]
        if pastMountains == 'left':
            end = (mountains[(2-i)].mPoints[0][1], 
                        random.randint(self.maxHeight-self.mDisplacement, 
                        self.maxHeight+self.mDisplacement))
        else:
            end = [mEnd, random.randint(self.maxHeight-self.mDisplacement, 
                                        self.maxHeight+self.mDisplacement)]
        self.mPoints.append(start)
        self.mPoints.append(end)

    def addPoint(self):
        newPoints = []
        oldPoints = self.mPoints
        for i in range(len(oldPoints)-1):
            midpoint = [(oldPoints[i][0]+ oldPoints[i+1][0])/2,
                        (oldPoints[i][1] + oldPoints[i+1][1])/2]
            midpoint[1] += (self.mDisplacement * random.choice([-1, 1]))
            newPoints.append(oldPoints[i])
            newPoints.append([midpoint[0], midpoint[1]])
        # add last point
        newPoints.append(oldPoints[len(oldPoints)-1])
        self.mPoints = newPoints
        # decay the displacement
        self.mDisplacement *= pow(2.0, -self.mSmooth)
    
    def draw(self, startM, endM, index):
        for i in range(len(self.mPoints)-1):
            point = self.mPoints[i]
            nextPoint = self.mPoints[i+1]
            drawLine(point[0], point[1], nextPoint[0], nextPoint[1],
                     fill = None)

        # draw polygon under points
        p = copy.deepcopy(self.mPoints)
        p.append([endM, 120])
        p.append([startM, 120])
        pList = []
        for i in range(len(p)):
            pList.append(p[i][0])
            pList.append(p[i][1])

        # colors
        if index == 0:
            color = 'mediumpurple'
        elif index == 1:
            color = 'mediumslateblue'
        else:
            color = 'slateblue'
        drawPolygon(*pList, fill = color)

# create projectile class
class Projectile(Map):
    def __init__(self, startX, startY, direction, color, velocity=5):
        super().__init__()
        self.x = startX
        self.y = startY
        self.direction = direction
        self.velocity = velocity
        self.lines = 4
        self.lineWidth = 7
        self.sin = 0.1
        self.color = color

    def draw(self):
        drawCircle(self.x, self.y, 3, fill=self.color)
    
    def fire(self):
        self.sin += 0.1
        if self.direction == 'right':
            self.x += 2
            self.y += 5*math.sin(2*self.sin)
        if self.direction == 'left':
            self.x -= 2
            self.y += 5*math.sin(2*self.sin)
    
    def isCollision(self, player):
        return ((player.x - ((player.charWidth//2)) <= self.x <= 
                 player.x + (player.charWidth)//2) and 
                (player.y - ((player.charHeight//2)) <= self.y <= 
                 player.y + (player.charHeight//2)))

# create shrubs as a subclass of map
class Shrub(Map):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

class Sun(Map):
    def __init__(self):
        super().__init__()
        self.x = 200//3
        self.y = 80
        self.sun = 'sun.png'
        self.width, self.height = getImageSize(self.sun)
    
    def drawSun(self):
        drawImage(self.sun, self.x, self.y, width=self.width*(2/3), 
                  height=self.height*(2/3))
        
    def moveSun(self, steps):
        if steps % 1200 <= 300:
            self.x += 0.05
            self.y -= 0.3
        elif steps % 1200 <= 600:
            self.x += 0.05
            self.y += 0.3

class Moon(Map):
    def __init__(self):
        super().__init__()
        self.x = 100
        self.y = 50
        self.moon = 'moon.png'
        self.width, self.height = getImageSize(self.moon)
    
    def drawMoon(self):
        drawImage(self.moon, self.x, self.y, width=self.width*(2/3), 
                  height=self.height*(2/3))

    def moveMoon(self, steps):
        if 600 <= (steps % 1200) <= 900:
            self.x += 0.05
            self.y -= 0.3
        elif 900 <= (steps % 1200) <= 1200:
            self.x += 0.05
            self.y += 0.3

class Wing(Map):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        image = Image.open('wings.png')
        self.image = CMUImage(image)
        flipped = image.transpose(Image.FLIP_LEFT_RIGHT)
        self.imageFlipped = CMUImage(flipped)
        self.width, self.height = getImageSize(self.image)
        self.onPlayer = False
        self.currImage = self.image
    
    def draw(self):
        drawImage(self.currImage, self.x, self.y, 
                  width=self.width//4, height=self.height//4)
        
    def followPlayer(self, char):
        if char.facing == 'right':
            self.currImage = self.image
            self.x = char.x-30
            self.y = char.y-10
        else:
            self.currImage = self.imageFlipped
            self.x = char.x+10
            self.y = char.y-10

class Food(Map):
    def __init__(self, x, y):
        super().__init__
        self.x = x
        self.y = y
        image = Image.open('watermelon.PNG')
        self.image = CMUImage(image)
        self.width, self.height = getImageSize(self.image)
    
    def draw(self):
        drawImage(self.image, self.x, self.y,
                  width=self.width//4, height=self.height//4)
        
class PacaMask(Map):
    def __init__(self, x, y):
        super().__init__
        self.x = x
        self.y = y
        self.onPlayer = False
        image = Image.open('alpacaMask.PNG')
        self.image = CMUImage(image)
        self.width, self.height = getImageSize(self.image)
    
    def draw(self):
        drawImage(self.image, self.x, self.y,
                  width=self.width/4.3, height=self.height/4.6)
        
    def followPlayer(self, char):
        self.x = char.x-17
        self.y = char.y-32


# distance function
def distance(x0, y0, x1, y1):
    return ((x1-x0)**2 + (y1-y0)**2)**0.5
