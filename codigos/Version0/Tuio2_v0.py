from multiprocessing import Queue
from threading import Thread
from lib import Client_v0
from lib import MPU9255_v0
from enum import Enum
import time


class Tuio2State(Enum):
    IDLE = 0
    MAIN = 1
    GAME = 2
    EXIT = 3

class Tuio2(object):
    def __init__(self):
        self.fsm = Tuio2FSM()
        Thread(target=self.tuio2fsm,).start()

    def tuio2fsm(self):
        while not self.fsm.current == Tuio2State.EXIT:
            self.fsm.next()

class Tuio2FSM(object):
    def __init__(self):
        self.client = Client_v0.Client()
        event = ("init_client","")
        self.client.fsm.create_event(event)
        self.imu_sensor = MPU9255_v0.Mpu9255()
        self.current = Tuio2State.IDLE
        self.events = Queue()

    # Proximo evento
    def next(self):
        # Eventos FSM TUIO2
        if not self.events.empty():
            #Obtener nuevo evento
            ev = self.events.get()
            #Procesar nuevo evento
            self.dispatch_event(ev)

        # Eventos recibidos desde TUIO1 (Server)
        if not self.client.fsm.data_from_server.empty():
            #Eventos del servidor
            ev = self.client.fsm.data_from_server.get()
            self.dispatch_event(ev)

        # Eventos MPU9255(Sensor)
        if not self.imu_sensor.fsm.data_sensor.empty():
            ev = self.imu_sensor.fsm.data_sensor.get()
            self.dispatch_event(ev)


    #Crear evento
    def create_event(self, ev):
        self.events.put(ev)

    #Manejo de eventos
    def dispatch_event(self, ev):
        tipo = ev[0] #Tipo de evento
        datos = ev[1]
        print('EVENTO TUIO2', ev)

        if tipo == "tuio1_connect":
            self.tuio1_connect()

        if tipo == "tuio1_disconnect":
            self.tuio1_disconnect()

        if tipo == "start_game":
            self.start_game()

        if tipo == "stop_game":
            self.stop_game()

        # Tipo de evento: Datos recibidos de TUIO1
        if tipo == "receive_data":
            self.data_treatment(datos)

        # Tipo de evento: Mandar datos a TUIO1
        if tipo == "send_data":
            self.send_data(datos)

        # Tipo de evento: Apagar dispositivo
        if tipo == "close_tuio2":
            self.close_tuio2()




    #---------------------------------------------------------------------------------
    #                         TRANSICIONES FSM TUIO1
    #---------------------------------------------------------------------------------

    # Metodo para transicion de estado IDLE a MAIN.
    # El dispositivo TUIO1 esta conectado.
    def tuio1_connect(self):
        if self.current == Tuio2State.IDLE:
            self.current = Tuio2State.MAIN
            print("TUIO1 CONECTADO")

    #Transicion al estado IDLE
    # El dispositivo TUIO1 esta desconectado
    def tuio1_disconnect(self):
        self.current = Tuio2State.IDLE
        print("TUIO1 DESCONECTADO")

    def start_game(self):
        if self.current == Tuio2State.MAIN:
            self.current = Tuio2State.GAME

    def stop_game(self):
        if self.current == Tuio2State.GAME:
            self.current = Tuio2State.MAIN


    def send_data(self,data):
        if self.current == Tuio2State.GAME:
            event = ("send_data",data)
            self.client.fsm.create_event(event)

    # Tratar datos recibidos desde TUIO1
    def data_treatment(self,datos):
        tipo = datos[0]
        accion = datos[1]
        print("tipo", tipo)
        print("accion", accion)

        if tipo == "start_game":
            event = ("start_game","")
            self.create_event(event)

        if tipo == "mpu_9255":
            event = ("data_sensor","")
            self.imu_sensor.fsm.create_event(event)
            print('CREADO EVENTO PARA SENSOR MPU9255')

  # Salir del dispositivo TUIO2
    def close_tuio2(self):
        self.current = Tuio2State.EXIT
        event = ("close_client","")
        self.client.fsm.create_event(event)
        event = ("exit_mpu9255","")
        self.imu_sensor.fsm.create_event(event)
        print("EXIT TUIO2!")


if __name__ == '__main__':
    tuio2 = Tuio2()
    time.sleep(50)
    event = ("close_tuio2", "")
    tuio2.fsm.create_event(event)
