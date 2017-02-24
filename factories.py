"""
A collection of factory objects
"""
from cells import Ground
import random


class NextItemFactory:
    """
    A factory that generates items to be placed on field. It knows about the
    field state to generate placeable objects
    """
    def __init__(self, cell_field):
        self.cell_field = cell_field


    def create_item(self):
        return Ground(ground_type=random.choice(('water', 'living')))