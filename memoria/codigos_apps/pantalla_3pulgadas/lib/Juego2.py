# ex30.py
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.properties import ListProperty
from kivy.vector import Vector as Vec
from kivy.clock import Clock
import kivy
from kivy.animation import Animation
from kivy.graphics import Rectangle, Triangle, Line, Color
from lib import Envio_datos


class Pieza_cuadrado(Widget):
    def __init__(self, **kwargs):
        super(Pieza_cuadrado, self).__init__(**kwargs)

    def color(self,color):
        with self.canvas:
            colores = ['rojo',(1,0,0),'azul',(0,0,.8),'amarillo',(1,1,0)]
            color = colores[colores.index(color)+1]
            print('color',color)
            Color(color[1],color[1],color[2], mode='rgb')


class Juego2(Widget):
    

    def __init__(self, **kwargs):
        super(Juego2, self).__init__(**kwargs)
        #self.crear_pieza('azul')
        self.comunicaciones = Envio_datos.Envio_datos()
        self.comunicaciones.mandar_datos((0,2,1))
    def mover_arriba(self):
        values = (0,2,2)
        self.comunicaciones.mandar_datos(values)
    
    def mover_abajo(self):
        values = (0,2,3)
        self.comunicaciones.mandar_datos(values)
        
    def mover_izquierda(self):
        values = (0,2,4)
        self.comunicaciones.mandar_datos(values)

    def mover_derecha(self):
        values = (0,2,5)
        self.comunicaciones.mandar_datos(values)
 
    def crear_pieza(self,color):
        values = (1,2,6,color)
        self.comunicaciones.mandar_datos(values)
             