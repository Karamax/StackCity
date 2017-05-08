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
                self.city_state.resources['workforce'] += 1
                self.growth_counter -= 0
                
    def on_placement(self):
        pass
            
    def __str__(self):
        return "{} ({}/{})".format(
            self.name, self.dwellers, self.max_dwellers
            )
    

class Workshop(Building):
    """
    A base class for workshops. Realizes the workforce logic.
    """
    def __init__(self, workers_required=1, **kwargs):
        super(Workshop, self).__init__(**kwargs)
        self.workers = 0
        self.workers_required = workers_required
    
    def on_placement(self):
        #  A workshop claims as many workers as it needs (or at least as many as
        # it can) right after placement
        if self.city_state.resources['workforce'] >= self.workers_required:
            self.city_state.resources['workforce'] -= self.workers_required
            self.workers = self.workers_required
        elif self.city_state.resources['workforce'] > 0:
            self.workers = self.city_state.resources['workforce']
            self.city_state.resources['workforce'] = 0
            
    def work_efficiency(self):
        """
        Return the efficiency (ie percentage of optimal production) of this
        workshop.
        It can depend on factors such as the amount of workers, neighbouring
        buildings, some city state variables and so on. Unless overridden, it's
        self.workers/self.workers_required
        :return:
        """
        return self.workers/self.workers_required
            
    def __str__(self):
        # Mention if it's understaffed in the name
        if self.workers == self.workers_required:
            return self.name
        elif self.workers > 0:
            return '{} (short of workers)'.format(self.name)
        else:
            return '{} (unmanned)'.format(self.name)

    
class FisherBoat(Workshop):
    """
    A fisher boat.
    Requires a unit of workforce. Produces two food a turn. Placeable on water.
    """
    
    def make_turn(self):
        if self.work_efficiency():
            self.city_state.resources['food'] += 1
    

class Smithery(Workshop):
    """
    A simple workshop.
    Requires two units of workforce. Produces one gold a turn. Placeable on
    an infrastructure ground
    """
    def make_turn(self):
        if self.work_efficiency() == 1:
            self.city_state.resources['gold'] += 1
    
    
    
class Barracks(Building):
    """
    A barrack. Requires two units of workforce, consumes one gold a turn,
    doesn't do shit. Placeable on a military ground.
    """
    def make_turn(self):
        pass
    
    def on_placement(self):
        pass
    
    def __str__(self):
        pass
