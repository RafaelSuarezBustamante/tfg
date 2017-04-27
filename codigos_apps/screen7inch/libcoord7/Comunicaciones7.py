from socket import *
import struct
import threading
import time


class Comunicaciones7(object):

	def __init__(self, **kwargs):
		print('Comunicaciones mandar datos')
		super(Comunicaciones7, self).__init__(**kwargs)
		''' Inicializacion canal envio de datos'''
		self.host = '0.0.0.0'
		self.port = 9006
		self.sock= socket(AF_INET, SOCK_STREAM)
		self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))
		self.sock.listen(10)
		self.finalizar = False
		self.conectar = False
		self.conexion_establecida = False
		self.packer = struct.Struct('f f f ? ?')
		self.datos = []
		self.t0 = threading.Thread(target=self.recibir_datos)
		self.t0.start()

	
	def mandar_datos(self,values):

		if self.conexion_establecida == True:
			print('Mandando Datos')
			packed_data = self.packer.pack (*values)
			self.con.send(packed_data)
		else:
			print('No es posible mandar datos')
	
	def recibir_datos(self):
	#Recibir datos pantalla 3.5inch
		while self.finalizar == False :
			unpacker = struct.Struct('f f f ? ?')
			print('esperando cliente')
			self.con, addr = self.sock.accept()
			self.conexion_establecida = True
			print('cliente conectado')

			while self.conexion_establecida == True:
				print('conexion establecida')
				data = self.con.recv(unpacker.size)
				if not data:
					self.conexion_establecida = False
					break
				unpacked_data = unpacker.unpack(data)
				if unpacked_data[4] == 1:
					self.conexion_establecida = False
					self.finalizar = True
					break	
				self.tratar_datos(unpacked_data)
			self.con.close()
		print('cierro recepcion de datos')

	def tratar_datos(self,data):
		self.datos.append(data[0])
		self.datos.append(data[1])
		self.datos.append(data[2])
		finalizar_35inch = data[3]
		if finalizar_35inch == True:
			values = (0.0, 0.0, 0.0 , 1, 0)
			self.mandar_datos(values)#Mandar cerrar conexion con 7inch

	def finalizar_conexion(self):
		if self.conexion_establecida == True:
			values = (0.0, 0.0, 0.0 , 0, 1)
			self.mandar_datos(values)
		else:
			s = socket(AF_INET, SOCK_STREAM)
			s.connect(('localhost', self.port))
			values = (0.0, 0.0, 0.0 , 0, 1)
			packed_data = self.packer.pack (*values)
			s.send(packed_data)
			s.close()
			self.finalizar = True
			self.conexion_establecida = False


			
