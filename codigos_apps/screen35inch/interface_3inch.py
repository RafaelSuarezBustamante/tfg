#interface_3inch.py

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
import threading
from lib_screen3inch import MPU9250
import time

'''Clase para la representacion de datos del dispositivo en la
   pantalla de 3.5 pulgadas '''

class Interface_3inch(Widget):
	#Atributo tipo string usado para representar el estado de las comunicaciones
	conect = StringProperty()


	#Constructor de la clase Coord35
	def __init__(self, **kwargs):
		super(Interface_3inch, self).__init__(**kwargs)
		
		#Objeto para obtener datos del IMU MPU9250
		self.mpu9250 = MPU9250.MPU9250()
		#Datos acelerometro, magnetometro, giroscopio IMU MPU9250
		self.mpu9250_datos =[0,0,0]

		#Se inicializa el estado de conexion
		self.conect = ''

		#Inicializacion de la variable usada para iniciar el programa
		self.iniciar = True
		self.mpu9250.iniciar = True
		#Hilo dedicado para actualizar los datos
		self.t0 = threading.Thread(target=self.actualizar_datos)
		self.t0.start()

	#Metodo para actualizar los datos que mostrar
	def actualizar_datos(self):
		
		while self.iniciar == True:

			#Ac
			self.mpu9250_datos[self.mpu9250.mpu9250_datos[0]] = self.mpu9250.mpu9250_datos[1:4]
			#Obtiene el estado de conexion del cliente con el servidor
			conexion = self.mpu9250.comunicaciones.conexion_establecida
			#self.atributos35.obtener_datos()
			''' Establece si la conexion esta establecida con el servidor'''
			if conexion == 1:
				self.conect = 'Conexion con pantalla 7inch establecida'
			elif conexion == 0:
				self.conect = 'Sin conexion con pantalla 7inch'
				#time.sleep(5)
				#self.mpu9250.mpu9250_crear_comunicaciones()
			else:
				break

	#Metodo para finalizar el programa	
	def finalizar(self):
		self.iniciar = False
		self.mpu9250.iniciar = False
		self.mpu9250.mpu9250_activar = False
		self.mpu9250.comunicaciones.finalizar_conexion()

#Clase de la aplicacion principal
class Interface_3inchApp(App):
	def build(self):
		return Interface_3inch()

if __name__=='__main__':
	Interface_3inchApp().run()

