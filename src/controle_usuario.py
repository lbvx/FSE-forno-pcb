from time import sleep
import uart
import threading

MODO_MANUAL = False
MODO_CURVA = True

class ControleUsuario(threading.Thread):
    def __init__(self, s:threading.Semaphore):
        super().__init__()
        self.est_sistema = False
        self.est_funcionamento = False
        self.modo = MODO_MANUAL

        self.sem = s

        uart.envia_comando(uart.Comandos.enviar_estado, False)
        uart.envia_comando(uart.Comandos.enviar_funcionamento, False)
        uart.envia_comando(uart.Comandos.enviar_modo, False)

    def run(self):
        while(True):
            self.sem.acquire()
            cmd = uart.envia_recebe(uart.Comandos.ler_comando_usuario)[3]

            # print('Comando:', cmd)
            if cmd == uart.Comandos.usuario.liga:
                uart.envia_comando(uart.Comandos.enviar_estado, True)
                self.est_sistema = True
            if cmd == uart.Comandos.usuario.desliga:
                uart.envia_comando(uart.Comandos.enviar_estado, False)
                self.est_sistema = False
            if cmd == uart.Comandos.usuario.inicia:
                uart.envia_comando(uart.Comandos.enviar_funcionamento, True)
                self.est_funcionamento = True
            if cmd == uart.Comandos.usuario.cancela:
                uart.envia_comando(uart.Comandos.enviar_funcionamento, False)
                self.est_funcionamento = False
            if cmd == uart.Comandos.usuario.menu:
                if self.modo == MODO_CURVA:
                    uart.envia_comando(uart.Comandos.enviar_modo, MODO_MANUAL)
                    self.modo = MODO_MANUAL
                else:
                    uart.envia_comando(uart.Comandos.enviar_modo, MODO_CURVA)
                    self.modo = MODO_CURVA

            self.sem.release()
            sleep(0.5)
