import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, ObjectProperty, AliasProperty
from kivy.clock import Clock

#Game engine
from cells import Cell, CellField
from factories import NextItemFactory


class CityGame(Widget):
    #  An item to be attached
    next_item = ObjectProperty(None)
    #  A field backend
    cell_field = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CityGame, self).__init__(**kwargs)
        self.cell_field = CellField(field_size=10)
        self.next_item_factory = NextItemFactory(self.cell_field)
        Clock.schedule_once(self.init_game)

    def init_game(self, stuff):
        self.ids['field'].populate_field()
        self.bind(next_item=self.ids['next_item_box'].update_next_item)
        self.start_turn()

    def start_turn(self):
        self.next_item = self.next_item_factory.create_item()


class PlayingField(GridLayout):

    def __init__(self, field_size=10, **kwargs):
        super(PlayingField, self).__init__(**kwargs)
        self.field_size = field_size

    def populate_field(self):
        for x in range(self.field_size*self.field_size):
            c = Cell()
            App.get_running_app().root.cell_field.append(c)
            self.add_widget(FieldCell(c))


class FieldCell(Widget):
    """
    A widget that displays a single field cell.
    Draws ground and bonuses (if any).
    """
    cell = ObjectProperty()

    def __init__(self, cell, **kwargs):
        self.cell = cell
        super(FieldCell, self).__init__(**kwargs)


class GrabbableCell(FieldCell):
    """
    A cell subclass that can be dragged around
    """

    def on_touch_down(self, touch):
        if self.x < touch.x < self.x+self.width and\
                self.y < touch.y < self.y+self.height:
            touch.grab(self)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center = touch.x, touch.y

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)


class ItemMakerWidget(GridLayout):
    """
    A window where the new item is spawned
    """

    def __init__(self, **kwargs):
        super(ItemMakerWidget, self).__init__(**kwargs)

    def update_next_item(self, stuff, more_stuff):
        """
        Accept a generated item
        :param item:
        :return:
        """
        self.add_widget(GrabbableCell(Cell(App.get_running_app().root.next_item)))


class RightBlock(BoxLayout):
    pass


class StackCityApp(App):

    def __init__(self, **kwargs):
        super(StackCityApp, self).__init__(**kwargs)

if __name__ == '__main__':
    StackCityApp().run()
