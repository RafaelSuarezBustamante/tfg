from socket import *
from threading import Thread
import struct
from enum import Enum
from multiprocessing import Queue
import time

class ServerState(Enum):
    IDLE = 0
    LISTEN = 1
    CONNECT = 2
    EXIT = 3

class Server(object):
    def __init__(self):
        self.fsm = ServerFSM()
        Thread(target=self.serverfsm,).start()

    def serverfsm(self):
        while not self.fsm.current==ServerState.EXIT:
            self.fsm.next()

class ServerFSM(object):
    def __init__(self):
        self.current = ServerState.IDLE                     # Estado inicial del servidor
        self.events = Queue()                               # Cola de eventos para el servidor
        self.data_from_client = Queue()                     # Cola de eventos datos recibidos
        self.host = '0.0.0.0'                               # Host de las comunicaciones
        self.port = 8890                                    # Puerto de comunicaciones
        self.sock = socket(AF_INET, SOCK_STREAM)            # Tipo de sockect en comunicaciones
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)   # Parametros del sockect
        self.sock.bind((self.host, self.port))              #
        self.sock.listen(10)                                #
        self.client_connection = None                       #
        self.data_struct = struct.Struct('25s'+'25s')       # Estructura de datos entrada/salida

    def next(self):
        if not self.events.empty():
            ev = self.events.get()   # Obtener nuevo evento
            self.dispatch_event(ev)  # Procesar nuevo evento

    def create_event(self, ev):
        self.events.put(ev) #Almacenar evento en la cola

    def dispatch_event(self, ev):
        tipo = ev[0] #Tipo de evento. Accion a realizar
        data = ev[1] #Datos para comunicacion con cliente

        if tipo == "init_server":
            Thread(target=self.init_server).start()

        if tipo == "close_server":
            self.close_server()

        if tipo == "reconnect":
            self.reconnect()

        if tipo == "wait_data":
            Thread(target=self.wait_data).start()

        if tipo == "receive_data":
            self.receive_data(data)

        if tipo == "send_data":
            self.send_data(data)

    def send_data(self,data):
        menssage = data
        if self.current == ServerState.CONNECT:
            try:
                packed_data = self.data_struct.pack(*menssage)
                self.client_connection.send(packed_data)
            except Exception:
                print("Fallo en el envio del mensaje")
                self.create_event(("reconnect", ""))

    def wait_data(self):
        if self.current == ServerState.LISTEN:
            self.current = ServerState.CONNECT

            while self.current == ServerState.CONNECT:
                try:
                    print("Esperando a recibir mensaje del cliente")
                    request = self.client_connection.recv(1024)
                    print("mensaje recibido")
                    unpacked_data = self.data_struct.unpack(request)
                    menssage1 = unpacked_data[0].decode('UTF-8').rstrip('\x00')
                    menssage2 = unpacked_data[1].decode('UTF-8').rstrip('\x00')
                    print(menssage1)
                    print(menssage2)
                    self.create_event(("receive_data", (menssage1, menssage2)))

                except Exception:
                    print("Fallo al recibir mensaje ")
                    self.create_event(("reconnect",""))
                    break

    def receive_data(self,data):
        if self.current == ServerState.CONNECT:
            self.data_from_client.put(("data_received",data))


    # Crear el servidor
    def init_server(self):
        if self.current ==  ServerState.IDLE:
            self.current = ServerState.LISTEN
            try:
                self.sock.settimeout(10)
                print("Esperando cliente")
                self.client_connection, client_address = self.sock.accept()
                self.sock.settimeout(None)
                print("Cliente conectado")
                event_serverfsm = ("wait_data","")
                self.create_event(event_serverfsm)
                event = ("tuio2_connect","")
                self.data_from_client.put(event)
            except Exception:
                print("Tiempo agotado. Sin cliente")
                self.create_event(("reconnect", ""))

    #Reconectar el servidor
    def reconnect(self):
        if not self.current == ServerState.EXIT:
            self.current = ServerState.IDLE
            event = ("tuio2_disconnect","")
            self.data_from_client.put(event)
            event = ("init_server", "")
            self.create_event(event)

    #Cerrar el servidor
    def close_server(self):
        self.current = ServerState.EXIT
        if not self.client_connection==None:
            self.client_connection.close()
