from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Line
from kivy.lang import Builder
from multiprocessing import Queue
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from lib import InterfaceManagement


from kivy.properties import ObjectProperty, BooleanProperty

Builder.load_file('lib/paintgame.kv')

class PaintScreen(Screen):
    pass


class PaintGameFSM(object):
    def __init__(self):
        self.internal_events = Queue()
        self.external_events = Queue()
        self.paintgame = PaintGame()

    def next(self):

        if not self.paintgame.colorspanel.color_events.empty():
            ev = self.paintgame.colorspanel.color_events.get()
            self.dispatch_event(ev)

        if not self.paintgame.board.touch_events.empty():
            ev = self.paintgame.board.touch_events.get()
            self.dispatch_event(ev)

        if not self.internal_events.empty():
            ev = self.internal_events.get()
            self.dispatch_event(ev)

    def dispatch_event(self, ev):
        event_type = ev[0]
        givens = ev[1:]

        if event_type == "start_game":
            self.start_game()

        if event_type == "stop_game":
            self.stop_game()

        if event_type == "change_color":
            self.change_color(givens)

        if event_type == "clear_canvas":
            self.clear_canvas()

        if event_type == "draw_pos":
            self.draw_pos(givens)

        if event_type == "cursor_size":
            self.cursor_size(givens)

        if event_type == "cursor_pos":
            self.cursor_pos(givens)

        if event_type == "cursor_off":
            self.cursor_off()

        if event_type == "cursor_on":
            self.cursor_on()

    def cursor_pos(self, gv):
        pos = gv
        event = ("send_data", (b'paint_game', b'cursor_pos', *(pos)))
        self.external_events.put(event)

    def cursor_on(self):
        self.paintgame.board.cursor_select = False

        event = ("send_data", (b'paint_game', b'cursor_on', *(0, 0, 0, 0)))
        self.external_events.put(event)

    def cursor_off(self):
        self.paintgame.board.cursor_select = True
        event = ("send_data", (b'paint_game', b'cursor_off', *(0, 0, 0, 0)))
        self.external_events.put(event)

    def draw_pos(self, gv):
        pos = gv
        event = ("send_data", (b'paint_game', b'draw_pos', *(pos)))
        self.external_events.put(event)

    def clear_canvas(self):
        self.paintgame.board.canvas.clear()
        event = ("send_data", (b'paint_game', b"clear_canvas", *(0, 0, 0, 0)))
        self.external_events.put(event)

    def change_color(self, gv):
        color = gv
        self.paintgame.board.paint_color = tuple(color)
        event = ("send_data", (b'paint_game', b'change_color', *(color)))
        self.external_events.put(event)

    def start_game(self):
        InterfaceManagement.sm.switch_to(PaintScreen(name='paint_screen'))
        InterfaceManagement.sm.get_screen('paint_screen').add_widget(self.paintgame)

    def stop_game(self):
        self.clear_canvas()
        InterfaceManagement.sm.get_screen('paint_screen').remove_widget(self.paintgame)
        InterfaceManagement.sm.clear_widgets()
        event = ("stop_game", "paint_game", "")
        self.external_events.put(event)

    def cursor_size(self, gv):
        cursor_size = gv
        self.paintgame.board.cursor_size = cursor_size
        event = ("send_data", (b'paint_game', b'cursor size', *(cursor_size)))

class ClearButton(Button):
    def __init__(self, **kwargs):
        super(ClearButton, self).__init__(**kwargs)
        self.background_normal = 'data/icons/clear_icon.png'
        self.size_hint = .12, .5

class Back_button(Button):
    def __init__(self, **kwargs):
        super(Back_button, self).__init__(**kwargs)
        self.background_normal = 'data/icons/back_button.png'
        self.size_hint = .12, .5

class PaintGame(BoxLayout):
    def __init__(self, **kwargs):
        super(PaintGame, self).__init__(**kwargs)
        self.board = Board()
        self.add_widget(self.board)
        self.colorspanel = ColorPanel()
        self.add_widget(self.colorspanel)

class ColorPanel(StackLayout):
    sources = ObjectProperty()
    cursor = BooleanProperty()
    def __init__(self, **kwargs):
        self.sources = {'blue': (0, 0, 1, 1),
                        'red': (1, 0, 0, 1), 'green': (0, 1, 0, 1),
                        'yellow': (1, 1, 0, 1), 'magenta': (1, 0, 1, 1),
                        'cyan': (0, 1, 1, 1)}
        super(ColorPanel, self).__init__(**kwargs)
        self.color_events = Queue()
        self.cursor = False
        self.colors = {}


    def init_buttons(self):
        for colors, code in self.sources.items():
            self.colors[colors] = (Button(background_color=code, size_hint=(.15, .5)))


    def add_buttons(self):
        for color in self.colors:
            color_to_change = self.sources[color]
            self.colors[color].bind(on_press=lambda x, color_to_change=color_to_change  : self.change_color(color_to_change))
            self.add_widget(self.colors[color])

        clear_button = ClearButton()
        clear_button.bind(on_press=lambda x: self.clear_board())
        self.add_widget(clear_button)

        back_button = Back_button()
        back_button.bind(on_press=lambda x: self.exit_game())
        self.add_widget(back_button)

    def cursor_state(self):
        if self.cursor == False:
            self.cursor = True
            event = ("cursor_on", "")
            self.color_events.put(event)
        else:
            self.cursor = False
            event = ("cursor_off", "")
            self.color_events.put(event)

    def cursor_off(self):
        event = ("cursor_off", "")
        self.color_events.put(event)

    def exit_game(self):
        event = ("stop_game", "")
        self.color_events.put(event)

    def change_color(self, color):
        color_code = self.sources[color]
        event = ("change_color", *color_code)
        self.color_events.put(event)

    def clear_board(self):
        event = ("clear_canvas", "")
        self.color_events.put(event)

class Board(Widget):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        self.touch_events = Queue()
        self.paint_color = (1, 1, 1, 1)
        self.cursor_select = True

    def on_touch_down(self, touch):
        with self.canvas:
            if touch.y > 50:
                self.canvas.clear()
                self.cursor_position = Line(circle=(touch.x,touch.y, 30, 0, 359), closed=True)
                self.canvas.add(self.cursor_position)

        self.touch_event(touch)

    def on_touch_move(self, touch):
        with self.canvas:
            if touch.y > 50:
                Color(1, 1, 1)
                d = 10.
                self.canvas.clear()
                self.cursor_position = Line(circle=(touch.x,touch.y, d, 0, 359), closed=True)
                self.canvas.add(self.cursor_position)
        self.touch_event(touch)


    def touch_event(self, touch):
        if not self.cursor_select:
            event = ("draw_pos", *touch.pos , 0, 0)
        else:
            event = ("cursor_pos", *touch.pos, 0, 0)
        self.touch_events.put(event)

