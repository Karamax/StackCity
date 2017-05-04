"""
A collection of buildings.
All classes in this file inherit from cells.Building, overriding only
`make_turn` and `__str__`.
Probably later they will all be replaced by some sort of metaclass(?) magic that
creates them from stored data, but for now it's easier to implement them as
classes than get boggled with writing a proper composition-based system.
"""

from cells import Building

class Dwelling(Building):
    """
    A simple hut.
    It starts empty and produces one dweller (ie a unit of workforce) every ten
    turns. Five, if there is a neighbouring Dwelling. Placeable on living ground
    """
    def make_turn(self):
        pass
    
    def __str__(self):
        pass
    
    
class FisherBoat(Building):
    """
    A fisher boat.
    Requires a unit of workforce. Produces two food a turn. Placeable on water.
    """
    def make_turn(self):
        pass
    
    def __str__(self):
        pass
    
    
class Workshop(Building):
    """
    A simple workshop.
    Requires two units of workforce. Produces one gold a turn. Placeable on
    an infrastructure ground
    """
    def make_turn(self):
        pass
    
    def __str__(self):
        pass
    
    
class Barracks(Building):
    """
    A barrack. Requires two units of workforce, consumes one gold a turn,
    doesn't do shit. Placeable on a military ground.
    """
    def make_turn(self):
        pass
    
    def __str__(self):
        pass
