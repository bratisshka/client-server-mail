#! /usr/bin/env Python

import os, sys
from socket import *
import ssl # Зашифрованный канал
import threading # Потоки
import time
import sqlite3 # DataBase
import datetime
import hashlib
import cPickle
import base64
import CryptUnit
import Captcha
import io
from random import randint
from Queue import Queue
from StringIO import StringIO
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.dates import date2num
from matplotlib.dates import num2date
from matplotlib.ticker import FuncFormatter
from time import sleep

BUFSIZ = 1024 # Размер буфера
Worked = True # Работа сервера
MAX_COUNT_CLIENTS = 10 # Максимальное количество клиентов
OnLineClients = dict() # Список подключенных клиентов
NewMessagesList = dict() # Новые сообщения для каждого клиента
KEYS = None # Ключи для открытого шифрования
CashCaptImgList = []
CommandSet = [
    "Debug", # Debug
    "Kick", # Kick
    "Setfilter", # Setfilter
    "Filter", # Filter
    "Unsetfilter", # Removefilter
    "Users", # Usersonline
    "Deluser", # Deluser
    "Setpassw", # Set user password
    "Maxclients", # Max clients online
    "Clearfilter", # Clear filter
    "Help", # Help for commands
    "Userscount", # Count of online users
    "Plot",
    "Statistic",
    "Exit" # Stop server
]
FilterQuest = ['Reply']
CashSize = 10
ClientCommand = ("", 0)
tmpBytesCount = [0, 0]

def Gentext(MaxSize):
    tmp = []
    for i in range(MaxSize):
        T = randint(0, 2);
        if T == 0:
            tmp.append(chr(randint(ord('A'), ord('Z') )))
        elif T == 1:
            tmp.append(chr(randint(ord('a'), ord('z') )))
        elif T == 2:
            tmp.append(chr(randint(ord('0'), ord('9') )))
    return "".join(tmp)

def GenerateCaptchaCash(Tmp):
    while True:
        if Worked == False: return True # Если сервер остановлен - выходим
        for i in range(len(CashCaptImgList), CashSize): # Пополняем кэш изображениями
            SecretText = Gentext(5)
            CaptImg = Captcha.captcha(SecretText, 200, 80, "bin\Fonts\comic-sans-ms.ttf")
            CashCaptImgList.append((SecretText, CaptImg ))
        time.sleep(0.001)
    return

def ListeningNewConnections(SerSock, addr): # Прослушивание новых подключений
    while True:
        global Worked
        time.sleep(0.001)    
        if Worked == False: return True # Если сервер остановлен - выходим
        try:
            tcpCliSock, addr = SerSock.accept() # Создание нового подключения
        except error:
            continue # В случае отсутствия подключения - ожидаем
        else:
            Conn = True
            print 'Client ', addr, 'connected'
            HelloMessage =  "Server v4.4"#'Hello!\nServer on the python v' + sys.version # Инфо о системе
            if MAX_COUNT_CLIENTS - 1 < len(OnLineClients):
                print 'MAX COUNT CLIENTS!'
                SendData( tcpCliSock, "No" ) # Сервер перегружен
            else:
                SendData( tcpCliSock, HelloMessage ) # Отправка приветствия клиенту
            # Вешаем прослушивание клиента в отдельный поток
            threading._start_new_thread(ReceivingMessages, ( tcpCliSock, addr, 'UNNAMED' ) )
    return True


def ReceivingMessages(Client, addr, USERNAME): # Прием данных от клиентов
    UsersDB = None
    UsersCur = None
    Id = 0 # Id клиента
    Login = '' # Логин клиента
    IsLogin = False
    global KEYS
    global ClientCommand
    global FilterQuest
    PUBLICKEY = ''
    DEBUG = False
    try:
        UsersDB = sqlite3.connect("Bin\DB\USERS.db") # Подключение к базе данных
        UsersCur = UsersDB.cursor() # создание курсора для запросов
        while True:
            try:
                global Worked
                time.sleep(0.001)
                if Worked == False: # Выходим из потока, если потребуется
                    return True
                # #########################################################################
                # ######################## Работа с сообщениями от клиента ################
                # #########################################################################
                data = ReciveData( Client ) # Полученные данные
                # Обработка команд сервера
                if ClientCommand[0]:
                    print "OK"
                    _ClientCommand = ClientCommand[1]
                    ClientCommand = ("", 0)
                    if _ClientCommand == 1: # Kick
                        return
                    elif _ClientCommand == 0: # Debug
                        if DEBUG:
                            DEBUG = False
                        else:
                            DEBUG = True

                if data:
                    Msg = data.split('?') # Выделим команды
                    if DEBUG and not Msg[0] in FilterQuest: print DebugStr, Msg # Отладочное сообщение
                    # Проверка соединения
                    if Msg[0] == 'Reply':
                        if OnLineClients[Id][1]:
                            SendData(Client, "Refresh")
                            continue
                        SendData(Client, 'OK')


                    #
                    elif Msg[0] == 'HowManyNews':
                        SendData(Client, OnLineClients[Id][1])


                    # Передача данных о пользователе
                    elif Msg[0] == 'UserData':
                        SendData(Client, GetRecordsData(UsersDB, UsersCur, 'Users', "Id='" + str(Id) + "'", "*")[0][:4])

                    # Авторизация
                    #
                    elif Msg[0] == 'Login':
                        Login = Msg[1] # Выделим логин из сообщения
                        Id = UserInBase(UsersCur, Login) # Получение ID пользователя из базы
                        if Id and not Id in OnLineClients: # Если пользователь зарегистрирован и не подключен
                            UserData =  GetRecordsData(UsersDB, UsersCur, 'Users', "Id='" + str(Id) + "'", "*")[0]
                            Md5Pass = hashlib.md5() # Получение хэша пароля
                            Md5Pass.update(Msg[2])
                            HashPass = Md5Pass.hexdigest()
                            if UserData[4] == HashPass: # Аутентификация
                                SendData(Client, KEYS[1])
                                PUBLICKEY = ReciveData(Client) # Сохраним публичный ключ клиента
                                OnLineClients[Id] = [' '.join(UserData[:4]), 0] # Добавим клиента в список и его данные
                                IsLogin = True # Авторизирован
                                Login = Login.capitalize()
                                DebugStr = "DEBUG " + Login + " id=" + str(Id) + " >>"
                                continue
                        SendData(Client, 'NO') # Аутентификация не пройдена


                    # Регистрация
                    #
                    elif Msg[0] == 'Reg':
                        # Обработаем капчу
                        req = True
                        CaptText = ''
                        SendData(Client, 'SendingCapt')
                        while req:
                            req = ReciveData( Client ).split("?")
                            if req[0] == "CaptImage": # Обновление
                                while( len(CashCaptImgList) == 0 ):
                                    pass
                                Capt = CashCaptImgList.pop()
                                CaptText = Capt[0]
                                data = list(Capt[1].getdata())
                                SendData(Client, data)
                            elif req[0] == 'Exit': # Выход из программы
                                return
                            elif req[0] == "EndCapt": # Возврат (кнопка cansel)
                                return
                            elif req[0] == "CaptText": # Проверка кода
                                if req[1].capitalize() != CaptText.capitalize():
                                    SendData(Client, 'NO') # Неверный код
                                    return
                                SendData(Client, 'OK')
                                break

                        Msg = ReciveData( Client ).split('?')

                        if AddUser(UsersDB, UsersCur, Msg[0].capitalize(), Msg[2].capitalize(), Msg[1].capitalize(), Msg[3].capitalize(), Msg[4]):
                            SendData(Client, 'OK')
                        else:
                            SendData(Client, 'Login') # Пользователь с таким логином уже зарегистрирован


                    elif Msg[0] == 'STOP':
                         # Команда завершения работы сервера
                        Worked = False


                    # Передача списка сообщений
                    #
                    elif Msg[0] == 'Messages':
                        UsersCur.execute('''
                            SELECT M.Id, _From.Login, _From.Name, _From.Surname,
                            _To.Login, _To.Name, _To.Surname, M.Topic, M.File,
                            M.Date, M.Read
                            FROM Messages M, Users _From, Users _To
                            WHERE (M._From = ''' + str(Id) + ''' OR M._To = ''' + str(Id) + " ) " + '''
                            AND _To.id = M.__To AND _From.id = M.__From ORDER BY Date DESC
                        ''')
                        MessList = UsersCur.fetchall() # Получение списка сообщений пользователя
                        if MessList: # Есть сообщения, отправляем блоками по 5 штук
                            length = len(MessList) # Количество сообщений
                            blocks = length / 5
                            if length % 5:
                                blocks += 1

                            SendData(Client, blocks) # Передаем количество блоков
                            for i in range(blocks):
                                SendData(Client, MessList[i * 5:(i + 1) * 5]) # Передаем сообщения
                        else:
                            SendData(Client, '0') # Сообщений нет
                        OnLineClients[int(Id)][1] = 0
                        MessList = ''


                    # Передача сообщения
                    #
                    elif Msg[0] == 'GetMessage':
                        UsersCur.execute('''
                            SELECT  _From.Login, _From.Name, _From.Surname,
                                    _To.Login, _To.Name, _To.Surname,
                                    M.Topic, M.File, M.Date
                            FROM Messages M, Users _From, Users _To
                            WHERE M.id = ''' + Msg[1] + ''' AND _From.id = M.__From AND _To.id = M.__To''')
                        Message = UsersCur.fetchone() # Получение метаданных сообщения
                        SendData(Client, Message) # Отправим метаданные
                        UsersCur.execute("SELECT TextMessage FROM Messages WHERE id = '" + Msg[1] + "'")
                        Message = UsersCur.fetchone()[0] # Получим текст сообщения
                        # Передадим зашифрованное сообщение
                        # и получим ответ о получении
                        SendData( Client, CryptUnit._GenSessionKeyAndEncryptMsg(Message.encode("utf-16"), PUBLICKEY, KEYS[0]) )

                        Message = ''


                    # Изменение статуса сообщения
                    #
                    elif Msg[0] == 'MessageReaded':
                        try:
                            UsersCur.execute("SELECT _From FROM Messages WHERE id = '" + Msg[1] + "'")
                            Message = UsersCur.fetchall()[0] # Получаем метаданные сообщения
                            if Message[0] != Id:
                                UsersCur.execute("UPDATE Messages SET Read = 1 WHERE Id='" + Msg[1] + "'")
                                UsersDB.commit() # сохраняем изменения
                                SendData(Client, 'OK')
                                continue
                            SendData(Client, 'NO')
                        except Exception, e:
                            print 'EXSEPT ', e.args
                            SendData(Client, 'NO')
                        Message = ''


                    # Удаление сообщений
                    #
                    elif Msg[0] == 'DelMessage':
                        try:
                            UsersCur.execute("SELECT _From, _To FROM Messages WHERE id = '" + Msg[1] + "'")
                            Message = UsersCur.fetchall()[0] # Получаем метаданные сообщения
                            From = Message[0]
                            To = Message[1]
                            if From == Id: # Если хост - отправитель
                                UsersCur.execute("UPDATE Messages SET _From = 0 WHERE Id='" + Msg[1] + "'")
                                From = 0
                            elif To == Id: # Если хост - получатель
                                UsersCur.execute("UPDATE Messages SET _To = 0 WHERE Id='" + Msg[1] + "'")
                                To = 0
                            if To == 0 and From == 0: # Сообщение удалено у обоих пользователей
                                DelMessage(UsersDB, UsersCur, Msg[1]) # Удаляем сообщение из базы
                                SendData(Client, 'OK')
                                continue
                            UsersDB.commit() # сохраняем изменения
                            SendData(Client, 'OK')
                        except Exception, e:
                            print 'EXSEPT ', e.args
                            SendData(Client, 'NO')
                        Message = ''


                    # Получение сообщения
                    #
                    elif Msg[0] == 'NewMessage':
                        # Загружаем сообщение на сервер

                        Data = Msg[1:] # Сохраним метаданные
                        Data.append("") # Место под текст

                        AdrList = Data[1].split(';')
                        AdrIdList = []
                        for Addressee in AdrList:
                            if Addressee: # Если есть логин ( просто не исключаются варианты ";;;user;;" )
                                _id = UserInBase(UsersCur, Addressee) # Получение ID получателя из базы
                                if _id:
                                    AdrIdList.append((_id, Addressee))

                        if not AdrIdList: # Если получателей нет в базе
                            SendData(Client, 'NO')
                            continue

                        SendData(Client, 'OK')

                       # Принимаем файл в кодировке Base64
                        FileSize = ReciveData(Client) # Размер файла
                        File = []
                        Ex = False # Отмена передачи
                        while FileSize and not Ex:
                            FilePortion = ReciveData(Client) # Получаем часть файла
                            if FilePortion == 'stoploading':
                                break
                            if FilePortion: # Добавляем часть файла
                                if FilePortion == 'stop': # Отмена загрузки
                                    Ex = True
                                    break
                                #FileSize -= sys.getsizeof(FilePortion)
                            File.append(FilePortion) # Допишем часть файла
                            SendData(Client, '')     # Дописываем в список, для быстрой
                                                     # быстрой передачи данных
##                        # Принимаем файл в кодировке Base64
##                        CountBlocks = int(ReciveData(Client)) # Получение количества частей
##                        File = []
##                        Ex = False # Отмена передачи
##                        for i in range(CountBlocks):
##                            FilePortion = ReciveData(Client) # Получаем часть файла
##                            if FilePortion: # Добавляем часть файла
##                                if FilePortion == 'stop': # Отмена загрузки
##                                    Ex = True
##                                    break
##                            File.append(FilePortion) # Допишем часть файла
##                            SendData(Client, '')     # Дописываем в список, для быстрой
##                                                     # быстрой передачи данных
                        if Ex:
                            continue
                        SendData(Client, 'OK')

                        X = ReciveData(Client) # Получим зашифрованное сообщение

                        Data[4] = CryptUnit._DecryptMessageAndCheckDS(X[0], X[1], KEYS[0], KEYS[1], PUBLICKEY) # Расшифруем сообщение
                        Data[4] = Data[4].decode("utf-16")

                        SendData(Client, 'OK') # Говорим клиенту, что приняли сообщение
                        File = ''.join(File) # Складываем все части файла (узкое место в программе)
                        for Addressee in AdrIdList:
                            # Сохраняем сообщение в базе
                            AddMessage(UsersDB, UsersCur, Id, Addressee[0], Data[2], 0, Data[3], Data[4], File)

                            if int(Addressee[0]) in OnLineClients: # Сообщим клиенту получателю о новом сообщении
                                OnLineClients[int(Addressee[0])][1] += 1

                        File = '' # Высвободим память от файла
                        Data = ''

                    # Передача файла клиенту
                    #
                    elif Msg[0] == 'LoadFile':
                        UsersCur.execute("SELECT DataFile FROM Files WHERE id = '" + Msg[1] + "'")
                        File = UsersCur.fetchone()[0] # Получим файл в кодировке Base64
                        FileSize = len(File)
                        blocksize = (1024 * 1024)
                        SendData(Client, FileSize) # Передаем размер файла в байтах
                        CurSize = 0
                        while CurSize < FileSize:
                            SendData(Client, File[CurSize:CurSize + blocksize]) # Передаем сообщения
                            CurSize += blocksize
                            answ = ReciveData(Client)
                            if str(answ) == 'stop': # Отмена загрузки
                                break
                            if answ != blocksize:
                                blocksize = answ
                        File = '' # Высвободим память от файла
                        continue
##                        UsersCur.execute("SELECT DataFile FROM Files WHERE id = '" + Msg[1] + "'")
##                        File = UsersCur.fetchone()[0] # Получим файл в кодировке Base64
##                        length = len(File) # Количество сообщений
##                        blocks = length / (1024 * 1024)
##                        if length % (1024 * 1024):
##                            blocks += 1
##                        SendData(Client, blocks) # Передаем количество блоков
##                        for i in range(blocks):
##                            SendData(Client, File[i * 1024 * 1024:(i + 1) * 1024 * 1024]) # Передаем сообщения
##                            if ReciveData(Client) == 'stop': # Отмена загрузки
##                                break
##                        SendData(Client, 'OK') # Передаем сообщение об успехе
##                        File = '' # Высвободим память от файла
##                        continue


                    # Изменение данных пользователя
                    #
                    elif Msg[0] == 'UpdateUserData':
                        # В полученном сообщении:
                        # Логин - 1
                        # ИОФ - 2, 3, 4
                        # Новый пароль - 5
                        # Старый пароль - 6

                        UserData =  GetRecordsData(UsersDB, UsersCur, 'Users', "Id='" + str(Id) + "'", "*")[0] # получим данные пользователя
                        Md5Pass = hashlib.md5() # Получение хэша пароля
                        Md5Pass.update(Msg[6])
                        if UserData[4] == Md5Pass.hexdigest(): # Аутентификация
                            # Пройдена, изменяем данные
                            if Msg[1].capitalize() != Login.capitalize(): # Если изменяется логин
                                if UserInBase(UsersCur, Msg[1].capitalize()): # С таким логином уже зарегестрированы
                                    SendData(Client, 'Login')
                                    continue
                            Login = Msg[1].capitalize()
                            UsersCur.execute("UPDATE Users SET Login = '" + Msg[1].capitalize() +
                                "', Surname = '" + Msg[4].capitalize() +
                                "', Name = '" + Msg[2].capitalize() +
                                "', Patronomic = '" + Msg[3].capitalize() + "' WHERE Id='" + str(Id) + "'")
                            if Msg[5] != '': # Смена пароля
                                Pass = hashlib.md5() # Получение хэша пароля
                                Pass.update(Msg[5])
                                UsersCur.execute("UPDATE Users SET Password = '" + Pass.hexdigest() + "' WHERE Id='" + str(Id) + "'")
                            SendData(Client, 'OK')
                            UsersDB.commit() # сохраняем изменения
                            continue

                        SendData(Client, 'NO') # Аутентификация не пройдена


                    # Получение списка контактов Онлайн
                    #
                    elif Msg[0] == 'OnlineList':
                        if len(OnLineClients) == 1:
                            SendData(Client, [u"Нет контактов онлайн"])
                        else:
                            FriendsList = GetFriendsList(UsersDB, UsersCur, Id) # Получаем список контактов
                            if FriendsList:
                                OnlineFriends = []
                                for ClientOnline in OnLineClients: # Смотрим, кто из них онлайн
                                    if str(ClientOnline) in FriendsList:
                                        OnlineFriends.append(OnLineClients[ClientOnline][0]) # Формируем список клиентов онлайн
                                SendData(Client, OnlineFriends) # Передача списка на сервер
                            else:
                                SendData(Client, [u"Нет контактов онлайн"])
                            tmp = ''
                            OnlineFriends = []
                            FriendsList = ''


                    # Получение списка контактов
                    #
                    elif Msg[0] == 'GetFriendsList':
                        FriendsList = GetFriendsList(UsersDB, UsersCur, Id) # Получаем список контактов
                        if not FriendsList:
                            SendData(Client, FriendsList)
                            continue
                        Friends = []
                        for Friend in FriendsList:
                            InNet = u"Отключен"
                            if int(Friend) in OnLineClients: # Проверим, в сети ли контакт
                                InNet = u"В сети"
                            Data = [InNet]
                            UsersCur.execute("SELECT Login, Name, Patronomic, Surname FROM Users WHERE id = '" + Friend + "'")
                            for item in UsersCur.fetchone(): # Получение данных контакта
                                Data.append(item)

                            Friends.append(Data)
                        SendData(Client, Friends) # Передаем список контактов

                    # Запрос на поиск пользователя в базе
                    #
                    elif Msg[0] == 'UserInBase':
                        UsersCur.execute("SELECT Name, Patronomic, Surname FROM Users WHERE Login = '" + Msg[1].capitalize() + "'")
                        UserData = UsersCur.fetchone() # Получение данных контакта
                        if UserData:
                            SendData(Client, UserData)
                            continue
                        SendData(Client, ("No name", "No surname", "No patronomic", "-1"))


                    # Добавление контактов пользователю
                    #
                    elif Msg[0] == 'AddFriend':
                        FriendsList = GetFriendsList(UsersDB, UsersCur, Id) # Получаем список контактов

                        UsersCur.execute("SELECT Id FROM Users WHERE Login = '" + Msg[1].capitalize() + "'")
                        UserData = UsersCur.fetchone() # Получение данных контакта

                        if not UserData:
                            SendData(Client, ("No name", "No patronomic", "No surname", "-1"))
                            continue
                        if str(UserData[0]) in FriendsList or UserData[0] == Id:
                            SendData(Client, "Execute")
                            continue
                        AddUserFriends(UsersDB, UsersCur, Id, UserData[0])
                        SendData(Client, "OK")

                    # Удаление контактов пользователя
                    #
                    elif Msg[0] == 'DeleteFriends':
                        FriendsList = GetFriendsList(UsersDB, UsersCur, Id) # Получаем список контактов
                        if not FriendsList: # Список контактов пуст, возможно, какая-то ошибка
                            SendData(Client, "NO")
                            continue
                        SendData(Client, "OK")
                        DelFriendsList = ReciveData(Client) # Получили список логинов удаляемых контактов
                        try:
                            for Friend in DelFriendsList:
                                UsersCur.execute("SELECT Id FROM Users WHERE Login = '" + Friend + "'")
                                DelFriendID = UsersCur.fetchone()[0] # Получение данных контакта
                                DelFriendFromList(UsersDB, UsersCur, Id, DelFriendID)
                        except Exception, e:
                            print "Exception: Error del friend\n", e.args
                            SendData(Client, "NO")
                            continue
                        SendData(Client, "OK")

                    # Отключение клиента
                    #
                    elif Msg[0] == 'Exit':
                        return

                    # Если иная команда - выполняется эхо
                    else:
                        SendData(Client, ('[%s]: %s'%(addr, data))) # Отправление сообщения клиенту

                # #########################################################################
                # ######################## ******************************* ################
                # #########################################################################

            except Exception, e:
                print 'res except >', e.args, error
                # e.args[0] Содержит код ошибки
                # Ошибки:
                # 10054 Соединение разорвано удаленным узлом
                # 10035 Заблокирован метод сокета
                if e.args[0] == 2: continue # Если нет новых данных - выход
                return
            else:
                continue
    finally:
        #Завершение работы клиента
        if DEBUG: print DebugStr, "Завершение работы" # Отладочное сообщение
        if Id in OnLineClients and IsLogin: # Удаление пользователя из авторизированных
            OnLineClients.pop(Id) # Удалим данные из словаря
        if UsersCur: # Звыершение работы с базой данных
            UsersCur.close()
        if UsersDB:
            UsersDB.close()
        print 'Client ', addr, 'disconnected'
        Client.close() # Закрытие соединения
    return

# Получение данных
#
def ReciveData( CliSock ):
    try:
        string = recv_data( CliSock )
        if string:
            if string.startswith('S'): # Строка
                 data = string[1:]
            elif string.startswith('D'): # Иные данные - декодируем
                 data = cPickle.loads( string[1:] )
            return data
        raise NameError('Data is empty!')
    except Exception, e:
        print "Remote host doesn't respond" # Соединение было разорвано удаленным узлом
        raise
    return

# Передача данных
#
def SendData( CliSock, quest ):
    if quest.__class__ == str:
        send_data( CliSock, 'S' + quest ) # Строка - отправляем без кодирования
        return
    send_data( CliSock, 'D' + cPickle.dumps( quest ) ) # Инае данные - кодируем

# Передача запроса с ожиданием ответа
#
def SendQuestion( CliSock, quest):
    SendData(quest) # Передача данных на сервер
    data = ReciveData()
    return data

# Низкоуровневая передача данных
#
def send_data( CliSock, data ):
    global tmpBytesCount
    data = data.encode('zip') # Сжимаем
    try:
        tmpBytesCount[1] += len(data) + 8
        CliSock.send( '%08i'%len(data) ) # Отправляем размер данных
        CliSock.send( data ) # Передаем данные
    except Exception, e:
        print 'EXEPT SENDDATA:', e.args
        raise

# Низкоуровневое получение данных
#
def recv_data( CliSock ):
    global tmpBytesCount
    data = ''
    try:
        l = CliSock.recv(8) # Получаем расзмер данных
        if l == '':
            return
        length = int( l )
        tmpBytesCount[0] += length + 8
        while len(data) < length:
            data += CliSock.recv( length - len(data) ) # Получение данных
    except Exception, e:
        print 'EXEPT RECDATA:', e.args
        return
    data = data.decode('zip') # Распаковка сжатых данных
    return data

# Поиск пользователя по логину в базе
#
def UserInBase(DBCur, Login):
    DBCur.execute("SELECT id FROM Users WHERE Login='"+ Login.capitalize() +"'")
    Id = DBCur.fetchall()
    if Id != []:
        return Id[0][0]
    return False


# Добавление нового пользователя
#
def AddUser(DB, DBCur, Name, Surname, Patr, Login, Password):
    Md5Pass = hashlib.md5() # Хэшируем пароль
    Md5Pass.update(Password)
    if not UserInBase(DBCur, Login): # Если пользователя нет, то добавим его в базу
        DBCur.execute("INSERT INTO Users(Name, Surname, Patronomic, Login, Password) VALUES( ?, ?, ?, ?, ?)",
            (Name.capitalize(), Surname.capitalize(), Patr.capitalize(), Login.capitalize(), Md5Pass.hexdigest()))
        DB.commit() # сохраняем изменения
        return True
    return False


# Удаление пользователя из базы
#
def RemoveUser(DB, DBCur, ID):
    DBCur.execute("DELETE FROM Users WHERE Id='" + str(ID) + "'")
    DB.commit() # сохраняем изменения


# Удаление контакта из списка
#
def DelFriendFromList(DB, DBCur, ID, FriendID):
    FriendsList = GetFriendsList(DB, DBCur, ID) # Получили список строчных значений ID
    FriendsList.remove(str(FriendID))
    FriendsList = ';'.join(FriendsList)
    DBCur.execute("UPDATE Users SET Friends = '" + FriendsList + "' WHERE Id='" + str(ID) + "'")
    DB.commit() # сохраняем изменения


# Получание списка контактов
#
def GetFriendsList(DB, DBCur, ID):
    DBCur.execute("SELECT Friends FROM Users WHERE Id='"+ str(ID) +"'")
    tmp = DBCur.fetchall()[0][0]
    if tmp:
        return tmp.split(';')
    return ""


# Добавление контакта пользователю
# Возвращает СПИСОК СТРОК (АЙДИ ПРЕДСТАВЛЕН В ВИДЕ СТРОКИ!)
#
def AddUserFriends(DB, DBCur, ID, FriendID):
    DBCur.execute("SELECT Friends FROM Users WHERE Id='"+ str(ID) +"'")
    BaseFriends = DBCur.fetchall()[0][0]
    if BaseFriends:
        BaseFriends += ';' + str(FriendID)
    else:
        BaseFriends = str(FriendID)
    DBCur.execute("UPDATE Users SET Friends = '" + BaseFriends + "' WHERE Id='" + str(ID) + "'")
    DB.commit() # сохраняем изменения


# Получение кортежа данных по запросу
#
def GetRecordsData(DB, DBCur, Table, Quest, What):
    DBCur.execute("SELECT " + What + " FROM " + Table + " WHERE " + Quest )
    return DBCur.fetchall()


# Добавление сообщения в базу
#
def AddMessage(DB, DBCur, FromID, ToID, Topic, Read, File, TextMessage, DataFile):
    DBCur.execute('''INSERT INTO Messages(_From, _To, __From, __To, Topic, Read, File, Date, TextMessage)
        VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (FromID, ToID, FromID, ToID, Topic, Read, File, time.time(), TextMessage ))
    DBCur.execute('''INSERT INTO Files(DataFile)
        VALUES( ? )''',
        (sqlite3.Binary(DataFile), ))
    DB.commit() # сохраняем изменения




# Удаление сообщения
#
def DelMessage(DB, DBCur, Id):
    DBCur.execute("DELETE FROM Messages WHERE Id='" + str(Id) + "'")
    DBCur.execute("DELETE FROM Files WHERE Id='" + str(Id) + "'")
    DB.commit() # сохраняем изменения

# Изменение данных пользователя
#
def UpdateUserData(DB, DBCur, ID, NewDATA):
    DBCur.execute("UPDATE Users SET " + NewDATA + " WHERE Id='" + str(ID) + "'")
    DB.commit() # сохраняем изменения

def CommandInterpreter():
    global ClientCommand
    global CommandSet
    global Worked
    global FilterQuest
    try:
        try:
            UsersDB = sqlite3.connect("Bin\DB\USERS.db") # Подключение к базе данных
            UsersCur = UsersDB.cursor() # создание курсора для запросов
            Command = raw_input(">>").split()
            if not Command[0].capitalize() in CommandSet:
                print "Unknown command", Command[0]
            CommandNum = CommandSet.index(Command[0].capitalize())

            if CommandNum == 8: # Max clients
                print MAX_COUNT_CLIENTS
            elif CommandNum == 5: # Users list
                print OnLineClients # Список подключенных клиентов
            elif CommandNum == 1: # Kick client
                if len(Command) > 1:
                    #Id = UserInBase(UsersCur, Command[1].capitalize()) # Получение ID пользователя из базы
                    ClientCommand = (str(Command[1]).capitalize(), 1)
            elif CommandNum == 0: # Set/unset debug for client
                if len(Command) > 1:
                    ClientCommand = (str(Command[1]).capitalize(), 0)
            elif CommandNum == 2: # set filter
                if len(Command) > 1 and not Command[1] in FilterQuest:
                    FilterQuest.append(Command[1])
            elif CommandNum == 4: # unset filter
                if len(Command) > 1:
                    FilterQuest.remove(Command[1])
            elif CommandNum == 9: # clear filter
                if len(Command) > 1:
                    FilterQuest = []
            elif CommandNum == 3: # print filters
                print FilterQuest
            elif CommandNum == 6: # Delete user
                if len(Command) > 1:
                    if raw_input("Delete user? input Y\N:").split()[0].capitalize() == "Y":
                        UsersCur.execute("DELETE FROM Users WHERE Login='" + str(Command[1]).capitalize() + "'")
                        UsersDB.commit() # сохраняем изменения
            elif CommandNum == 7: # Set user password
                if len(Command) > 1:
                    if raw_input("Change user password? input Y\N:").split()[0].capitalize() == "Y":
                        Md5Pass = hashlib.md5() # Получение хэша пароля
                        Md5Pass.update(str(Command[2]))
                        HashPass = Md5Pass.hexdigest()
                        UsersCur.execute("UPDATE Users SET Password = '" + str(HashPass) +
                            "' WHERE Login='" + str(Command[1]).capitalize() + "'")
                        UsersDB.commit() # сохраняем изменения
            elif CommandNum == 10: # Help
                DescrComm = [
                    "<Login> <- Set\Unset debug", # Debug
                    "<Login> <- Kick user", # Kick
                    "<Filter value> <- Set new filter", # Setfilter
                    "<- Print filters", # Filter
                    "<Filter value> <- Unset filter", # Removefilter
                    "<- print Online users list", # Usersonline
                    "<Login> <- Delete user", # Deluser
                    "<Login> <Password> <- Change password", # Set user password
                    "<- Max clients on server", # Max clients online
                    "<- Clear filter list", # Clear filter
                    "<- Help commands", # Help for commands
                    "<- Count of online users",# Users count
                    "<- Draw traffic graphics",
                    "<- Stop server"
                ]
                for i in range(len(CommandSet)):
                    print CommandSet[i], DescrComm[i]
            elif CommandNum == 11: # Count online users
                print len(OnLineClients)
            elif CommandNum == 12: # Plot (Рисвоание графика)
                fig = plt.figure(edgecolor = 'g')
                Axis = fig.add_subplot(1, 1, 1)
                time_interval = 60
                XVal = [date2num(datetime.datetime.now() + datetime.timedelta(seconds = i)) for i in range(0, time_interval)]
                YVal = [[0] * time_interval, [0] * time_interval]
                def format_function(x, pos=None):
                     x = num2date(x)
                     label = x.strftime('%H:%M:%S.%f')
                     label = label.rstrip("0")
                     label = label.rstrip(".")
                     return label
                def animate(i):
                    global tmpBytesCount
                    if i % time_interval == 0:
                        for j in range(0, time_interval):
                            XVal[j] = date2num(datetime.datetime.now() + datetime.timedelta(seconds = j))
                            YVal[0][j] = 0
                            YVal[1][j] = 0
                    YVal[0][i % time_interval] = tmpBytesCount[0]
                    YVal[1][i % time_interval] = tmpBytesCount[1]
                    tmpBytesCount = [0, 0]
                    Axis.clear()
                    Axis.plot_date(XVal, YVal[0], "r-", label = "INPUT")
                    Axis.plot(XVal[0], [0], "b-", label = "CONNECTIONS: " + str(len(OnLineClients)))
                    Axis.plot_date(XVal, YVal[1], "g--", label = "OUTPUT")
                    Axis.xaxis.set_major_formatter(FuncFormatter(format_function))
                    plt.ylim(ymin=0)
                    Axis.legend(loc=u'upper center',
                      mode='expand',
                      borderaxespad=0,
                      ncol=3)
##
##                    XVal.pop(0)
##                    XVal.append(date2num(datetime.datetime.now() + datetime.timedelta(seconds = time_interval)))
##                    YVal[0].pop(0)
##                    YVal[0].append(tmpBytesCount[0])
##                    YVal[1].pop(0)
##                    YVal[1].append(tmpBytesCount[1])
##                    tmpBytesCount = [0, 0]
##                    Axis.clear()
##                    Axis.xaxis.set_major_formatter(DF('%H:%M:%S'))
##                    Axis.plot_date(XVal, YVal[0], "r-", label = "INPUT")
##                    Axis.plot_date(XVal, YVal[1], "g-", label = "OUTPUT")
##                    Axis.plot(XVal[0], [0], "b-", label = "CONNECTIONS: " + str(len(OnLineClients)))
##                    Axis.legend(loc=u'upper center',
##                          mode='expand',
##                          borderaxespad=0,
##                          ncol=3)
                ani = animation.FuncAnimation(fig, animate, interval=1000)
                plt.show()
            elif CommandNum == 13: # вывод статистики
				def update_statistic(t, UsersCur):  # получение статистик полученных/отправленных сообщений
					ids = set([x[3] for x in t]).union(set([x[4] for x in t]))
					# print(ids)
					user_logins = []
					all_messages_from = []
					all_messages_to = []
					all_messages_delete = []
					print(ids)
					for id in ids:
						# получение статистик из бд
						user = UsersCur.execute("SELECT * FROM users WHERE id=?",
												(str(id),)).fetchone()  # получение списка пользователей
						user_login = user[0]
						user_logins.append(user_login)
						user_id = user[7]
						# получение количества отправленных сообщений
						messages_from = len(UsersCur.execute("SELECT * from messages where __From = {}".format(user_id)).fetchall())
						# получение количества принятых сообщений
						messages_to = len(UsersCur.execute("SELECT * from messages where __To = {}".format(user_id)).fetchall())
						# получение количества удаленных сообщений
						messages_deleted = len(
							UsersCur.execute(
								"SELECT * from messages where (__FROM = {} and _FROM = 0) || (__TO = {} and _TO = 0)".format(user_id,
																															 user_id)).fetchall())
						print("{:10} {:<5d} {:<8d} {:<8d}".format(user_login, messages_from, messages_to, messages_deleted))
						# запись полученных значений в массивы
						all_messages_from.append(messages_from)
						all_messages_to.append(messages_to)
						all_messages_delete.append(messages_deleted)
					return user_logins, all_messages_from, all_messages_to, all_messages_delete
				def runStatistic():  # отображение статистики отправленных/полученных сообщений
					UsersDB = sqlite3.connect("..\Server\Bin\DB\USERS.db")
					UsersCur = UsersDB.cursor()

					prev_t = []
					# print("{:10} {:5} {:8} {:8}".format("USER", "SEND", "RECIEVED", "DELETED"))

					UsersCur = UsersDB.cursor()  # создание курсора
					t = UsersCur.execute("SELECT * FROM messages").fetchall()
					diff = list(set(t) - set(prev_t))
					prev_t = t
					user_logins, all_messages_from, all_messages_to, all_messages_delete = update_statistic(diff,
																											UsersCur)  # получение статистик
					UsersCur.close()

					n_groups = len(user_logins)

					from pandas import DataFrame  # формирование графика
					change = all_messages_from
					messages_to = all_messages_to
					user = user_logins
					change = [[a, b, c] for a, b, c in zip(all_messages_from, all_messages_to, all_messages_delete)]
					grad = DataFrame(change, columns=['Send', 'Recieved', 'Deleted'])
					pos = np.arange(len(change))

					grad.plot(kind='barh', title='Scotres by users')  # настройка вида графика

					# расстановка меток
					for p, c, ch in zip(pos, user, all_messages_from):
						plt.annotate(str(ch), xy=(ch + 0.05, p - 0.19), va='center')
					for p, c, ch in zip(pos, user, all_messages_to):
						plt.annotate(str(ch), xy=(ch + 0.05, p - 0.01), va='center')
					for p, c, ch in zip(pos, user, all_messages_delete):
						plt.annotate(str(ch), xy=(ch + 0.05, p + 0.165), va='center')
					ticks = plt.yticks(pos, user)
					xt = plt.xticks()[0]
					plt.xticks(xt, [' '] * len(xt))
					plt.show()  # вывод графика

            elif CommandNum == 14: # Exit
                Worked = False
                return
        except Exception, e:
            print 'ERROR:', e.args # Соединение было разорвано удаленным узлом
            raw_input("Press ENTER to continue")
    finally:
        if UsersCur:
            UsersCur.close()
        if UsersDB:
            UsersDB.close()

def main():
    # Настройки сервера
    global KEYS
    HOST = ''
    PORT = 21564
    ADDR = (HOST, PORT)
    tcpSerSock = None
    UsersDB = None
    UsersCur = None
    try:
        print 'Python v' + sys.version # Инфо о системе
        print "Server v4.4"
        print 'Inicialize database...'
        try:
            # Инициализвация БД
            UsersDB = sqlite3.connect("Bin\DB\USERS.db") # Подключение к базе данных
            UsersCur = UsersDB.cursor() # создание курсора для запросов
            UsersCur.execute('''CREATE TABLE IF NOT EXISTS Users(
                            Login TEXT,
                            Name TEXT,
                            Patronomic TEXT,
                            Surname TEXT,
                            Password TEXT,
                            Friends TEXT,
                            ConConection BOOLEAN DEFAULT 1,
                            id INTEGER PRIMARY KEY
                        )''')  # Создание таблицы пользователей, если ее не было
            UsersCur.execute('''CREATE TABLE IF NOT EXISTS Messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                _From INTEGER,
                _To INTEGER,
                __From INTEGER,
                __To INTEGER,
                Topic TEXT,
                Read INTEGER,
                File TEXT,
                Date INTEGER,
                TextMessage TEXT
            )''') # Создание таблицы сообщений, если ее не было
            UsersCur.execute('''CREATE TABLE IF NOT EXISTS Files(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                DataFile BLOB
            )''') # Создание таблицы файлов, если ее не было
            #UsersCur.execute("vacuum") # Сжимаем базу
            s = ''
        except sqlite3.DatabaseError, e:
            print ('error ', e.args)
            return
###UsersCur.execute("SELECT _From, _To, Topic, File, Date FROM Messages WHERE id = '" + Msg[1] + "'")
##        ID = 9
##        UsersCur.execute('''
##            SELECT _From.Login, _To.Login, M.Topic, M.File, M.Date FROM Messages M, Users _From, Users _To
##            WHERE (M._From = ''' + str(ID) + ''' OR M._To = ''' + str(ID) + ''' )''' +
##            ''' AND _To.id = M._To AND _From.id = M._From''')
##        UsersCur.execute(
##        '''
##        SELECT _From.Login, _To.Login, M.Topic, M.File, M.Date FROM Messages M, Users _From, Users _To WHERE M.id = 5 AND _From.id = M._From AND _To.id = M._To
##        ''')
##        '''
##        SELECT Users.Login
##        FROM Users, Messages WHERE Messages.id = 5 and Messages._To = Users.id UNION SELECT Users.Login
##        FROM Users, Messages WHERE Messages._From = Users.id;
##        '''
##        DelFriendID = UsersCur.fetchall() # Получение данных контакта
##        print DelFriendID

        if UsersCur: #, Messages.Topic, Messages.Read, Messages.File, Messages.Date
            UsersCur.close()
        if UsersDB:
            UsersDB.close() # Звыершение инициализации базы данных

##        return

        print 'OK.'


        print "Initialize Encrypt keys..."
        KEYS = CryptUnit._GenerateKeys()
        print 'OK.'
        print ('Initialize socket %s...'%(ADDR,))
        tcpSerSock = ssl.wrap_socket(socket(AF_INET, SOCK_STREAM), 'Bin\SSL\server.key', 'Bin\SSL\server.crt', True) # Создание шифрованного сокета
        try:
            tcpSerSock.bind(ADDR) # Инициалищация сокета
        except error, e:
            print ('error #%i: %s'%e.args)
            return
        print 'OK.'

        tcpSerSock.listen(MAX_COUNT_CLIENTS) # Режим прослушивания (максимум на MAX_COUNT_CLIENTS клиентов)
        tcpSerSock.setblocking(0) # Разблокирование сокета сервера

        print ('Initialize generator images for captcha...')
        try:
            threading._start_new_thread(GenerateCaptchaCash, (1,))
        except error, e:
            print ('error #%i: %s'%e.args)
            return
        print 'OK.'

        print ('Starting general loop...')
        try:
            threading._start_new_thread(ListeningNewConnections, (tcpSerSock, ADDR) ) # Проверка нового подключения
        except error, e:
            print ('error #%i: %s'%e.args)
            return
        print 'OK.'
        print 'Server is running.'

        # Рабочий цикл сервера
        while Worked:
            if Worked == False:
                break
            CommandInterpreter()

    finally:
        #Завершение работы сервера
        while threading.active_count() != 1: # Ожидаем завершения всех второстепенных потоков
            pass
        print 'Stop server.'
        if tcpSerSock:
            tcpSerSock.close() # Закрытие сокета сервера

main()