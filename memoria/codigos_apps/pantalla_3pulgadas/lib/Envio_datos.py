from socket import *
import struct
import threading
import time

class Envio_datos(object):
	"""docstring for Envio_recepcion"""
	def __init__(self, **kwargs):
		print('ENVIO RECEPCION DE DATOS')
		super(Envio_datos, self).__init__(**kwargs)
		self.conexion_con_servidor = False
		self.s = None

	#Metodo para mandar datos al servidor
	def mandar_datos(self,values):

		if self.conexion_con_servidor == 1:
			#Estructura para enviar datos
			packer = struct.Struct('i ' + 'i ' + 'i ' +str(values[0])+'f')
			packed_data = packer.pack (*values)
			
			try:
				self.s.send(packed_data)
			except BrokenPipeError as err:
				print('No se pueder enviar mensaje, conexion perdida:', err)
				self.conexion_con_servidor = 0
				time.sleep(2)
		else:
			print('no hay conexion con servidor')