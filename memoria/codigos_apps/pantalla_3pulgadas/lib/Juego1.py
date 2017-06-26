from kivy.uix.widget import Widget
from kivy.app import App
from kivy.animation import Animation
from kivy.properties import StringProperty
from kivy.properties import ListProperty
from kivy.graphics import *
from kivy.properties import NumericProperty
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
import time


class Aviso1(Widget):
    pass


class Cuadrado(Widget):

    def __init__(self, **kwargs):
        super(Cuadrado, self).__init__(**kwargs)

    def animacion_cuadrado(self,trayectoria):
        Animation.cancel_all(self)

        print('Trayectoria', trayectoria)
        anim = Animation(pos=(trayectoria[0]),duration=0.)
        for i in range(1, len(trayectoria)):
            anim += Animation(pos=(trayectoria[i]),duration=3.)
            anim.start(self)
        
        print('posicion cuadrado',self.pos)
    def detener_animacion(self):
        Animation.cancel_all(self)


class Matriz_juego(Widget):

    posiciones_widget = ListProperty([0,0,0])
    posx_cuadrado = NumericProperty(0)
    posy_cuadrado = NumericProperty(0)
    def __init__(self, **kwargs):
        super(Matriz_juego, self).__init__(**kwargs)
        print('inicio juego1')
        self.iniciar = False
        #self.cuadrado = Cuadrado()
        self.aviso1 = Aviso1()
        self.trayectoria = []
        self.estado_aviso1 = False
        self.trayectoria_juego = 0
        self.recorrido_botones = 0 
        self.posiciones_widget = [0,0,0]
        self.posx_cuadrado = 0
        self.posy_cuadrado = 0
        self.poner_aviso()
        
    def establecer_recorrido_botones(self,recorrido):
        trayectoria = []
        for i in range(len(recorrido)):
            self.ids['button_' + str(int(recorrido[i]))].text = str(i+1)
            trayectoria.append(self.ids['button_' + str(int(recorrido[i]))].center)

        self.comienzo_juego(trayectoria)

    def posicion_widget(self,posiciones):
        self.posiciones_widget[0] = posiciones[0]
        self.posiciones_widget[1] = posiciones[1]

    def reestablecer_juego(self):
        self.iniciar = False
        self.trayectoria = []
        
        for i in range(1,16):
            self.ids['button_' + str(i)].text = ''
    
    def comienzo_juego(self,trayectoria):
        self.iniciar = True
        #self.add_widget(self.cuadrado)
        #self.cuadrado.animacion_cuadrado(trayectoria)
        print('TRAYE',trayectoria)
        anim = Animation(pos=(trayectoria[0]),duration=0.)
        for i in range(1, len(trayectoria)):
            anim += Animation(pos=(trayectoria[i]),duration=3.)
            anim.start(self.ids.cuadrado)
   
    def poner_aviso(self):
        if self.estado_aviso1 == False:
            self.add_widget(self.aviso1)
            self.estado_aviso1 = True

    def quitar_aviso(self):
        if self.estado_aviso1 == True:
            self.remove_widget(self.aviso1)
            self.estado_aviso1 = False

    def pausar_juego(self):
        self.cuadrado.detener_animacion()



     # for i in range(len(trayectoria)-1):
        #     if trayectoria[i][0] != trayectoria[i+1][0]:
        #         if trayectoria[i][0] > trayectoria[i+1][0]:
        #             a = round(trayectoria[i][0])
        #             b = round(trayectoria[i+1][0])
        #             c = 1
        #         else:
        #             a = round(trayectoria[i+1][0])
        #             b = round(trayectoria[i][0])
        #             c = -1
        #     print('ABC1',a,b,c)
        #     for j in range(a,b,c):
        #         self.posx_cuadrado = j 
        #         time.sleep(0.05)
        #     if trayectoria[i][1] != trayectoria[i+1][1]:
        #         if trayectoria[i][1] > trayectoria[i+1][1]:
        #             a = round(trayectoria[i][1])
        #             b = round(trayectoria[i+1][1])
        #             c = 1
        #         else:
        #             a = round(trayectoria[i+1][1])
        #             b = round(trayectoria[i][1])
        #             c = -1
        #     print('ABC2',a,b,c)
        #     for j in range(a,b,c):
        #         self.posy_cuadrado = j
        #         print(self.posy_cuadrado)
        #         time.sleep(0.05)