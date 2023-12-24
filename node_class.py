class Node:
   def __init__(self, position=None, parent=None):
       self.position = position
       self.f = 0
       self.g = 0
       self.h = 0
       self.parent = parent


   def closeTo(self, other):
       if isinstance(other, Node):
           return ((self.position[0]-10 <= other.position[0] <= self.position[0]+10) 
                   and (self.position[1]-10 <= other.position[1] <= self.position[1]+10))