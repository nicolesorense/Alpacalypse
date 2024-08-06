from cmu_graphics import *
import random
from PIL import Image
import copy
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
        self.shields = []
        self.caves = []
        self.cavesToDraw = []
        self.caveBorders = []
        self.separateCaves = []
        self.walls = []
        self.tunnels = []
    
    def drawShrubs(self, numShrubs, canvasWidth, char, zoom):
        image = '/Users/nicolesorensen/Downloads/15112/shrubs.png'
        # draw previous shrubs
        for shrub in self.shrubs:
            x = char.x-(char.lastX-shrub.x)*3 if zoom else shrub.x
            y = char.y-(char.lastY-shrub.y)*3 if zoom else shrub.y
            size = 160 if zoom else 40
            drawImage(image, x, y, width=size, height=size)

        # draw shrubs on app start
        if len(self.shrubs) < numShrubs:
            for newShrub in range(numShrubs):
                x = random.randint(0, canvasWidth)
                y = random.randint(120, 280)
                self.shrubs.append(Shrub(x,y))
                drawImage(image, x, y, width=40, height=40)

    # draw new shrubs when player moves at border
    def drawAtBorder(self, char, canvasWidth, canvasHeight):
        # image drawn on ipad using ibis paint
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

    def drawMountains(self, start, end, char, zoom):
        for mountain in self.mountains:
            index = self.mountains.index(mountain) % 3
            mountain.draw(start, end, index, char, zoom)

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

    def generateShield(self, caves):
        cave = random.choice(caves)
        if len(cave) >= 20 and len(self.shields) == 0:
            (x,y) = random.choice(cave)
            self.shields.append(Shield(x*20, y*20+300))

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


    def drawCaves(self, char, zoom):
        for row in range(len(self.caves)-1):
            for col in range(len(self.caves[0])-1):
                if self.caves[row][col] == 1:
                    x = char.x - (char.lastX - row*20)*3 if zoom else row*20
                    y = char.y - (char.lastY - (col*20+300))*3 if zoom else col*20 + 300
                    size = 20*3 if zoom else 20
                    drawRect(x, y, size, size, fill='darkgrey')

    
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

    def drawBorders(self, caveBorders, char, zoom):
        for point in caveBorders:
            borderX = char.x - (char.lastX-point[0]*20)*3 if zoom else point[0]*20
            borderY = char.y - (char.lastY-(point[1]*20 + 300))*3 if zoom else point[1]*20 + 300
            size = 20*3 if zoom else 20
            drawRect(borderX, borderY, size, size, fill='black',
                    opacity=50)


    def pathsFromGrassToCaves(self):
        grassStart = 190
        for cave in self.separateCaves:
            # check if cave is close enough to surface
            if cave[0][1] <= 30 and len(cave) > 30:
                # if it is --> create tunnel straight down to it
                self.tunnels.append((cave[0][0], cave[0][1], 400))
                    # append the x coord and the height of the rect
    
    def drawTunnels(self, char, zoom):
        for tunnel in self.tunnels:
            x = char.x - (char.lastX-tunnel[0]*20)*3 if zoom else tunnel[0]*20
            y = char.y - (char.lastY - 190) if zoom else 190
            width = 30*3 if zoom else 30
            height = tunnel[2]*3 if zoom else tunnel[2]
            drawRect(x, y, width, height, fill='darkgrey')

    
    # Identify caves using floodfill algorithm
    # https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf
    # https://www.educative.io/answers/what-is-the-flood-fill-algorithm
        # got idea for algorithm, did not copy code
    def identifyCaves(self, canvasWidth, canvasHeight):
        # keep checking random caves until the list of caves is at least 6
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

    def onZoomIn(self, zoomWidth, zoomHeight, zoomCX, zoomCY):
        pass

    def drawTerrain(self, grass, char, appWidth, zoom):
        width, height = getImageSize(grass)
        if not zoom:
            # drawImage(grass, 0, 120, width=appWidth, height=190)
            drawRect(0, 120, appWidth, 190, fill='mediumseagreen')
        else:
            # find distance between old grass top and char
            # multiply that distance by 4
            # subtract it from chary
            top = char.y - (char.lastY - 120)*3
            side = char.x - (char.lastX)*3
            # drawImage(grass, side, top, width=appWidth*3, height=190*3)
            drawRect(side, top, appWidth*3, 190*3, fill='mediumseagreen')
    
    def drawSky(self, char, appWidth, appHeight, zoom):
        if app.terrain.time == 'day':
            y = char.y - (char.lastY)*3 if zoom else 0
            width = appWidth*3 if zoom else appWidth
            height = (appHeight*3)//3 if zoom else appHeight//3
            img = 'sky.PNG'
            drawImage(img, 0, y, width=width, height=height)
            app.sun.drawSun(char, zoom)
        if app.terrain.time == 'night':
            y = char.y - (char.lastY)*3 if zoom else 0
            img = 'nightSky.png'
            width = appWidth*3 if zoom else appWidth
            height = (appHeight*3)//3 if zoom else appHeight//3
            drawImage(img, 0, y, width=width, height=height)
            app.moon.drawMoon(char, zoom)


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
    identifyCavesHelper(self, width, height, x-1, y, cave, visited) # left
    identifyCavesHelper(self, width, height, x+1, y, cave, visited) # right
    identifyCavesHelper(self, width, height, x, y-1, cave, visited) # up
    identifyCavesHelper(self, width, height, x, y+1, cave, visited) # down

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
    
    def draw(self, startM, endM, index, char, zoom):
        for i in range(len(self.mPoints)-1):
            point = self.mPoints[i]
            nextPoint = self.mPoints[i+1]
            # x = char.x - (char.lastX-self.x)*4 if zoom else self.x
            # y = char.y - (char.lastY-self.y)*4 if zoom else self.y
            # width = self.width*(8/3) if zoom else self.width*(2/3)
            # height = self.height*(8/3) if zoom else self.height*(2/3)
            x0 = char.x - (char.lastX-point[0])*3 if zoom else point[0]
            x1 = char.x - (char.lastX-nextPoint[0])*3 if zoom else nextPoint[0]
            y0 = char.y - (char.lastY-point[1])*3 if zoom else point[1]
            y1 = char.y - (char.lastY-nextPoint[1])*3 if zoom else nextPoint[1]
            drawLine(x0, y0, x1, y1, fill = None)

        # draw polygon under points
        p = copy.deepcopy(self.mPoints)
        base = char.y - (char.lastY-120)*3 if zoom else 120
        end = char.x - (char.lastX-endM)*3 if zoom else endM
        start = char.x - (char.lastX-startM)*3 if zoom else startM
        p.append([end, base])
        p.append([start, base])
        pList = []
        for i in range(len(p)):
            x = char.x - (char.lastX-p[i][0])*3 if zoom else p[i][0]
            y = char.y - (char.lastY-p[i][1])*3 if zoom else p[i][1]
            pList.append(x)
            pList.append(y)

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

    def draw(self, char, zoom):
        x = char.x - (char.lastX-self.x)*3 if zoom else self.x
        y = char.y - (char.lastY-self.y)*3 if zoom else self.y
        size = 3*3 if zoom else 3
        drawCircle(x, y, size, fill=self.color)
    
    def fire(self):
        self.sin += 0.1
        if self.direction == 'right':
            self.x += 2
            self.y += 5*math.sin(2*self.sin)
        if self.direction == 'left':
            self.x -= 2
            self.y += 5*math.sin(2*self.sin)
    
    def isCollision(self, player, zoom):
        playerX = player.lastX if zoom else player.x
        playerY = player.lastY if zoom else player.y
        dX = player.charWidth//(2*3) if zoom else player.charWidth//2
        dY = player.charHeight//(2*3) if zoom else player.charHeight//2
        return ((playerX - dX <= self.x <= 
                 playerX + dX) and 
                (playerY - dY <= self.y <= 
                 playerY + dY))

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
    
    def drawSun(self, char, zoom):
        x = char.x - (char.lastX-self.x)*3 if zoom else self.x
        y = char.y - (char.lastY-self.y)*3 if zoom else self.y
        width = self.width*(6/3) if zoom else self.width*(2/3)
        height = self.height*(6/3) if zoom else self.height*(2/3)
        drawImage(self.sun, x, y, width=width, 
                  height=height)
        
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
    
    def drawMoon(self, char, zoom):
        x = char.x - (char.lastX-self.x)*3 if zoom else self.x
        y = char.y - (char.lastY-self.y)*3 if zoom else self.y
        width = self.width*(6/3) if zoom else self.width*(2/3)
        height = self.height*(6/3) if zoom else self.height*(2/3)
        drawImage(self.moon, x, y, width=width, 
                  height=height)

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
    
    def draw(self, char, zoom):
        x = char.x - (char.lastX - self.x)*3 if zoom else self.x
        y = char.y - (char.lastY - self.y)*3 if zoom else self.y
        width = self.width*3//4 if zoom else self.width//4
        height = self.height*3//4 if zoom else self.height//4
        drawImage(self.image, x, y,
                  width=width, height=height)
        
class PacaMask(Map):
    def __init__(self, x, y):
        super().__init__
        self.x = x
        self.y = y
        self.onPlayer = False
        image = Image.open('alpacaMask.PNG')
        self.image = CMUImage(image)
        self.width, self.height = getImageSize(self.image)
    
    def draw(self, char, zoom):
        if zoom and not self.onPlayer:
            x = char.x - (char.lastX - self.x)*3
            y = char.y - (char.lastY - self.y)*3
        else:
            x = self.x
            y = self.y
        width = self.width/4.3*3 if zoom else self.width/4.3
        height = self.height/4.6*3 if zoom else self.height/4.6
        drawImage(self.image, x, y, width=width, height=height)
        
    def followPlayer(self, char, zoom):
        xShift = 17*3 if zoom else 17
        yShift = 32*3 if zoom else 32
        self.x = char.x-xShift
        self.y = char.y-yShift


# distance function
def distance(x0, y0, x1, y1):
    return ((x1-x0)**2 + (y1-y0)**2)**0.5

class Shield(Map):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.shieldImage = CMUImage(Image.open('shield.PNG'))
        width, height = getImageSize(self.shieldImage)
        self.shieldWidth = width//5
        self.shieldHeight = height//5
        self.sparkleIndex = 0
        self.sparkleImages = []
        self.onPlayer = False
        for i in range(0, 3):
            self.sparkleImages.append(f'sparkle{i}.PNG')
        width, height = getImageSize(self.sparkleImages[0])
        self.sparkleWidth = width//5
        self.sparkleHeight = height//5

    def draw(self, char, zoom):
        if not self.onPlayer:
            if zoom:
                x = char.x - (char.lastX - self.x)*3
                y = char.y - (char.lastY - self.y)*3
            else:
                x = self.x
                y = self.y
            width = self.shieldWidth*3 if zoom else self.shieldWidth
            height = self.shieldHeight*3 if zoom else self.shieldHeight
            drawImage(self.shieldImage, x, y, width=width, height=height)
        else:
            drawImage(self.sparkleImages[self.sparkleIndex], self.x, self.y,
                      width = self.sparkleWidth, height = self.sparkleHeight,
                      align='center')

    def shieldAroundPlayer(self, char):
        self.x = char.x
        self.y = char.y
