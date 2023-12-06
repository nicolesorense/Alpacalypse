from cmu_graphics import *
import random
from PIL import Image
import os, pathlib
import copy
import tkinter as tk
from tkinter import font
import math

# all images drawn on ipad using ibisPaint

# create player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lastY = None
        self.health = 5
        self.hunger = 5
        self.items = []
        self.isMoving = False
        self.isAtLeftBorder = False
        self.isAtRightBorder = False
        self.daysSurvived = 0
        self.facing = 'right'
        # key hold
        self.dirMoving = None

        # walking
        self.isWalking = False
        self.walkImages = []
        self.walkFlippedImages = []
        self.walkIndex = 0
        numImages = 8
        for i in range(numImages):
            filename = f'walk{i}.png'
            imPIL = Image.open(filename)
            imCMU = CMUImage(imPIL)
            imFlipped = imPIL.transpose(Image.FLIP_LEFT_RIGHT)
            imFlippedCMU = CMUImage(imFlipped)
            self.walkImages.append(imCMU)
            self.walkFlippedImages.append(imFlippedCMU)

        # jumping
        self.jumpIndex = 0
        self.isJumping = False
        self.jumpImages = []
        self.jumpFlippedImages = []
        self.jumpImageIndex = 0
        numImages = 5
        for i in range (1, numImages):
            filename = f'jump{i}.png'
            imPIL = Image.open(filename)
            imCMU = CMUImage(imPIL)
            imFlipped = imPIL.transpose(Image.FLIP_LEFT_RIGHT)
            imFlippedCMU = CMUImage(imFlipped)
            self.jumpImages.append(imCMU)
            self.jumpFlippedImages.append(imFlippedCMU)

        # images
        # used https://www9.lunapic.com/editor/ to make background transparent
        self.character = 'MainCharacter.png'
        self.characterFlipped = 'MainCharacterFlipped.png'
        charWidth, charHeight = getImageSize(self.character)
        self.charWidth = charWidth*(2/3)
        self.charHeight = charHeight*(2/3)
        self.charFlippedWidth, self.charFlippedHeight = getImageSize(self.characterFlipped)
    
        # when riding alpaca
        self.alpacaRiding = None
        self.ridingTimer = 0
        image = Image.open('playerRiding.png')
        self.ridingIm = CMUImage(image)
        imFlipped = image.transpose(Image.FLIP_LEFT_RIGHT)
        self.ridingImFlipped = CMUImage(imFlipped)

        # power ups
        self.wingPowerUp = None
        self.dFromGround = 0
        self.wingTimer = 0
        self.maskPowerUp = None
        self.maskTimer = 0


        # so don't walk through walls
        self.atWall = False
        self.atCaveBorder = False

    def drawHealth(self):
        fullHeart = 'fullHeart.png'
        emptyHeart = 'emptyHeart.png'
        for i in range (self.health):
            drawImage(fullHeart, 1320+20*i, 5, width=20, height=20)

    def drawHunger(self):
        apple = 'apple.PNG'
        for i in range(self.hunger):
            drawImage(apple, 1310+22*i, 750, width=25, height=25)

    def jump(self, index):
        gravity = 0.3
        velocity = 8
        if index <= 6:
            self.y -= velocity + index*gravity
        elif index < 12:
            self.y += velocity + index*(gravity)
        else:
            self.jumpIndex = 0
            self.isJumping = False

    def isAtCaveBorder(self, borders, tunnels):
        for border in borders:
            borderX = border[0]*20
            borderY = border[1]*20 + 300
            if (((not self.isInTunnel(tunnels)) and ((borderX <= self.x <= borderX+10) and 
                (borderY <= self.y <= borderY+10)))
                or (not self.isInTunnel(tunnels) and (290 <= self.y <= 320))):
                self.atCaveBorder = True
                return
        self.atCaveBorder = False

    def isInTunnel(self, tunnels):
        for tunnel in tunnels:
            x = tunnel[0]*20
            y = 310 # grass end
            if x < self.x < x+30 and y < self.y < y+400:
                return True
            
    def drawChar(self):
        # draw character facing direction of last key press
        if not self.isJumping and not self.isWalking:
            if self.facing == 'right' and not self.alpacaRiding:
                drawImage(self.character, self.x, self.y, align='center',
                        width=self.charWidth//2, height=self.charHeight//2)
            elif not self.alpacaRiding:
                drawImage(self.characterFlipped, self.x, self.y, align='center',
                        width=self.charWidth//2, height=self.charHeight//2)
            elif self.facing == 'right' and self.alpacaRiding:
                drawImage(self.ridingIm, self.x, self.y+10, align='center',
                        width=self.charWidth//2+5, height=self.charHeight//2)
            else:
                drawImage(self.ridingImFlipped, self.x, self.y+10, align='center',
                        width=self.charWidth//2+5, height=self.charHeight//2)

    def drawJumping(self):
        if self.isJumping == True:
            if self.dirMoving in ['right', 'rightUp', 'rightDown', None, 'up']:
                image = self.jumpImages[self.jumpImageIndex]
                drawImage(image, self.x, self.y, width=self.charWidth//2,
                        height=self.charHeight//2, align='center')
                # draw cast shadow
                if not self.wingPowerUp:
                    drawOval(self.x, self.lastY+(self.charHeight//4), 
                            20 - (self.jumpImageIndex % 2)*3, 6,
                            opacity=(100-(self.jumpImageIndex % 2)*20))
            if self.dirMoving in ['left', 'leftUp', 'leftDown', 'down']:
                image = self.jumpFlippedImages[self.jumpImageIndex]
                drawImage(image, self.x, self.y, width=self.charWidth//2,
                        height=self.charHeight//2, align='center')
                # draw cast shadow
                if not self.wingPowerUp:
                    drawOval(self.x, self.lastY+(self.charHeight//4), 
                            20 - (self.jumpImageIndex % 2)*3, 6,
                            opacity=(100-(self.jumpImageIndex % 2)*20))
                    
    def drawWalking(self):
        if (self.isWalking == True and not (self.isJumping or self.alpacaRiding)):
            if self.dirMoving in ['right', 'rightUp', 'rightDown']:
                image = self.walkImages[self.walkIndex]
                imageWidth, imageHeight = getImageSize(image)
                imageWidth = imageWidth*(2/3)
                imageHeight = imageHeight*(2/3)
                drawImage(image, self.x, self.y, width=imageWidth//2,
                        height=imageHeight//2, align='center')
            if (self.dirMoving in ['left', 'leftUp', 'leftDown']):
                image = self.walkFlippedImages[self.walkIndex]
                imageWidth, imageHeight = getImageSize(image)
                imageWidth = imageWidth*(2/3)
                imageHeight = imageHeight*(2/3)
                drawImage(image, self.x, self.y, width=imageWidth//2,
                        height=imageHeight//2, align='center')
        elif (self.isWalking == True and not (self.isJumping)):
            if self.dirMoving in ['right', 'rightUp', 'rightDown']:
                drawImage(self.ridingIm, self.x, self.y+10, align='center',
                        width=self.charWidth//2+5, height=self.charHeight//2)
            elif self.dirMoving in ['left', 'leftUp', 'leftDown']:
                drawImage(self.ridingImFlipped, self.x, self.y+10, align='center',
                        width=self.charWidth//2+5, height=self.charHeight//2)
                
    def updateOnKeyHold(self, keys):
        if 'right' in keys:
            self.dirMoving = 'right'
            self.isWalking = True
        if 'down' in keys:
            self.dirMoving = 'down'
        if 'left' in keys:
            self.dirMoving = 'left'
            self.isWalking = True
        if 'up' in keys:
            self.dirMoving = 'up'
        if (('right' in keys) and ('up' in keys)):
            self.dirMoving = 'rightUp'
            self.isWalking = True
        if (('right' in keys) and ('down' in keys)):
            self.dirMoving = 'rightDown'
            self.isWalking = True
        if (('left' in keys) and ('down' in keys)):
            self.dirMoving = 'leftDown'
            self.isWalking = True
        if (('left' in keys) and ('up' in keys)):
            self.dirMoving = 'leftUp'
            self.isWalking = True

    def moveOnKeyHold(self):
        if ((self.dirMoving == 'right') and (not self.isAtRightBorder) and 
        not (self.atCaveBorder)):
            self.x += 10
        if ((self.dirMoving == 'left') and (not self.isAtLeftBorder) and 
            not (self.atCaveBorder)):
            self.x -= 10
        if ((self.dirMoving == 'up' or 
            (self.dirMoving == 'rightUp' and (self.isAtRightBorder)) or
            ((self.dirMoving == 'leftUp') and (self.isAtLeftBorder))) and
            not self.isJumping and not (self.atCaveBorder)):
            self.y -= 10
        if ((self.dirMoving == 'down' and not (self.atCaveBorder)) or 
            ((self.dirMoving == 'leftDown') and (self.isAtLeftBorder)) or
            ((self.dirMoving == 'rightDown') and (self.isAtRightBorder)) and 
            (not self.isJumping) and not (self.atCaveBorder)):
            self.y += 10
        if ((self.dirMoving == 'rightUp') and (not self.isAtRightBorder) and 
            not (self.atCaveBorder)):
            if self.isJumping:
                self.x += 10
            else:
                self.x += 10
                self.y -= 10
        if ((self.dirMoving == 'leftUp') and (not self.isAtLeftBorder) and 
            not (self.atCaveBorder)):
            if self.isJumping:
                self.x -= 10
            else:
                self.x -= 10
                self.y -= 10
        if ((self.dirMoving == 'leftDown') and (not self.isAtLeftBorder) and 
            not (self.atCaveBorder)):
            if self.isJumping:
                self.x -= 10
            else:
                self.x -= 10
                self.y += 10
        if ((self.dirMoving == 'rightDown') and (not self.isAtRightBorder) and 
            not (self.atCaveBorder)):
            if self.isJumping:
                self.x += 10
            else:
                self.x += 10
                self.y += 10