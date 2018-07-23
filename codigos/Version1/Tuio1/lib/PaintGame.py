
from multiprocessing import Queue
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from enum import Enum
from lib import InterfaceManagement

class GameState(Enum):
    IDLE = 0
    MAIN = 1
    GAME = 2
    EXIT = 3

class PaintScreen(Screen):
    pass

class PaintGameFSM(object):
    def __init__(self):
        self.current = GameState.IDLE
        self.internal_events = Queue()
        self.paintgame = PaintGame()

    def next(self):
        if not self.current == GameState.EXIT:

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

        if event_type == "draw_pos":
            self.draw_pos(*givens)

        if event_type == "clear_canvas":
            self.clear_canvas()

        if event_type == "change_color":
            self.change_color(givens)

        if event_type == "cursor_pos":
            self.cursor_pos(*givens)

    def start_game(self):
        InterfaceManagement.sm.switch_to(PaintScreen(name='paint_screen'))
        InterfaceManagement.sm.get_screen('paint_screen').add_widget(self.paintgame)

    def stop_game(self):
        self.clear_canvas()
        InterfaceManagement.sm.get_screen('paint_screen').remove_widget(self.paintgame)
        InterfaceManagement.sm.clear_widgets()

    def cursor_pos(self, gv):
        self.paintgame.cursor_pos(gv)

    def draw_pos(self, gv):
        self.paintgame.draw_line(gv)

    def clear_canvas(self):
        self.paintgame.canvas.clear()

    def change_color(self, gv):
        color = gv[0]
        self.paintgame.paint_color = color


class PaintGame(Widget):
    def __init__(self, **kwargs):
        super(PaintGame, self).__init__(**kwargs)
        self.paint_board = Widget()
        self.add_widget(self.paint_board)
        self.cursor_board = Widget()
        self.add_widget(self.cursor_board)
        self.paint_color = (1, 1, 1, 1)

    def cursor_pos(self, gv):
        px = int(gv[0]) * 1.66
        py = int(gv[1]) * 1.66

        self.cursor_board.canvas.clear()
        with self.cursor_board.canvas:
            Color(1, 1, 1)
            cursor_position = Line(circle=(px, py, 50, 0, 359), closed=True)
            self.cursor_board.canvas.add(cursor_position)

    def draw_line(self, gv):
        px = int(gv[0]) * 1.66
        py = int(gv[1]) * 1.66
        color = self.paint_color
        self.cursor_board.canvas.clear()
        with self.paint_board.canvas:
            Color(*color, mode='rgba')
            d = 50.
            Ellipse(pos=(px - d / 2, py - d / 2), size=(d, d))