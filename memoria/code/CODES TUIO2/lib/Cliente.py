
from socket import *
from enum import Enum
from queue import Queue
import threading
import time
import struct


#--------------------------------------------------------------
# Clase para enumerar los diferentes estados del FSM cliente
#--------------------------------------------------------------
class ClienteEstado(Enum):
	CERRADO = 0
	ESPERA = 1
	ESTABLECIDO = 2

class Cliente(object):
	def __init__(self):
		self.finalizar = False

	def comunicacionesfsm(self):
		self.fsm = ClienteFSM()
		while self.finalizar == False:
			time.sleep(.1)
			self.fsm.next()

#--------------------------------------------------------------
# Clase dedicada a la maquina de estados (FSM) del Cliente 
#--------------------------------------------------------------
class ClienteFSM(object):
	def __init__(self):
		self.current = ClienteEstado.CERRADO
		self.events_input = Queue()
		self.events_fsm = Queue()
		self.events_output = Queue()
		self.host = '0.0.0.0'
		self.port = 9017
		self.create_fsm_event(("create_client"," "))

#--------------------------------------------------------------
# Metodo para obtener, procesar y almacenar eventos relacionados
# con el Cliente FSM
#--------------------------------------------------------------
	def next(self):
		if not self.events_fsm.empty():
			#Obtener evento almacenado
			event = self.events_fsm.get()
			#Procesar/evaluar evento y obtener nuevo evento
			next_event = self.dispatch_event(event)
			#Almacenar nuevo evento
			if next_event != None:
				self.create_fsm_event(next_event)

#--------------------------------------------------------------
# Metodo evaluar los nuevos eventos
#--------------------------------------------------------------
	def dispatch_event(self,ev):
		tipo = ev[0]

		if tipo == "create_client":
			ev = self.create_client()

		if tipo == "wait_server":
			ev = self.wait_server()

		if tipo == "conectado":
			ev = self.conectado()

		if tipo == "wait_input_event":
			t1 = threading.Thread(target=self.wait_input_event)
			t1.start()
			ev = (("check_output_events",))

		if tipo == "check_output_events":
			ev = self.check_output_events()

		if tipo == "send_event":
			ev = self.send_event(*ev[1:])

		if tipo =="closed":
			ev = self.closed()

		if tipo == "terminar":
			ev = self.terminar()

		return ev


	def check_output_events(self):
		if self.current == ClienteEstado.ESTABLECIDO:
			if not self.events_output.empty():
				event_output = self.events_output.get()
				next_event = (("send_event",event_output))
			else:
				next_event = (("check_output_events",))
		
			return next_event

#-------------------------------------------------------------
# Metodo para crear un nuevo cliente
#--------------------------------------------------------------	
	def create_client(self):
		if self.current == ClienteEstado.CERRADO:
			self.current = ClienteEstado.ESPERA
			self.socket = socket(AF_INET, SOCK_STREAM)	
			next_event = (("wait_server",))
			return next_event

#--------------------------------------------------------------
# Metodo para la espera de conectarse con el servidor
#--------------------------------------------------------------
	def wait_server(self):
		if self.current == ClienteEstado.ESPERA:
			try:
				self.socket.connect((self.host, self.port))	
			except ConnectionRefusedError as err:
				next_event = (("wait_server"," "))
				time.sleep(2)
				return next_event
	
		next_event = (("conectado"," "))
		return next_event

#--------------------------------------------------------------------------------
# Metodo que indica la conexion con el servidor
#--------------------------------------------------------------------------------
	def conectado(self):
		if self.current == ClienteEstado.ESPERA:
			self.current = ClienteEstado.ESTABLECIDO
			next_event = (("wait_input_event"," "))
			return next_event

#--------------------------------------------------------------------------------
# Metodo para la espera de un mensaje desde el servidor
#--------------------------------------------------------------------------------
	def wait_input_event(self):
		while self.current == ClienteEstado.ESTABLECIDO:
			time.sleep(.1)
			try:
				data = self.socket.recv(1024)
				event_received = data.decode("utf-8")
				self.events_input.put(event_received)
			except:
				print('conexion no establecida')
				break
		print('fin wait')

#--------------------------------------------------------------
# Metodo para mandar mensajes al servidor 
#--------------------------------------------------------------
	def send_event(self,ev):
		event_to_send = ev
		if self.current == ClienteEstado.ESTABLECIDO:
			try:
				self.socket.send(event_to_send.encode('utf-8'))
			except:
				next_event = (("closed"," "))
				return next_event

#--------------------------------------------------------------
# Metodo para cerrar y crear un nuevo cliente 
#--------------------------------------------------------------
	def closed(self):
		time.sleep(1)
		if self.current ==  ClienteEstado.ESTABLECIDO:
			self.current = ClienteEstado.CERRADO
			try:
				self.socket.shutdown(1)
			except:
				print('error')
			
			self.socket.close()
			next_event = (("create_client"," "))

			return next_event

#--------------------------------------------------------------
# Metodo para cerrar cliente y terminar conexion con el servidor
#--------------------------------------------------------------
	def terminar(self):
		print('finalizando')
		self.current = ClienteEstado.CERRADO
		try:
			self.socket.shutdown(1)
		except:
			print('error')
		self.socket.close()

	def create_input_event(self,ev):
		input_event = ev
		self.events_input.put(input_event)

#--------------------------------------------------------------
# Metodo para crear nuevos eventos recibidos desde el servidor 
#--------------------------------------------------------------
	def create_fsm_event(self,ev):
		self.events_fsm.put(ev)

if __name__=='__main__':
	Comunicaciones()
