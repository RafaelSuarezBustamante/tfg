#coordenadas.py

''' Junto con el archivo coord7.kv muestra en el dispositivo con pantalla
	de 7 pulgadas la aplicacion. En esta primera version se muestra el estado
	de conexion con el cliente (dispositivo con pantalla de 3.5 pulgadas).
'''

from kivy.vector import Vector
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.app import App
import threading
from libcoord7 import Localizacion
from libcoord7 import Comunicaciones7


'''Clase para la representacion de datos del dispositivo en la
   pantalla de 7 pulgadas '''

class Pantalla7inch(Widget):
	#Muestra en pantalla en etiqueta el valor de la distancia entre puntos
	medida = NumericProperty(0) 	
	
	#Muestra en pantalla mediante etiqueta el valor del area del triangulo
	area_tri = NumericProperty(0) 			
	
	#Lista de coordenadas para mostrar los puntos de contacto
	coordenadas_i = ListProperty([(0,0,0),(0,0,0),(0,0,0)]) 
	
	#
	coordenadas_touch = ListProperty([])
	
	#Atributo tipo string usado para representar el estado de las comunicaciones
	conect = StringProperty()

	#
	dato = ListProperty([(0,0)])

	#Constructor de la clase 
	def __init__(self, **kwargs):
		super(Pantalla7inch, self).__init__(**kwargs)
		
		#Valor de distancia entre los dos ultimos puntos sobre la pantalla
		self.medida = 0
		
		#Valor del area del triangulo formado entre los tres puntos sobre la pantalla
		self.area_tri = 0
		
		#Lista de valores de las coordenadas de los puntos que estan sobre la pantalla
		self.coordenadas_touch = [(10,10),(10,10),(10,10)]
		
		#Inicializacion de la variable usada para iniciar el programa
		self.iniciar = True
		
		#Objeto dedicado a tratar los toques sobre la pantalla y determinar la localizacion
		self.atributos = Localizacion.Localizacion()

		#Parametros de la pantalla
		self.conexion_send = self.atributos.com.conexion_establecida
		self.coordenadas_init = self.atributos.coordenadas
		
		#Hilo para actualizacion de datos para mostrar en pantalla
		self.t2 = threading.Thread(target=self.actualizar_datos)
		self.t2.start()

	#Eventos de toque en la pantalla tactil
	def on_touch_down(self,touch):
		super(Pantalla7inch, self).on_touch_down(touch)

		#Se asigna los datos del toque en los atributos para ser tratados 
		self.atributos.pulsacion(touch)

	#Eventos cuando se solta el toque
	def on_touch_up(self,touch):
		#Asignacion de la identidad del toque que ha sido soltado
		self.atributos.toque_up(touch.id)

	#Metodo para actualizar los datos en pantalla
	def actualizar_datos(self):
		
		while self.iniciar == True:

			'''Actualizacion de los datos a mostrar en pantalla '''
			self.coordenadas_i = self.atributos.coordenadas
			self.medida = self.atributos.m
			self.area_tri = self.atributos.area
			self.conexion_send = self.atributos.com.conexion_establecida

			''' Establece si la conexion esta establecida con el servidor'''
			if self.conexion_send == True:
				self.conect = 'Conexion con pantalla 3.5inch establecida'
			else:
				self.conect = 'Sin conexion con pantalla 3.5inch'
	
	#Metodo para salir de la aplicacion
	def salir(self):
		self.iniciar = False
		self.atributos.com.finalizar_conexion()

#Clase de la aplicacion principal
class Coord7App(App):
	def build(self):
		return Pantalla7inch()

if __name__=='__main__':
	Coord7App().run()

