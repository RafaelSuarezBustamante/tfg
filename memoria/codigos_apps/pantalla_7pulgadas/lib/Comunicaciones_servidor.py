from socket import *
import struct
import threading
import time


class Comunicaciones7(object):

	def __init__(self, **kwargs):
		super(Comunicaciones7, self).__init__(**kwargs)
		''' Inicializacion canal envio de datos'''
		self.host = '0.0.0.0'
		self.port = 8960
		self.sock= socket(AF_INET, SOCK_STREAM)
		self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.finalizar_cliente = False
		self.conectar = False
		self.conexion_con_cliente = False
		self.sock.bind((self.host, self.port))
		self.sock.listen(10)
		self.unpacked_data = ''
		self.t0 = threading.Thread(target=self.recibir_datos)
		self.t0.start()

	def mandar_datos(self,values):

		if self.conexion_con_cliente == True:
			try:
				packer = struct.Struct('i ' + 'i ' + 'i ' +str(values[0])+'f')
				packed_data = packer.pack (*values)
				self.con.send(packed_data)
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
				
				#Se invoca a la funcion para tratar los datos recibidos
				self.tratar_datos(unpacked_data)
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

	## Funcion para finalizar conexion con cliente y cerrar servidor
	# Si existe conexion con cliente, se envia un mensaje al cliente
	# para indicar que se quiere cerrar la conexion (el cliente queda
	# a la espera de que vuelva a conectarse el servidor)

	# Si no existe conexion con ningun cliente se crea un cliente local
	# para finalizar la espera de un cliente por parte del servidor y 
	# finalmente se cierra el servidor
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


			