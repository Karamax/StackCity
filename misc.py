"""
Miscellanous functions and classes that don't really belong anywhere else
Somehow I get the feeling
"""

from itertools import chain
from functools import reduce

def shape_copy(old_list):
    """
    For a nested list, return a None-filled list of the same shape.
    All elements that are neither lists nor tuples are treated as scalars and
    aren't expanded
    >>>shape_copy(['asd', 1])
    >>>[None, None]
    >>>shape_copy([[1,0,1],[2,2,0]])
    >>>[[None, None, None], [None, None, None]]
    >>>shape_copy([[12], 1])
    >>>[[None], None]
    :param list:
    :return:
    """
    r = []
    for x in old_list:
        if isinstance(x, list) or isinstance(x, tuple):
            r.append(shape_copy(x))
        else:
            r.append(None)
    return r


def make_filled_shape(size, value=True):
    """
    Return a list of a given shape, completely filled with the same value.
    Basically an analogue of numpy.zeros, numpy.ones and the kind
    :param size:
    :return:
    """
    return [[value for x in range(size[0])] for y in range(size[1])]
    

def all_equal(iterable):
    """
    Return True if all elements of the iterable are equal
    :param iterable:
    :return:
    """
    running = None
    for x in iterable:
        # Sadly I cannot just pop an element from a generator. But this does not
        # create any issues with None-containing list.
        if not running:
            running = x
        if running and x != running:
            return False
    return True


def name_ground_list(land_list):
    """
    Return a correct name for a nested list of grounds
    :param land_list:
    :return:
    """
    name = None
    for land in chain.from_iterable(land_list):
        if not name and land:
            name = land.ground_type
        if land and name != land.ground_type:
            return 'A chunk of land'
    return name
