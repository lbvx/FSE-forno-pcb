import struct
import serial
import crc

matricula_b = b'\x03\x00\x08\x08'
class Comandos:
    ler_temp_interna = (0x01, 0x23, 0xC1)
    ler_temp_referencia = (0x01, 0x23, 0xC2)
    ler_comando_usuario = (0x01, 0x23, 0xC3)
    enviar_sinal_controle = (0x01, 0x16, 0xD1)
    enviar_temp_referencia = (0x01, 0x16, 0xD2)
    enviar_estado = (0x01, 0x16, 0xD3)
    enviar_modo = (0x01, 0x16, 0xD4)
    enviar_funcionamento = (0x01, 0x16, 0xD5)
    enviar_temp_ambiente = (0x01, 0x16, 0xD6)

    class usuario:
        liga = 0xA1
        desliga = 0xA2
        inicia = 0xA3
        cancela = 0xA4
        menu = 0xA5

ser = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1.0)

def envia_comando(comando:tuple, *args) -> None:
    msg = struct.pack('<BBB', *comando) + matricula_b

    for a in args:
        if type(a) == int:
            msg += struct.pack('i', a)
        elif type(a) == float:
            msg += struct.pack('f', a)
        elif type(a) == bool:
            msg += struct.pack('B', a)
        else: raise TypeError('Tipo nao suportado')

    msg += struct.pack('H', crc.calcula_crc(msg))
    ser.write(msg)

def envia_recebe(comando:tuple, *args):
    while True:
        msg = ser.readline()
        envia_comando(comando, *args)

        fmt_ret = '<BBB'
        if comando == Comandos.ler_temp_interna or\
           comando == Comandos.ler_temp_referencia:
            fmt_ret += 'f'
        elif comando == Comandos.ler_comando_usuario:
            fmt_ret += 'i'
        else: tipo_ret = None
        fmt_ret += 'H'

        msg = ser.readline()
        if crc.verifica_crc(msg):
            print('Erro CRC')
            continue

        try:
            msg = struct.unpack(fmt_ret, msg)
        except struct.error as e:
            # print(msg)
            # print(e)
            print('Erro struct')
            continue

        return msg
