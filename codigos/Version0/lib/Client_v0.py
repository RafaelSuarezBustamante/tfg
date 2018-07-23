from socket import *
from threading import Thread
import struct
from enum import Enum
from multiprocessing import Queue
import time


class ClientState(Enum):
    CLOSED = 0
    LISTEN = 1
    ESTABLECIDO = 2
    EXIT = 3

class Client(object):
    def __init__(self):
        self.fsm = ClientFSM()
        Thread(target=self.clientfsm,).start()

    def clientfsm(self):
        while not self.fsm.current == ClientState.EXIT:
            self.fsm.next()

class ClientFSM(object):
    def __init__(self):
        #Estado inicial Cliente FSM
        self.current = ClientState.CLOSED
        #Lista de eventos Cliente FSM
        self.events = Queue()
        #Datos recibidos desde el servidor (TUIO1)
        self.data_from_server = Queue()
        #Parametros del cliente
        self.host = 'localhost'
        self.port = 8890
        self.client_connection = socket(AF_INET, SOCK_STREAM)
        #Estructura de los datos a enviar
        self.data_struct = struct.Struct('25s'+'25s')

    #Proximo eventos Cliente FSM
    def next(self):
        if not self.events.empty():
            #Obtener nuevo evento
            ev = self.events.get()
            #Procesar nuevo evento
            self.dispatch_event(ev)

    #Crear evento Cliente FSM
    def create_event(self, ev):
        print('EVENTO', ev)
        self.events.put(ev)

    #Ejecutar tipo de evento Cliente FSM
    def dispatch_event(self, ev):
        tipo = ev[0] #Tipo de evento. Accion a ejecutar en cliente FSM
        data = ev[1] #Datos para comunicacion con servidor (TUIO1)
        print('TIPO CLIENTE', tipo)

        #Tipo de evento: Cerrar cliente
        if tipo == "close_client":
            self.close_client()

        #Tipo de evento: Reconnectar con el servidor
        if tipo == "reconnect":
            self.reconnect()

        #Tipo de evento: Crear cliente
        if tipo == "init_client":
            self.init_client()

        #Tipo de evento: Esperar datos desde servidor (TUIO1)
        if tipo == "wait_data":
            Thread(target=self.wait_data).start()

        #Tipo de evento: Datos recibidos desde el servidor (TUIO1)
        if tipo == "receive_data":
            print('MENSAJE RECIBIDO')
            print(data)
            self.data_from_server.put(("data_received",data))

        #Tipo de evento: Mandar datos a servidor (TUIO1)
        if tipo == "send_data":
            self.send_data(data)

    #Mandar datos al servidor
    def send_data(self,data):
        menssage = data
        if self.current == ClientState.ESTABLECIDO:
            try:
                packed_data = self.data_struct.pack(*menssage)
                self.client_connection.send(packed_data)
            except Exception:
                print("Fallo en el envio del mensaje")
                self.create_event(("reconnect", ""))

    #Esperar datos desde servidor (TUIO1)
    def wait_data(self):
        if self.current == ClientState.LISTEN:
            self.current = ClientState.ESTABLECIDO

            while self.current == ClientState.ESTABLECIDO:
                try:
                    print("Esperando a recibir mensaje del servidor")
                    request = self.client_connection.recv(1024)
                    print("mensaje recibido")
                    unpacked_data = self.data_struct.unpack(request)
                    menssage1 = unpacked_data[0].decode('UTF-8').rstrip('\x00')
                    menssage2 = unpacked_data[1].decode('UTF-8').rstrip('\x00')
                    print(menssage1)
                    print(menssage2)
                    self.create_event(("receive_data", (menssage1,menssage2)))

                except Exception:
                    print("Fallo al recibir mensaje ")
                    self.create_event(("reconnect", ""))
                    break

    #Crear cliente
    def init_client(self):
        if self.current ==  ClientState.CLOSED:
            self.current = ClientState.LISTEN
            try:
                print("Esperando servidor.")
                self.client_connection.settimeout(10)
                self.client_connection.connect((self.host, self.port))
                self.client_connection.settimeout(None)
                print("Servidor conectado")
                event = ("wait_data","")
                self.create_event(event)
                event = ("tuio1_connect","")
                self.data_from_server.put(event)
            except Exception:
                print("Sin servidor")
                time.sleep(5)
                self.create_event(("reconnect", ""))


    #Reconectar el cliente
    def reconnect(self):
        if not self.current == ClientState.EXIT:
            self.current = ClientState.CLOSED
            event = ("tuio2_disconnect", "")
            self.data_from_server.put(event)
            event = ("init_client", "")
            self.create_event(event)

    # Cerrar cliente. Finalizar comunicaciones
    def close_client(self):
        self.current = ClientState.EXIT
        if not self.client_connection == None:
            self.client_connection.close()
