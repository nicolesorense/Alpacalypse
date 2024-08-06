from cmu_graphics import *
import random
from PIL import Image
from node_class import Node

# images drawn on ipad using ibis paint

# create class
class Alpaca:
    def __init__(self, x, y, type, speed=10):
        self.color = random.choice(['pink', 'blue', 'purple'])
        self.x = x
        self.y = y
        self.speed = 15
        self.nightMode = False
        self.facing = 'right'
        self.playerOnBack = False
        self.type = type
        self.shortestPath = []
        self.followingPlayer = False
        self.followCoolDown = 0

        # walking
        self.walkIndex = 0
        self.walkImages = []
        self.walkFlippedImages = []
        numImages = 3
        for i in range (1, numImages):
            filename = f'pink_alpaca{i}.png'
            imPIL = Image.open(filename)
            imCMU = CMUImage(imPIL)
            imFlipped = imPIL.transpose(Image.FLIP_LEFT_RIGHT)
            imFlippedCMU = CMUImage(imFlipped)
            self.walkImages.append(imCMU)
            self.walkFlippedImages.append(imFlippedCMU)

    def attack(self, target):
        # if player is in front of alpaca and close enough, move towards player
        pass
    
    def drawPaca(self, char, zoom):
        # pink paca
        pinkPaca = self.walkImages[self.walkIndex]
        pinkPacaFlipped = self.walkFlippedImages[self.walkIndex]
        # pinkImPIL = Image.open('pink_alpaca.png')
        # pinkPaca = CMUImage(pinkImPIL)
        # pinkImFlipped = pinkImPIL.transpose(Image.FLIP_LEFT_RIGHT)
        # pinkPacaFlipped = CMUImage(pinkImFlipped)
        width, height = getImageSize(pinkPaca)
        width = width*3 if zoom else width
        height = height*3 if zoom else height
        if self.playerOnBack and zoom:
            x = self.x
            y = self.y
        else:
            x = char.x-(char.lastX-self.x)*3 if zoom else self.x
            y = char.y-(char.lastY-self.y)*3 if zoom else self.y
        if (self.color == 'pink') and (self.facing == 'right'):
            drawImage(pinkPaca, x, y,
                      width=width//3, height=height//3, align='center')
        elif (self.color == 'pink') and (self.facing == 'left'):
            drawImage(pinkPacaFlipped, x, y,
                      width=width//3, height=height//3, align='center')
            
        # blue paca
        blueImPIL = Image.open('blue_alpaca.png')
        bluePaca = CMUImage(blueImPIL)
        blueImFlipped = blueImPIL.transpose(Image.FLIP_LEFT_RIGHT)
        bluePacaFlipped = CMUImage(blueImFlipped)
        if (self.color == 'blue') and (self.facing == 'right'):
            drawImage(bluePaca, x, y, 
                      width=width//3, height=height//3, align='center')
        elif (self.color == 'blue') and (self.facing == 'left'):
            drawImage(bluePacaFlipped, x, y, 
                      width=width//3, height=height//3, align='center')
            
        # purple paca
        purpleImPIL = Image.open('purple_alpaca.png')
        purplePaca = CMUImage(purpleImPIL)
        purpleImFlipped = purpleImPIL.transpose(Image.FLIP_LEFT_RIGHT)
        purplePacaFlipped = CMUImage(purpleImFlipped)
        if (self.color == 'purple') and (self.facing == 'right'):
            drawImage(purplePaca, x, y, 
                      width=width//3, height=height//3, align='center')
        elif (self.color == 'purple') and (self.facing == 'left'):
            drawImage(purplePacaFlipped, x, y, 
                      width=width//3, height=height//3, align='center')
            
    def isFacingPlayer(self, player, zoom):
        charX = player.lastX if zoom else player.x
        if self.facing == 'left' and player.facing == 'right':
            return (self.isNearPlayer(player, zoom) and self.x > charX)
        if self.facing == 'right' and player.facing == 'left':
            return (self.isNearPlayer(player, zoom) and self.x < charX)

    def isNearPlayer(self, player, zoom):
        charX = player.lastX if zoom else player.x
        charY = player.lastY if zoom else player.y
        return (distance(self.x, self.y, charX, charY) < 70)
    
    def move(self, steps, walls):
        if self.type == 'ground' and not self.followingPlayer:
            if self.y < 120:
                self.y += 5
            if self.y > 220:
                self.y -= 5
            if self.color == 'blue' and not self.playerOnBack:
                if steps % 100 <= 25:
                    self.facing = 'right'
                    self.x += 5
                elif steps % 100 <= 50:
                    self.facing = 'right'
                    self.y += 5
                elif steps % 100 <= 75:
                    self.facing = 'left'
                    self.x -= 5
                elif steps % 100 <= 100:
                    self.facing = 'left'
                    self.y -= 5
            if self.color == 'pink' and not self.playerOnBack:
                if steps % 80 <= 20:
                    self.facing = 'left'
                    self.y -= 3
                elif steps % 80 <= 40:
                    self.facing = 'right'
                    self.y += 3
                elif steps % 80 <= 60:
                    self.facing = 'right'
                    self.x += 3
                elif steps % 80 <= 80:
                    self.facing = 'left'
                    self.x -= 3
            if self.color == 'purple' and not self.playerOnBack:
                if steps % 90 <= 15:
                    self.facing = 'right'
                    self.x += 5
                elif steps % 90 <= 30:
                    self.facing = 'right'
                    self.y -= 5
                elif steps % 90 <= 45:
                    self.facing = 'right'
                    self.x += 5
                elif steps % 90 <= 60:
                    self.facing = 'left'
                    self.x -= 5
                elif steps % 90 <= 75:
                    self.facing = 'left'
                    self.y += 5
                else:
                    self.facing = 'left'
                    self.x -= 5
        elif self.type == 'cave' and not self.followingPlayer:
            if steps % 80 <= 40:
                self.facing = 'right'
                self.x += 1
            else:
                self.facing = 'left'
                self.x -= 1

    def moveWithPlayer(self, player, zoom):
        yShift = 35*3 if app.zoom else 35
        if self.playerOnBack:
            self.facing = player.facing
            self.x = player.x
            self.y = player.y + yShift

    # move alpacas when player is walking at border
    def scroll(self, direction):
        if direction == 'right':
            self.x -= 10
        if direction == 'left':
            self.x += 10

    def isAtCaveBorder(self, borders):
        for border in borders:
            borderX = border[0]*20
            borderY = border[1]*20 + 300
            if ((self.x-10 <= borderX <= self.x+10) and 
                (self.y-10 <= borderY <= self.y+10)):
                return True
            
     # idea from https://www.kodeco.com/3016-introduction-to-a-pathfinding?page=2
       # and https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf


   # find shortest path from char to mask using A* algorithm
    def findShortestPath(self, player, appWidth, appHeight):
       # start is char, end is mask
       startPoint = Node((self.x, self.y))
       goalPoint = Node((player.x, player.y))

       open = [] # nodes that need to be checked
       closed = [] # nodes already evaluated
       open.append(startPoint) # F, G, H scores, and parent


       while len(open) > 0:
           # node in open with lowest F-cost
           curr = getLowestFcost(open)
           open.remove(curr)
           closed.append(curr)
           if curr.closeTo(goalPoint):
               # backtrack to start to find path
               path = []
               while curr != None:
                   path.append(curr.position)
                   curr = curr.parent # set curr = parent
               self.shortestPath.append(path[::-1]) # add reversed path
               return


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
               neighbor.g = (curr.g +
                   distance(neighX, neighY, curr.position[0], curr.position[1]))
               # H-score -> distance from neigh to end
               neighbor.h = distance(neighX, neighY, goalPoint.position[0], goalPoint.position[1])
               neighbor.f = neighbor.g + neighbor.h


               # check if neighbor is already in open list
               for openNode in open:
                   # if g-score is better
                   if neighbor == openNode and neighbor.g > openNode.g:
                       continue
               open.append(neighbor)

    def chasePlayer(self, player):
        # if alpaca is close enough to player
        if (((self.x-5 <= player.x <= player.x+5) and
            (self.y-5 <= player.y <= player.y+5)) or len(self.shortestPath[0]) == 0):
            self.shortestPath = []
            self.followCoolDown = 800
            self.followingPlayer = False
            return
        if (self.shortestPath[0] != [] and 
            len(self.shortestPath[0][0]) > 0): # THIS IS THE ISSUE
            x, y = self.shortestPath[0][0]
            if x >= self.x+5:
                self.facing = 'right'
                self.x += 5
            elif x <= self.x-5:
                self.facing = 'left'
                self.x -= 5
            if y >= self.y+5:
                self.y += 5
            elif y <= self.y-5:
                self.y -= 5
            # check if alpaca is close enough to the point
            if self.x-5 <= x <= self.x+5 and self.y-5 <= y <= self.y+5:
                self.shortestPath[0].pop(0)
                return
            return

    def decreaseFollowCoolDown(self):
        if self.followCoolDown > 0:
            self.followCoolDown -= 1
            self.followingPlayer = False
        

def getNeighbors(curr, appWidth, appHeight):
    neighbors = []
    indices = [-20, 0, 20]
    for i in indices:
        for j in indices:
            if not (i == j == 0): # if not curr
                neighborPos = (curr.position[0]+i, curr.position[1]+j)
                if ((0 < neighborPos[0] < appWidth) and
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
