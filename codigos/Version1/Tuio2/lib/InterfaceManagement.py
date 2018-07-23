# -*- coding: utf-8 -*-

from multiprocessing import Queue
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from lib import Buttons

Builder.load_file('lib/interfacemanagement.kv')

class LogoScreen(Screen):
    pass

class IdleScreen(Screen):
    pass

class MainScreen(Screen):
    pass

class MenuScreen(Screen):
    pass

class PaintScreen(Screen):
    pass


class InterfaceManagement(object):
    def __init__(self):
        self.events = Queue()
        self.screens = {'idle_screen': IdleScreen(name='idle_screen'),
                        'main_screen': MainScreen(name='main_screen'),
                        'menu_screen': MenuScreen(name='menu_screen'),
                        'logo_screen': LogoScreen(name='logo_screen')}

    def create_event(self, ev):
        event = ev
        self.events.put(event)

    def init_interface(self):
        sm.add_widget(self.screens['logo_screen'])
        self.screens['idle_screen'].add_widget(Buttons.Exit_button(on_press=lambda x:
                                    self.create_event(("exit_tuio2", "", ""))))

        self.screens['main_screen'].add_widget(Buttons.Paint_button(on_press=lambda x:
                                    self.create_event(("start_game", "paint_game", ""))))

        self.screens['main_screen'].add_widget(Buttons.Capture_button(on_press=lambda x:
                                    self.create_event(("start_game", "capture_game", ""))))

    def switch_screen(self, gv):
        screen = gv
        if sm.current is not screen:
            screen_to_remove = sm.current
            sm.add_widget(self.screens[screen])
            sm.current = screen
            sm.remove_widget(self.screens[screen_to_remove])

    def main_state(self):
        sm.switch_to(self.screens['main_screen'])

    def idle_state(self):
        sm.switch_to(self.screens['idle_screen'])

    def tuio2_connect(self):
        self.switch_screen("main_screen")

    def tuio2_disconnect(self):
        self.switch_screen("idle_screen")


    def close_interface(self):
        App.get_running_app().stop()
        Window.close()

class GUI_Tuio2App(App):
    def build(self):
        Window.size = (480, 320)
        return sm


sm = ScreenManager()

