import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty


class CityGame(Widget):
    def __init__(self, **kwargs):
        super(CityGame, self).__init__(**kwargs)


class PlayingField(GridLayout):
    cells = ListProperty()

    def __init__(self, field_size=10, **kwargs):
        super(PlayingField, self).__init__(**kwargs)
        self.field_size = field_size
        for x in range(self.field_size*self.field_size):
            c = FieldCell()
            self.cells.append(c)
            self.add_widget(c)


class FieldCell(Widget):
    pass


class StackCityApp(App):
    pass

if __name__ == '__main__':
    StackCityApp().run()