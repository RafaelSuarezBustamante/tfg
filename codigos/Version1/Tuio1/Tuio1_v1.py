# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------
#                               MODULOS Y LIBRERIAS
# ---------------------------------------------------------------------------------
from multiprocessing import Queue
from threading import Thread
from lib import Server_v1, InterfaceManagement, PaintGame, CaptureGame
from enum import Enum
import time
from kivy.clock import Clock

# ---------------------------------------------------------------------------------
#                               ESTADOS FSM TUIO1
# ---------------------------------------------------------------------------------
class Tuio1State(Enum):
    IDLE = 0  # Estado inicial de la maquina de estados. Sin comunicaciones
    MAIN = 1  # Estado principal de la aplicación. Comunicaciones establecidas.
    GAME = 2  # Juego activo.
    EXIT = 3  # Estado final de la aplicación


# ---------------------------------------------------------------------------------
#                           MAQUINA DE ESTADOS FSM TUIO1
# ---------------------------------------------------------------------------------

class Tuio1FSM(object):
    def __init__(self):
        self.current = Tuio1State.IDLE  # Estado inicial de TUIO1
        self.server = Server_v1.ServerFSM()  # Objeto para las comunicaciones
        self.interface = InterfaceManagement.InterfaceManagement()
        self.paint_game = PaintGame.PaintGameFSM()
        self.capture_game = CaptureGame.CaptureGameFSM()
        self.init_plataform()
        self.start_thread_next()

    def start_thread_next(self):
        Thread(target=self.thread_next, ).start()

    def thread_next(self):
        Clock.schedule_interval(self.next, 0.01)

    # Obtener proximo evento
    def next(self, dt):

        if not self.current == Tuio1State.EXIT:

            # Eventos servidor (datos de entrada TUIO2/client)
            if not self.server.server_events.empty():
                ev = self.server.server_events.get()  # Obtener evento de comunicaciones
                self.dispatch_event(ev)

            self.interface.next()
            if not self.interface.external_events.empty():
                ev = self.interface.external_events.get()
                self.dispatch_event(ev)

            self.paint_game.next()

            self.capture_game.next()
            if not self.capture_game.external_events.empty():
                ev = self.capture_game.external_events.get()
                self.dispatch_event(ev)

    def dispatch_event(self, ev):
        event_type = ev[0]
        givens = ev[1:]
        
        if event_type == "init_plataform":
            self.init_plataform()

        # Evento empezar juego en ambos dispositivos
        if event_type == "start_game":
            self.start_game(givens)

        if event_type == "send_data":
            self.server.send_data(*givens)

        # Evento detener juego en ambos dispositivos
        if event_type == "stop_game":
            self.stop_game(givens)

        # Evento salir del dispositivo TUIO1
        if event_type == "exit_tuio1":
            self.exit_tuio1()

        if event_type == "paint_game":
            self.paint_game.internal_events.put(givens)

        if event_type =="capture_game":
            self.capture_game.internal_events.put(givens)

        # Evento dispositivo TUIO2 conectado. Llama al método tuio2_connect()
        if event_type == "tuio2_connect":
            self.tuio2_connect()

        # Evento dispositivo TUIO2 desconectado. LLamada al método tuio2_disconect()
        if event_type == "tuio2_disconnect":
            self.tuio2_disconnect()

    def init_plataform(self):
        self.server.thread_init_server()
        self.interface.init_interface()

    # Transicion desde el estado MAIN a GAME
    # Comienza el juego en TUIO1 y TUIO2
    def start_game(self, gv):
        game = gv[0]
        
        if self.current == Tuio1State.MAIN:
            self.current = Tuio1State.GAME
            if game == "paint_game":
                event = ("start_game", "", "")
                self.paint_game.internal_events.put(event)

            if game == "capture_game":
                event = ("start_game", "", "")
                self.capture_game.internal_events.put(event)

    def stop_game(self, gv):
        game = gv[0]
        if self.current == Tuio1State.GAME:
            self.current = Tuio1State.MAIN
            event = ("stop_game","", "")
            if game == "paint_game":
                self.paint_game.internal_events.put(event)
            if game == "capture_game":
                self.capture_game.internal_events.put(event)

            self.interface.main_state()

    # Transicion al estado EXIT
    # El dispositivo TUIO1 sale de la aplicacion
    def exit_tuio1(self):
        self.server.close_server()  # Crear evento para el servidor
        time.sleep(1)
        self.current = Tuio1State.EXIT
        time.sleep(10)
        event = ("close_interface", "", "")
        self.interface.internal_events.put(event)
        Clock.unschedule(self.next)

    def tuio2_connect(self):
        if self.current == Tuio1State.IDLE:
            self.current = Tuio1State.MAIN
            self.interface.main_state()

    def tuio2_disconnect(self):
        self.current = Tuio1State.IDLE
        self.interface.idle_state()


if __name__ == '__main__':
    tuio1 = Tuio1FSM()
    InterfaceManagement.GUI_Tuio1App().run()
