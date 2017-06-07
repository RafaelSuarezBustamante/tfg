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
from lib import Panel_tactil

class Cuadrado(Widget):

    def __init__(self, **kwargs):
        super(Cuadrado, self).__init__(**kwargs)
        
    def animacion_cuadrado(self,trayectoria):
        Animation.cancel_all(self)

        anim = Animation(pos=(trayectoria[0]),duration=0.)
        for i in range(1,len(trayectoria)):
            print('i',i)
            anim += Animation(pos=(trayectoria[i]),duration=3.)
            anim.start(self)
        
        print('posicion cuadrado',self.pos)
    def detener_animacion(self):
        Animation.cancel_all(self)

class Ball(Widget):

    def __init__(self, **kwargs):
        super(Ball, self).__init__(**kwargs)
        print('inicio bola')

    def animacion(self,posx,posy):
        Animation.cancel_all(self)
        anim = Animation(center_x = posx,
                         center_y = posy,
                         t = 'in_back')
        anim.start(self)

class Matriz_juego(Widget):


    contador = NumericProperty(0)
    puntos_trayectoria = ListProperty([0,0]) 
    def __init__(self, **kwargs):
        super(Matriz_juego, self).__init__(**kwargs)
        print('inicio juego1')
        self.matriz = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.ultima_coordenada = [[0,0]]
        self.puntos_trayectoria = []
        self.contador = 0
        self.trayectoria_juego = []
        #self.botones_id = []
        self.boton_visible = True
        self.cuadrado = Cuadrado()
        self.panel_tactil = Panel_tactil.Localizacion()


    #Eventos de toque en la pantalla tactil
    def on_touch_down(self,touch):

        super(Matriz_juego, self).on_touch_down(touch)

        #Se asigna los datos del toque en los atributos para ser tratados 
        self.panel_tactil.pulsacion(touch)

    #Eventos cuando se solta el toque
    def on_touch_up(self,touch):
        #Asignacion de la identidad del toque que ha sido soltado
        self.panel_tactil.toque_up(touch.id)


    def inicio(self,idb,fila,columna):
        print('boton')
        print(idb)

        print(fila)
        print(columna)
        print(self.ultima_coordenada)

        if idb == 0:
            self.reestablecer_juego()
        elif idb ==2:
            self.comienzo_juego()
            
        elif ((self.ultima_coordenada[0][0] == fila or self.ultima_coordenada[0][1] == columna) 
            and self.matriz[fila][columna] == 0):
            if self.contador == 1:
                self.ids.button_comenzar.disabled = False
            self.ultima_coordenada[0][0] = fila
            self.ultima_coordenada[0][1] = columna
            self.matriz[fila][columna] = 1
            self.ids.ball_id.animacion(idb.center_x,idb.center_y)
            self.puntos_trayectoria.append(idb.center_x)
            self.puntos_trayectoria.append(idb.center_y)
            self.trayectoria_juego.append(idb.center)
            self.contador = self.contador+1
            idb.text = str(self.contador)
            idb.text_halign = 'left'
            idb.font_size = 73
            #idb.background_color = 0.0, 0.0, 1.0, 1.0
            idb.disabled = True
        else:
            idb.background_down = 'data/icons/boton_error.png'
 
    def reestablecer_juego(self):
        self.ids.button_comenzar.disabled = True
        self.puntos_trayectoria = []
        self.ids.ball_id.animacion(-20,-20)
        self.matriz = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.ultima_coordenada=[[0,0]]
        self.contador = 0
        for i in range(16):
            self.ids['button_' + str(i)].text = ''
            self.ids['button_' + str(i)].disabled = False
        self.trayectoria_juego = []
        self.remove_widget(self.cuadrado)

    def comienzo_juego(self):
        self.puntos_trayectoria = []
        self.ids.ball_id.animacion(-20,-20)
        for i in range(16):
            self.ids['button_' + str(i)].disabled = True
        self.ids.button_comenzar.disabled = True
        self.add_widget(self.cuadrado)
        self.cuadrado.animacion_cuadrado(self.trayectoria_juego)
    
    def pausar_juego(self):
        self.cuadrado.detener_animacion()

