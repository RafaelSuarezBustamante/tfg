#coord35.py

''' Junto con el archivo coord35.kv muestra en el dispositivo con pantalla
	de 3.5 pulgadas la aplicacion. En esta primera version se muestra el estado
	de conexion con el servidor (dispositivo con pantalla de 7 pulgadas).

	En la siguiente modificacion se mostrara lo que ocurre debajo de la pantalla
	de 7 pulgadas al ser situada encima la pantalla de 3.5 pulgadas, haciendo
	un efecto "cristal".'''

from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from socket import *
import threading
from libcoord35 import Comunicaciones35


'''Clase para la representacion de datos del dispositivo en la
   pantalla de 3.5 pulgadas '''

class Coord35(Widget):
	#Atributo tipo string usado para representar el estado de las comunicaciones
	conect = StringProperty()

	#Constructor de la clase Coord35
	def __init__(self, **kwargs):
		super(Coord35, self).__init__(**kwargs)
		
		#Objeto dedicado a las comunicaciones con el servidor creando un cliente
		self.obj_35 = Comunicaciones35.Comunicaciones35()

		#Se inicializa el estado de conexion
		self.conect = ''

		#Inicializacion de la variable usada para iniciar el programa
		self.iniciar = True

		#Hilo dedicado para actualizar los datos
		self.t0 = threading.Thread(target=self.actualizar_datos)
		self.t0.start()

	#Metodo para actualizar los datos que mostrar
	def actualizar_datos(self):
		
		while self.iniciar == True:

			#Obtiene el estado de conexion del cliente con el servidor
			conexion = self.obj_35.conexion_establecida

			''' Establece si la conexion esta establecida con el servidor'''
			if conexion == 1:
				self.conect = 'Conexion con pantalla 7inch establecida'
			elif conexion == 0:
				self.conect = 'Sin conexion con pantalla 7inch'
			elif conexion == 2:
				self.conect = 'Creando un nuevo cliente'
				#Se crea un nuevo cliente si el servidor cierra la conexion
				self.obj_35 = Comunicaciones35.Comunicaciones35()
			else:
				break

	#Metodo para finalizar el programa	
	def finalizar(self):
		self.iniciar = False
		self.obj_35.finalizar_conexion()

#Clase de la aplicacion principal
class Coord35App(App):
	def build(self):
		return Coord35()

if __name__=='__main__':
	Coord35App().run()

