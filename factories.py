"""
A collection of factory objects
"""
from misc import make_filled_shape, shape_copy
from cells import Ground, Building
import random


class NextItemFactory:
    """
    A factory that generates items to be placed on field. It knows about the
    field state to generate placeable objects
    """
    
    def __init__(self, cell_field):
        self.cell_field = cell_field
        self.maker_functions = {'ground_block': self.create_ground_block,
                                'house': self.create_house}
        self.possible_items = ('ground_block',
                               'house')
        
    @staticmethod
    def get_shape_list(size):
        """
        Get a list of shapes of a given size.
        This method should be replaced by loading shapes from files when I get
        to loading *anything* from files
        :return:
        """
        if size[0] == 1 or size[1] == 1:
            return [make_filled_shape(size)]
        if size[1] == 2:
            if size[0] == 2:
                return [
                    [[True, False], [False, True]],  # Diagonal
                    [[True, False], [True, True]],  # L-shaped
                    [[True, True], [True, True]]  # A filled square
                ]
            elif size[0] == 3:
                return [
                    [[True, False], [True, False], [True, True]],  # L-shaped
                    [[True, True], [True, False], [True, True]],  # C-shaped
                    [[True, False], [True, True], [True, False]]  # The tetris one
                ]
        elif size[1] == 3:
            if size[0] == 2:
                return [
                    [[True, True, True], [True, False, False]],
                    [[True, True, True], [True, False, True]],
                    [[True, True, True], [False, True, False]]
                ]
            elif size[0] == 3:
                return [
                    [[False, True, False],  # Cross-shaped
                     [True, True, True],
                     [False, True, False]],
                    [[True, True, True],  # Dumbell-shaped
                     [False, True, False],
                     [True, True, True]]
                ]
        
    def shape_ground_block(self, size=(2, 2), ground_type='water'):
        """
        Create a ground block of a given size and type.
        The block is given a random shape from the shapes available in a given size
        :param size:
        :param ground_type:
        :return:
        """
        shape_list = self.get_shape_list(size)
        shape_index = random.randint(0, len(shape_list)-1)
        shape = shape_list[shape_index]
        r = shape_copy(shape)
        for y in range(len(r)):
            for x in range(len(r[y])):
                if shape[y][x]:
                    r[y][x] = Ground(ground_type=ground_type)
        return r

    def create_ground_block(self):
        """
        Create a random rectangular block of ground
        :return:
        """
        xsize = random.randint(1, 3)
        ysize = random.randint(1, 3)
        ground_type = random.choice(('water', 'living',
                                     'military', 'infrastructure'))
        return self.shape_ground_block((ysize, xsize), ground_type)
    
    @staticmethod
    def create_house():
        return Building(image_source='House.png',
                        acceptable_ground=['living', 'empty'])

    def create_item(self):
        # return [[Ground(ground_type='water'), None, Ground(ground_type='water')]]
        next_thing = random.choice(self.possible_items)
        return self.maker_functions[next_thing]()
