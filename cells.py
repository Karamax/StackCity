class Cell():
    """
    A cell backend class.
    This class is an ObjectProperty of FieldCell and contains all the game-relevant
    qualities of the cell. Currently these are ground type and bonus type.
    Since buildings may take multiple cells, it only stores a boolean for a
    building: whether this cell is occupied or not.
    It also stores a cell number which is set when the cell is placed into a
    CellGrid and can later be used to look up its neighbours.
    """
    def __init__(self, ground='empty', bonus=None, built=False):
        self.ground = ground
        self.bonus = bonus
        self.built = False
        self.number = None
        # A ref to the building, should it be placed on this cell
        self.building = None


class CellField():
    """
    A grid of cells.
    This class is a list of cells. It supports operations such as addressing any
    cell, adding or removing cells, etc.
    """
    def __init__(self, field_size):
        self.cells = [None for x in range(field_size*field_size)]

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


class StackCityException(Exception):
    """
    An exception raised within StackCity engine
    """
    pass