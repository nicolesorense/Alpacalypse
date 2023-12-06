class Node:
    def __init__(self, position=None, parent=None):
        self.position = position
        self.f = 0
        self.g = 0
        self.h = 0
        self.parent = parent

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.position == other.position