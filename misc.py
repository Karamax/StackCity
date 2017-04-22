"""
Miscellanous functions and classes
"""

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
    
