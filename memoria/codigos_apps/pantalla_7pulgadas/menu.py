import time
from kivy.app import App
from os.path import dirname, join
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from lib import Juego1
#from lib import Comunicaciones_servidor
import threading

class Menu(Screen):

	fullscreen = BooleanProperty(False)

	def add_widget(self, *args):
		if 'content' in self.ids:
			return self.ids.content.add_widget(*args)
		return super(Menu, self).add_widget(*args)
		

class MenuApp(App):

	index = NumericProperty(-1)
	screen_names = ListProperty([])
	
	def build(self):
		self.iniciar = True
		self.juego1 = Juego1.Matriz_juego()
		self.t0 = threading.Thread(target=self.actualizar_datos)
		self.t0.start()
		self.pantallas = {}
		self.pantallas_disponibles = sorted([
            'PantallaPrincipal','PantallaJuegos','PantallaAyuda','PantallaConfigurar','PantallaJuego1' ])
		self.screen_names = self.pantallas_disponibles
		directorio = dirname(__file__)
		self.pantallas_disponibles = [join(directorio, 'data', 'pantallas',
			'{}.kv'.format(fn).lower()) for fn in self.pantallas_disponibles]
		
		self.go_screen(4)

	def cargar_pantalla(self, index):
		if index in self.pantallas:
			print('index1')
			return self.pantallas[index]
		screen = Builder.load_file(self.pantallas_disponibles[index])
		self.pantallas[index] = screen
		print('index2')
		return screen

	def go_screen(self, idx):
		self.index = idx
		self.root.ids.sm.switch_to(self.cargar_pantalla(idx), direction='left')
	

	def actualizar_datos(self):
		while self.iniciar == True:
			if self.juego1.panel_tactil.comunicaciones.conexion_con_cliente == False :
				self.root.ids.conexion.text = 'DESCONECTADO'
				self.root.ids.conexion.background_disabled_normal='data/icons/wifi_desconectado.png'
			else:
				self.root.ids.conexion.text = 'CONECTADO'
				self.root.ids.conexion.background_disabled_normal='data/icons/wifi_conectado.png'

			time.sleep(1)

	def salir(self):
		self.iniciar = False
		self.juego1.panel_tactil.comunicaciones.finalizar_conexion()

if __name__=='__main__':
    MenuApp().run()