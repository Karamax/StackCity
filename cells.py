"""
Classes for various stuff that can be placed on a map
"""


#  This class should go to something like util.py, when I make that file
class StackCityException(Exception):
    """
    An exception raised within StackCity engine
    """
    pass


class Cell:
    """
    A cell backend class.
    This class is an ObjectProperty of FieldCell and contains all the game-relevant
    qualities of the cell. Currently these are ground type and bonus type.
    Since buildings may take multiple cells, it only stores a boolean for a
    building: whether this cell is occupied or not.
    It also stores a cell number which is set when the cell is placed into a
    CellGrid and can later be used to look up its neighbours.
    """
    def __init__(self, ground=None, bonus=None):
        if ground:
            self.ground = ground
        else:
            self.ground = Ground('empty')
        self.bonus = bonus
        self.built = False
        self.number = None
        # A ref to the building, should it be placed on this cell
        self.building = None

    def can_accept(self, item):
        """
        Return True if this item can be added to this cell
        :param item:
        :return:
        """
        # Currently a placeholder
        if self.ground.ground_type in item.acceptable_ground:
            return True
        else:
            return False

    def add_item(self, item):
        """
        Attach an item to this cell
        :param item:
        :return:
        """
        if isinstance(item, Ground):
            self.ground = item
        elif isinstance(item, Building):
            self.building = item
        else:
            raise StackCityException('Incorrect item type added to cell')

    def __str__(self):
        return str(self.ground)


class CellField:
    """
    A grid of cells.
    This class is a list of cells. It supports operations such as addressing any
    cell, adding or removing cells, etc.
    """
    def __init__(self, field_size):
        self.field_size = field_size
        self.cells = [None for x in range(self.field_size*self.field_size)]

    def __getitem__(self, item):
        return self.cells[item]
    
    def connect_citystate(self, state):
        """
        Connect to the CityState object
        :param state:
        :return:
        """
        self.city_state = state

    def append(self, item):
        assert isinstance(item, Cell)
        placed = False
        for x in range(len(self.cells)):
            if not self.cells[x]:
                self.cells[x] = item
                item.number = x
                placed = True
                break
        if not placed:
            raise StackCityException('Adding cell to a field that is full!')

    def get_neighbours(self, number):
        """
        Given cell number, return a list of all its neighbours.
        Cell numbers in the list are ordered as following:
          0 1 2
          3 q 4
          5 6 7
        Where q is query cell and numbers are list indices. There are always 8
        elements in the list. When the neighbouring cell is unavailable (eg due
        to query being a border cell), None is added in its place
        :param number:
        :return:
        """
        r = []
        # if's within list declarations check for going beyond left&right map borders
        # maps check for going beyond upper and lower borders
        upper = [number-self.field_size-1 if number % self.field_size > 0 else None,
                 number-self.field_size,
                 number-self.field_size+1 if number % self.field_size < self.field_size-1 else None]
        #  Check for values outside map
        r += map(lambda x: x if x and x > 0 else None, upper)
        if number % self.field_size > 0:
            r.append(number-1)
        else:
            r.append(None)
        if number % self.field_size < self.field_size-1:
            r.append(number+1)
        else:
            r.append(None)
        lower = [number+self.field_size-1 if number % self.field_size > 0 else None,
                 number+self.field_size,
                 number+self.field_size+1 if number % self.field_size < self.field_size-1 else None]
        r += map(lambda x: x if x and x < self.field_size*self.field_size else None, lower)
        return r


class Placeable:
    """
    Something that can be placed on the field
    """
    def __init__(self, acceptable_ground=('empty', )):
        #  The ground this can be placed on
        self.acceptable_ground = acceptable_ground
        self.cell_field = None
        self.position = None
        
    def get_placed(self, cell_field, number):
        """
        Remember that self was placed on a given map in a given place
        :param cell_field:
        :param position:
        :return:
        """
        self.cell_field = cell_field
        self.number = number


class Ground(Placeable):
    """
    A class for ground type
    """
    ground_types = {'empty', 'water', 'living', 'military', 'infrastructure'}

    def __init__(self, ground_type, **kwargs):
        super(Ground, self).__init__(**kwargs)
        if not ground_type in self.ground_types:
            raise StackCityException('Unknown ground type')
        self.ground_type = ground_type

    # String representation just in case
    def __str__(self):
        return self.ground_type


class Building(Placeable):
    """
    A backend class for the building
    """

    def __init__(self, image_source='House.png',
                 name='BaseBuilding', effect=None, **kwargs):
        super(Building, self).__init__(**kwargs)
        self.name = name
        self.effect = effect
        self.image_source = image_source
        self.widget = None
        
    def make_turn(self):
        """
        Make this building's turn.
        :param cellField:
        :return:
        """
        has_neighbours = False
        for cell in self.cell_field.get_neighbours(self.number):
            if self.cell_field[cell].building and \
                    self.cell_field[cell].building.name == self.name:
                has_neighbours = True
                break
        if has_neighbours:
            print('Building {} at {} makes turn with its neighbour'.\
                  format(self.name, self.number))
            self.cell_field.city_state.resources['gold'] += 3
        else:
            print('Building {} at {} makes turn'.format(self.name, self.number))
            self.cell_field.city_state.resources['gold'] += 2

    def __str__(self):
        return self.name
