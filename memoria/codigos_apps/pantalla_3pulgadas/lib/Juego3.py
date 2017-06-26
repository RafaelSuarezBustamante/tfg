import time
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.properties import ListProperty
from kivy.vector import Vector as Vec
from kivy.clock import Clock
import kivy
from kivy.animation import Animation
from kivy.graphics import Rectangle, Triangle, Line, Color
import threading
from random import randint
from lib import Envio_datos


class Juego3(Widget):

    def __init__(self, **kwargs):
        super(Juego3, self).__init__(**kwargs)
        self.comunicaciones = Envio_datos.Envio_datos()
        
    def iniciar(self):
        self.comunicaciones.mandar_datos((0,3,1))
        

    def finalizar(self):
            if self.piezas[0].pos[0] == 625 and self.piezas[0].pos[1] == 43:
                print('EXITO!!')
                self.captura()
            self.accion_sin_realizar()
            self.iniciar3 = False
            Animation.cancel_all(self.piezas[0])
            self.piezas.pop(0)
            print('FIN OK')
