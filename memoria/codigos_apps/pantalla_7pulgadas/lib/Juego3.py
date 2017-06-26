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

class Pieza_muros(Widget):

    def __init__(self, **kwargs):
        super(Pieza_muros, self).__init__(**kwargs)

    def color(self):
        with self.canvas:
            Color(0,0,1, mode='rgb')


class Pieza_cuadrado(Widget):
    def __init__(self, **kwargs):
        super(Pieza_cuadrado, self).__init__(**kwargs)

    def color(self):
        with self.canvas:
            colores = [(1,0,0),(0,0,.8),(1,1,0)]
            c = randint(0, 2)
            #color = colores[color]
            Color(colores[c][0],colores[c][1],colores[c][2], mode='rgb')

class Pieza_retroalim(Widget):

    def __init__(self, **kwargs):
        super(Pieza_retroalim, self).__init__(**kwargs)

    def color(self):
        with self.canvas:
            Color(0,0,0, mode='rgb')

class Juego3(Widget):

    def __init__(self, **kwargs):
        super(Juego3, self).__init__(**kwargs)
        self.contador = 0
        self.colision = False
        self.muros = []
        self.num_acciones = [0,0,0,0,0,0,0,0]
        self.iniciar3 = True
        self.retro = []
        self.piezas = []
        self.crear_pieza()
        self.crear_muros()
        self.crear_retroalimentacion()
        self.n = 0
        self.ejemplo()
        #self.t0 = threading.Thread(target=self.update)
        #self.t0.start()

    #Funcion que genera la lista de piezas a usar en el juego con colores
    #aleatorios. Estas piezas son situadas en la parte superior del juego
    
    def crear_muros(self):

        #Muro izquierda
        self.muros.append(Pieza_muros())
        self.add_widget(self.muros[-1])
        self.muros[0].size = 20,400
        self.muros[0].pos = 0,0

        #Muro abajo
        self.muros.append(Pieza_muros())
        self.add_widget(self.muros[-1])
        self.muros[-1].size = 800,20
        self.muros[-1].pos = 0,0

        #Muro intermedio izquierda
        self.muros.append(Pieza_muros())
        self.add_widget(self.muros[-1])
        self.muros[-1].size = 8,180
        self.muros[-1].pos = 139,125
        #Muro intermedio arriba
        self.muros.append(Pieza_muros())
        self.add_widget(self.muros[-1])
        self.muros[-1].size = 400,8
        self.muros[-1].pos = 139,300

        #Muro superior
        self.muros.append(Pieza_muros())
        self.add_widget(self.muros[-1])
        self.muros[-1].size = 760,8
        self.muros[-1].pos = 0,400

        for i in range(len(self.muros)-1):
            self.muros[i].color()

    
    def crear_retroalimentacion(self):
        x = 25
        for i in range(4):
            y = 175
            for j in range(2):
                self.retro.append(Pieza_retroalim())
                self.add_widget(self.retro[-1])
                self.retro[-1].color()
                self.retro[-1].size = 15,15
                self.retro[-1].pos = x,y
                y = y - 60
            x = x + 145

    def crear_pieza(self):

        x = 45
        for i in range(7):
            self.piezas.append(Pieza_cuadrado())
            self.add_widget(self.piezas[i])
            self.piezas[i].color()
            self.piezas[i].size = 70,80
            self.piezas[i].pos = x,313
            x = x + 82


    def ejemplo(self):
        self.contador = 0
        self.n = 0
        self.acciones(0,1)
        self.acciones(1,2)
        self.acciones(3,-1)
        self.acciones(2,2)
        self.acciones(4,2)
        self.acciones(6,1)
        self.acciones(7,2)
        
        print('ACCIONES', self.num_acciones)


    def acciones(self,pos,num_accion):
        self.num_acciones[pos] = num_accion
        self.contador +=1

    def comienzo_secuencia(self):
        t0 = threading.Thread(target=self.update)
        t0.start()
        animaciones = Animation(pos=(45, 313),duration=1) + Animation(pos=(45, self.piezas[0].pos[1]-100),duration=1)  
        animaciones.bind(on_complete = lambda x,y: self.asignar_secuencia())
        animaciones.start(self.piezas[0])

    def asignar_secuencia(self):
        
        if self.contador>0:
            if self.num_acciones[self.n] == -1:  #Movimiento hacia arriba
                animaciones = Animation(pos=(self.piezas[0].pos[0], 
                                        self.piezas[0].pos[1] + 170),duration=3)
            elif self.num_acciones[self.n] == 1: #Movimiento hacia abajo
                animaciones = Animation(pos=(self.piezas[0].pos[0], 
                                        self.piezas[0].pos[1] - 170),duration=3)
            elif self.num_acciones[self.n] == -2: #Movimiento hacia izquierda
                animaciones = Animation(pos=(self.piezas[0].pos[0] - 145, 
                                        self.piezas[0].pos[1]),duration=3)
            elif self.num_acciones[self.n] == 2:  #Movimiento hacia derecha
                animaciones = Animation(pos=(self.piezas[0].pos[0] + 145, 
                                        self.piezas[0].pos[1]),duration=3)
            elif self.num_acciones[self.n] == 4:  #Giro 180 grados
                print('giro')
            else:
                animaciones = Animation(pos=(self.piezas[0].pos[0], 
                                        self.piezas[0].pos[1]),duration=.0)
            try:
                #Actualizar la retroalimentacion de las acciones
                self.accion_finalizada()
                self.n = self.n + self.num_acciones[self.n]
                self.contador = self.contador - 1
                self.procesado_secuencias(animaciones)
                
            except IndexError as err:
                print('Movimiento no valido', err)
                self.finalizar()

        else: 
            self.finalizar()

    def procesado_secuencias(self,animaciones):
            animaciones.bind(on_complete = lambda x,y: self.asignar_secuencia())
            animaciones.start(self.piezas[0])

   
    def accion_sin_realizar(self):
        for i in range(len(self.retro)):
            self.retro[i-1].canvas.add(Color(0,0,0))

    def accion_en_curso(self):
        self.retro[self.n].canvas.add(Color(1,1,0))

    def accion_finalizada(self):
        self.retro[self.n].canvas.add(Color(0,1,0))


    def captura(self):
        self.remove_widget(self.piezas[0])

    def update(self):
        while self.iniciar3 == True:
            for muro in self.muros:
                if muro.collide_widget(self.piezas[0]) == True:
                    Animation.cancel_all(self.piezas[0])
                    print('colosion')
                    self.colision = True
                    self.finalizar()

    def finalizar(self):
            if self.piezas[0].pos[0] == 625 and self.piezas[0].pos[1] == 43:
                print('EXITO!!')
                self.captura()
            self.accion_sin_realizar()
            self.iniciar3 = False
            Animation.cancel_all(self.piezas[0])
            self.piezas.pop(0)
            print('FIN OK')
