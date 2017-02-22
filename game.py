import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, ObjectProperty

#Game engine
from cells import Cell, CellField


class CityGame(Widget):
    def __init__(self, **kwargs):
        super(CityGame, self).__init__(**kwargs)


class PlayingField(GridLayout):
    cell_field = ObjectProperty(CellField(10))

    def __init__(self, field_size=10, **kwargs):
        super(PlayingField, self).__init__(**kwargs)
        self.field_size = field_size
        for x in range(self.field_size*self.field_size):
            c = Cell()
            self.cell_field.append(c)
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


class RightBlock(BoxLayout):
    pass


class StackCityApp(App):
    pass

if __name__ == '__main__':
    StackCityApp().run()