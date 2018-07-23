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


class ClientFSM(object):
    def __init__(self):
        #Estado inicial Cliente FSM
        self.current = ClientState.CLOSED
        #Datos recibidos desde el servidor (TUIO1)
        self.client_events = Queue()
        #Parametros del cliente
        self.host = 'localhost'
        #self.host = '192.168.1.2'
        self.port = 8807
        self.client_connection = socket(AF_INET, SOCK_STREAM)
        #Estructura de los datos a enviar
        self.data_struct = struct.Struct('25s'+'25s'+'4f')

    def thread_send_data(self, data):
        Thread(target=self.send_data, args=(data, ) ).start()

    #Mandar datos al servidor
    def send_data(self,data):
        menssage = data
        if self.current == ClientState.ESTABLECIDO:
            try:

                packed_data = self.data_struct.pack(*menssage)
                self.client_connection.send(packed_data)
            except Exception:

                self.reconnect()

    def thread_wait_data(self):
        Thread(target=self.wait_data, ).start()

    #Esperar datos desde servidor (TUIO1)
    def wait_data(self):
        if self.current == ClientState.LISTEN:
            self.current = ClientState.ESTABLECIDO

            while self.current == ClientState.ESTABLECIDO:
                try:
                    request = self.client_connection.recv(68)
                    unpacked_data = self.data_struct.unpack(request)
                    menssage1 = unpacked_data[0].decode('UTF-8').rstrip('\x00')
                    menssage2 = unpacked_data[1].decode('UTF-8').rstrip('\x00')
                    menssage3 = unpacked_data[2]
                    menssage4 = unpacked_data[3]
                    menssage5 = unpacked_data[4]
                    menssage6 = unpacked_data[5]

                    data= ((menssage1, menssage2, (menssage3, menssage4, menssage5, menssage6)))
                    self.receive_data(data)

                except Exception:
                    self.reconnect()
                    break

    def receive_data(self, data):
        if self.current == ClientState.ESTABLECIDO:
            event = data
            self.client_events.put(event)

    def thread_init_client(self):
        Thread(target=self.init_client, ).start()

    #Crear cliente
    def init_client(self):
        if self.current ==  ClientState.CLOSED:
            self.current = ClientState.LISTEN
            try:
                self.client_connection.settimeout(10)
                self.client_connection.connect((self.host, self.port))
                self.client_connection.settimeout(None)
                self.thread_wait_data()
                event = ("tuio1_connect","")
                self.client_events.put(event)
            except Exception:
                time.sleep(5)
                self.reconnect()


    #Reconectar el cliente
    def reconnect(self):
        if not self.current == ClientState.EXIT:
            self.current = ClientState.CLOSED
            event = ("tuio1_disconnect", "")
            self.client_events.put(event)
            self.thread_init_client()

    # Cerrar cliente. Finalizar comunicaciones
    def close_client(self):
        self.current = ClientState.EXIT
        if not self.client_connection is None:
            self.client_connection.close()

