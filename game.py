import kivy
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, ObjectProperty, AliasProperty, StringProperty
from kivy.clock import Clock

#Game engine
from cells import Cell, CellField, Ground, Building
from factories import NextItemFactory


class CityGame(Widget):
    #  An item to be attached
    next_item = ObjectProperty(None)
    #  A field backend
    cell_field = ObjectProperty(None)
    #  buildings list
    buildings = ListProperty(None)

    def __init__(self, **kwargs):
        super(CityGame, self).__init__(**kwargs)
        self.cell_field = CellField(field_size=18)
        self.next_item_factory = NextItemFactory(self.cell_field)
        Clock.schedule_once(self.init_game)

    def init_game(self, stuff):
        self.ids['field'].populate_field()
        self.bind(next_item=self.ids['next_item_box'].update_next_item)
        self.start_turn()

    def start_turn(self):
        self.next_item = self.next_item_factory.create_item()
        self.ids['next_item_label'].text = str(self.next_item)


class PlayingField(GridLayout):
    """
    A grid of cells where the city is built
    """
    def __init__(self, **kwargs):
        super(PlayingField, self).__init__(**kwargs)
        #  A placeholder value. It will be updated in self.populate_field
        self.field_size = 10

    def populate_field(self):
        """
        Fill the game field with empty terrain
        :return:
        """
        self.field_size = App.get_running_app().root.cell_field.field_size
        self.cols = self.field_size
        self.rows = self.field_size
        for x in range(self.field_size*self.field_size):
            c = Cell()
            App.get_running_app().root.cell_field.append(c)
            self.add_widget(FieldCell(c))


    def get_cell_by_pos(self, pos):
        """
        Return cell that is on current position (if any). Return None otherwise
        :param pos:
        :return:
        """
        if self.collide_point(*pos):
            for widget in self.children:
                if isinstance(widget, FieldCell)and widget.collide_point(*pos):
                        return widget
        return None

    def get_cell_widgets(self, numbers):
        """
        Yield cell widgets whose IDs are in `numbers`
        :param numbers:
        :return:
        """
        for widget in self.children:
            if isinstance(widget, FieldCell) and widget.cell.number in numbers:
                yield widget


class FieldCell(Widget):
    """
    A widget that displays a single field cell.
    Draws ground and bonuses (if any).
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

    def accept_item(self):
        item = App.get_running_app().root.next_item
        if self.cell.can_accept(item):
            self.cell.add_item(item)
            self.update_widget()
            if isinstance(item, Building):
                App.get_running_app().root.buildings.append(item)
                self.parent.add_widget(BuildingWidget(item))
            App.get_running_app().root.start_turn()
            return True
        return False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.accept_item()
            # Whether or not it's accepted, touch should not be propagated
            return True

    def update_widget(self):
        #  Later here will be some complex canvas magic
        #  Changing source on the fly has the unnecessary overhead due to disk IO (?)
        source = 'atlas://grounds/{0}'.format(self.cell.ground.ground_type)
        if self.cell.number:
            #  Neighborhood only checked for the tiles placed on map
            if self.cell.ground.ground_type == 'water':
            #  Currently only waterfronts are supported
                source += self.get_neighbour_postfix()
        if source != self.ids['cell_image'].source:
            self.ids['cell_image'].source = source
            for neighbour in App.get_running_app().root.ids['field'].get_cell_widgets(
                App.get_running_app().root.cell_field.get_neighbours(self.cell.number)):
                neighbour.update_widget()

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
        self.update_widget()

    def update_widget(self):
        self.ids['building_image'].source = self.building.image_source


# This and Grabbable cell are repeating the same boilerplate, but I couldn't get
# multiple inheritance working to save my life.
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
            if acceptor:
                accepted = acceptor.accept_item()
            if not accepted:
                a = Animation(pos=self.starting_pos, duration=0.3)
                a.start(self)
            touch.ungrab(self)
            return True


class GrabbableCell(FieldCell):
    """
    A cell subclass that can be dragged around
    """
    def __init__(self, cell, **kwargs):
        super(GrabbableCell, self).__init__(cell, **kwargs)
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
            if acceptor:
                accepted = acceptor.accept_item()
            if not accepted:
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

    def update_next_item(self, stuff, more_stuff):
        """
        Accept a generated item
        :param item:
        :return:
        """
        if self.next_item:
            self.remove_widget(self.next_item)
        if isinstance(App.get_running_app().root.next_item, Ground):
            self.next_item = GrabbableCell(Cell(App.get_running_app().root.next_item))
        elif isinstance(App.get_running_app().root.next_item, Building):
            self.next_item=GrabbableBuilding(App.get_running_app().root.next_item)
        self.add_widget(self.next_item)


class RightBlock(BoxLayout):
    pass


class StackCityApp(App):

    def __init__(self, **kwargs):
        super(StackCityApp, self).__init__(**kwargs)

if __name__ == '__main__':
    StackCityApp().run()
