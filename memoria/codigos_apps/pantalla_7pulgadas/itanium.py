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
import threading
from multiprocessing.pool import ThreadPool
from kivy.clock import Clock
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

		#########################################################################
		############## COMUNICACIONES DEL SERVIDOR CON EL CLIENTE ###############
		#########################################################################
		self.host = '0.0.0.0' 								#host del servidor
		self.port = 8909									#puerto de escucha      
		self.sock= socket(AF_INET, SOCK_STREAM)				#
		self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.finalizar_cliente = False
		self.conectar = False
		self.conexion_con_cliente = False
		self.sock.bind((self.host, self.port))
		self.sock.listen(10)
		self.unpacked_data = ''
		self.t0 = threading.Thread(target=self.recibir_datos)
		self.t0.start()

		self.root.ids.conexion.text = 'DESCONECTADO'
		self.root.ids.conexion.background_disabled_normal='data/icons/wifi_desconectado.png'


		self.iniciar = True
		self.iniciar3 = False
		
		#Variables juego 1
		self.estado_juego = 0
		self.recorrido_botones = 0
		self.posicion_widget = (0,8,8)
		
		#self.comunicaciones = Comunicaciones()
		#self.juego1 = Juego1.Matriz_juego()
		#self.comunicaciones = Comunicaciones_servidor.Comunicaciones7()
		print('servidor creado')
		self.datos_posicion = 0
		self.datos_trayectoria = 0

		#########################################################################
		##############        ADMINISTRACION DE PANTALLAS         ###############
		#########################################################################
		#Objeto dedicado a almacenar los datos de los archivos .kv de cada una
		#de las pantallas
		self.pantallas = {} 
		#Listado de las pantallas disponibles
		self.pantallas_disponibles = sorted([
            						'PantallaPrincipal','PantallaJuegos','PantallaAyuda',
            						'PantallaConfigurar','PantallaJuego1','PantallaJuego2',
            						'PantallaJuego3' ])
		#Copia de los nombres de las pantallas para ser usados simplemente en el acceso
		self.screen_names = self.pantallas_disponibles
		#Se crea un listado con la ruta de cada una de las pantallas en formato .kv
		directorio = dirname(__file__)
		self.pantallas_disponibles = [join(directorio, 'data', 'pantallas',
			'{}.kv'.format(fn).lower()) for fn in self.pantallas_disponibles]
		
		#Cargar toda la lista de pantallas disponibles.
		#for i in range(len(self.pantallas_disponibles)-1):
			#self.go_screen(i)
		
		#Cargar la pantalla principal
		idx = self.screen_names.index('PantallaPrincipal')
		self.go_screen(idx)


	#Metodo para cargar el codigo de la pantalla
	def cargar_pantalla(self, index):
		if index in self.pantallas:
			return self.pantallas[index]
		screen = Builder.load_file(self.pantallas_disponibles[index])
		self.pantallas[index] = screen
		return screen

	#Metodo para mostrar la pantalla deseada
	def go_screen(self, idx):
		self.index = idx
		self.root.ids.sm.switch_to(self.cargar_pantalla(idx), direction='left')

		# if idx == self.screen_names.index('PantallaJuego3'):
		# 	t0 = threading.Thread(target=self.root.ids.sm.get_screen('PantallaJuego3').ids.juego3.update())
		# 	t0.start()

	def mandar_datos(self,values):

		if self.conexion_con_cliente == True:
			try:
				packer = struct.Struct('i ' + 'i ' + 'i ' +str(values[0])+'f')
				packed_data = packer.pack (*values)
				self.con.send(packed_data)
				print('enviando values', values)
			except BrokenPipeError as err:
				print('No se pueder enviar mensaje, conexion perdida:', err)
				time.sleep(2)

		else:
			print('No es posible mandar datos')
	
	def recibir_datos(self):
	#Recibir datos pantalla 3.5inch
		while self.finalizar_cliente == False :
			#self.unpacker = struct.Struct('i f f f ? ?')
			print('esperando cliente')
			self.con, addr = self.sock.accept()
			self.root.ids.conexion.text = 'CONECTADO'
			self.root.ids.conexion.background_disabled_normal='data/icons/wifi_conectado.png'
			self.conexion_con_cliente = True
			print('cliente conectado')
			while self.conexion_con_cliente == True:
				try:
					data = self.con.recv(1024)
				except ConnectionResetError as err:
					print('No se pueder realizar la conexion con el cliente:', err)
					time.sleep(2)

				#Si el cliente cierra su conexion, el servidor
				#queda a la espera de un nuevo cliente
				if not data:
					print('Finalizar cliente actual')
					self.conexion_con_cliente = False
					break

				#Se extraen los datos recibidos para ser tratados
				unpacker = struct.Struct('i ' + 'i ' + 'i ' +str(data[0])+'f')
				unpacked_data = unpacker.unpack(data)
				#self.datos = unpacked_data
				print(unpacked_data)
				#Se invoca a la funcion para tratar los datos recibidos
				#self.tratar_datos(unpacked_data)
				#return

			self.con.close()
			
		print('cierro recepcion de datos')

	#Función para interpretar los datos recibidos
	def tratar_datos(self,data):
		
		#Finalizar servidor por peticion del mismo servidor
		if data[1] == 0 and data[2] == 0:
			self.conexion_con_cliente = False
			self.finalizar_cliente = True
		
		#Finalizar cliente a peticion del cliente 
		if data[1] == 0 and data[2] == 1:
			values = (0, 0, 1)
			self.mandar_datos(values)#Mandar cerrar conexion con 7inch
			print('mando datos para finalizar')
			#time.sleep(2)
			self.conexion_con_cliente = False
			self.finalizar_cliente = True

		#########################################################
		#######  TRATAMIENTO DE DATOS PARA EL JUEGO2    #########
		#########################################################
		# if data[2] == 1 and self.root.ids.sm.current == 'PantallaJuego2':
		# 	if data[2] == 2 and self.juego_habilitado == True:
		# 		self.root.ids.sm.get_screen('PantallaJuego1').ids.matriz.establecer_recorrido_botones(data[3:len(data)])

		if data[1] == 2 and self.root.ids.sm.current == 'PantallaJuego2':

			if data[2] == 0:
				self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.iniciar = False
			
			if data[2] == 1:
				self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.iniciar = True

			if data[2] == 2:
				self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.mover_arriba()
			
			if data[2] == 3:
				self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.mover_abajo()

			if data[2] == 4:
				self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.mover_izquierda()

			if data[2] == 5:
				self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.mover_derecha()

			if data[2] == 6:
				self.root.ids.sm.get_screen('PantallaJuego2').ids.juego2.crear_pieza(int(data[3]))


		if data[1] == 3 and self.root.ids.sm.current == 'PantallaJuego3':

			if data[2] == 0:
				self.root.ids.sm.get_screen('PantallaJuego3').ids.juego3.iniciar3 = False
			
			if data[2] == 1:
				self.root.ids.sm.get_screen('PantallaJuego3').ids.juego3.iniciar3 = True

			print(data)


	# ## Funcion para finalizar conexion con cliente y cerrar servidor
	# # Si existe conexion con cliente, se envia un mensaje al cliente
	# # para indicar que se quiere cerrar la conexion (el cliente queda
	# # a la espera de que vuelva a conectarse el servidor)

	# # Si no existe conexion con ningun cliente se crea un cliente local
	# # para finalizar la espera de un cliente por parte del servidor y 
	# # finalmente se cierra el servidor
	def finalizar_conexion(self):
		print('finalizar conexion')
		if self.conexion_con_cliente == True:
			values = (0, 0, 0)
			self.mandar_datos(values) #Pecition de mensaje finalizar por parte del servidor al cliente
		else:
			s = socket(AF_INET, SOCK_STREAM)
			s.connect(('localhost', self.port))
			values = (0, 0, 0)
			packer = struct.Struct('i ' + 'i ' + 'i ' +str(values[0])+'f')
			packed_data = packer.pack (*values)
			s.send(packed_data) #Peticion desde el propio servidor para finalizar 
			s.close()
			self.finalizar_cliente = True
			self.conexion_con_cliente = False

	def finalizar(self):
		if self.root.ids.sm.current == 'PantallaJuego3':
			self.root.ids.sm.get_screen('PantallaJuego3').ids.juego3.finalizar()


if __name__=='__main__':
    ItaniumApp().run()

