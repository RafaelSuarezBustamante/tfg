import time
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.app import App
from kivy.properties import ListProperty
from kivy.vector import Vector as Vec
from kivy.clock import Clock
import kivy
from kivy.animation import Animation
from kivy.graphics import Rectangle, Triangle, Line, Color
import threading
from random import randint
from kivy.uix.screenmanager import Screen


class ExampleGame1Screen(Screen):
	pass

class Background_Game(Widget):
	source  = StringProperty()
	def __init__(self, **kwargs):
		super(Background_Game, self).__init__(**kwargs)
		self.source = "data/fondos/fondo_juego3.jpg"

class AnimationIcon(Widget):
	source = StringProperty()
	def __init__(self, **kwargs):
		super(AnimationIcon, self).__init__(**kwargs)
		self.source = "data/icons/tuio2.png"

class Mensaje_Game(Widget):
	source = StringProperty()
	def __init__(self, **kwargs):
		super(Mensaje_Game, self).__init__(**kwargs)
		self.source = "data/fondos/imagen_interaccion.jpg"
		

class ExampleGame1(Widget):
	
	def __init__(self, **kwargs):
		
		super(ExampleGame1, self).__init__(**kwargs)
		self.mensaje = Mensaje_Game()
		self.tuio2_icon = AnimationIcon()
		self.background_game = Background_Game()
		self.add_widget(self.background_game)
		self.background_game.pos = 0,0
		self.background_game.size = 480,320
		#mensaje.pos = 0,0
		#mensaje.size = 480,320
		#mensaje.color()
		self.create_menssage()

	def background_game_coordinates(self,coor):
		print('COOR', coor)
		px = coor[0]
		py = coor[1]
		angle = coor[2]
		print('TIPO',type(px))
		self.background_game.pos = -float(px),-float(py)

	def create_menssage(self):
		if self.mensaje and self.tuio2_icon in self.children:
			return		
		self.add_widget(self.mensaje)
		self.add_widget(self.tuio2_icon)
		self.tuio2_icon.pos = 210,110
		animacion_tuio2 = Animation(pos=(210, 50),duration=5) + Animation(pos=(210, 110),duration=5) 
		animacion_tuio2.start(self.tuio2_icon)

	def clear(self):
		if self.mensaje not in self.children:
			return
		self.remove_widget(self.mensaje)
		self.remove_widget(self.icon_tuio2)
		Animation.stop_all()


	# def __init__(self):
	#     self.menu = Widget()

	# def clear_widgets(self):
	#     self.menu.clear_widgets()

	# def example_game1(self):
	#     button = Button(text='Capturar', font_size=14)
	#     add_widget(self.menu.button)

