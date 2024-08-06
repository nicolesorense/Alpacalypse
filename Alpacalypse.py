from cmu_graphics import *
import random
from PIL import Image
from player_class import Player # used lecture slides to figure out how to organize files
from alpaca_class import Alpaca
from map_class import Map, Projectile, Sun, Moon, Food

# all images drawn using ibis paint on ipad

# keep track of stats

def newGame(app):
    app.items = []
    app.terrain = Map()

    # instructions typed up using google drawings
    app.instructions = 'instructions.png'
    app.helpWidth, app.helpHeight = getImageSize(app.instructions)

    # keep track of steps
    app.welcomeSteps = 0
    app.steps = 0

    # track alpacas
    app.alpacas = []
    app.caveAlpacas = []

    # track count so pacas are drawn every 10 seconds
    app.paca = False

    app.lastWidth = 0
    app.lastHeight = app.width//4

    # create character
    app.char = Player(app.width//2, 200)
    # set app dimensions
    app.width = 1450
    app.height = 800

    # sun
    app.sun = Sun()

    # moon
    app.moon = Moon()

    # generate mountains and powerups
    app.terrain.generateMountains(0, app.width)
    for i in range(5):
        app.terrain.addMountainPoint()
    app.terrain.generateWings(app.width, app.height)
    app.terrain.generateFood(app.width, app.height)

    # welcome image
    app.image = None
    app.gameTitle = None

    # when game over
    app.gameOver = False
    app.endMessage = None

    # generate caves
    app.terrain.generateCaves(app.width, app.height)
    app.terrain.getCavesToDraw()
    app.terrain.identifyCaves(app.width, app.height)
    app.separateCaves = app.terrain.separateCaves
    app.terrain.pathsFromGrassToCaves()
    app.terrain.getCaveBorders()
    app.caveBorders = app.terrain.caveBorders
    app.caves = app.terrain.cavesToDraw
    app.walls = app.terrain.walls
    app.tunnels = app.terrain.tunnels

    app.setMaxShapeCount(8000)

    app.background = 'gray'
    app.showInstructions = False

    app.drawBorder = False

    app.zoom = False

    app.zoomWidth = app.width
    app.zoomHeight = app.height

    # grass
    app.grass = CMUImage(Image.open('grass.PNG'))

def onAppStart(app):
    newGame(app)

#----------------------------------------------------
# got guidance from class demo

def welcome_redrawAll(app):
    if app.image != None:
        imageWidth, imageHeight = getImageSize(app.image)
        drawImage(app.image, 0, 0, width=imageWidth*1.13, height=imageHeight*1.1)
    
    if app.gameTitle:
        imageWidth, imageHeight = getImageSize(app.gameTitle)
        drawImage(app.gameTitle, app.width//2-170, app.height//2-165, 
                  width=imageWidth*.62,
                  height=imageHeight*.6)
    
    drawRect(app.width//2+190, app.height//2+20, 200, 50, align='center',
             fill='lightPink')
    drawLabel('Instructions', app.width//2+190, app.height//2+20, size=30,
              fill = 'black')
    drawLabel('Press space to begin', app.width//2+190, app.height//2+70,
              size=30, fill='white')
    if app.showInstructions == True:
        drawRect(app.width//2, app.height//2, app.helpWidth+10, app.helpHeight+10,
                 align='center', fill='white')
        drawImage(app.instructions, app.width//2, app.height//2, width=app.helpWidth, 
                  height=app.helpHeight, align='center')
        # draw the x
        drawRect(app.width//2+app.helpWidth//2 - 15, app.height//2-app.helpHeight//2+15,
                 15, 5, rotateAngle = 45, fill='white', align='center')
        drawRect(app.width//2+app.helpWidth//2 - 15, app.height//2-app.helpHeight//2+15,
                 15, 5, rotateAngle = -45, fill='white', align='center')

def welcome_onKeyPress(app, key):
    if key == 'space':
        setActiveScreen('game')

def welcome_onStep(app):
    app.welcomeSteps += 1
    if (app.welcomeSteps % 70 <= 10) or (app.welcomeSteps % 50 <= 8):
        app.image = 'madPaca.PNG'
        app.gameTitle = 'alpacalypseTitle.PNG'
    else:
        # drawn on ipad using ibisPaint
        # got inspiration from this photo: https://play-lh.googleusercontent.com/gIR2nsM93g7ZB3WWRlnJEp89gvhFd_NQfI1CV6l1KJ9GV8OIHa_gWuhShMPuGNaHePNo
        app.image = 'alpacalypseStartingScreen.PNG'
        app.gameTitle = None

def welcome_onMousePress(app, mouseX, mouseY):
    # check if clicked instructions
    if (app.width//2 + 90 <= mouseX <= app.width//2 + 290 and 
        app.height//2 - 5 <= mouseY <= app.height//2 + 75):
        app.showInstructions = True

    # check if clicked x
    if (app.width//2+app.helpWidth//2 - 25 <= mouseX <= app.width//2+app.helpWidth//2 and 
        app.height//2-app.helpHeight//2+5 <= mouseY <= app.height//2-app.helpHeight//2+20):
        app.showInstructions = False

#----------------------------------------------------

def game_redrawAll(app):
    if not app.gameOver:
        # if day draw clouds and sun
        app.terrain.drawSky(app.char, app.width, app.height, app.zoom)

        # draw caves
        app.terrain.drawCaves(app.char, app.zoom)

        # draw tunnels
        app.terrain.drawTunnels(app.char, app.zoom)

        # draw border
        if app.drawBorder == True:
            app.terrain.drawBorders(app.caveBorders, app.char, app.zoom)

        # draw mountains
        app.terrain.drawMountains(0, app.width, app.char, app.zoom)

        # draw terrain
        app.terrain.drawTerrain(app.grass, app.char, app.width, app.zoom)

        # draw shrubs
        numShrubs = 30
        app.terrain.drawShrubs(numShrubs, app.width, app.char, app.zoom)

        # draw alpacas
        for alpaca in app.alpacas:
            alpaca.drawPaca(app.char, app.zoom)

        # draw character
        char = app.char
        char.drawChar()

        # draw labels
        fill = 'white' if app.terrain.time == 'night' else 'black'
        drawLabel(f"Days survived: {char.daysSurvived}", 60, 10, size=16,
                                        fill = fill)

        # draw projectiles
        for projectile in app.terrain.projectiles:
                projectile.draw(app.char, app.zoom)

        # draw new shrubs when player is at border
        app.terrain.drawAtBorder(char, app.width, app.height)

        # draw health and hunger
        char.drawHealth()
        char.drawHunger()

        # jumping
        char.drawJumping()
            
        # walking
        char.drawWalking()
                
        # draw wings
        for wing in app.terrain.wings:
            wing.draw()

        # draw food
        for food in app.terrain.food:
            food.draw(char, app.zoom)
        
        # draw alpaca masks
        for mask in app.terrain.pacaMasks:
            mask.draw(char, app.zoom)

        # draw shields
        for shield in app.terrain.shields:
            shield.draw(char, app.zoom)

        # flying
        if char.wingPowerUp:
            # draw cast shadow
            drawOval(char.x, char.lastJumpY+(char.charHeight//4)+20, 
                        20, 8)
            
        # draw shortest paths
        for alpaca in app.alpacas:
            if alpaca.shortestPath != [] and len(alpaca.shortestPath[0]) > 0:
                for x,y in alpaca.shortestPath[0]:
                    pathX = char.x - (char.lastX - x)*3 if app.zoom else x
                    pathY = char.y - (char.lastY - y)*3 if app.zoom else y
                    size = 20*3 if app.zoom else 20
                    drawRect(pathX, pathY, size, size, fill='blue', opacity=50)

    if app.gameOver:
        image = 'EndScreen.PNG'
        width, height = getImageSize(image)
        drawRect(0, 0, app.width, app.height, fill='black')
        drawImage(image, app.width//2, app.height//2 - 7, width=width*1, 
                  height=height*1,align='center')
        drawLabel(app.endMessage, app.width//2+400, app.height//2-300,
                  size = 30, fill='white')
    
def game_onKeyPress(app, key):
    char = app.char
    # check if character is close to border
    if not (50 <= char.x):
        app.terrain.scroll('left')
        for alpaca in app.alpacas:
            alpaca.scroll('left')
        char.isAtLeftBorder = True
    else:
        char.isAtLeftBorder = False
    if not (char.x <= app.width-50):
        app.terrain.scroll('right')
        for alpaca in app.alpacas:
            alpaca.scroll('right')
        char.isAtRightBorder = True
    else:
        char.isAtRightBorder = False

    if key == 'up' and not char.isJumping and not char.atTopCaveBorder:
        char.y -= 10
    if key == 'down' and not char.isJumping and not char.atBottomCaveBorder:
        char.y += 10
    # if char is at border, don't move
    if not char.isAtRightBorder and not char.atRightCaveBorder:
        if key == 'right':
            char.x += 10
            char.facing = 'right' 
    if not char.isAtLeftBorder and not char.atRightCaveBorder:
        if key == 'left': 
            char.x -= 10
            char.facing = 'left'

    # jump
    if key == 'space' and not app.gameOver:
        char.isJumping = True
        char.lastJumpY = char.y

    if key == 'space' and app.gameOver:
        newGame(app)
        
    if key == 'tab':
        newGame(app)
    
    if key == 'b':
        app.drawBorder = not app.drawBorder

    if key == 'z':
        app.zoom = not app.zoom
        char.centered = not char.centered
        if app.zoom == True:
            app.zoomWidth = app.width // 3
            app.zoomHeight = app.height // 3
            char.lastX = char.x
            char.lastY = char.y
            zoomIn(app)
        if app.zoom == False:
            zoomOut(app)

def zoomIn(app):
    zoomCX = app.char.x
    zoomCY = app.char.y
    app.char.onZoomIn(app.width, app.height)
    app.terrain.onZoomIn(app.zoomWidth, app.zoomHeight, zoomCX, zoomCY)

def zoomOut(app):
    app.char.onZoomOut()

def game_onKeyHold(app, keys):
    char = app.char
    char.updateOnKeyHold(keys)

    # check if character is close to border
    if not (50 <= char.x):
        app.terrain.scroll('left')
        for alpaca in app.alpacas:
            alpaca.scroll('left')
        char.isAtLeftBorder = True
    else:
        char.isAtLeftBorder = False
    if not (char.x <= app.width-50):
        app.terrain.scroll('right')
        for alpaca in app.alpacas:
            alpaca.scroll('right')
        char.isAtRightBorder = True
    else:
        char.isAtRightBorder = False

def game_onKeyRelease(app, key):
    char = app.char
    char.isWalking = False
    if key in ['left', 'right', 'up', 'down', 'rightUp', 'leftUp', 'leftDown',
               'rightDown']:
        char.dirMoving = None

def game_onStep(app):
    char = app.char
    app.paca = False
    app.steps += 1
    app.stepsPerSecond = 20

    # player moves if key is held
    char.moveOnKeyHold()

    # alpacas spit if near and facing player
    projectiles = app.terrain.projectiles
    for alpaca in app.alpacas:
        if alpaca.isFacingPlayer(app.char, app.zoom) and not char.maskPowerUp:
            direction = alpaca.facing
            projectiles.append(Projectile(alpaca.x, alpaca.y-10, 
                                                direction, alpaca.color))
    for projectile in projectiles:
        projectile.fire()

    # check for collision every 0.5 seconds, skip if have shield powerup
    if app.steps % 10 == 0 and not char.shieldPowerUp:
        for projectile in projectiles:
            if projectile.isCollision(char, app.zoom):
                char.health -= 1

    # create new alpaca (not in wall)
    if app.steps % 30 == 0:
        if len(app.alpacas) <= 9:
            (x, y) = generatePaca(app)
            app.alpacas.append(Alpaca(x, y, 'ground'))
            app.paca = True
        # have alpacas spawn in large enough distinct caves
        cave = random.choice(app.separateCaves)
        if len(cave) >= 20 and len(app.alpacas) <= 7:
            (x, y) = random.choice(cave)
            app.alpacas.append(Alpaca(x*20, y*20+300, 'cave'))
            app.paca = True
                
    # have food spawn in large enough distinct caves
    cave = random.choice(app.separateCaves)
    if len(cave) >= 20 and len(app.terrain.food) <= 7:
        (x, y) = random.choice(cave)
        app.terrain.food.append(Food(x*20, y*20+300))

    # generate alpacaMask occasionally in caves
    if app.steps % 100 == 0:
        app.terrain.generatePacaMask(app.separateCaves)

    # generate shield occasionally in caves
    if app.steps % 150 == 0:
        app.terrain.generateShield(app.separateCaves)

    # alpaca movement
    for alpaca in app.alpacas:
        alpaca.move(app.steps, app.walls)
    
    if app.steps % 1200 <= 600:
        # move sun
        app.terrain.time = 'day'
        app.sun.moveSun(app.steps)
    else:
        # move moon
        app.terrain.time = 'night'
        app.moon.moveMoon(app.steps)

    # update days survived
    if app.steps % 600 == 0:
        app.char.daysSurvived += 1

    # jumping
    if char.isJumping == True:
        if app.steps % 8 == 0:
            char.jumpImageIndex += 1
            char.jumpImageIndex %= len(char.jumpImages)
        char.jumpIndex += 1
        char.jump(char.jumpIndex)

    # walking
    if char.isWalking:
        char.walkIndex += 1
        char.walkIndex %= len(char.walkImages)

    for alpaca in app.alpacas:
        if app.steps % 10 == 0:
            alpaca.walkIndex += 1
            alpaca.walkIndex %= len(alpaca.walkImages)

    # check if player jumps on alpaca
    for alpaca in app.alpacas:
        x = char.x - (char.lastX - alpaca.x)*3 if app.zoom else alpaca.x
        y = char.y - (char.lastY - alpaca.y)*3 if app.zoom else alpaca.y
        xMargin = 10*3 if app.zoom else 10
        if ((char.x-xMargin <= x <= char.x+xMargin) and 
            ((char.y+char.charHeight//2)-xMargin <= y <= (char.y+char.charHeight//2)+xMargin) and
            not char.wingPowerUp):
            char.alpacaRiding = alpaca
            alpaca.playerOnBack = True
            char.ridingTimer = 200
        alpaca.moveWithPlayer(char, app.zoom)

    # after 10 seconds, character gets off of alpaca
    if char.ridingTimer > 0:
        char.ridingTimer -= 2
    if char.ridingTimer == 0 and char.alpacaRiding != None:
        char.alpacaRiding.playerOnBack = False
        char.alpacaRiding = None

    # check if player bumps into alpaca
    for alpaca in app.alpacas:
        if ((char.x-10 <= alpaca.x <= char.x+10) and 
            ((char.y+char.charHeight//2)-10 <= alpaca.y <= (char.y+char.charHeight//2)+10) and
            char.facing != alpaca.facing):
            char.health -= 1
    
    # end game if health is 0
    if char.health <= 0:
        app.gameOver = True
        app.endMessage = "The pacas got to you D:"

    # check if char got wing powerup
    for wing in app.terrain.wings:
        if ((wing.x-10 <= char.x <= wing.x+10) and 
            (wing.y-30 <= char.y <= wing.y+30)) and not char.alpacaRiding:
            char.wingPowerUp = wing
            wing.onPlayer = True
            if char.wingTimer == 0:
                char.wingTimer = 100
    
    # follow player if have wing power up
    if char.wingPowerUp:
        for wing in app.terrain.wings:
            if wing.onPlayer:
                wing.followPlayer(char)
        char.isWalking = False
        char.lastJumpY = char.y
        char.dFromGround = 20

    # lose wing power up after 10 seconds
    if char.wingTimer > 0:
        char.wingTimer -= 1
    if char.wingTimer == 0 and char.wingPowerUp != None:
        char.wingPowerUp.onPlayer = False
        app.terrain.wings.remove(char.wingPowerUp)
        char.wingPowerUp = None

    # check if player gets alpaca mask
    for mask in app.terrain.pacaMasks:
        x = char.x - (char.lastX - mask.x) if app.zoom else mask.x
        y = char.y - (char.lastY - mask.y) if app.zoom else mask.y
        xRange = 10*3 if app.zoom else 10
        yRange = 30*3 if app.zoom else 30
        if ((x-xRange <= char.x <= x+xRange) and 
            (y-yRange <= char.y <= y+yRange)) and not char.alpacaRiding:
            char.maskPowerUp = mask
            mask.onPlayer = True
            if char.maskTimer == 0:
                char.maskTimer = 100

    # move mask with player
    for mask in app.terrain.pacaMasks:
        if mask.onPlayer == True:
            mask.followPlayer(char, app.zoom)

    # lose mask power up after 10 seconds
    if char.maskTimer > 0:
        char.maskTimer -= 1
    if char.maskTimer == 0 and char.maskPowerUp != None:
        char.maskPowerUp.onPlayer = False
        app.terrain.pacaMasks.remove(char.maskPowerUp)
        char.maskPowerUp = None

    # check if character got shield
    for shield in app.terrain.shields:
        x = char.x - (char.lastX - shield.x) if app.zoom else shield.x
        y = char.y - (char.lastY - shield.y) if app.zoom else shield.y
        xRange = 10*3 if app.zoom else 10
        yRange = 30*3 if app.zoom else 30
        if (((x-xRange <= char.x <= x+xRange) and 
            (y-yRange <= char.y <= y+yRange)) and not char.alpacaRiding and
            not char.maskPowerUp):
            char.shieldPowerUp = shield
            shield.onPlayer = True
            if char.shieldTimer == 0:
                char.shieldTimer = 100

    # shield around player if get shield power up
    if char.shieldPowerUp:
        for shield in app.terrain.shields:
            shield.shieldAroundPlayer(char)

    # update sparkle index
    if app.steps % 2 == 0:
        for shield in app.terrain.shields:
            shield.sparkleIndex += 1
            shield.sparkleIndex %= len(shield.sparkleImages)
    
    # lose shield power up after 10 seconds
    if char.shieldTimer > 0:
        char.shieldTimer -= 1
    if char.shieldTimer == 0 and char.shieldPowerUp != None:
        char.shieldPowerUp.onPlayer = False
        app.terrain.shields.remove(char.shieldPowerUp)
        char.shieldPowerUp = None

    # check if character is at wall if in cave
    if char.y >= 280:
        char.isAtCaveBorder(app.caveBorders, app.tunnels, app.zoom)
    else:
        char.atLeftCaveBorder = False
        char.atRightCaveBorder = False
        char.atTopCaveBorder = False
        char.atBottomCaveBorder = False
        char.atCaveStart = False

    # decrease hunger every 10 seconds
    if app.steps % 100 == 0:
        char.hunger -= 1

    # die if hunger depletes
    if char.hunger == 0:
        app.gameOver = True
        app.endMessage = "You forgot to nom :("

    # check if player gets food
    for food in app.terrain.food:
        x = char.x - (char.lastX-food.x)*3 if app.zoom else food.x
        y = char.y - (char.lastY-food.y)*3 if app.zoom else food.y
        xRange = 10*3 if app.zoom else 10
        yRange = 30*3 if app.zoom else 30
        if ((x-xRange <= char.x <= x+xRange) and 
            (y-yRange <= char.y <= y+yRange)):
            app.terrain.food.remove(food)
            app.terrain.generateFood(app.width, app.height)
            if char.hunger < 5:
                char.hunger += 1

    # alpacas attack player at night if close enough
    if app.terrain.time == 'day':
        for alpaca in app.alpacas:
            if ((not alpaca.followingPlayer) and alpaca.followCoolDown == 0 and
                    distance(alpaca.x, alpaca.y, char.x, char.y) < 125):
                alpaca.findShortestPath(char, app.width, app.height)
                alpaca.followingPlayer = True
                # input()

    # alpacas chase player
    for alpaca in app.alpacas:
        alpaca.decreaseFollowCoolDown()
        if alpaca.followingPlayer:
            # stop folliwng if no more nodes
            # if alpaca.shortestPath[0] == []:
            #     alpaca.followingPlayer = False
            alpaca.chasePlayer(char)

def generatePaca(app):
    x = random.randint(0, app.width)
    y = random.randint(150, 300)
    return (x,y)

def distance(x0, y0, x1, y1):
    return ((x1-x0)**2 + (y1-y0)**2)**0.5

def main():
    runAppWithScreens(initialScreen='welcome')

main()
