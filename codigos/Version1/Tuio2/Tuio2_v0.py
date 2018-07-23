from multiprocessing import Queue
from threading import Thread
from lib import InterfaceManagement, PaintGame, Client_v1, CaptureGame
from kivy.clock import Clock
from enum import Enum
import time

class Tuio2State(Enum):
    IDLE = 0
    MAIN = 1
    GAME = 2
    EXIT = 3

class Tuio2FSM(object):
    def __init__(self):

        self.current = Tuio2State.IDLE
        self.events = Queue()
        self.client = Client_v1.ClientFSM()
        self.interface = InterfaceManagement.InterfaceManagement()
        self.paint_game = PaintGame.PaintGameFSM()
        self.capture_game = CaptureGame.CaptureGameFSM()
        self.init_plataform()
        self.start_thread_next()

    def start_thread_next(self):
        Thread(target=self.thread_next, ).start()

    def thread_next(self):
        Clock.schedule_interval(self.next, 0.01)

    # Proximo evento
    def next(self, dt):

        if not self.current == Tuio2State.EXIT:
            # Eventos FSM TUIO2
            if not self.events.empty():
                #Obtener nuevo evento
                ev = self.events.get()
                #Procesar nuevo evento
                self.dispatch_event(ev)

        # Eventos recibidos desde TUIO1 (Server)
        if not self.client.client_events.empty():
            ev = self.client.client_events.get()
            self.dispatch_event(ev)

        if not self.interface.events.empty():
            ev = self.interface.events.get()
            self.dispatch_event(ev)

        self.paint_game.next()
        if not self.paint_game.external_events.empty():
            ev = self.paint_game.external_events.get()
            self.dispatch_event(ev)

        self.capture_game.next()
        if not self.capture_game.external_events.empty():
            ev = self.capture_game.external_events.get()
            self.dispatch_event(ev)

    # Metodo crear evento.
    # Argumento de entrada ev: evento para almacenar en la cola
    def create_event(self, ev):
        event = ev
        self.events.put(event)

    def dispatch_event(self, ev):
        event_type = ev[0]
        givens = ev[1:]

        if event_type == "init_plataform":
            self.init_plataform()

        if event_type == "send_data":
            self.client.send_data(*givens)

        # Evento empezar juego en ambos dispositivos
        if event_type == "start_game":
            self.start_game(givens)

        # Evento detener juego en ambos dispositivos
        if event_type == "stop_game":
            self.stop_game(givens)

        # Evento salir del dispositivo TUIO1
        if event_type == "exit_tuio2":
            self.exit_tuio2()

        if event_type =="capture_game":
            self.capture_game.internal_events.put(givens)

        if event_type == "paint_game":
            self.paint_game.internal_events.put(givens)

        # Evento dispositivo TUIO2 conectado. Llama al método tuio2_connect()
        if event_type == "tuio1_connect":
            self.tuio1_connect()

        # Evento dispositivo TUIO2 desconectado. LLamada al método tuio2_disconect()
        if event_type == "tuio1_disconnect":
            self.tuio1_disconnect()

    def init_plataform(self):
        self.client.thread_init_client()
        self.interface.init_interface()

    # Transicion desde el estado MAIN a GAME
    # Comienza el juego en TUIO1 y TUIO2
    def start_game(self, gv):
        game = gv[0]
        if self.current == Tuio2State.MAIN:
            self.current = Tuio2State.GAME
            if game == "paint_game":
                event = ("start_game", "", "")
                self.paint_game.internal_events.put(event)
                self.client.send_data((b'start_game', game.encode(), *(0, 0, 0, 0)))

            if game == "capture_game":
                event = ("start_game", "", "")
                self.capture_game.internal_events.put(event)
                self.client.send_data((b'start_game', game.encode(), *(0, 0, 0, 0)))

    # Transicion desde el estado GAME a MAIN
    # Juego detenido en TUIO1 y TUIO2
    def stop_game(self, gv):
        game = gv[0]
        if self.current == Tuio2State.GAME:
            self.current = Tuio2State.MAIN
            if game == "paint_game":
                self.client.send_data((b'stop_game', game.encode(), *(0, 0, 0, 0)))
                self.interface.main_state()

            if game == "capture_game":
                self.client.send_data((b'stop_game', game.encode(), *(0, 0, 0, 0)))
                self.interface.main_state()

    def tuio1_connect(self):
        if self.current == Tuio2State.IDLE:
            self.current = Tuio2State.MAIN
            screen = "main_screen"
            self.interface.switch_screen(screen)

    def tuio1_disconnect(self):
        self.current = Tuio2State.IDLE
        screen = "idle_screen"
        self.interface.switch_screen(screen)


   # Transicion al estado EXIT
    # El dispositivo TUIO1 sale de la aplicacion
    def exit_tuio2(self):
        self.client.close_client()  # Crear evento para el servidor
        time.sleep(1)
        self.current = Tuio2State.EXIT
        time.sleep(10)
        self.interface.close_interface()
        Clock.unschedule(self.next)

if __name__ == '__main__':
    tuio2 = Tuio2FSM()
    InterfaceManagement.GUI_Tuio2App().run()
