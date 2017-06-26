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
import threading
class Lineas(Widget):
    def __init__(self, **kwargs):
        super(Lineas, self).__init__(**kwargs)

    #def on_size(self,*args):
        self.px = []
        self.py = []
        w = self.width
        h = self.height
        for r in range(1,7):
            rw = r / 7.0
            self.px.extend([rw*w,0,rw*w,h])
            self.py.extend([0,rw*h,w,rw*h])
        self.canvas.clear()
        with self.canvas:
            #Color(1,0,0)
            #Rectangle(size=self.size)
            Color(0,0,0)
            for i in range(6):
                Line(points=self.px[i*4:i*4+4],width=2)
                Line(points=self.py[i*4:i*4+4],width=2)

class Barrera_izquierda(Widget):
    pass

class Barrera_derecha(Widget):
    pass

class Barrera_arriba(Widget):
    pass

class Barrera_abajo(Widget):
    pass

class Pieza_cuadrado(Widget):
    def __init__(self, **kwargs):
        super(Pieza_cuadrado, self).__init__(**kwargs)

    def color(self,color):
        with self.canvas:
            colores = [(1,0,0),(0,0,.8),(1,1,0)]
            #color = colores[color]
            Color(colores[color][0],colores[0][1],colores[0][2], mode='rgb')


class Pieza_rectangulo(Widget):
    pass

class Pieza_triangulo(Widget):
    def __init__(self, **kwargs):
        super(Pieza_triangulo, self).__init__(**kwargs)

    def color(self,color):
        with self.canvas.after:
            colores = ['rojo',(1,0,0),'azul',(0,0,.8),'amarillo',(1,1,0)]
            color = colores[colores.index(color)+1]
            print('color',color)
            Color(color[1],color[1],color[2], mode='rgb')
            self.triangle = Triangle(points=[150,150, 200,200, 250,150])
    #puntos = ListProperty([150,50, 200,100, 250,50])

class Juego2(Widget):
    
    

    def __init__(self, **kwargs):
        super(Juego2, self).__init__(**kwargs)

        
        self.iniciar = True
        
        self.barrera_izquierda = Barrera_izquierda()
        self.add_widget(self.barrera_izquierda)
        self.barrera_izquierda.pos = 0,0

        self.barrera_derecha = Barrera_derecha()
        self.add_widget(self.barrera_derecha)
        self.barrera_derecha.pos = 800,0

        self.barrera_arriba = Barrera_arriba()
        self.add_widget(self.barrera_arriba)
        self.barrera_arriba.pos= 0,400
       
        self.barrera_abajo = Barrera_abajo()
        self.add_widget(self.barrera_abajo)
        self.barrera_abajo.pos = 0,0

        self.ultimo_movimiento = 'abajo'
        self.ultima_posicion = [0,0]
       
        self.lista_piezas = [self.barrera_izquierda,self.barrera_derecha,self.barrera_arriba,self.barrera_abajo]
        self.pieza_actual = 0
        self.crear_pieza(1)

        self.lineas = Lineas()
        self.add_widget(self.lineas)

        #self.t0 = threading.Thread(target=self.update)
        #self.t0.start()

    def crear_pieza(self,color):


        if self.pieza_actual !=0:
            self.lista_piezas.append(self.pieza_actual)
        
        self.pieza_actual = Pieza_cuadrado()
        self.add_widget(self.pieza_actual)
        print('color',color)
        self.pieza_actual.color(color)
        self.pieza_actual.pos = 10,10

        if self.pieza_actual.collide_widget(self.lista_piezas[len(self.lista_piezas)-1]) == True:
            self.remove_widget(self.pieza_actual)
            self.pieza_actual = self.lista_piezas[len(self.lista_piezas)-1]
            self.lista_piezas.pop()

    def update(self):
        while self.iniciar == True:
            for pieza in self.lista_piezas:
                if pieza.collide_widget(self.pieza_actual) == True and self.ultimo_movimiento == 'izquierda':
                    Animation.cancel_all(self.pieza_actual)
                    self.pieza_actual.pos[0]+=24
                    print('colosion')

                if pieza.collide_widget(self.pieza_actual) == True and self.ultimo_movimiento == 'derecha':
                    Animation.cancel_all(self.pieza_actual)
                    self.pieza_actual.pos[0]-=24
                    print('colosion')

                if pieza.collide_widget(self.pieza_actual) == True and self.ultimo_movimiento == 'arriba':
                    Animation.cancel_all(self.pieza_actual)
                    print('ULTIMA POSICION',self.ultima_posicion, self.pieza_actual.pos)
                    self.pieza_actual.pos[1]-=24
                    print('colosion')

                if pieza.collide_widget(self.pieza_actual) == True and self.ultimo_movimiento == 'abajo':
                    Animation.cancel_all(self.pieza_actual)
                    self.pieza_actual.pos[1]+=24
                    print('colosion')
        

    def mover_arriba(self):
        
        if self.pieza_actual.pos[1]<296:
            self.ultimo_movimiento = 'arriba'
            self.ultima_posicion = self.pieza_actual.pos
            anim = Animation(pos=(self.pieza_actual.pos[0], self.pieza_actual.pos[1] + 57),duration=.1)
            anim.start(self.pieza_actual)
    
    def mover_abajo(self):
        
        if self.pieza_actual.pos[1]>10:
            self.ultimo_movimiento = 'abajo'
            anim = Animation(pos=(self.pieza_actual.pos[0], self.pieza_actual.pos[1] - 57),duration=.1)
            anim.start(self.pieza_actual)
        

    def mover_izquierda(self):
        if self.pieza_actual.pos[0]>11:
            self.ultimo_movimiento = 'izquierda'
            anim = Animation(pos=(self.pieza_actual.pos[0] - 114, self.pieza_actual.pos[1]),duration=.1)
            anim.start(self.pieza_actual)
     

    def mover_derecha(self):
      
        if self.pieza_actual.pos[0]<694:
            self.ultimo_movimiento = 'derecha'
            anim = Animation(pos=(self.pieza_actual.pos[0] + 114, self.pieza_actual.pos[1]),duration=.1)
            anim.start(self.pieza_actual)
             