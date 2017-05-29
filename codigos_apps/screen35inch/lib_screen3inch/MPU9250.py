## MPU9250
#  Libreria dedicada a la lectura y envio de los datos leidos por el dispositivo IMU MPU9250
import smbus
import time
import threading
from lib_screen3inch import Comunicaciones_cliente

## Direccion I2C IMU9250 por defecto (AD0 - LOW)
IMU_ADDRESS    = 0x68
## Direccion I2C magnetometro AK8963 
MAG_ADDRESS    = 0x0C
## Identificacion del dispositivo
DEVICE_ID      = 0x71

''' MPU-9250 Mapa de registros '''
CONFIG         = 0x1A
GYRO_CONFIG    = 0x1B
ACCEL_CONFIG   = 0x1C
ACCEL_CONFIG_2 = 0x1D

SMPLRT_DIV     = 0x19
INT_PIN_CFG    = 0x37

INT_STATUS     = 0x3A
ACCEL_OUT      = 0x3B

GYRO_OUT       = 0x43


PWR_MGMT_1     = 0x6B
PWR_MGMT_2     = 0x6C

WHO_AM_I       = 0x75

## Escala del giroscopio 250dps
GFS_250        = 0x00
## Escala del acelerometo 2G
AFS_2G         = 0x00

# AK8963 Register Addresses
AK8963_ST1        = 0x02
AK8963_MAGNET_OUT = 0x03
AK8963_CNTL1      = 0x0A
AK8963_CNTL2      = 0x0B
AK8963_ASAX       = 0x10

# CNTL1 Mode select
## Power down mode
AK8963_MODE_DOWN  = 0x00

## Continous data output 8Hz
AK8963_MODE_C8HZ  = 0x02

# Seleccion de escala del magnetometro
## Salida 16 bits
AK8963_BIT_16     = 0x01

## smbus
i2c = smbus.SMBus(1)



## Clase de control I2C para IMU MPU9250
class MPU9250:
    print('mpu')
    ## Constructor para inicializar MPU9250
    #  Parametro [in] direccion I2C MPU9250 I2C // Direccion IMU por defecto:0x68
    def __init__(self, address=IMU_ADDRESS):
        self.address = address
        self.configMPU9250()
        self.configAK8963()
        
        #Objeto dedicado a las comunicaciones con el servidor (envio de datos)
        self.mpu9250_crear_comunicaciones()
        self.mpu9250_activar = False
        self.mpu9250_datos = [0,0,0,0]
        self.iniciar = True

        #Hilo dedicado para actualizar los datos
        self.t0 = threading.Thread(target=self.enviar_mpu9250_datos)
        self.t0.start()

        #self.enviar_mpu9250_datos()
    
    def mpu9250_crear_comunicaciones(self):
        #Objeto dedicado a las comunicaciones con el servidor (envio de datos)
        #time.sleep(5)
        self.comunicaciones = Comunicaciones_cliente.Comunicaciones3()


    def enviar_mpu9250_datos(self):
        while self.iniciar == True:
            while self.mpu9250_activar and self.comunicaciones.conexion_establecida == True:
                self.mpu9250_datos[1] = self.leerAcelerometro()
                self.mpu9250_datos[2] = self.leerGiroscopio()
                self.mpu9250_datos[3] = self.leerMagnetometro()

    ## Buscar dispositivo
    #  Parametro [in] self Puntero al objeto
    #  Retorna true si el dispositivo esta conectado
    #  Retorna false si el dispositivo no esta conectado
    def busquedaDispositivo(self):
        who_am_i = bus.read_byte_data(self.address, WHO_AM_I)
        if(who_am_i == DEVICE_ID):
            return true
        else:
            return false

    ## Configuracion giroscopio y acelerometro del IMU MPU9250
    #  Parametro [in] self Puntero al objeto
    #  Parametro [in] gfs Gyro Full Scale Select(por defecto:GFS_250[+250dps])
    #  @param [in] afs Accel Full Scale Select(default:AFS_2G[2g])
    def configMPU9250(self):
        
        #Resolucion del giroscopio y el acelerometro
        self.gres = 250.0/32768.0
        self.ares = 2.0/32768.0

        # Desactivar el modo sleep
        i2c.write_byte_data(self.address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
   
        # DLPF_CFG
        i2c.write_byte_data(self.address, CONFIG, 0x03)
        # sample rate divider
        i2c.write_byte_data(self.address, SMPLRT_DIV, 0x04)
        
        # Selector toda la escala (full scale) giroscopio 
        i2c.write_byte_data(self.address, GYRO_CONFIG, 0x00)
        # Selector toda la escala (full scale) acelerometro
        i2c.write_byte_data(self.address, ACCEL_CONFIG, 0x00)
        
        i2c.write_byte_data(self.address, ACCEL_CONFIG_2, 0x03)
        # BYPASS_EN
        i2c.write_byte_data(self.address, INT_PIN_CFG, 0x02)
        time.sleep(0.1)


    ## Configuracion magnetometro
    #  @param [in] self The object pointer.
    #  @param [in] mode Magneto Mode Select(default:AK8963_MODE_C8HZ[Continous 8Hz])
    #  @param [in] mfs Magneto Scale Select(default:AK8963_BIT_16[16bit])
    def configAK8963(self):
        #  Resolucion magnetometro
        self.mres = 4912.0/32760.0

        i2c.write_byte_data(MAG_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set read FuseROM mode
        i2c.write_byte_data(MAG_ADDRESS, AK8963_CNTL1, 0x0F)
        time.sleep(0.01)

        # read coef data
        data = i2c.read_i2c_block_data(MAG_ADDRESS, AK8963_ASAX, 3)

        self.magXcoef = (data[0] - 128) / 256.0 + 1.0
        self.magYcoef = (data[1] - 128) / 256.0 + 1.0
        self.magZcoef = (data[2] - 128) / 256.0 + 1.0

        # set power down mode
        i2c.write_byte_data(MAG_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)


    ## brief Check data ready
    #  @param [in] self The object pointer.
    #  @retval true data is ready
    #  @retval false data is not ready
    def checkDataReady(self):
        drdy = i2c.read_byte_data(self.address, INT_STATUS)
        if drdy & 0x01:
            return True
        else:
            return False


    ## Lecturas del acelerometro
    #  Parametro [in] self Puntero al objeto
    #  Valores de retorno  
    #  x : x-axis data
    #  y : y-axis data
    #  z : z-axis data
    def leerAcelerometro(self):
        data = i2c.read_i2c_block_data(self.address, ACCEL_OUT, 6)
        
        #Ordenar los bytes correctamente mediante la funcion dataConv
        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        #Redondeo de valores
        x = round(x*self.ares, 3)
        y = round(y*self.ares, 3)
        z = round(z*self.ares, 3)

        values = (1,x,y,z,1,0)
        self.mandar_datos(values)

    ## Lecturas del giroscopio
    #  Parametro [in] self Puntero al objeto
    #  Valores de retorno:
    #  x : x-giro data
    #  y : y-giro data
    #  z : z-giro data
    def leerGiroscopio(self):
        data = i2c.read_i2c_block_data(self.address, GYRO_OUT, 6)

        #Ordenar los bytes correctamente mediante la funcion dataConv
        x = self.dataConv(data[1], data[0])
        y = self.dataConv(data[3], data[2])
        z = self.dataConv(data[5], data[4])

        #Ajuste de escala y redondeo de valores
        x = round(x*self.gres, 3)
        y = round(y*self.gres, 3)
        z = round(z*self.gres, 3)

        values = (2,x,y,z,1,0)
        self.mandar_datos(values)

    ## Lectura del magnetometro
    #  Parametro [in] self Puntero al objeto
    #  Valores de retorno:
    #  x : X datos magnetometro 
    #  y : y datos magnetometro 
    #  z : Z datos magnetometro 
    def leerMagnetometro(self):
        x=0
        y=0
        z=0

        
        data = i2c.read_i2c_block_data(MAG_ADDRESS, AK8963_MAGNET_OUT, 7)

        #Ordenar los bytes correctamente mediante la funcion dataConv
        x = self.dataConv(data[0], data[1])
        y = self.dataConv(data[2], data[3])
        z = self.dataConv(data[4], data[5])
                
        #Redondeo de valores
        x = round(x * self.mres * self.magXcoef, 3)
        y = round(y * self.mres * self.magYcoef, 3)
        z = round(z * self.mres * self.magZcoef, 3)

        values = (3,x,y,z,1,0)
        self.mandar_datos(values)

    
    ## Conversion y ordenacion de datos
    #  Parametro [in] self Puntero al objeto
    # @param [in] data1 LSB
    # @param [in] data2 MSB
    # @retval Value MSB+LSB(int 16bit)
    def dataConv(self, data1, data2):
        value = data1 | (data2 << 8)
        if(value & (1 << 16 - 1)):
            value -= (1<<16)
        return value

    def mandar_datos(self,values):
        self.comunicaciones.mandar_datos(values)