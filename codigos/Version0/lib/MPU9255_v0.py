# -*- coding: utf-8 -*-

from multiprocessing import Queue
from threading import Thread
from enum import Enum


class MPU9255State(Enum):
    SLEEP = 0
    DATA = 1
    EXIT = 2

class Mpu9255(object):
    def __init__(self):
        self.fsm = Mpu9255FSM()
        Thread(target=self.mpu9255fsm,).start()

    def mpu9255fsm(self):
        while not self.fsm.current == MPU9255State.EXIT:
            self.fsm.next()

class Mpu9255FSM(object):
    def __init__(self):
        self.current = MPU9255State.SLEEP
        self.events = Queue()
        self.data_sensor = Queue()

    #Proximo evento
    def next(self):
        if not self.events.empty():
            #Obtener nuevo evento
            ev = self.events.get()
            #Procesar nuevo evento
            self.dispatch_event(ev)

    #Crear evento
    def create_event(self, ev):
        print('EVENTO MPU', ev)
        self.events.put(ev)

    #Manejo de eventos
    def dispatch_event(self, ev):
        tipo = ev[0]
        data = ev[1]
        print('EVENTO T', tipo)

        if tipo == "sleep_mode":
            self.sleep_mode()


        if tipo == "data_sensor":
            self.sensor_values()

        if tipo == "exit_mpu9255":
            self.exit_mpu9255()

    def sleep_mode(self):
        if self.current == MPU9255State.DATA:
            self.current = MPU9255State.SLEEP

    def sensor_values(self):
        if self.current == MPU9255State.SLEEP:
            self.current = MPU9255State.DATA
            while self.current == MPU9255State.DATA:
                data = (b'MPU9255_giroscopio', b'(datos)')
                event = ("send_data",data)
                self.data_sensor.put(event)
                self.current = MPU9255State.SLEEP

    def exit_mpu9255(self):
        self.current = MPU9255State.EXIT
