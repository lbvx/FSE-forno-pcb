import RPi.GPIO as GPIO
from time import sleep, time
from datetime import datetime
import uart
from simple_pid import PID
import threading
from sys import exit
import board
from adafruit_bme280 import basic as adafruit_bme280

def clamp(l, r, x):
    return min(r, max(l, x))
    
class ControleTemperatura(threading.Thread):
    def __init__(self, s:threading.Semaphore):
        super().__init__()
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)    #resistor
        GPIO.setup(24, GPIO.OUT)    #ventoinha

        self.sem = s

        self.resistor = GPIO.PWM(23, 1000)
        self.ventoinha = GPIO.PWM(24, 1000)
        self.ventoinha.start(0.0)
        self.resistor.start(0.0)

        i2c = board.I2C()
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

        self.pid = PID(30., 0.2, 400., sample_time=0.5)
        self.temp_ref = 0.0
        self.temp_interna = 0.0
        self.ultimo_log = time()

    def run(self):
        while True:            
            self.sem.acquire()
            self.temp_ref = uart.envia_recebe(uart.Comandos.ler_temp_referencia)[3]
            self.temp_interna = uart.envia_recebe(uart.Comandos.ler_temp_interna)[3]
            self.temp_ambiente = self.bme280.temperature
            
            self.pid.setpoint = self.temp_ref
            pid_curr = self.pid(self.temp_interna)

            print('Temperatura Interna: ', round(self.temp_interna, 2), '°C', sep='')
            print('Temperatura Referência: ', round(self.temp_ref, 2), '°C', sep='')
            print('Temperatura Ambiente: ', round(self.temp_ambiente, 2), '°C', sep='')
            print('PID: ', round(pid_curr, 3), sep='')
            print()

            sinal = int(clamp(-100., 100., pid_curr))
            sinalRes = clamp(0., 100., pid_curr)
            sinalVen = clamp(40., 100., -pid_curr)
            self.resistor.ChangeDutyCycle(clamp(0., 100., pid_curr))
            self.ventoinha.ChangeDutyCycle(clamp(0., 100., -pid_curr))

            uart.envia_comando(uart.Comandos.enviar_sinal_controle, sinal)
            self.sem.release()

            hora = time()
            if hora - self.ultimo_log >= 1.0:
                self.log(sinalRes, sinalVen)

            sleep(0.5)

    def log(self, sRes, sVen):
        horario = datetime.now()
        while True:
            try:
                with open('log.csv', 'a') as f:
                    f.write('%d-%d-%d %d:%d:%d,%f,%f,%f,%f,%f\n' %
                     (horario.year, horario.month, horario.day, horario.hour,
                     horario.minute, horario.second, round(self.temp_interna, 2),
                     round(self.temp_ambiente, 2), round(self.temp_ref, 2),
                     round(sRes, 2), round(sVen, 2))
                    )
                return
            except FileNotFoundError:
                print('Criando arquivo de log')
                with open('log.csv', 'w') as f:
                    f.write('Data,TempInt,TempAmb,TempRef,Resistor,Ventoinha\n')

    def stop(self):
        exit(0)
