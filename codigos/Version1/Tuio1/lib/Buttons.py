# -*- coding: utf-8 -*-
import time
from threading import Thread
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.lang import Builder

Builder.load_file('lib/interfacemanagement.kv')

class ExitButton(Button):
    def __init__(self, **kwargs):
        super(ExitButton, self).__init__(**kwargs)
        self.background_normal = 'data/icons/boton_salir.png'
        self.size_hint = .15, .15
        self.pos = 10, 10


class Return_button(Button):
    def __init__(self, **kwargs):
        super(Return_button, self).__init__(**kwargs)
        self.background_normal = 'data/icons/jugar.png'
        self.size_hint = .2, .15
        self.pos = 100, 100



class Back_button(Button):
    def __init__(self, **kwargs):
        super(Back_button, self).__init__(**kwargs)
        self.background_normal = 'data/icons/back_button.png'
        self.size_hint = .2, .15
        self.pos = 180, 180


class BarState(Widget):
    def __init__(self, **kwargs):
        super(BarState, self).__init__(**kwargs)
        self.bar = []
        self.init_bar()
        Thread(target=self.bar_state, ).start()

    def init_bar(self):
        source = ['data/icons/bar_state0.png', 'data/icons/bar_state1.png', 'data/icons/bar_state2.png',
                  'data/icons/bar_state3.png']
        for i in source:
            self.bar.append(Image(source=i, size=(200, 200), pos=(300, 0)))

    def bar_state(self):
        while True:
            for i in self.bar:
                self.add_widget(i)
                time.sleep(1)
                self.remove_widget(i)

class LogoAnimation(Widget):
    def __init__(self, **kwargs):
        super(LogoAnimation, self).__init__(**kwargs)
        self.logo = []
        self.init_logo()

    def init_logo(self):
        sources = ['data/icons/logo/logo0.png', 'data/icons/logo/logo1.png',
                  'data/icons/logo/logo2.png', 'data/icons/logo/logo3.png',
                  'data/icons/logo/logo4.png', 'data/icons/logo/logo5.png',
                  'data/icons/logo/logo6.png']
        j = 0
        for source in sources:
            self.logo.append(Image(source=source, size=(0, 0), pos_hint=(1, 1)))
            self.add_widget(self.logo[j])
            j += 1

        Thread(target=self.start_animation, ).start()

    def start_animation(self):
        k = 50
        for i in self.logo:
            anim = Animation(x=k, y=300, size=(100, 100), t='in_quad')
            anim.start(i)
            k += 100
            time.sleep(.6)