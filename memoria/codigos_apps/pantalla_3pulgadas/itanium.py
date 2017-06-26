import time
from kivy.app import App
from os.path import dirname, join
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from lib import Juego1
from lib import Juego2
from lib import Juego3
#from lib import Comunicaciones_cliente
import threading
from multiprocessing.pool import ThreadPool
from socket import *
import struct

class Itanium(Screen):

	fullscreen = BooleanProperty(False)

	def add_widget(self, *args):
		if 'content' in self.ids:
			return self.ids.content.add_widget(*args)
		return super(Itanium, self).add_widget(*args)
		

class ItaniumApp(App):

	index = NumericProperty(-1)
	screen_names = ListProperty([])
	
	def build(self):

		####################################################
		#### COMUNICACIONES DEL CLIENTE CON EL SERVIDOR ####
		####################################################
		self.host = '192.168.0.157' #host del servidor
		self.port = 8908	    #puerto de escucha del servidor
		self.s = socket(AF_INET, SOCK_STREAM)
		
		#Atributo dedicado a indicar el estado de la conexion:
		self.conexion_con_servidor = False
		'''Conexion no establecida                         -- 0
		   Conexion establecida                            -- 1'''
		self.root.ids.conexion.text = 'DESCONECTADO'
		self.root.ids.conexion.background_disabled_normal='data/icons/wifi_desconectado.png'
		#Variable dedicada al almacenamiento de los datos recibidos
		self.datos = [0,0,0,0,0,0]
		self.unpacked_data = [8,8,8]
		
		


		####################################################
		####             PARAMETROS DEL MENU            ####
		####################################################
		self.iniciar = True
		#self.comunicaciones = Comunicaciones()
		#self.juego1 = Juego1.Matriz_juego()
		#self.comunicaciones = Comunicaciones_cliente.Comunicaciones3()
		self.juego1_habilitado = False
		self.juego2_habilitado = False
		self.datos_posicion = 0
		

		self.datos_trayectoria = 0
		self.estado_juego = 0
		self.recorrido_botones = 0
		
		#self.t1 = threading.Thread(target=self.actualizar)
		#self.t1.start()
		
		self.pantallas = {}
		self.pantallas_disponibles = sorted(['PantallaPrincipal','PantallaControles',
									'PantallaAyuda','PantallaConfigurar', 'PantallaJuego1', 
									'PantallaJuego2', 'PantallaJuego3'])

		self.screen_names = self.pantallas_disponibles
		directorio = dirname(__file__)
		self.pantallas_disponibles = [join(directorio, 'data', 'pantallas',
			'{}.kv'.format(fn).lower()) for fn in self.pantallas_disponibles]
		idx = self.screen_names.index('PantallaPrincipal')
		self.go_screen(idx)
		#Hilo dedicado a crear un cliente
		t0 = threading.Thread(target=self.crear_cliente)
		t0.start()
	####################################################
	####             METODOS PARA EL MENU           ####
	####################################################

	def cargar_pantalla(self, index):
		if index in self.pantallas:
			return self.pantallas[index]
		screen = Builder.load_file(self.pantallas_disponibles[index])
		self.pantallas[index] = screen
		return screen

	def go_screen(self, idx):
		self.index = idx
		self.root.ids.sm.switch_to(self.cargar_pantalla(idx), direction='left')



	####################################################
	####      METODOS PARA LAS COMUNICACIONES       ####
	####################################################

	#Metodo para crear un cliente
	def crear_cliente(self):
		
		while self.conexion_con_servidor == False:
			try:
				#Conectar con el servidor
				self.s.connect((self.host, self.port))	
				self.conexion_con_servidor = True
				self.root.ids.conexion.text = 'CONECTADO'
				self.root.ids.conexion.background_disabled_normal='data/icons/wifi_conectado.png'
				#idx = self.screen_names.index('PantallaJuego3')
				#self.go_screen(idx)
				#self.root.ids.sm.get_screen('PantallaJuego3').ids.juego3.comunicaciones.s = self.s
				#self.root.ids.sm.get_screen('PantallaJuego3').ids.juego3.comunicaciones.conexion_con_servidor = True	
				
				print('conexion con servidor establecida')
				#Hilo dedicado a la recepcion de datos del servidor
				t1 = threading.Thread(target=self.recibir_datos)
				t1.start()
			except ConnectionRefusedError as err:
				#print('No se pueder realizar la conexion con el servidor:', err)
				time.sleep(.1)

		print('fin hilo crear cliente')
	
	#Metodo para la recepcion de datos
	def recibir_datos(self):

		while self.conexion_con_servidor == True:
			#Recibir datos del servidor y almacenar en data
			data = self.s.recv(1024)
			#Si el servidor cierra la conexion se cierra y se crea nuevo cliente
			if not data:
				time.sleep(5)
				self.conexion_con_servidor = False
				break

			#Estructura de los datos que se van a recibir
			unpacker = struct.Struct('i ' + 'i ' + 'i ' +str(data[0])+'f')
			self.unpacked_data = unpacker.unpack(data)
			#Llamada al metodo para tratar los datos recibidos
			self.tratar_datos(self.unpacked_data)


		#Cierre conexion socket
		self.s.close()
		self.root.ids.conexion.text = 'DESCONECTADO'
		self.root.ids.conexion.background_disabled_normal='data/icons/wifi_desconectado.png'
		#self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.comunicaciones.conexion_con_servidor = False
	#Metodo para mandar datos al servidor
	def mandar_datos(self,values):
		print('mandar datos')

		if self.conexion_con_servidor == True:
			#Estructura para enviar datos
			packer = struct.Struct('i ' + 'i ' + 'i ' +str(values[0])+'f')
			packed_data = packer.pack (*values)
			
			try:
				self.s.send(packed_data)
			except BrokenPipeError as err:
				print('No se pueder enviar mensaje, conexion perdida:', err)
				self.conexion_con_servidor = False
				time.sleep(2)
	

	#Metodo para interpretar los datos recibidos del servidor	
	def tratar_datos(self,data):

		#Datos para las comunicaciones cliente-servidor
		#Si el servidor indica que quiere cerrar la conexion
		if data[1] == 0 and data[2] == 0:
			values = (0, 0, 0)
			self.mandar_datos(values)#Mandar cerrar conexion con 7inch			
			self.conexion_con_servidor = False

		if data[1] == 0 and data[2] == 1:
			self.conexion_con_servidor = False



		#TRATAMIENTO DE DATOS PARA JUEGO 1
		if data[1] == 1 and self.root.ids.sm.current == 'PantallaJuego1':

			#print(self.comunicaciones.unpacked_data) 
			if data[2] == 2 and self.juego1_habilitado == True:
				self.root.ids.sm.get_screen('PantallaJuego1').ids.matriz.establecer_recorrido_botones(data[3:len(data)])
			
			if data[2] == 1 and self.root.ids.sm.get_screen('PantallaJuego1').ids.matriz.iniciar == False:
				self.juego1_habilitado = True
				#self.root.ids.sm.get_screen('PantallaJuego1').ids.matriz.comienzo_juego()
			
			if data[2] == 3 and self.juego1_habilitado == True: #!= self.comunicaciones.unpacked_data[3:len(self.comunicaciones.unpacked_data)]:
				#posicion = self.comunicaciones.unpacked_data[3:len(self.comunicaciones.unpacked_data)]
				print(data[3:len(data)])
				self.root.ids.sm.get_screen('PantallaJuego1').ids.matriz.posicion_widget(data[3:len(data)])
				self.root.ids.sm.get_screen('PantallaJuego1').ids.matriz.quitar_aviso()
			else:
				self.root.ids.sm.get_screen('PantallaJuego1').ids.matriz.poner_aviso()

			if data[2] == 0:
				self.juego1_habilitado = False
				self.root.ids.sm.get_screen('PantallaJuego1').ids.matriz.reestablecer_juego()


	def actualizar(self):
		while self.iniciar == True:
			# if self.root.ids.sm.current == 'PantallaJuego2':
			# 	self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.comunicaciones.s = self.s
			# 	self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.comunicaciones.conexion_con_servidor = True
			
			if self.root.ids.sm.current == 'PantallaJuego3':
				self.root.ids.sm.get_screen('PantallaJuego3').ids.juego3.comunicaciones.s = self.s
				self.root.ids.sm.get_screen('PantallaJuego3').ids.juego3.comunicaciones.conexion_con_servidor = True	
		

	#Metodo para finalizar la conexion del cliente con el servidor
	def finalizar_conexion(self):
		if self.conexion_con_servidor == True:
			values = (0, 0, 1)
			self.mandar_datos(values)
			time.sleep(2)
			self.conexion_con_servidor = False
		else:
			print('cierre sin conexion')
			self.conexion_con_servidor = True		
			self.s.close()

			

	def finalizar(self):
		print('finalizar')
		self.finalizar_conexion()
		self.iniciar = False


if __name__=='__main__':
    ItaniumApp().run()