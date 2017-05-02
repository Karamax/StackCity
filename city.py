"""
The logic of the city as a whole
"""

from collections import namedtuple

Resource = namedtuple('Resource', 'name icon_source')
resources = {'gold': Resource(name='Gold', icon_source='Coins.png'),
             'food': Resource(name='Food', icon_source='Food.png')}


class CityState:
    """
    An object that remembers the state of the entire city
    """
    
    def __init__(self, name='Irkutsk'):
        self.name = name
        #  How many of each resource is stored
        self.resources = {'gold': 0,
                          'food': 0}
    
    def load_from_file(self):
        """
        A stub. Sometime there will be a system to save and load city
        :return:
        """
        raise NotImplementedError('The saves will work... sometime')
    
    def __str__(self):
        """
        Serialize an entire city to be saved
        :return:
        """
        raise NotImplementedError('The saves will work... sometime')
