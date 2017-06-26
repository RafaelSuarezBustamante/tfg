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


class Borde(Widget):
    pass


class Cuadrado(Widget):

    def __init__(self, **kwargs):
        super(Cuadrado, self).__init__(**kwargs)

    def animacion_cuadrado(self,trayectoria):
        Animation.cancel_all(self)
        print(trayectoria)
        print(len(trayectoria))

        anim = Animation(pos=(trayectoria[0]),duration=0.)
        for i in range(1,len(trayectoria)):
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
    print('MATRIZ JUEGO1')
    contador = NumericProperty(0)
    puntos_trayectoria = ListProperty([0,0]) 
    def __init__(self, **kwargs):
        super(Matriz_juego, self).__init__(**kwargs)
        print('inicio juego1')
        self.iniciar = False
        self.matriz = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.ultima_coordenada = [[0,0]]
        self.puntos_trayectoria = []
        self.contador = 0
        
        self.trayectoria_juego = []
        self.botones_activos = []
        self.botones_id = []
        
        self.boton_visible = True

        #Estado del juego1
        self.estado_juego = 0
        #Datos recorrido del juego (botones)
        self.recorrido_botones = 0

        
        self.cuadrado = Cuadrado()
        self.trayectoria = ()
        self.boton_comenzar_juego1 = Button(
                pos = (250,320),
                size_hint = (None, None),
                size = ('130dp', '78dp'),
                background_normal = ('data/icons/boton_comenzar_juego1.png'),
                on_press = lambda a: self.comienzo_juego())
        
        self.boton_nuevo_juego1 = Button(
                pos = (420,320),
                size_hint = (None, None),
                size = ('130dp', '78dp'),
                background_normal = ('data/icons/boton_nuevo_juego1.png'),
                on_press = lambda a: self.reestablecer_juego())         

        print('crear localizacion panel tactil')
        self.panel_tactil = Panel_tactil.Localizacion()
        print('fin matriz juego init')
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
        
        ibut = self.ids['button_' + str(idb)]
       

        if ((self.ultima_coordenada[0][0] == fila or self.ultima_coordenada[0][1] == columna) 
            and self.matriz[fila][columna] == 0):
            if self.contador == 1:
                #self.ids.button_comenzar.disabled = False
                self.ids.menu_juego1.add_widget(self.boton_comenzar_juego1)
                self.ids.menu_juego1.add_widget(self.boton_nuevo_juego1)
            
            

            self.ultima_coordenada[0][0] = fila
            self.ultima_coordenada[0][1] = columna
            self.matriz[fila][columna] = 1
            self.ids.ball_id.animacion(ibut.center_x,ibut.center_y)
            self.puntos_trayectoria.append(ibut.center_x)
            self.puntos_trayectoria.append(ibut.center_y)
            self.trayectoria_juego.append(ibut.center)
            self.botones_activos.append(idb)
            self.trayectoria += tuple(ibut.center)
            print('TRAYECTORIA JUEGO',self.trayectoria)
            
            print('BOTONES ACTIVOS', self.botones_activos)
            self.contador = self.contador+1
            ibut.text = str(self.contador)
            ibut.text_halign = 'left'
            ibut.font_size = 73
            #idb.background_color = 0.0, 0.0, 1.0, 1.0
            ibut.disabled = True

            


        else:
            ibut.background_down = 'data/icons/boton_error.png'

 
    def reestablecer_juego(self):
        #self.ids.button_comenzar.disabled = True
        

        self.botones_activos = []
        self.trayectoria = ()

        self.datos_juego_comunicaciones(0,tuple(self.botones_activos),self.panel_tactil.values)
        
        self.ids.menu_juego1.remove_widget(self.boton_comenzar_juego1)
        #self.iniciar = False
        self.puntos_trayectoria = []
        
        self.ids.ball_id.animacion(-20,-20)
        self.matriz = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.ultima_coordenada=[[0,0]]
        self.contador = 0
        for i in range(1,17):
            self.ids['button_' + str(i)].text = ''
            self.ids['button_' + str(i)].disabled = False
        self.trayectoria_juego = []
        self.remove_widget(self.cuadrado)
        
        self.ids.menu_juego1.remove_widget(self.boton_nuevo_juego1)
    
    def comienzo_juego(self):
        self.datos_juego_comunicaciones(1,tuple(self.botones_activos),self.panel_tactil.values)
        self.ids.menu_juego1.remove_widget(self.boton_comenzar_juego1)
        self.iniciar = True
        self.puntos_trayectoria = ()
        
        #for i in range(len(self.trayectoria_juego)):
         #   self.puntos_trayectoria += tuple(self.trayectoria_juego[i])
        
        self.ids.ball_id.animacion(-20,-20)
        
        for i in range(1,17):
            self.ids['button_' + str(i)].disabled = True
        
        self.add_widget(self.cuadrado)
        
        self.cuadrado.animacion_cuadrado(self.trayectoria_juego)
    
    def datos_juego_comunicaciones(self, estado, recorrido, posicion):
        
        #Estado juego 1. Habilitado /  Deshabilitado
        self.estado_juego = (0,1,estado)
        #Datos recorrido del juego (botones)
        self.recorrido_botones = (len(recorrido),1,2)+recorrido
        print('RECORRIDO BOTONES',self.recorrido_botones)
        #Datos trayectoria del cuadrado
        #self.trayectoria_cuadrado = (len(trayectoria),1,3)+trayectoria
        #print('TRAYECTORIA CUADRADO', self.trayectoria_cuadrado)
        
        #Datos posicion del widget tangible sobre la pantalla
        self.posicion_widget = (len(posicion),1,3)+posicion
        
        
        
    def pausar_juego(self):
        self.cuadrado.detener_animacion()

