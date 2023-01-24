from controle_temperatura import ControleTemperatura
from controle_usuario import ControleUsuario
from threading import Semaphore

def main():
    s = Semaphore()
    tt = ControleTemperatura(s)
    tt.start()

    ut = ControleUsuario(s)
    ut.start()

    try:
        tt.join()
    except KeyboardInterrupt:
        tt.stop()

if __name__ == '__main__':
    main()
