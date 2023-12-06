from cmu_graphics import *
import random
from PIL import Image
import os, pathlib
import copy
import tkinter as tk
from tkinter import font
import math

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

    def attack(self, target):
        # if player is in front of alpaca and close enough, move towards player
        pass
    
    def drawPaca(self):
        # pink paca
        pinkImPIL = Image.open('pink_alpaca.png')
        pinkPaca = CMUImage(pinkImPIL)
        pinkImFlipped = pinkImPIL.transpose(Image.FLIP_LEFT_RIGHT)
        pinkPacaFlipped = CMUImage(pinkImFlipped)
        width, height = getImageSize(pinkPaca)
        if (self.color == 'pink') and (self.facing == 'right'):
            drawImage(pinkPaca, self.x, self.y,
                      width=width//3, height=height//3, align='center')
        elif (self.color == 'pink') and (self.facing == 'left'):
            drawImage(pinkPacaFlipped, self.x, self.y,
                      width=width//3, height=height//3, align='center')
            
        # blue paca
        blueImPIL = Image.open('blue_alpaca.png')
        bluePaca = CMUImage(blueImPIL)
        blueImFlipped = blueImPIL.transpose(Image.FLIP_LEFT_RIGHT)
        bluePacaFlipped = CMUImage(blueImFlipped)
        if (self.color == 'blue') and (self.facing == 'right'):
            drawImage(bluePaca, self.x, self.y, 
                      width=width//3, height=height//3, align='center')
        elif (self.color == 'blue') and (self.facing == 'left'):
            drawImage(bluePacaFlipped, self.x, self.y, 
                      width=width//3, height=height//3, align='center')
            
        # purple paca
        purpleImPIL = Image.open('purple_alpaca.png')
        purplePaca = CMUImage(purpleImPIL)
        purpleImFlipped = purpleImPIL.transpose(Image.FLIP_LEFT_RIGHT)
        purplePacaFlipped = CMUImage(purpleImFlipped)
        if (self.color == 'purple') and (self.facing == 'right'):
            drawImage(purplePaca, self.x, self.y, 
                      width=width//3, height=height//3, align='center')
        elif (self.color == 'purple') and (self.facing == 'left'):
            drawImage(purplePacaFlipped, self.x, self.y, 
                      width=width//3, height=height//3, align='center')
            
    def isFacingPlayer(self, player):
        if self.facing == 'left' and player.facing == 'right':
            return (self.isNearPlayer(player) and self.x > player.x)
        if self.facing == 'right' and player.facing == 'left':
            return (self.isNearPlayer(player) and self.x < player.x)

    def isNearPlayer(self, player):
        return (distance(self.x, self.y, player.x, player.y) < 70)
    
    def move(self, steps, walls):
        if self.type == 'ground':
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
        elif self.type == 'cave':
            if steps % 80 <= 40:
                self.facing = 'right'
                self.x += 1
            else:
                self.facing = 'left'
                self.x -= 1

    def moveWithPlayer(self, player):
        if self.playerOnBack:
            self.facing = player.facing
            self.x = player.x
            self.y = player.y + 35

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