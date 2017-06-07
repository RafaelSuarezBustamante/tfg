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
from lib import Panel_tactil
from lib import Interface_datos7inch
import time

 

'''Clase para la representacion de datos del dispositivo en la
   pantalla de 7 pulgadas '''

class Interface_7inch(Widget):

	
	#Lista de coordenadas para mostrar los puntos de contacto
	#coordenadas_i = ListProperty([(0,0,0),(0,0,0),(0,0,0)]) 
	
	#
	#coordenadas_touch = ListProperty([])
	
	#Atributo tipo string usado para representar el estado de las comunicaciones
	
	#Coordenadas tactiles el widget capacitivo (A,B,C)
	coordenadas = ListProperty([(0,0,0),(0,0,0),(0,0,0)]) 

	conect = StringProperty()

	#
	#dato = ListProperty([(0,0)])

	#MPU9250
	mpu9250_datos = ListProperty([0,(0,0,0),(0,0,0),(0,0,0)])


	#Constructor de la clase 
	def __init__(self, **kwargs):
		super(Interface_7inch, self).__init__(**kwargs)
		
		#Objeto Panel tactil.
		#Mostrar en la interface la localizacion de los puntos activos sobre pantalla.
		self.panel_tactil = Panel_tactil.Localizacion()

		#Coordenadas A B C del widget tangible
		self.coordenadas = self.panel_tactil.coordenadas
		
		#Inicializacion de la variable usada para iniciar el programa
		self.iniciar = True

		#Parametros del mpu9250
		self.mpu9250_datos = [0,0,0,0]

		#Hilo para actualizacion de datos para mostrar en pantalla+
		print('inicio actualizar datos')
		self.t2 = threading.Thread(target=self.actualizar_datos)
		self.t2.start()

	#Eventos de toque en la pantalla tactil
	def on_touch_down(self,touch):

		super(Interface_7inch, self).on_touch_down(touch)

		#Se asigna los datos del toque en los atributos para ser tratados 
		self.panel_tactil.pulsacion(touch)

	#Eventos cuando se solta el toque
	def on_touch_up(self,touch):
		#Asignacion de la identidad del toque que ha sido soltado
		self.panel_tactil.toque_up(touch.id)

	#Metodo para actualizar los datos en pantalla
	def actualizar_datos(self):
		
		while self.iniciar == True:

			self.coordenadas = self.panel_tactil.coordenadas

			self.mpu9250_datos[self.panel_tactil.comunicaciones.datos[0]] = self.panel_tactil.comunicaciones.datos[1:4]
		

			''' Muestra si la conexion esta establecida con el servidor'''
			if self.panel_tactil.comunicaciones.conexion_con_cliente == True:
				self.conect = 'Conexion con pantalla 3.5inch establecida'
			else:
				self.conect = 'Sin conexion con pantalla 3.5inch'
			time.sleep(0.5)
			
	#Metodo para salir de la aplicacion
	def salir(self):
		self.iniciar = False
		self.panel_tactil.comunicaciones.finalizar_conexion()

#Clase de la aplicacion principal
class Interface_7inchApp(App):
	def build(self):
		return Interface_7inch()

if __name__=='__main__':
	Interface_7inchApp().run()

