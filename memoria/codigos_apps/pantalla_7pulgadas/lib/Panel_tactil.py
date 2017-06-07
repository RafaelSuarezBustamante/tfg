
from kivy.vector import Vector
import time
import math
import threading
import errno
from lib import Comunicaciones_servidor



class Localizacion(object):
	def __init__(self, **kwargs):
		super(Localizacion, self).__init__(**kwargs)
		self.puls = []                                      #Lista de coordenadas xy de toques
		self.m = 0 											#Distancia entre los dos ultimos puntos
		self.dist = [(0,'NADA')]							#Listado de distancias entre puntos
		self.coordenadas = [(0,0,0),(0,0,0),(0,0,0)]   #Lista de coordenadas posicion pantalla 3,5"
		self.area = 0										#Area del triangulo formado por las coordenadas		
		self.contador = 0
		#self.values = (0, 0, 0, 0, 1, 0)
		self.comunicaciones = Comunicaciones_servidor.Comunicaciones7()
		self.comunicaciones.iniciar_socket()
	def pulsacion(self,t):
		if (len(self.puls)) < 6 :
			self.puls.append((t.x,t.y,t.id))  #Almacenar las coordenadas del toque
			if (len(self.puls)) > 1 :
				print(self.puls)
				self.determinar_distancias()

	def toque_up(self,t):
		print(self.puls)
		for i in range(len(self.puls)):
			print(t)
			if t == self.puls[i][2]:
				self.puls.pop(i)
				break

	#Determinar la distancia entre los dos ultimos toques realizados
	def determinar_distancias(self):
		print('determinar distancias')
		i = len(self.puls) #tamaño de la lista de toques
		no_add = False

		for a in range (i-1):
			self.m = Vector(self.puls[(i-1)][0:2]).distance(self.puls[a][0:2]) #Calculo de la distancia entre toques
			self.determinar_lados(self.m,self.puls[i-1],self.puls[a]) #Determinar a que segmento pertenece (AB, BC, AC)

			if self.contador > 1:
				self.determinar_puntos()
				break

	#Determinar segmento segun distancia entre puntos
	def determinar_lados(self,m,toq1,toq2):
		print('determinar lados')
		k = len(self.dist)
		if m>120 and self.m<150 and self.dist[k-1][1]!='AB':
			self.dist.append((m,'AB',toq1,toq2))
			self.contador = self.contador + 1
		elif m>160 and m<200 and self.dist[k-1][1]!='BC':
			self.dist.append((m,'BC',toq1,toq2))
			self.contador = self.contador + 1
		elif m>210 and m<260 and self.dist[k-1][1]!='AC':
			self.dist.append((m,'AC',toq1,toq2))
			self.contador = self.contador + 1


	def determinar_puntos(self):
		print('determinar puntos')
		k = len(self.dist)

		if self.dist[1][1] == 'AC' and self.dist[2][1] == 'AB':
			self.asignar_puntos(0,2,1,'A','C','B')
		if self.dist[1][1] == 'AC' and self.dist[2][1] == 'BC':
			self.asignar_puntos(2,0,1,'C','A','B')

		if self.dist[1][1] == 'AB' and self.dist[2][1] == 'AC':
			self.asignar_puntos(0,1,2,'A','B','C')
		if self.dist[1][1] == 'AB' and self.dist[2][1] == 'BC':
			self.asignar_puntos(1,0,2,'B','A','C')

		if self.dist[1][1] == 'BC' and self.dist[2][1] == 'AC':
			self.asignar_puntos(2,1,0,'C','B','A')
		if self.dist[1][1] == 'BC' and self.dist[2][1] == 'AB':
			self.asignar_puntos(1,2,0,'B','C','A')


		self.area = self.calculo_area(self.coordenadas) #Calculo del area

		if self.area>9545 and self.area<16000: #Condicion del area del triangulo u2
			self.coordenadas_init = self.coordenadas[:] #Copia para enviar a la pantalla y mostrar puntos de contacto
			angulo = self.calculo_angulo(self.coordenadas)
			print('Area correcta')
			values = (0, self.coordenadas[0][0], self.coordenadas[0][1], angulo, 1, 0)
			print('values')
			print(values)
			self.enviar_datos(values)

		else:
			print('Area erronea')
		
		self.inicializar_a_0()
		
	def asignar_puntos(self,c,c1,c2,p,p1,p2):

		for a in range(2):
			for b in range(2):
				print('distanciasss',self.dist)
				if self.dist[1][a+2][2] == self.dist[2][b+2][2]:
					#punto en comun
					self.coordenadas[c] = (self.dist[1][a+2][0],self.dist[1][a+2][1],p)
					if a == 0:
						self.coordenadas[c1] = (self.dist[1][3][0],self.dist[1][3][1],p1)
					else:
						self.coordenadas[c1] = (self.dist[1][2][0],self.dist[1][2][1],p1)
					if b == 0:
						self.coordenadas[c2] = (self.dist[2][3][0],self.dist[2][3][1],p2)
					else:
						self.coordenadas[c2] = (self.dist[2][2][0],self.dist[2][2][1],p2)
					break

		print('fin asignar puntos')
		print(self.coordenadas)
		#Calculo del area del triangulo mediante determinante
	def calculo_area(self, c):
		print('calculo de area')
		det = abs((c[0][0]*c[1][1])+(c[0][1]*c[2][0])+(c[2][1]*c[1][0])-
			((c[1][1]*c[2][0])+(c[0][1]*c[1][0])+(c[0][0]*c[2][1])))*0.5
		return(det)

	def calculo_angulo(self,c):
		print('calculo del angulo')
		print(c)
		angulo = (math.atan((c[1][1]-c[0][1])/(c[1][0]-c[0][0])+0.0001))*180/math.pi
		return angulo


	def enviar_datos(self,values):
		self.comunicaciones.mandar_datos(values)

	def inicializar_a_0(self):
		self.dist = [(0,'NADA')] #Inicializar lista de distancias	
		self.contador = 0
		self.toq = []
