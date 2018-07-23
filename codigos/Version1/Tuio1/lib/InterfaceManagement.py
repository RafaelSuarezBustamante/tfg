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

class InterfaceManagement(object):
    def __init__(self):
        self.internal_events = Queue()
        self.external_events = Queue()

        self.screens = {'idle_screen': IdleScreen(name='idle_screen'),
                        'main_screen': MainScreen(name='main_screen'),
                        'logo_screen': LogoScreen(name='logo_screen')}

        self.screens['main_screen'].add_widget(Buttons.ExitButton(on_press=lambda x:
                                    self.create_event(("exit_tuio1", "", ""))))

        self.screens['idle_screen'].add_widget(Buttons.ExitButton(on_press=lambda x:
                                    self.create_event(("exit_tuio1", "", ""))))

    def create_event(self, ev):
        event = ev
        self.internal_events.put(event)

    def next(self):
        if not self.internal_events.empty():
            ev = self.internal_events.get()
            self.dispatch_event(ev)


    def dispatch_event(self, ev):
        event_type = ev[0]
        givens = ev[1:]

        if event_type == "init_interface":
            self.init_interface()

        if event_type == "main_state":
            self.main_state()

        if event_type == "close_interface":
            self.close_interface()

        if event_type == "exit_tuio1":
            event = ("exit_tuio1", "", "")
            self.external_events.put(event)

    def main_state(self):
        sm.switch_to(self.screens['main_screen'])

    def idle_state(self):
        sm.switch_to(self.screens['idle_screen'])

    def init_interface(self):
        sm.add_widget(self.screens['logo_screen'])
        sm.current = 'logo_screen'

    def close_interface(self):
        App.get_running_app().stop()
        Window.close()


class GUI_Tuio1App(App):
    def build(self):
        Window.size = (800, 480)
        return sm

sm = ScreenManager()