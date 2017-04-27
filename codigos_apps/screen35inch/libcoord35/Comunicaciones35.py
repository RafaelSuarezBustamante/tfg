from socket import *
import struct
import threading
import time

'''Clase dedicada a las comunicaciones desde el dispositivos;
pantalla 3,5 pulgadas con la pantalla de 7 pulgadas '''

class Comunicaciones35(object):
	#Constructor para las comunicaciones entre ambos dispositivos.
	def __init__(self, **kwargs):
		print('Comunicaciones mandar datos')
		super(Comunicaciones35, self).__init__(**kwargs)
		#Parametros de inicializacion del socket
		self.host = '192.168.0.156' #host del servidor
		self.port = 9006		    #puerto de escucha del servidor
		self.s = socket(AF_INET, SOCK_STREAM)
		
		#Atributo dedicado a indicar el estado de la conexion:
		self.conexion_establecida = 0
		'''Conexion no establecida                         -- 0
		   Conexion establecida                            -- 1
		   Servidor cerrado (cerrar y crear nuevo cliente) -- 2
		   Cerrar cliente                                  -- 3'''
		
		#Variable dedicada al almacenamiento de los datos recibidos
		self.datos = []
		
		#Estructura de los datos enviados y recibidos(3 float, 2 bool)
		self.unpacker = self.packer struct.Struct('f f f ? ?')
		
		#Hilo dedicado a crear un cliente
		self.t0 = threading.Thread(target=self.crear_cliente)
		self.t0.start()
	
	#Metodo para crear un cliente
	def crear_cliente(self):
		
		while self.conexion_establecida == 0:

			try:
				#Conectar con el servidor
				self.s.connect((self.host, self.port))	
				self.conexion_establecida = 1
				#Hilo dedicado a la recepcion de datos del servidor
				t1 = threading.Thread(target=self.recibir_datos)
				t1.start()
			except ConnectionRefusedError as err:
				print('No se pueder realizar la conexion con el servidor:', err)
				time.sleep(2)

		print('fin hilo crear cliente')
	
	#Metodo para la recepcion de datos
	def recibir_datos(self):

		while self.conexion_establecida == 1:
			#Recibir datos del servidor y almacenar en data
			data = self.s.recv(self.unpacker.size)
			
			#Si el servidor cierra la conexion se cierra y se crea nuevo cliente
			if not data:
				time.sleep(5)
				self.conexion_establecida = 2
				break

			#Estructura de los datos que se van a recibir
			unpacked_data = self.unpacker.unpack(data)
			
			#Llamada al metodo para tratar los datos recibidos
			self.tratar_datos(unpacked_data)

			#Cierre de hilo y crea nuevo cliente si el servidor indica que cierra conexion
			if unpacked_data[4] == 1:
				time.sleep(5)
				self.conexion_establecida = 2
				break

		#Cierre conexion socket
		self.s.close()

	#Metodo para mandar datos al servidor
	def mandar_datos(self,values):

		if self.conexion_establecida == 1:
			#Estructura para enviar datos
			packed_data = self.packer.pack (*values)
			#Mandar datos al servidor
			self.s.send(packed_data)

	#Metodo para interpretar los datos recibidos del servidor	
	def tratar_datos(self,data):
		self.datos.append(data[0])
		self.datos.append(data[1])
		self.datos.append(data[2])

		#Si el servidor indica que quiere cerrar la conexion
		if data[4] == True:
			values = (0.0, 0.0, 0.0 , 0, 1)
			self.mandar_datos(values)#Mandar cerrar conexion con 7inch


	#Metodo para finalizar la conexion del cliente con el servidor
	def finalizar_conexion(self):
		if self.conexion_establecida == 0:
			self.conexion_establecida = 3
			self.s.close()
		else:		
			values = (0.0, 0.0, 2.4 , 1, 0)
			self.mandar_datos(values)
			self.conexion_establecida = 3



