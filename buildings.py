"""
A collection of buildings.
All classes in this file inherit from cells.Building, overriding only
`make_turn` and `__str__`.
Probably later they will all be replaced by some sort of metaclass(?) magic that
creates them from stored data, but for now it's easier to implement them as
classes than get boggled with writing a proper composition-based system.
"""

from cells import Placeable, Building
    
    
class Dwelling(Building):
    """
    A simple hut.
    It starts empty and produces one dweller (ie a unit of workforce) every ten
    turns. Five, if there is a neighbouring Dwelling. Placeable on living ground
    """
    def __init__(self, max_dwellers=5, *args, **kwargs):
        super(Dwelling, self).__init__(*args, **kwargs)
        # Growth counter set to 10 to return the initial worker upon placement
        self.growth_counter = 10
        self.dwellers = 0
        self.max_dwellers = 5
        
    def make_turn(self):
        if self.dwellers < self.max_dwellers:
            has_neighbours = False
            for cell in self.cell_field.get_neighbours(self.number):
                if self.cell_field[cell].building and \
                        self.cell_field[cell].building.name == self.name:
                    has_neighbours = True
                    break
            if has_neighbours:
                self.growth_counter += 2
            else:
                self.growth_counter += 1
            if self.growth_counter >= 10:
                self.dwellers += 1
                self.cell_field.city_state.resources['workforce'] += 1
                self.growth_counter -= 0
            
    def __str__(self):
        return "{} ({}/{})".format(
            self.name, self.dwellers, self.max_dwellers
            )
    
    
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
