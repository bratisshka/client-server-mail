#! /usr/bin/env Python

import threading # Потоки
from socket import *
import ssl
import cPickle
from  ConfigParser import ConfigParser

CliSock = None # Сокет клиента
ADDR = ('127.0.0.1', 21564)

def ConnectToServer(Count):
    global CliSock
    IsConnected = False
    for i in range(Count + 1):
        try:
           print ('Connecting to %s...'%(ADDR, )), ('(%s)'%(i,)) if i != 0 else ''
           CliSock.connect(ADDR) # Подключение к серверу
           IsConnected = True
           CliSock.settimeout(15) # Установим тайм-аут соединения в 15 секунд
           #CliSock.setblocking(0) # Разблокирование сокета
           break
        except Exception:
            continue
    return IsConnected # После Count попыток подключения, возвращает состояние соединения

def CloseSocket():
    global CliSock
    if CliSock:
        CliSock.close() # Закрытие соединения
        CliSock = None

# Получение данных
#
def ReciveData( ):
    global CliSock

    try:
        string = recv_data( CliSock )
        if not string:
            print "Reciving data is empty"
            return
        if string.startswith('S'): # Строка
             data = string[1:]
        elif string.startswith('D'): # Иные данные - декодируем
             data = cPickle.loads( string[1:] )
        return data
    except Exception, e:
        print e.args
        print "Remote host doesn't respond" # Соединение было разорвано удаленным узлом
    return

# Передача данных
#
def SendData( quest ):
    global CliSock
    if quest.__class__ == str:
        send_data( CliSock, 'S' + quest ) # Строка - отправляем без кодирования
        return
    send_data( CliSock, 'D' + cPickle.dumps( quest ) ) # Инае данные - кодируем

# Передача запроса с ожиданием ответа
#
def SendQuestion( quest):
    SendData(quest) # Передача данных на сервер
    data = ReciveData()
    return data

# Низкоуровневая передача данных
#
def send_data( CliSock, data ):
    if not CliSock:
        return
    data = data.encode('zip') # Сжимаем
    try:
        CliSock.send( '%08i'%len(data) ) # Отправляем размер данных
        CliSock.send( data ) # Передаем данные
    except Exception, e:
        print 'EXEPT SENDDATA:', e.args
        raise

# Низкоуровневое получение данных
#
def recv_data( CliSock ):
    if not CliSock:
        return
    data = ''
    try:
        l = CliSock.recv(8) # Получаем расзмер данных
        if l == '':
            return
        length = int( l )
        while len(data) < length:
            data += CliSock.recv( length - len(data) ) # Получение данных
    except Exception, e:
        print 'EXEPT RECDATA:', e.args
        raise
        return
    data = data.decode('zip') # Распаковка сжатых данных
    return data

def InitSocket():
    global ADDR
    global CliSock
    config = ConfigParser()
    if (config.read("bin\config.ini")):
        ADDR = (config.get("server", "ip"), int(config.get("server", "port")))
    CliSock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM)) # Создание шифрованного сокета

#InitSocket()