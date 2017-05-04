#! /usr/bin/python3

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty, DictProperty,\
    StringProperty
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

# Game engine
from cells import Cell, CellField, Building
from city import CityState, resources as resource_reference
from factories import NextItemFactory
from misc import shape_copy, name_ground_list


class CityGame(Widget):
    #  An item to be attached
    next_item = ObjectProperty(None)
    #  A field backend
    cell_field = ObjectProperty(None)
    #  Resources view
    resources = DictProperty(None)
    #  buildings list
    buildings = ListProperty(None)

    def __init__(self, **kwargs):
        super(CityGame, self).__init__(**kwargs)
        self.cell_field = CellField(field_size=18)
        self.cell_field.connect_citystate(CityState())
        self.resources = self.cell_field.city_state.resources
        self.next_item_factory = NextItemFactory(self.cell_field)
        Clock.schedule_once(self.init_game)

    def init_game(self, stuff):
        self.ids['field'].populate_field()
        self.bind(next_item=self.ids['next_item_box'].update_next_item)
        self.bind(resources=self.ids['resource_box'].update_resources)
        self.start_turn()

    def start_turn(self):
        self.next_item = self.next_item_factory.create_item()
        #  Updating next item label
        #  Widgetry gets updated by RightBlock's children
        if isinstance(self.next_item, Building):
            label = str(self.next_item)
        elif isinstance(self.next_item, list):
            # Assuming only ground comes in lists
            label = name_ground_list(self.next_item)
        self.ids['next_item_label'].text = label
        #  Buildings, if any, make turn
        for building in self.buildings:
            building.make_turn()
        #  Making resources available for subwidgets
        self.resources = self.cell_field.city_state.resources


class PlayingField(Widget):
    """
    A grid of cells where the city is built
    """
    def __init__(self, **kwargs):
        super(PlayingField, self).__init__(**kwargs)
        #  A placeholder value. It will be updated in self.populate_field
        self.field_size = 10
        self.cells_grid = GridLayout(pos=self.pos, size=self.size,
                                     cols=self.field_size, rows=self.field_size)
        self.add_widget(self.cells_grid)
        self.buildings_layer = FloatLayout(size=self.size, pos=self.pos)
        self.add_widget(self.buildings_layer)
        self.bind(size=self.update_subwidgets)
        self.bind(pos=self.update_subwidgets)

    def update_subwidgets(self, stuff, stuff2):
        self.cells_grid.pos = self.pos
        self.cells_grid.size = self.size
        self.buildings_layer.pos = self.pos
        self.buildings_layer.size = self.size

    def populate_field(self):
        """
        Fill the game field with empty terrain
        :return:
        """
        self.field_size = App.get_running_app().root.cell_field.field_size
        self.cells_grid.cols = self.field_size
        self.cells_grid.rows = self.field_size
        for x in range(self.field_size*self.field_size):
            c = Cell()
            App.get_running_app().root.cell_field.append(c)
            self.cells_grid.add_widget(FieldCell(c))

    def get_cell_by_pos(self, pos):
        """
        Return cell that is on a given position (if any). Return None otherwise.
        :param pos:
        :return:
        """
        if self.collide_point(*pos):
            for widget in self.cells_grid.children:
                if isinstance(widget, FieldCell)and widget.collide_point(*pos):
                        return widget
        return None

    def get_cell_widget(self, number):
        """
        Get cell widget with a given ID. Return None if there is no such cell.
        :param number:
        :return:
        """
        for widget in self.cells_grid.children:
            if isinstance(widget, FieldCell) and widget.cell.number == number:
                return widget
        return None

    def get_cell_widgets(self, numbers):
        """
        Yield cell widgets whose IDs are in `numbers`
        :param numbers:
        :return:
        """
        for widget in self.cells_grid.children:
            if isinstance(widget, FieldCell) and widget.cell.number in numbers:
                yield widget

    def add_building(self, building, number):
        """
        Add a building widget to cell #number
        :param building:
        :param number:
        :return:
        """
        building_widget = BuildingWidget(building,
                                 pos=self.get_cell_widget(number).pos)
        self.buildings_layer.add_widget(building_widget)


class FieldCell(Widget):
    """
    A widget that displays a single field cell.
    Draws ground and bonuses (if any). Is also responsible for checking item
    acceptance.
    """
    cell = ObjectProperty()
    cell_text = StringProperty('')
    images = {'military': 'atlas://grounds/military',
              'living': 'atlas://grounds/living',
              'infrastructure': 'atlas://grounds/infrastructure',
              'water': 'atlas://grounds/water',
              'empty': 'atlas://grounds/empty'}

    def __init__(self, cell, **kwargs):
        self.cell = cell
        super(FieldCell, self).__init__(**kwargs)
        self.update_widget()
        self.tooltip = None
        self.updating = False # See FieldCell.update_widget

    def accept_item(self, item):
        # item = App.get_running_app().root.next_item
        self.cell.add_item(item)
        self.update_widget()
        # Grounds get added to self, while Buildings have to be passed to
        # PlayingField
        if isinstance(item, Building):
            self.cell.building = item
            App.get_running_app().root.buildings.append(item)
            App.get_running_app().root.ids['field'].\
                add_building(item, self.cell.number)
        return True

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.create_tooltip()

    def create_tooltip(self):
        print('Tooltip created')
        self.tooltip = Label(text='{0} on {1} ground'.format(self.cell.building,
                                                 self.cell.ground.ground_type),
                             x=self.x, y=self.y-20, color=(1, 0, 0, 1))
        self.parent.parent.add_widget(self.tooltip)
        Clock.schedule_once(self.remove_tooltip, 1.2)

    def remove_tooltip(self, dt):
        self.parent.parent.remove_widget(self.tooltip)

    def update_widget(self):
        #  This boolean prevents this method being called when another instance
        #  of it is running already, thus avoiding infinite recursion caused by
        #  updating neighbours
        self.updating = True
        #  Later here will be some complex canvas magic
        #  Changing source on the fly has the unnecessary overhead due to disk IO (?)
        source = 'atlas://grounds/{0}'.format(self.cell.ground.ground_type)
        if self.cell.number:
            #  Neighborhood only checked for the tiles placed on map
            if self.cell.ground.ground_type == 'water':
                #  Currently only waterfronts are supported
                source += self.get_neighbour_postfix()
                for neighbour in App.get_running_app().root.ids['field'].get_cell_widgets(
                    App.get_running_app().root.cell_field.get_neighbours(self.cell.number)):
                    if not neighbour.updating:
                        neighbour.update_widget()
        # Source can be either newly created or changed by neighbours
        if source != self.ids['cell_image'].source:
            self.ids['cell_image'].source = source
        self.updating = False

    def get_neighbour_postfix(self):
        """
        Get a postfix for tile ID based on neighbours
        This method is a sort of placeholder: no more than 2 borders per cell are
        supported. This is mostly due to there being no 3-walled or 4-walled
        tiles and is to be fixed sometime later. In addition, border choice is
        dependent on position of neighbours: upper takes precedence over lower
        and left -- over right. This, too, is to be fixed when I have more tiles
        :param cell_field:
        :param neighbours:
        :return:
        """
        # Take references purely for code readability
        cell_field = App.get_running_app().root.cell_field
        own_ground = self.cell.ground.ground_type
        neighbours = cell_field.get_neighbours(self.cell.number)
        if neighbours[1] and cell_field[neighbours[1]].ground.ground_type not in ('empty', own_ground):
            if neighbours[3] and cell_field[neighbours[3]].ground.ground_type == cell_field[neighbours[1]].ground.ground_type:
                return '_{0}_7'.format(cell_field[neighbours[1]].ground.ground_type)
            elif neighbours[4] and cell_field[neighbours[4]].ground.ground_type == cell_field[neighbours[1]].ground.ground_type:
                return '_{0}_9'.format(cell_field[neighbours[1]].ground.ground_type)
            else:
                return '_{0}_8'.format(cell_field[neighbours[1]].ground.ground_type)
        elif neighbours[3] and cell_field[neighbours[3]].ground.ground_type not in ('empty', own_ground):
            if neighbours[6] and cell_field[neighbours[6]].ground.ground_type == cell_field[neighbours[3]].ground.ground_type:
                return '_{0}_1'.format(cell_field[neighbours[3]].ground.ground_type)
            else:
                return '_{0}_4'.format(cell_field[neighbours[3]].ground.ground_type)
        elif neighbours[4] and cell_field[neighbours[4]].ground.ground_type not in ('empty', own_ground):
            if neighbours[6] and cell_field[neighbours[6]].ground.ground_type == cell_field[neighbours[4]].ground.ground_type:
                return '_{0}_3'.format(cell_field[neighbours[4]].ground.ground_type)
            else:
                return '_{0}_6'.format(cell_field[neighbours[4]].ground.ground_type)
        elif neighbours[6] and cell_field[neighbours[6]].ground.ground_type not in ('empty', own_ground):
            return '_{0}_2'.format(cell_field[neighbours[6]].ground.ground_type)
        else:
            return ''


class BuildingWidget(Widget):
    """
    A building widget class. Displays a building
    """
    def __init__(self, building, **kwargs):
        super(BuildingWidget, self).__init__(**kwargs)
        self.building = building
        self.building.widget = self
        self.update_widget()

    def update_widget(self):
        self.ids['building_image'].source = self.building.image_source


#  Classes for stuff that can be dragged from the ItemMakerWidget to the field.
#  These are *not* used for already placed items, they're temporary
# This and Grabbable cell are repeating the same boilerplate, but I couldn't get
# mixin class correctly working to save my life.
#  All Grabbable* classes are expected to start turn in their on_touch_up if the
#  item was accepted.


class GrabbableBuilding(BuildingWidget):
    """
    A building subclass that can be dragged around
    """
    def __init__(self, building, **kwargs):
        super(GrabbableBuilding, self).__init__(building, **kwargs)
        self.starting_pos = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            #  Just `self.starting_pos = self.pos` makes starting_pos a ref
            self.starting_pos = self.pos[0], self.pos[1]
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center = touch.x, touch.y

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            accepted = False
            acceptor = App.get_running_app().root.ids['field'].get_cell_by_pos(touch.pos)
            if acceptor and acceptor.cell.can_accept(self.building):
                self.building.get_placed(cell_field=App.get_running_app().root. \
                                         cell_field, number=acceptor.cell.number)
                acceptor.accept_item(self.building)
                App.get_running_app().root.start_turn()
            if not accepted:
                a = Animation(pos=self.starting_pos, duration=0.3)
                a.start(self)
            touch.ungrab(self)
            return True


class GrabbableGroundGroup(Widget):
    """
    A group of cells that can be dragged around.
    It can be placed like a single cell, but all cells must be accepted!
    """
    def __init__(self, cells, *args, **kwargs):
        super(GrabbableGroundGroup, self).__init__(*args, **kwargs)
        self.starting_pos = None
        self.cells = cells
        #  Calculating offsets and initially placing widgets
        self.cell_widgets = shape_copy(self.cells)
        self.offsets = shape_copy(self.cells)
        y_midpoint = int(len(self.cells)/2)
        for y in range(len(self.cells)):
            # Makes little sense to recalculate it every turn, but whatever
            x_midpoint = int(len(cells[y])/2)
            for x in range(len(cells[y])):
                self.offsets[y][x] = [32*(x-x_midpoint),
                                      32*(y-y_midpoint)]
                if self.cells[y][x]:
                    self.cell_widgets[y][x] = FieldCell(Cell(ground=self.cells[y][x]),
                                center_x=self.center_x + self.offsets[y][x][0],
                                center_y=self.center_y + self.offsets[y][x][1])
                    self.add_widget(self.cell_widgets[y][x])
        self.bind(pos=self.update_cells)
        
    def update_cells(self, *args):
        for y in range(len(self.cells)):
            for x in range(len(self.cells[y])):
                if self.cells[y][x]:
                    self.cell_widgets[y][x].center = [
                        self.center_x + self.offsets[y][x][0],
                        self.center_y + self.offsets[y][x][1]
                    ]
            
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            #  Just `self.starting_pos = self.pos` makes starting_pos a ref
            self.starting_pos = self.pos[0], self.pos[1]
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center = touch.x, touch.y

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            will_accept = True
            for y in range(len(self.cells)):
                for x in range(len(self.cells[y])):
                    if self.cells[y][x]:
                        acceptor = App.get_running_app().root.ids['field'].\
                            get_cell_by_pos((
                                self.center_x + self.offsets[y][x][0],
                                self.center_y + self.offsets[y][x][1]
                                ))
                        # Either released out of field or in incorrect pos
                        if not acceptor or not acceptor.cell.can_accept(self.cells[y][x]):
                            will_accept = False
                            break
            if will_accept:
                for y in range(len(self.cells)):
                    for x in range(len(self.cells[y])):
                        if self.cells[y][x]:
                            acceptor = App.get_running_app().root.ids['field'].\
                                get_cell_by_pos((
                                self.center_x + self.offsets[y][x][0],
                                self.center_y + self.offsets[y][x][1]
                            ))
                            acceptor.accept_item(self.cells[y][x])
                App.get_running_app().root.start_turn()
            else:
                a = Animation(pos=self.starting_pos, duration=0.3)
                a.start(self)
            touch.ungrab(self)
            return True


class ItemMakerWidget(GridLayout):
    """
    A window where the new item is spawned
    """

    def __init__(self, **kwargs):
        super(ItemMakerWidget, self).__init__(**kwargs)
        self.next_item = None

    def update_next_item(self, *args):
        """
        Accept a generated item
        :param item:
        :return:
        """
        if self.next_item:
            self.remove_widget(self.next_item)
        next_item_object = App.get_running_app().root.next_item
        if isinstance(next_item_object, Building):
            self.next_item = GrabbableBuilding(App.get_running_app().root.next_item)
        elif isinstance(next_item_object, list):
            self.next_item = GrabbableGroundGroup(next_item_object)
        self.add_widget(self.next_item)


class ResourceView(BoxLayout):
    """
    A view for a single resource
    """
    def __init__(self, resource_icon='Coins.png', **kwargs):
        super(ResourceView, self).__init__(**kwargs)
        self.ids['resource_icon'].source = resource_icon


class ResourceBox(BoxLayout):
    """
    A box of ResourceViews
    """
    def __init__(self, *args, **kwargs):
        super(ResourceBox, self).__init__(*args, **kwargs)
        self.resource_fields = {}
        for x in resource_reference.keys():
            self.resource_fields[x] = ResourceView(
                resource_icon=resource_reference[x].icon_source)
            self.add_widget(self.resource_fields[x])
            
    def update_resources(self, ins, val):
        for x in val.keys():
            self.resource_fields[x].ids['resource_count'].text = str(val[x])
        
        
class RightBlock(BoxLayout):
    pass


class StackCityApp(App):

    def __init__(self, **kwargs):
        super(StackCityApp, self).__init__(**kwargs)

if __name__ == '__main__':
    StackCityApp().run()
