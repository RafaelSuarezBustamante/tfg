import struct
from enum import Enum
from multiprocessing import Queue
from socket import *
from threading import Thread

class ServerState(Enum):
    IDLE = 0
    LISTEN = 1
    CONNECT = 2
    EXIT = 3

class ServerFSM(object):
    def __init__(self):
        self.current = ServerState.IDLE  # Estado inicial del servidor
        self.server_events = Queue()  # Cola de eventos datos recibidos
        self.host = '0.0.0.0'  # Host de las comunicaciones
        self.port = 8807  # Puerto de comunicaciones
        self.sock = socket(AF_INET, SOCK_STREAM)  # Tipo de sockect en comunicaciones
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Parametros del sockect
        self.sock.bind((self.host, self.port))  #
        self.sock.listen(10)  #
        self.client_connection = None  #
        self.data_struct = struct.Struct('25s' + '25s' + '4f')  # Estructura de datos entrada/salida

    def send_data(self, data):
        menssage = data
        if self.current == ServerState.CONNECT:
            try:
                packed_data = self.data_struct.pack(*menssage)
                self.client_connection.send(packed_data)
            except Exception:
                event = ("tuio2_disconnect", "")
                self.server_events.put(event)
                self.reconnect()

    def thread_wait_data(self):
        Thread(target=self.wait_data, ).start()

    def wait_data(self):
        if self.current == ServerState.LISTEN:
            self.current = ServerState.CONNECT

            while self.current == ServerState.CONNECT:
                try:
                    request = self.client_connection.recv(68)
                    unpacked_data = self.data_struct.unpack(request)
                    menssage1 = unpacked_data[0].decode('UTF-8').rstrip('\x00')
                    menssage2 = unpacked_data[1].decode('UTF-8').rstrip('\x00')
                    menssage3 = unpacked_data[2]
                    menssage4 = unpacked_data[3]
                    menssage5 = unpacked_data[4]
                    menssage6 = unpacked_data[5]
                    data = (menssage1, menssage2, (menssage3, menssage4, menssage5, menssage6))
                    self.receive_data(data)
                except Exception:

                    event = ("tuio2_disconnect", "")
                    self.server_events.put(event)
                    self.reconnect()
                    break

    def receive_data(self, data):
        if self.current == ServerState.CONNECT:
            event = data
            self.server_events.put(event)

    def thread_init_server(self):
        Thread(target=self.init_server, ).start()

    # Crear el servidor
    def init_server(self):
        if self.current == ServerState.IDLE:
            self.current = ServerState.LISTEN

            try:
                self.sock.settimeout(10)
                self.client_connection, client_address = self.sock.accept()
                self.sock.settimeout(None)
                self.thread_wait_data()
                event = ("tuio2_connect", "")
                self.server_events.put(event)

            except Exception:
                event = ("tuio2_disconnect", "")
                self.server_events.put(event)
                self.reconnect()

    # Reconectar el servidor
    def reconnect(self):
        if not self.current == ServerState.EXIT:
            self.current = ServerState.IDLE
            self.thread_init_server()

    # Cerrar el servidor
    def close_server(self):
        self.current = ServerState.EXIT
        if not self.client_connection is None:
            self.client_connection.close()
