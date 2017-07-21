from kivy.properties import StringProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from enum import Enum
from queue import Queue
import threading
import time
import ast
from lib import Cliente
from lib import ExampleGame1


#--------------------------------------------------------------
# Clase para enumerar los diferentes estados del FSM Juego
#--------------------------------------------------------------		
class JuegoEstado(Enum):
	IDLE = 0
	MENU = 1
	PLAYING = 2

#--------------------------------------------------------------
# Clase para la administracion y carga de pantallas de la app
#--------------------------------------------------------------
class ScreenManagement(ScreenManager):
	pass

#--------------------------------------------------------------------
# Clase de la pantalla principal
#--------------------------------------------------------------------
class MainScreen(Screen):
    pass

#--------------------------------------------------------------------
# Clase de la barra de herramientas mostrada en la pantalla principal
#--------------------------------------------------------------------
class ToolBar(BoxLayout):
	texto  = StringProperty()
	source  = StringProperty()
	def __init__(self, **kwargs):
		super(ToolBar, self).__init__(**kwargs)
		self.texto = "DISPOSITIVO CONECTADO"
		self.source = "data/icons/wifi_conectado.png"

#--------------------------------------------------------------------
# Clase para la gestion del mensajes para mostrar en pantalla principal
#--------------------------------------------------------------------
class CustomMenssage(Widget):
	texto  = StringProperty()
	def __init__(self, **kwargs):
		super(CustomMenssage, self).__init__(**kwargs)
		self.texto = ""

#--------------------------------------------------------------
# Clase pricipal de la aplicaccion
#--------------------------------------------------------------
class ItaniumApp(App):

	def build(self):

		#Carga del archivo principal de la aplicacion
		self.root = Builder.load_file("main.kv")
		
		#Se incluye la barra de herramientas a la pantalla principal
		self.toolbar = ToolBar()
		self.root.ids.main.add_widget(self.toolbar)

		#Se incluye un mensaje para mostrar en la pantalla principal
		self.screen_menssage = CustomMenssage()
		self.root.ids.main.add_widget(self.screen_menssage)

		#Atributo para finalizar la aplicacion
		self.finalizar = False
		
		#Se crean los dos objetos de la maquinas de estado
		self.fsm = JuegoFSM()
		self.comunicaciones = Cliente.Cliente()

		#Hilo dedicado a la maquina de estados del juego
		t0 = threading.Thread(target=self.juegofsm)
		t0.start()

		#Hilo para la maquina de estados de las comunicaciones cliente
		t1 = threading.Thread(target=self.comunicaciones.comunicacionesfsm)
		t1.start()
		
		return self.root

#--------------------------------------------------------------
# Metodo dedicado a obtener eventos de entrada desde el servidor
#--------------------------------------------------------------	

	def input_events(self):
		if not self.comunicaciones.fsm.events_input.empty():
			event = ast.literal_eval(self.comunicaciones.fsm.events_input.get())
			self.fsm.create_event(event)

#--------------------------------------------------------------
# Metodo dedicado a obtener y mostrar las pantallas de la aplicacion
#--------------------------------------------------------------
	def screen_selector(self):
		if not self.fsm.screen_names.empty():
			screen_name = self.fsm.screen_names.get()
			self.root.current = screen_name

#--------------------------------------------------------------
# Metodo dedicado a mostrar mensajes en la pantalla principal
#--------------------------------------------------------------
	def mensajes_pantalla(self):
		if self.fsm.mensajes.empty():
			return
		mensaje = self.fsm.mensajes.get()
		self.screen_menssage.texto = mensaje
	
#--------------------------------------------------------------
# Metodo dedicado a la maquina de estados del juego
#--------------------------------------------------------------
	def juegofsm(self):
		while self.finalizar == False:
			time.sleep(.1)
			self.input_events()
			self.fsm.next()
			self.screen_selector()
			self.mensajes_pantalla()

#--------------------------------------------------------------
# Metodo para finalizar la aplicacion.
#--------------------------------------------------------------
	def exit_app(self):
		self.finalizar = True
		self.comunicaciones.finalizar = True
		self.comunicaciones.fsm.events_fsm.put(("closed",))


#--------------------------------------------------------------
# Clase de la maquina de estados del juego
#--------------------------------------------------------------
class JuegoFSM(object):
	def __init__(self):
		self.current = JuegoEstado.IDLE
		self.events = Queue()
		self.mensajes = Queue()
		self.touch_events = Queue()
		self.output_events = Queue()
		self.screen_names = Queue()

#--------------------------------------------------------------
# Metodo para obtener y procesar los eventos
#--------------------------------------------------------------
	def next(self):
		if self.events.empty():
			return
		ev = self.events.get()
		self.dispatch_event(ev)
		return self.current.name

#--------------------------------------------------------------
# Metodo para evaluar los eventos
#--------------------------------------------------------------
	def dispatch_event(self,ev):

		tipo = ev[0]
		
		if tipo =="init":
			self.init()

		if tipo =="init_game":
			self.init_game(ev[1])

		if tipo == "menu":
			self.menu()

		if tipo == "clear":
			self.clear()

		if tipo == "mensaje":
			self.mensaje(ev[1])

		if tipo == "touch":
			self.touch(ev[1:])

#--------------------------------------------------------------
# Metodo para cambiar de estado al inicial (IDLE)
#--------------------------------------------------------------
	def init(self):
		if self.current == JuegoEstado.PLAYING:
			self.current = JuegoEstado.IDLE
			self.create_screen_name_event('main')

#--------------------------------------------------------------
# Metodo para establecer estado de juego a PLAYING
#--------------------------------------------------------------
	def init_game(self,ev):
		event = ev
		if self.current == JuegoEstado.IDLE:
			self.current = JuegoEstado.PLAYING
			self.create_screen_name_event(event)

	def menu(self):
		if self.current == JuegoEstado.PLAYING:
			self.current = JuegoEstado.MENU


	def clear(self):
		if self.current == JuegoEstado.MENU:
			self.current = JuegoEstado.PLAYING

#--------------------------------------------------------------
# Metodo para añadir un evento tipo mensaje
#--------------------------------------------------------------
	def mensaje(self,ms):
		mensaje_en_pantalla = ms
		self.mensajes.put(mensaje_en_pantalla)

#--------------------------------------------------------------
# Metodo para indicar las acciones a realizar con el menu
#--------------------------------------------------------------
	def touch(self,ev):
		if self.current == JuegoEstado.PLAYING:
			self.touch_events.put(ev)

#--------------------------------------------------------------
# Metodo almacenar los eventos para la FSM del juego
#--------------------------------------------------------------
	def create_event(self,ev):
		nuevo_evento = ev
		self.events.put(nuevo_evento)

#--------------------------------------------------------------
# Metodo almacenar los eventos relacionados con las pantallas
# de la aplicacion
#--------------------------------------------------------------
	def create_screen_name_event(self,ev):
		screen_name = ev
		self.screen_names.put(screen_name)

if __name__=='__main__':
	ItaniumApp().run()
