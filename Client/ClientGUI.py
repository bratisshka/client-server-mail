# coding=utf-8
from Tkinter import *
import ttk
import Tix
import time
import os
from PIL import Image, ImageTk
import Tkinter
from tkMessageBox import *
from tkFileDialog import askopenfilename, asksaveasfilename
from PostNetwork import *
import random
import base64
import CryptUnit
from StringIO import StringIO
import Queue


class GUI(ttk.Frame):
    def __init__(self):
        ttk.Frame.__init__(self)
        self.style = ttk.Style()  # Настройка стилей программы
        self.style.theme_use('clam')
        self.style.configure('TEntry', font='Arial 10')
        self.style.configure('TLabel', font='Arial 10')
        self.style.configure('TCombobox', font='Arial 10')
        self.style.configure('TButton', justify=CENTER, font='Arial 10', padding=2)
        self.TimerID = 0
        self.SendingMessage = False  # Разрешение на передачу файла
        # Создание главного каркаса приложения
        self.GeneralNotes = ttk.Notebook()  # Основа
        self.FilePath = ''
        self.CountNewMessages = ''
        self.MAX_FILE_SIZE = 160  # Максимальный размер передаваемого файла в мб
        self.StartLogo = ttk.Frame(self.GeneralNotes)  # Форма стартового логотипа (ХОД КОНЕМ во время ожидания :)
        self.LoginFrame = ttk.Frame(self.GeneralNotes)  # Форма авторизации
        self.RegFrame = ttk.Frame(self.GeneralNotes)  # Форма регистрации
        self.Message = ttk.Frame(self.GeneralNotes)  # Форма сообщения
        self.GeneralTab = ttk.Frame(self.GeneralNotes)  # Главная форма
        self.Options = ttk.Frame(self.GeneralNotes)  # Форма настроек
        self.AdrrBook = ttk.Frame(self.GeneralNotes)  # Форма адресной книги
        self.AddFriend = ttk.Frame(self.GeneralNotes)  # Форма добавления пользователя в адресную книгу
        self.CaptchaForm = ttk.Frame(self.GeneralNotes)  # Форма защиты от авторегистрации
        self.Widgets = []  # Список виджетов для сообщений
        self.editlist = [[], [], [], [], [], [], [], [], []]  # Список Edit'ов
        self.CommandQueue = Queue.Queue()  # Очередь команд
        self.KEYS = None  # Пара ключей для шифрования
        self.PUBLICKEY = None  # Публичный ключ сервера
        threading._start_new_thread(self.GenKeys, ())  # Генерируем ключи для асинхронного шифрования
        self.bind('<Destroy>', self.CloseProgram)  # Событие закрытие окна
        self.CheckStop = False  # Флаг проверка соединения
        self.StopCheckTimer = False  # Остановка таймера проверки соединения
        self.Connected = False  # Статус соединения
        self.TimerID1 = self.after(0, self.Timer)  # Запустим таймер синхронизации
        self.CurMesID = 0  # Айди открытого сообщения
        self.MouseX = 0  # Позиция мыши на кнопке
        self.MouseY = 0
        self.MousePointerID = 'hand2'  # Указатель на кнопках
        self.MessageDate = 0  # Дата читаемого сообщения
        self.FIO = ""  # ФИО Отправителя
        # Загрузка иконок
        self.ImageList = []  # Список иконок
        imgdir = os.path.join(os.path.abspath(unicode(os.curdir)), u'bin\img')
        for i in range(29):
            self.ImageList.append(Tkinter.PhotoImage(u'img' + str(i), file=os.path.join(imgdir, str(i) + u'.gif')))

        # Логотип
        # #########
        # Метки
        ttk.Label(self.StartLogo, image=self.ImageList[25]).place(x=6, y=0)
        ttk.Label(self.StartLogo, text='Почтовый клиент 4.4v', font='Arial 12').place(x=14, y=190)

        # Форма авторизации
        # #################
        # Кнопки
        self.LoginButton = ttk.Button(self.LoginFrame, text='Войти', cursor=self.MousePointerID,
                                      state='disabled', command=self.LoginOnServer, width=23)
        self.LoginButton.grid(row=6, padx=10, pady=5)
        ttk.Button(self.LoginFrame, text='Зарегистрироваться', width=23, cursor=self.MousePointerID,
                   command=self.OpenRegTab).grid(row=7)

        # Метки
        self.StatusLabel1 = ttk.Label(self.LoginFrame, foreground='red')  # Сообщения статуса
        self.StatusLabel1.grid(row=5, pady=1, padx=10, sticky='w')
        ttk.Label(self.LoginFrame, text='Логин').grid(row=1, padx=10, pady=5, sticky='w')
        ttk.Label(self.LoginFrame, text='Пароль').grid(row=3, padx=10, pady=5, sticky='w')

        # Поля ввода
        self.LoginEdit = Entry(self.LoginFrame, text='', width=28)
        self.PasswordEdit = Entry(self.LoginFrame, text='', show='*', width=28)
        self.LoginEdit.bind('<KeyRelease>', self._edit_change_1)
        self.PasswordEdit.bind('<KeyRelease>', self._edit_change_1)
        self.LoginEdit.grid(row=2)
        self.PasswordEdit.grid(row=4)

        # Форма регистрации
        # #################
        # Метки
        NameLabel = ttk.Label(self.RegFrame, text='Имя', cursor='question_arrow')
        NameLabel.grid(row=1, padx=10, pady=2, sticky='w')
        SurnameLabel = ttk.Label(self.RegFrame, text='Фамилия', cursor='question_arrow')
        SurnameLabel.grid(row=5, padx=10, pady=2, sticky='w')
        PatrLabel = ttk.Label(self.RegFrame, text='Отчество', cursor='question_arrow')
        PatrLabel.grid(row=3, padx=10, pady=2, sticky='w')
        LoginLabel = ttk.Label(self.RegFrame, text='Логин', cursor='question_arrow')
        LoginLabel.grid(row=1, column=1, padx=10, pady=2, sticky='w')
        PassLabel = ttk.Label(self.RegFrame, text='Пароль', cursor='question_arrow')
        PassLabel.grid(row=3, column=1, padx=10, pady=2, sticky='w')
        ttk.Label(self.RegFrame, text='Подтверждение пароля').grid(row=5, column=1, padx=10, pady=2, sticky='w')
        self.StatusLabel2 = ttk.Label(self.RegFrame, foreground='red')
        self.StatusLabel2.grid(row=13, padx=10, pady=5, sticky='w', columnspan=2)
        self.SetHint(PassLabel,
                     'Пароль должен состоять не\nменее чем из 8 символов и\nсодержать латинские буквы,\nцифры, знаки !@#$%^&*()-_+=:,./?\|`~[]{}.')
        TextRools = 'Текст должен состоять из\n двух или более символов'
        self.SetHint(NameLabel, TextRools)
        self.SetHint(SurnameLabel, TextRools)
        self.SetHint(PatrLabel, TextRools)
        self.SetHint(LoginLabel, TextRools)

        # Поля ввода
        for i in range(6):
            self.editlist[1].append(Entry(self.RegFrame, width=28))
        for i in range(1, 7):
            self.editlist[1][i - 1].grid(row=(i % 4 + i / 4) * 2, column=i / 4, padx=10)
        for i in range(6):
            self.editlist[1][i].bind('<KeyRelease>', self._edit_change_2)
        self.editlist[1][5]['show'] = '*'
        self.editlist[1][4]['show'] = '*'

        # Кнопки
        self.RegRegisterBtn = ttk.Button(self.RegFrame, text='Зарегистрироваться', state='disabled',
                                         command=self.RegisterForDataBase, cursor=self.MousePointerID, width=23)
        self.RegRegisterBtn.grid(row=14, column=1, padx=10, pady=5)
        ttk.Button(self.RegFrame, text='Отмена', width=23, cursor=self.MousePointerID, command=self.OpenLoginTab).grid(
            row=14, column=0)

        # Форма сообщения
        # ######################

        # Тулбар
        self.Toolbar2 = ttk.Frame(self.Message, height=100)
        self.Toolbar2.grid(row=7)

        # Метки
        TextList1 = ['От:', 'Кому:', 'Тема:']
        for i in range(3):
            ttk.Label(self.Message, text=TextList1[i]).grid(row=i + 1, padx=10, pady=5, sticky='w')
        self.FileLabel = ttk.Label(self.Message, text='No attached files')
        self.FileLabel.place(x=160, y=110)
        self.SpeedLabel = ttk.Label(self.Message, text='v=10000kb/s t=00:00:15')
        StatusSendLabel = ttk.Label(self.Message, text='')
        StatusSendLabel.grid(row=0)

        # Поля ввода
        self.editlist[2].append(Entry(self.Message, width=88))
        self.editlist[2].append(ttk.Combobox(self.Message, width=85, values=['']))  # Поле адресата

        self.editlist[2][1].bind('<Button-1>', self.load_clients);
        self.editlist[2][1].bind('<<ComboboxSelected>>', self.AddrSelect);

        self.editlist[2].append(Entry(self.Message, width=88))

        MemoFr1 = Frame(self.Message)  # Поле ввода сообщения
        MemoFr1.grid(row=6, sticky='w', padx=12, pady=5)
        self.editlist[2].append(Text(MemoFr1, borderwidth=0, bg="white", wrap='word',
                                     font='Arial 10', highlightthickness=0))
        scrollbar1 = ttk.Scrollbar(MemoFr1, command=self.editlist[2][3].yview)  # Соединяем поле с полосой прокрутки
        scrollbar1.pack(side='right', fill='y')
        self.editlist[2][3].pack(side='left')
        self.editlist[2][3]['yscrollcommand'] = scrollbar1.set

        for i in range(3):
            self.editlist[2][i].grid(row=i + 1, sticky='w', columnspan=2, padx=55)

        for i in range(4):
            self.editlist[2][i].bind('<KeyRelease>', self._edit_change_3)

        # Кнопки
        self.SendBtn = ttk.Button(self.Toolbar2, text='Отправить', image=self.ImageList[8],
                                  cursor=self.MousePointerID, compound=LEFT, state='disabled', width=9)
        self.SendBtn.grid(row=0, column=2, padx=20, pady=5)
        self.forwBtn = ttk.Button(self.Toolbar2, text='Назад', width=9, cursor=self.MousePointerID,
                                  image=self.ImageList[13], compound=LEFT, command=self.Forward)
        self.forwBtn.grid(row=0, column=0)
        self.AttBtn = ttk.Button(self.Message, text='Прикрепить\nфайл', cursor=self.MousePointerID,
                                 compound=LEFT, image=self.ImageList[3], width=12)
        self.AttBtn.grid(row=5, padx=12, sticky='w')

        self.PorgressLoadMess = ttk.Progressbar(self.Message, length=428)
        self.PorgressLoadMess.place(x=160, y=134)

        # ####  Главная форма #######
        # ###########################

        # Тулбар
        self.Toolbar3 = ttk.Frame(self.GeneralTab)
        OptBtnIndex = 4  # Индекс столбца начала размещения кнопок управления
        GBtn1 = ttk.Button(self.Toolbar3, text='', width=3, image=self.ImageList[1],
                           cursor=self.MousePointerID, compound=LEFT, command=self.OpenNewMesTab)
        GBtn1.grid(row=0, column=OptBtnIndex, padx=2)
        GBtn2 = ttk.Button(self.Toolbar3, text='', width=3, image=self.ImageList[10],
                           cursor=self.MousePointerID, compound=LEFT, command=self.DelMess)
        GBtn2.grid(row=0, column=OptBtnIndex + 1, padx=2)
        GBtn3 = ttk.Button(self.Toolbar3, text='', width=3, image=self.ImageList[17],
                           cursor=self.MousePointerID, compound=LEFT, command=self.OpenBook)
        GBtn3.grid(row=0, column=OptBtnIndex + 2, padx=2)
        GBtn4 = ttk.Button(self.Toolbar3, text='', width=3, image=self.ImageList[23],
                           cursor=self.MousePointerID, compound=LEFT, command=self.Refresh)
        GBtn4.grid(row=0, column=OptBtnIndex + 3, padx=2)
        GBtn5 = ttk.Button(self.Toolbar3, text='', width=3, image=self.ImageList[18],
                           cursor=self.MousePointerID, compound=LEFT, command=self.OpenOptions)
        GBtn5.grid(row=0, column=OptBtnIndex + 4, padx=2)
        GBtn6 = ttk.Button(self.Toolbar3, text='', width=3, image=self.ImageList[24],
                           cursor=self.MousePointerID, compound=LEFT, command=self.LogOut)
        GBtn6.grid(row=0, column=OptBtnIndex + 5, padx=2)

        SortBtnIndex = 0  # Индекс столбца начала размещения кнопок сортировки
        ttk.Label(self.Toolbar3, text='     ').grid(row=0, column=SortBtnIndex + 3)
        # Кнопки сортировки сообщений
        for i in range(3):
            self.editlist[3].append(ttk.Button(self.Toolbar3, text='', width=4,
                                               image=self.ImageList[19 + i], cursor=self.MousePointerID))
            self.editlist[3][i].grid(row=0, column=i + SortBtnIndex, padx=2)
        self.editlist[3][0]['command'] = self.SetSort0
        self.editlist[3][1]['command'] = self.SetSort1
        self.editlist[3][2]['command'] = self.SetSort2
        self.editlist[3][0]['state'] = 'disabled'
        self.SortIndex = 0

        # Информация о пользователе
        self.UserInfo = ttk.Frame(self.GeneralTab, padding=6)
        self.LabelList = []
        TextList2 = ['Логин:', 'Имя:', 'Отчество:', 'Фамилия:', 'LOGIN', 'NAME', 'PATRONOMIC', 'SURNAME']
        for i in range(8):
            self.LabelList.append(ttk.Label(self.UserInfo, text=TextList2[i]))
            self.LabelList[i].grid(row=i % 4, column=i / 4, sticky='w', padx=4, pady=2)

        self.UserInfo.pack(fill=X)  # Размещаем поле данных пользователя
        self.Toolbar3.pack()  # и тулбар с кнопками

        # Окно сообщений
        self.lowFrame = ttk.Labelframe(self.GeneralTab)  # Основа поля
        self.lowFrame.pack()

        self.canvas = Canvas(self.lowFrame, width=568, height=430,
                             borderwidth=-2)
        self.MessageBox = ttk.Frame(self.canvas)

        self.scrollbar = ttk.Scrollbar(self.lowFrame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side='right', fill=Y)
        self.canvas.pack(side='left', fill=Y)
        self.MessageBoxID = self.canvas.create_window((0, 0), window=self.MessageBox, anchor='nw')
        self.CountOfMessageBox = 0

        def conf(event):  # Реация на прокрутку поля
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
            self.canvas.yview_scroll(-event.delta / 35, UNITS)

        self.MessageBox.bind('<Configure>', conf)  # Ставим обработку прокрутки
        self.MessageBox.bind_all("<MouseWheel>", conf)

        # Сам список сообщений
        self.MesageList = []
        self.WidjetID = []

        # Форма настроек
        # ######################

        # Метки
        TextList2 = ['', 'Логин', 'Имя', 'Отчество', 'Фамилия', 'Новый пароль',
                     'Для применения\nизменений\nвведите пароль', '']
        ttk.Label(self.Options).grid(row=0, pady=0)
        for i in range(1, len(TextList2)):
            if i == 6:
                ttk.Label(self.Options, text=TextList2[i], justify=CENTER).grid(row=6, column=0, padx=10, pady=4,
                                                                                sticky='s', rowspan=2)
                continue
            ttk.Label(self.Options, text=TextList2[i]).grid(row=i, column=0, padx=10, pady=5, sticky='se')

        # Поля ввода
        for i in range(0, len(TextList2) - 3):
            self.editlist[4].append(Entry(self.Options, width=25))
            self.editlist[4][i].grid(row=i + 1, column=1, sticky='w', columnspan=1, padx=4)
            self.editlist[4][i].bind('<KeyRelease>', self._edit_change_4)
        self.editlist[4].append(Entry(self.Options, width=25))
        self.editlist[4][5].grid(row=6, column=1, padx=5, rowspan=2)
        self.editlist[4][5].bind('<KeyRelease>', self._edit_change_4)
        self.editlist[4][4]['show'] = '*'
        self.editlist[4][5]['show'] = '*'

        # Кнопки
        self.forwBtn2 = ttk.Button(self.Options, text='Назад', width=10, cursor=self.MousePointerID,
                                   image=self.ImageList[13], compound=LEFT, command=self.Forward)
        self.forwBtn2.grid(row=8, pady=15, padx=10, column=0)
        self.Apply = ttk.Button(self.Options, text='Применить', compound=LEFT,
                                cursor=self.MousePointerID, image=self.ImageList[14], width=12,
                                command=self.ChangeUserData)
        self.Apply.grid(row=8, column=1, pady=15, padx=10, sticky='e')

        # Форма адресной книги
        # ######################

        # Метки
        self.InformAddrBook = ttk.Label(self.AdrrBook, text=
        'Выберите контакты из списка для отправки сообщения (выбор нескольких с пом. Ctrl)')
        # Кнопки
        self.PosBtnsY = 553
        self.PosBtnsX = 103

        self.forwBtn3 = ttk.Button(self.AdrrBook, text='Назад', width=10, cursor=self.MousePointerID,
                                   image=self.ImageList[13], compound=LEFT, command=self.Forward)
        self.AddFriendsBtn = ttk.Button(self.AdrrBook, text='Добавить', compound=LEFT,
                                        cursor=self.MousePointerID, image=self.ImageList[12], width=10,
                                        command=self.OpenAddFormFriend)
        self.DelFriendsBtn = ttk.Button(self.AdrrBook, text='Удалить', compound=LEFT,
                                        cursor=self.MousePointerID, image=self.ImageList[16], width=10,
                                        command=self.DeleteFriends)
        self.forwBtn3.place(x=self.PosBtnsX, y=self.PosBtnsY)
        self.AddFriendsBtn.place(x=self.PosBtnsX + 136, y=self.PosBtnsY)
        self.DelFriendsBtn.place(x=self.PosBtnsX + 272, y=self.PosBtnsY)

        def autoscroll(sbar, first, last):
            """Hide and show scrollbar as needed."""
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)

        tree_columns = ("Status", "Login", "Name", "Surname", "Patr")
        tree_title = ("Статус", "Логин", "Имя", "Отчество", "Фамилия")

        container = ttk.Frame(self.AdrrBook)
        container.place(x=0, y=0)

        self.tree = ttk.Treeview(columns=tree_columns, show="headings", height=24)
        vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for i in range(len(tree_columns)):
            self.tree.heading(tree_columns[i], text=tree_title[i].title())
            self.tree.column(tree_columns[i], stretch=0, width=125)

        self.tree.column("Status", stretch=0, width=80)
        self.sortby(self.tree, "Status", 0)

        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)

        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # Форма добавления контактов
        # ##########################
        # Метки
        ttk.Label(self.AddFriend, text="Логин добавляемого контакта", ).grid(row=0,
                                                                             padx=10, pady=2, columnspan=2, sticky='w')

        self.editlist[7].append(Entry(self.AddFriend, width=30))  # Поле ввода логина пользователя
        self.editlist[7][0].grid(row=1, padx=10, pady=5, sticky='w', columnspan=2)

        LabelText = ("Имя", "Отчество", "Фамилия")
        for i in range(len(LabelText)):
            ttk.Label(self.AddFriend, text=LabelText[i]).grid(row=i + 2, padx=10, pady=2, sticky='w')

        for i in range(len(LabelText)):
            self.editlist[7].append(ttk.Label(self.AddFriend, text=LabelText[i]))
            self.editlist[7][i + 1].grid(row=i + 2, column=1, padx=10, pady=2, sticky='w')

        # Кнопки
        self.SearchUserBtn = ttk.Button(self.AddFriend, compound=CENTER,
                                        cursor=self.MousePointerID, image=self.ImageList[11], width=0,
                                        command=self.SearchUser)
        self.forwBtn4 = ttk.Button(self.AddFriend, text='', width=3,
                                   cursor=self.MousePointerID, image=self.ImageList[13], compound=CENTER,
                                   command=self.OpenBook)
        self.AddContactToFriendBtn = ttk.Button(self.AddFriend, text='', cursor=self.MousePointerID,
                                                compound=CENTER, image=self.ImageList[12], width=3,
                                                command=self.AddFriendToBase)
        self.SearchUserBtn.grid(row=1, column=3, padx=2, pady=2, sticky='w')
        self.forwBtn4.place(x=60, y=140)
        self.AddContactToFriendBtn.place(x=130, y=140)

        # Форма защиты (капча)
        # ###############################
        self.CanselCaptFunc = NONE

        # Метки
        ttk.Label(self.CaptchaForm, text="Введите код с картинки").place(x=12, y=2)

        # Изображение капчи
        self.l = ttk.Label(self.CaptchaForm, image=self.ImageList[27])
        self.l.image = self.ImageList[27]
        self.l.place(x=10, y=20)

        # Поле ввода капчи
        self.editlist[8].append(Entry(self.CaptchaForm, width=27))  # Поле ввода текста капчи
        self.editlist[8][0].place(x=12, y=110)

        # Кнопки
        self.SendCaptBtn = ttk.Button(self.CaptchaForm, text='Продолжить')
        self.CanselCaptBtn = ttk.Button(self.CaptchaForm, text='Отмена')
        self.RefreshCaptBtn = ttk.Button(self.CaptchaForm, compound=CENTER,
                                         image=self.ImageList[26], width=0, command=self.RefreshCapt)

        self.SendCaptBtn.place(x=116, y=140, height=25, width=95)
        self.CanselCaptBtn.place(x=12, y=140, height=25, width=95)
        self.RefreshCaptBtn.place(x=185, y=108)

        # Заполнение каркаса
        self.GeneralNotes.add(self.LoginFrame)
        self.GeneralNotes.add(self.RegFrame)
        self.GeneralNotes.add(self.Message)
        self.GeneralNotes.add(self.GeneralTab)
        self.GeneralNotes.add(self.Options)
        self.GeneralNotes.add(self.StartLogo)
        self.GeneralNotes.add(self.AdrrBook)
        self.GeneralNotes.add(self.AddFriend)
        self.GeneralNotes.add(self.CaptchaForm)

        # всплывающие подсказки
        #
        self.WaitHint = 600  # млс
        self.HintLabelTimer = None  # Таймер срабатывания подсказки
        self.HintLabel = ttk.Label(background='gainsboro', justify=CENTER, relief='sunken',
                                   padding=3)  # Надпись подсказки
        self.SetHint(GBtn1, 'Новое письмо')
        self.SetHint(GBtn2, 'Удалить письма')
        self.SetHint(GBtn3, 'Адресная книга')
        self.SetHint(GBtn4, 'Обновить список\nсообщений')
        self.SetHint(GBtn5, 'Настройки данных\nпользователя')
        self.SetHint(GBtn6, 'Отключиться\nот сервера')
        self.SetHint(self.editlist[3][0], 'Все письма')
        self.SetHint(self.editlist[3][1], 'Только входящие\nписьма')
        self.SetHint(self.editlist[3][2], 'Только исходящие\nписьма')
        self.SetHint(self.SearchUserBtn, 'Найти контакт')

        self.GeneralNotes.place(x=0, y=-26)  # TabSheets
        self.GeneralNotes.bind('<<NotebookTabChanged>>', self.SelectTab)
        self.GeneralNotes.select(5)  # Стартовая вкладка 5 - стартовый логотип

        # Количество новых сообщений
        self.NewMessCounter = ttk.Label(self.GeneralTab, text='0', foreground='white',
                                        compound=CENTER, image=self.ImageList[28])

    ##################################################
    # #################### МЕТОДЫ ####################
    ##################################################


    # Установка подсказки виджету
    #
    def SetHint(self, Wdj, HintText):
        Wdj.bind('<Enter>', lambda e: self.HintTimer(e, HintText))
        Wdj.bind('<Leave>', self.ForgetHint)

    # Корректное размещение текста в виджете
    #
    def CatTextAndSetHint(self, Wdj, Text, Count):
        if Count > 3 and len(Text) > Count - 3:
            self.SetHint(Wdj, Text)
            Wdj['text'] = Text[:Count - 3] + '...'
            return True
        Wdj['text'] = Text
        return False

    # Сохранение координат на виджете
    #
    def SaveMouseCoordinates(self, event):
        self.MouseX = event.x
        self.MouseY = event.y

    # Таймер подсказок
    #
    def HintTimer(self, event, _text):
        self.update()

        # Таймер был запущен ранее..
        if self.HintLabelTimer:
            self.after_cancel(self.HintLabelTimer)
        # Запуск нового таймера
        self.HintLabelTimer = self.after(self.WaitHint, lambda: self.ShowHint(event, _text))
        event.widget.bind('<Motion>', self.SaveMouseCoordinates)

    # Вычисление координат виджета относительно окна
    #
    def RecCalculatingCoordinates(self, wdg, x, y):
        x += wdg.winfo_x()
        y += wdg.winfo_y()
        ParentName = wdg.winfo_parent()
        if ParentName == '.':
            return (x, y)
        Parent = self.nametowidget(ParentName)
        return self.RecCalculatingCoordinates(Parent, x, y)

    # Вывод подсказки
    #
    def ShowHint(self, event, _text):
        Coordinates = self.RecCalculatingCoordinates(event.widget, self.MouseX, 0)
        self.update()
        wdg = event.widget

        ClientX = self.master.winfo_width()
        px = Coordinates[0]
        self.HintLabel['text'] = _text
        py = Coordinates[1] + wdg.winfo_height()
        MaxLen = 0
        CharWidth = 4
        for Part in _text.split('\n'):
            MaxLen = max(len(Part), MaxLen)

        WidthHint = MaxLen * CharWidth
        if px + WidthHint + 5 > ClientX:
            px -= WidthHint
        self.HintLabel.place(x=px, y=py + 3, anchor='nw')

    # Удаление подсказки
    #
    def ForgetHint(self, event):
        # Остановим таймер, если был запущен
        if self.HintLabelTimer:
            self.after_cancel(self.HintLabelTimer)
            self.HintLabelTimer = None
        event.widget.unbind('<Motion>')
        self.HintLabel.place_forget()
        return

    def DelayForLoadCapt(self):
        self.CheckStop = True  # Остановка проверки соединения
        self.CommandQueue.put(("StateRefrCaptBtn", "disabled"), True)
        self.l["image"] = self.ImageList[27]
        self.l.image = self.ImageList[27]
        req = SendQuestion("CaptImage")
        if not req:
            self.CanselCaptFunc()
            self.CheckStop = False  # Возобновление проверки соединения
            self.RefreshCaptBtn["state"] = "enabled"
            return
        im = Image.new("RGB", (200, 80), "white")
        im.putdata(req)
        CaptImg = ImageTk.PhotoImage(im)
        self.l["image"] = CaptImg
        self.l.image = CaptImg
        self.CheckStop = False  # Возобновление проверки соединения
        self.CommandQueue.put(("StateRefrCaptBtn", "enabled"), True)

    def RefreshCaptThread(self):
        try:
            self.CheckStop = True  # Остановка проверки соединения
            self.CommandQueue.put(("StateRefrCaptBtn", "disabled"), True)
            self.CommandQueue.put(("LoadImageCapt", self.ImageList[27]), True)
            ##            self.l["image"] = self.ImageList[27]
            ##            self.l.image = self.ImageList[27]
            req = SendQuestion("CaptImage")
            if not req:
                self.CanselCaptFunc()
                self.CommandQueue.put(("StateRefrCaptBtn", "enabled"), True)
                self.CheckStop = False  # Возобновление проверки соединения
                ##                self.RefreshCaptBtn["state"] = "enabled"
                return
            im = Image.new("RGB", (200, 80), "white")
            im.putdata(req)
            CaptImg = ImageTk.PhotoImage(im)
            self.CommandQueue.put(("LoadImageCapt", CaptImg), True)
            ##            self.l["image"] = CaptImg
            ##            self.l.image = CaptImg
            self.CheckStop = False  # Возобновление проверки соединения
            ##            self.RefreshCaptBtn["state"] = "enabled"
            self.CommandQueue.put(("StateRefrCaptBtn", "enabled"), True)
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Обновление капчи
    #
    def RefreshCapt(self):
        try:
            threading._start_new_thread(self.RefreshCaptThread, ())
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Удаление выделенных контактов
    #
    def DeleteFriends(self):
        try:
            if self.tree.selection():
                if not askyesno("Удаление контактов",
                                "Вы действительно хотите удалить выбранные контакты?"):
                    return
                DelFriendsList = []
                for Friend in self.tree.selection():
                    DelFriendsList.append(
                        str(self.tree.item(Friend).get("values")[1]))  # Получим индексы выделенных элементов
                if SendQuestion("DeleteFriends") == "OK":
                    if SendQuestion(DelFriendsList) == "OK":
                        for item in self.tree.selection():
                            self.tree.delete(item)
                        return
                showerror("Ошибка", "Операция отменена сервером")
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Добавление контакта пользователю
    #
    def AddFriendToBase(self):
        try:
            req = SendQuestion("AddFriend?" + self.editlist[7][0].get())
            if req == "OK":  # Добавление контакта
                self.OpenBook()
                return
            elif req == "Execute":
                showwarning("Внимание", "Пользователь уже есть в Ваших контактах")
                return
            for i in range(3):
                self.editlist[7][i + 1]["text"] = req[i]
            showwarning("Внимание", "Пользователь с таким логином не найден")
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Поиск пользователя при добавлении в контакты
    #
    def SearchUser(self):
        try:
            UserData = SendQuestion("UserInBase?" + self.editlist[7][0].get())  # Поиск контакта по логину
            if len(UserData) != 3:
                showwarning("Внимание", "Пользователь с таким логином не найден")
            for i in range(3):
                self.editlist[7][i + 1]["text"] = UserData[i]
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Обработчик кнопки "назад"
    #
    def Forward(self):
        self.GeneralNotes.select(3)
        self.master.title("Почтовый клиент")

    # Обработчик кнопки "назад" при рассылке
    #
    def BackToWrite(self):
        self.GeneralNotes.select(2)
        self.InformAddrBook.place_forget()
        self.tree["height"] = 25
        self.forwBtn3["command"] = self.Forward
        self.AddFriendsBtn["command"] = self.OpenAddFormFriend
        self.DelFriendsBtn.place(x=self.PosBtnsX + 136 * 2, y=self.PosBtnsY)
        self.AddFriendsBtn.place_configure(x=self.PosBtnsX + 136)
        self.forwBtn3.place_configure(x=self.PosBtnsX)
        self.master.title("Новое сообщение")

    # Добавление выделенных адресатов в список получателей
    #
    def AddToListOfAddressee(self):
        if self.tree.selection():
            Addressees = []

            for Friend in self.tree.selection():
                FriendInfo = self.tree.item(Friend).get("values");
                FriendInfoStr = "<%s> %s %s" % (FriendInfo[1], FriendInfo[2], FriendInfo[4])
                Addressees.append(FriendInfoStr)  # Получим индексы выделенных элементов
            if "" != ";".join(Addressees):
                self.editlist[2][1].set(";".join(Addressees))  # Добавим адресатов в форму через ";"
        self.tree.selection_toggle(self.tree.selection())  # Снимем с них выделение
        self.BackToWrite()

    # Сортировка строк в списке контактов
    #
    def sortby(self, tree, col, descending):
        """Sort tree contents when a column is clicked on."""
        # grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        # reorder data
        data.sort(reverse=descending)
        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)

        # switch the heading so that it will sort in the opposite direction
        tree.heading(col,
                     command=lambda col=col: self.sortby(tree, col, int(not descending)))

    # Открытие вкладки
    #
    def SelectTab(self, widget):
        id = self.GeneralNotes.index('current')

        # Размеры форм (Величины должны быть четными для корректной центровки окон)
        SizeOfTabs = list([
            (200, 200),
            (390, 220),
            (600, 620),
            (600, 620),
            (310, 325),
            (200, 220),
            (600, 620),
            (246, 200),
            (227, 180)
        ])
        self.GeneralNotes.configure(width=SizeOfTabs[id][0], height=SizeOfTabs[id][1])
        self.master.geometry(str(SizeOfTabs[id][0]) + 'x' + str(SizeOfTabs[id][1]))
        if self.master.winfo_height() > 100 and self.master.winfo_width() > 100:
            x = self.master.winfo_x() + (self.master.winfo_width() - SizeOfTabs[id][0]) / 2
            y = self.master.winfo_y() + (self.master.winfo_height() - SizeOfTabs[id][1]) / 2
            self.master.wm_geometry("+%d+%d" % (x, y))  # Центруем окно относительно предыдущего

    # Изменение полей ввода сообщения
    # и пароля на окне авторизации
    #
    def _edit_change_1(self, event):
        # Если логин > 2 символов и пароль >=8 и ключ сгенерирован, позволим войти
        if (len(self.LoginEdit.get()) >= 2) and (len(self.PasswordEdit.get()) >= 8):
            self.LoginButton['state'] = 'enabled'
        else:
            self.LoginButton['state'] = 'disabled'

    # Изменение полей ввода
    # на окне регистрации
    #
    def _edit_change_2(self, event):
        i = 0
        while i < 6:
            if len(self.editlist[1][i].get()) < 2:
                break
            i += 1

        if (len(self.editlist[1][4].get()) < 8 or
                    len(self.editlist[1][5].get()) < 8 or
                    self.editlist[1][5].get() != self.editlist[1][4].get() or
                    i != 6):
            self.RegRegisterBtn['state'] = 'disabled'
        else:
            self.RegRegisterBtn['state'] = 'enabled'

    # Изменение полей ввода
    # на окне нового сообщения
    #
    def _edit_change_3(self, event):
        state = "enabled"
        for i in range(3):
            if len(self.editlist[2][i].get()) < 2:
                state = 'disabled'
        self.CommandQueue.put(("StateSendBtn", state), True)

    # Изменение полей ввода
    # на окне изменения данных
    #
    def _edit_change_4(self, event):
        i = 0
        while i < 4:
            if len(self.editlist[4][i].get()) < 2:
                break
            i += 1
        if (len(self.editlist[4][5].get()) < 8 or
                (len(self.editlist[4][4].get()) != 0 and
                         len(self.editlist[4][4].get()) < 8) or
                    i != 4):
            self.Apply['state'] = 'disabled'
        else:
            self.Apply['state'] = 'enabled'

    def SendCaptForRegistration(self):
        req = SendQuestion('CaptText?' + self.editlist[8][0].get())
        self.GeneralNotes.select(1)
        if req == "OK":
            self.StatusLabel2['text'] = 'Регистрация пользователя..'
            # Формируем запрос
            quest = self.editlist[1][0].get()
            for i in range(1, 6):
                quest += '?' + self.editlist[1][i].get()
            req = SendQuestion(quest)  # Отправление запроса на регистрацию
            SendQuestion('Exit')  # Закрываем соединение
            CloseSocket()
            if req == 'OK':
                self.StatusLabel2['text'] = ''
                showinfo("Информация", "Пользователь успешно зарегестрирован!")
                self.CommandQueue.put(("OpenLT", 0), True)
                return
            self.StatusLabel2['foreground'] = 'red'
            if req == 'Login':  # Пользователь уже зарегистрирован
                self.StatusLabel2['text'] = 'Такой логин уже используется'
            else:
                self.StatusLabel2['text'] = 'Сервер недоступен'
            return
        self.StatusLabel2['foreground'] = 'red'
        self.StatusLabel2['text'] = 'Введен неверный код'

    def Cansel(self):
        req = SendQuestion("EndCapt")
        self.GeneralNotes.select(1)
        self.StatusLabel2['text'] = ''

    # Открытие окна капчи
    #
    def OpenCaptTab(self):
        self.editlist[8][0].delete(0, END)  # Очистим поля ввода
        self.master.title("Проверка")
        self.SendCaptBtn["command"] = self.SendCaptForRegistration
        self.CanselCaptBtn["command"] = self.Cansel
        self.CanselCaptFunc = self.Cansel
        self.GeneralNotes.select(8)  # Откроем соответствующую вкладку
        self.RefreshCapt()

    # Открытие окна регистрации
    #
    def OpenRegTab(self):
        self.RegRegisterBtn['state'] = 'disabled'
        self.GeneralNotes.select(1)  # Откроем соответствующую вкладку
        for i in range(6):  # Очистим поля ввода
            self.editlist[1][i].delete(0, END)
        self.StatusLabel2['text'] = ''
        self.master.title("Регистрация пользователя")

    # Открытие окна адресной книги
    #
    def OpenBook(self):
        try:
            self.CheckStop = True  # Остановка проверки соединения
            for item in self.tree.get_children():
                self.tree.delete(item)
            FriendsList = SendQuestion("GetFriendsList")  # Получение списка контактов
            if FriendsList:
                for Friend in FriendsList:
                    self.tree.insert('', 'end', values=Friend)
            self.GeneralNotes.select(6)  # Откроем соответствующую вкладку
            self.master.title("Адресная книга")
            self.CheckStop = False  # Возобновление проверки соединения
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Открытие окна авторизации
    #
    def OpenLoginTab(self):
        self.LoginButton['state'] = 'disabled'
        self.GeneralNotes.select(0)  # Откроем соответствующую вкладку
        # self.LoginEdit.delete(0, END) # Очистим поля ввода
        self.PasswordEdit.delete(0, END)
        self.LoginButton['state'] = 'disabled'
        self.master.title("Авторизация")

    # Открытие окна адресной книги для выбора пользователей
    #
    def OpenAdrrBookForSending(self):
        self.forwBtn3["command"] = self.BackToWrite
        self.AddFriendsBtn["command"] = self.AddToListOfAddressee
        self.DelFriendsBtn.place_forget()
        self.tree["height"] = 24
        self.InformAddrBook.place(x=25, y=self.PosBtnsY - 25)
        self.AddFriendsBtn.place_configure(x=self.PosBtnsX + 136 + 65)
        self.forwBtn3.place_configure(x=self.PosBtnsX + 65)
        self.OpenBook()

    # Выбор пользователя в списке адресатов
    #
    def AddrSelect(self, event):
        tmp = self.editlist[2][1].get()
        if self.editlist[2][1].get() == u"Нет контактов онлайн":
            self.editlist[2][1].set('')
        elif self.editlist[2][1].get() == u"Адресная книга...":
            self.editlist[2][1].set('')
            self.OpenAdrrBookForSending()
        else:
            tmp = tmp.split()
            self.editlist[2][1].set("<%s> %s %s" % (tmp[0], tmp[1], tmp[3]))

    # Загрузка клиентов онлайн
    #
    def load_clients(self, event):
        try:
            OnLineList = SendQuestion("OnlineList")  # Получение метаданных сообщения
            OnLineList.append(u"Адресная книга...")
            self.editlist[2][1]["values"] = OnLineList
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Открытие окна нового сообщения
    #
    def OpenNewMesTab(self):
        self.FilePath = ''
        self.PorgressLoadMess['value'] = 0
        self.CommandQueue.put(("StateSendBtn", "disabled"), True)
        self.CommandQueue.put(("StateBackBtn", "enabled"), True)
        self.GeneralNotes.select(2)  # Откроем соответствующую вкладку
        for i in range(3):  # Очистим поля ввода
            self.editlist[2][i]['state'] = 'normal'
            self.editlist[2][i].delete(0, END)
        self.editlist[2][0].insert(0, self.LabelList[4]['text'])
        self.editlist[2][0]['state'] = 'readonly'
        self.editlist[2][3]['state'] = 'normal'
        self.editlist[2][3].delete('0.0', END)
        self.SendBtn['text'] = 'Отправить'
        self.SendBtn['command'] = self.SendMessage
        self.AttBtn['state'] = "enable"
        self.AttBtn['text'] = 'Прикрепить\nфайл'
        self.FileLabel['text'] = "No attached file"
        self.AttBtn['command'] = self.AttFile
        self.master.title("Новое письмо")

    # Открытие окна сообщения
    #
    def OpenRecMesTab(self, event):
        try:
            self.FilePath = ''
            self.PorgressLoadMess['value'] = 0
            self.CommandQueue.put(("StateSendBtn", "enabled"), True)
            self.CommandQueue.put(("StateBackBtn", "enabled"), True)
            Index = self.Widgets.index(event.widget.winfo_id())
            MesID = self.Widgets[Index + 2]  # Получаем ID сообщения
            self.CurMesID = MesID
            # Очистим поля
            for i in range(3):  # Очистим поля ввода
                self.editlist[2][i]['state'] = 'normal'
                self.editlist[2][i].delete(0, END)
            self.editlist[2][3]['state'] = 'normal'
            self.editlist[2][3].delete('0.0', END)

            # Загружаем сообщение с сервера
            self.CheckStop = True  # Остановка проверки соединения
            Message = SendQuestion('GetMessage?' + str(MesID))  # Получение метаданных сообщения
            # Формат сообщения
            # Логин, Имя, Фамилия отправителя, Логин, Имя, Фамилия получателя,
            # Тема, Есть ли файл?, Дата
            FromStr = u"<%s> %s %s" % (Message[0], Message[1], Message[2])
            ToStr = u"<%s> %s %s" % (Message[3], Message[4], Message[5])
            self.editlist[2][0].insert(0, FromStr)
            self.editlist[2][1].insert(0, ToStr)
            self.editlist[2][2].insert(0, Message[6])
            self.FIO = "%s %s <%s>" % (Message[1], Message[2], Message[0])
            self.MessageDate = time.strftime('%d.%m.%Y %H:%M',
                                             time.localtime(float(Message[8])))
            self.AttBtn['state'] = 'enabled'
            if Message[7] == '':  # Добавляем сообщения в список
                self.AttBtn['state'] = 'disabled'
                self.FileLabel['text'] = 'No attached file'
            else:
                self.CatTextAndSetHint(self.FileLabel, Message[7], 43)

            X = ReciveData()  # Получим зашифрованное сообщение
            # Добавим его в поле вывода
            self.editlist[2][3].insert(END, CryptUnit._DecryptMessageAndCheckDS(X[0], X[1], self.KEYS[0], self.KEYS[1],
                                                                                self.PUBLICKEY).decode("utf-16"))

            self.CheckStop = False  # Возобновление проверки соединения

            if SendQuestion("MessageReaded" + '?' + str(MesID)) == 'OK':
                self.Widgets[Index + 1]['image'] = self.ImageList[6]  # Ставим статус прочитанного

            if Message[0].lower() != self.LabelList[4]['text'].lower():
                self.SendBtn['text'] = 'Ответить'
            else:
                self.SendBtn['text'] = 'Новое\nписьмо'

            self.GeneralNotes.select(2)
            for i in range(3):
                self.editlist[2][i]['state'] = 'readonly'
            self.editlist[2][1]['state'] = 'disabled'
            self.editlist[2][3]['state'] = 'disabled'
            self.SendBtn['command'] = self.SendMessage

            self.AttBtn['text'] = 'Скачать\nфайл'
            self.AttBtn['command'] = self.LoadFile

            self.master.title("Входящее (исходящее) письмо")
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Открытие главного окна приложения
    #
    def OpenGeneralTab(self):
        try:
            UserData = SendQuestion('UserData')
            for i in range(4):
                self.CatTextAndSetHint(self.LabelList[4 + i], UserData[i], 60)
            while len(self.MesageList):
                self.DestrComponentsOfMess(self.MesageList.pop())
            self.GetMessages()  # Получаем список сообщений
            self.GeneralNotes.select(3)
            self.master.title("Почтовый клиент")
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Открытие окна настроек
    #
    def OpenOptions(self):
        try:
            UserData = SendQuestion('UserData')
            for i in range(4):
                self.editlist[4][i].delete(0, END)
                self.editlist[4][i].insert(0, UserData[i])
            self.editlist[4][4].delete(0, END)
            self.editlist[4][5].delete(0, END)
            self.Apply['state'] = 'disabled'
            self.GeneralNotes.select(4)
            self.master.title("Настройки")
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Обновление поля сообщений
    #
    def Refresh(self):
        try:

            UserData = SendQuestion('UserData')
            for i in range(4):
                self.LabelList[4 + i]['text'] = UserData[i]
            while len(self.MesageList):
                self.DestrComponentsOfMess(self.MesageList.pop())
            self.GetMessages()  # Получаем список сообщений
            self.NewMessCounter.place_forget()
            self.CountNewMessages = ''
            self.canvas.yview_moveto(0)
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Добавление пользователей в адресную книгу
    #
    def OpenAddFormFriend(self):
        self.editlist[7][0].delete(0, END)
        self.editlist[7][1]["text"] = "No name"
        self.editlist[7][2]["text"] = "No patronomic"
        self.editlist[7][3]["text"] = "No surname"
        self.GeneralNotes.select(7)  # Откроем соответствующую вкладку
        self.master.title("Добавление контакта")

    # Получение списка сообщений от сервера
    #
    def GetMessages(self):
        try:
            # Запрос серверу
            self.CheckStop = True  # Остановка проверки соединения
            CountMessages = SendQuestion("Messages")  # Получение количества блоков
            # Структура сообщения:
            # Id сообщения, Логин, И, Ф отправителя, Логин, И, Ф получателя,
            # Тема письма, Имя файла, Дата, Было ли прочитано?
            for i in range(int(CountMessages)):
                ListMessage = ReciveData()  # Получаем блок сообщений
                for Message in ListMessage:
                    InfoStr = "%s %.1s. -> %s %.1s." % (Message[3], Message[2], Message[6], Message[5])
                    self.AddMesssage(InfoStr, Message[7],
                                     Message[8] != '', time.strftime('%d.%m.%Y %H:%M',
                                                                     time.localtime(float(Message[9]))),
                                     int(Message[10]),
                                     int(self.GetLoginFromFormatStr(Message[1].lower()) == self.LabelList[4][
                                         'text'].lower()),
                                     Message[0])  # Добавляем сообщения в список
            self.CheckStop = False  # Возобновление проверки соединения
            # Добавление получаемых сообщений
            # Сортировка выбранным способом
            if self.SortIndex == 1:
                self.SetSort1()
            elif self.SortIndex == 2:
                self.SetSort2()
            else:
                self.SetSort0()
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Удаление сообщений с сервера
    #
    def DelMess(self):
        # Список пуст
        if len(self.MesageList) == 0:
            return
        try:
            # Удаление сообщений из списка
            NoSelected = True  # Не выделено ни одно из сообщений
            index = 0
            index2 = 0

            for item in self.MesageList:
                if item[15].get() and item[16]:  # Если письмо выделено и отображается
                    NoSelected = False  # Есть выделенные
                    index += 1;
                if item[16]:  # Есть видимые
                    index2 += 1;

            if index == 0:  # Если выделенных нет - удалим все видимые
                index = index2
            if not askyesno("Удаление сообщений",
                            "Вы действительно хотите удалить (" + str(index) + ") сообщений?"):
                return

            index = 0
            while index < len(self.MesageList):
                item = self.MesageList[index]  # Выбор сообщения из списка
                if item[16] and (item[15].get() or NoSelected):
                    if 'NO' == SendQuestion('DelMessage?' + str(item[14])):  # Удаление сообщения на сервере
                        return  # в случае неудачи - выход
                    self.DestrComponentsOfMess(item)  # Удаление формы сообщения из списка
                    self.Widgets.remove(item[14])
                    self.Widgets.remove(item[10])
                    self.Widgets.remove(item[2].winfo_id())
                    self.MesageList.pop(index)
                else:
                    index += 1
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))  # Обновление формы
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Селектор кнопок сортировки
    #
    def SetStateBtn(self, i):
        self.editlist[3][2]['state'] = 'enabled'
        self.editlist[3][0]['state'] = 'enabled'
        self.editlist[3][1]['state'] = 'enabled'
        self.editlist[3][i]['state'] = 'disabled'

    # Сортировка по всем сообщениям
    #
    def SetSort0(self):
        self.SortIndex = 0
        self.SetStateBtn(self.SortIndex)
        for item in self.MesageList:
            self.DestrComponentsOfMess(item)
        for item in self.MesageList:
            self.LayComponentsOfMes(item)
        self.canvas.yview_moveto(0)

    # Сортировка по входящим сообщениям
    #
    def SetSort1(self):
        self.SortIndex = 1
        self.SetStateBtn(self.SortIndex)
        for item in self.MesageList:
            self.DestrComponentsOfMess(item)
        for item in self.MesageList:
            if item[11]['image'][0] == 'img20':
                self.LayComponentsOfMes(item)
        self.canvas.yview_moveto(0)

    # Сортировка по исходящим сообщениям
    #
    def SetSort2(self):
        self.SortIndex = 2
        self.SetStateBtn(self.SortIndex)
        for item in self.MesageList:
            self.DestrComponentsOfMess(item)
        for item in self.MesageList:
            if item[11]['image'][0] == 'img21':
                self.LayComponentsOfMes(item)
        self.canvas.yview_moveto(0)

    # Сортировка по исходящим сообщениям
    #
    def DestrComponentsOfMess(self, item):
        for i in range(1, 5):
            item[i].place_forget()
        item[13].place_forget()
        item[0].grid_forget()
        for i in range(5, 13):
            item[i].grid_forget()
        item[16] = False
        self.CountOfMessageBox -= 1
        if self.CountOfMessageBox < 1:
            self.CountOfMessageBox = 0
        if self.CountOfMessageBox < 5:
            self.canvas.itemconfig(self.MessageBoxID, height=86 * 5)
        else:
            self.canvas.itemconfig(self.MessageBoxID, height=0)

    # Размещение компонентов на форме
    #
    def LayComponentsOfMes(self, item):
        # Размещаем компоненты
        item[1].place(width=25, height=56, x=0, y=0)
        item[2].place(width=447, height=56, x=30, y=0)
        item[3].place(width=110, height=56, x=450, y=0)
        item[4].place(y=16, x=2)
        item[13].place(y=-1, height=65, x=447, width=3)
        item[5].grid(row=0, column=0, pady=3, padx=4, sticky='e')
        item[6].grid(row=0, column=1, pady=3, sticky='w')
        item[7].grid(row=1, column=0, pady=3, padx=4, sticky='e')
        item[8].grid(row=1, column=1, pady=3, sticky='w')
        item[9].grid(row=0, columnspan=3)
        item[10].grid(row=1, column=0)
        item[11].grid(row=1, column=1)
        item[12].grid(row=1, column=2)
        item[0].grid()
        item[16] = True
        self.CountOfMessageBox += 1
        if self.CountOfMessageBox < 1:
            self.CountOfMessageBox = 0
        if self.CountOfMessageBox < 5:
            self.canvas.itemconfig(self.MessageBoxID, height=86 * 5)
        else:
            self.canvas.itemconfig(self.MessageBoxID, height=0)

    # Добавление сообщения в список
    #
    def AddMesssage(self, From, Topic, AttF, Date, State, Type, MessID):
        self.MesageList.append([])
        item = self.MesageList[len(self.MesageList) - 1]
        # 0 Основа
        item.append(ttk.Labelframe(self.MessageBox, width=567, height=86, text=''))
        # 1 Фрейм под флажок
        item.append(ttk.Frame(item[0]))
        # 2 Фрейм под содержание
        item.append(ttk.Frame(item[0]))
        # 3 Фрейм под информацию
        item.append(ttk.Frame(item[0]))
        # 4 Флажок
        item.append(ttk.Checkbutton(item[1], text='', onvalue=1, offvalue=0))
        # 5, 6 От кого письмо
        item.append(ttk.Label(item[2], text='От\Кому:'))
        item.append(ttk.Label(item[2], text=From))
        self.CatTextAndSetHint(item[6], From, 50)
        # 7, 8 Тема письма
        item.append(ttk.Label(item[2], text='Тема:'))
        item.append(ttk.Label(item[2], text=Topic))
        self.CatTextAndSetHint(item[8], Topic, 50)
        # 9 Дата
        item.append(ttk.Label(item[3], text=Date))
        # 10 Иконка прочитанного\непрочитанного письма
        item.append(ttk.Label(item[3], image=self.ImageList[State + 5]))
        StatusText_1 = 'Письмо\nне прочитано'
        if State:
            StatusText_1 = 'Письмо\nпрочитано'
        item[10].bind('<Enter>', lambda e: self.HintTimer(e, StatusText_1))
        item[10].bind('<Leave>', self.ForgetHint)

        # 11 Иконка типа письма
        item.append(ttk.Label(item[3], image=self.ImageList[Type + 20]))
        StatusText_2 = 'Входящее\nписьмо'
        if Type:
            StatusText_2 = 'Исходящее\nписьмо'
        item[11].bind('<Enter>', lambda e: self.HintTimer(e, StatusText_2))
        item[11].bind('<Leave>', self.ForgetHint)

        # 12, 13 Иконка прикрепленного файла и разделительная линия
        item.append(ttk.Label(item[3], image=self.ImageList[AttF * 3]))
        if AttF:
            item[12].bind('<Enter>', lambda e: self.HintTimer(e, 'Прикреплен\nфайл'))
            item[12].bind('<Leave>', self.ForgetHint)
        item.append(ttk.Separator(item[0], orient='vertical'))

        # 14 параметр - уникальный ID сообщения
        item.append(MessID)
        # 15 параметр - Состояние флажка
        item.append(IntVar())
        item[4]['variable'] = item[15]
        # 16 параметр - Отображается ли письмо в списке
        item.append(True)
        # Реакция на нажатие центральной части панели сообщения
        item[2].bind("<Button-1>", self.OpenRecMesTab)
        self.Widgets.append(item[2].winfo_id())
        self.Widgets.append(item[10])
        self.Widgets.append(MessID)

        # Разместим компоненты
        self.LayComponentsOfMes(item)

    # Таймер для синхронизации потоков
    # необходим для согласования работы
    # интерфейса и асинхронных потоков
    def Timer(self):
        try:
            # Обработчик очереди
            while 1:
                self.update()
                if self.CommandQueue.empty():
                    continue
                # Получаем команду из очереди
                Command = self.CommandQueue.get(True)
                # command = (Name, Data)
                CommandName = Command[0]
                CommandData = Command[1]

                if CommandName == "Close":
                    return

                elif CommandName == "OpenLT":
                    self.OpenLoginTab()

                elif CommandName == "OpenGT":
                    self.OpenGeneralTab()

                # -- Форма капчи
                elif CommandName == "StateRefrCaptBtn":
                    self.RefreshCaptBtn["state"] = CommandData
                elif CommandName == "LoadImageCapt":
                    self.l["image"] = CommandData
                    self.l.image = CommandData
                # -- Форма капчи

                # ++ Форма сообщения
                elif CommandName == "StateSendBtn":  # Блокировка\разблокировка кнопки "отправка"
                    self.SendBtn['state'] = CommandData
                elif CommandName == "StateBackBtn":  # Блокировка\разблокировка кнопки "назад"
                    self.forwBtn['state'] = CommandData
                elif CommandName == "StateLoadBtn":  # Блокировка\разблокировка кнопки "загрузка файла"
                    self.AttBtn['state'] = CommandData
                elif CommandName == "PBSetMax":  # Настройки прогрессбара
                    self.PorgressLoadMess['maximum'] = CommandData
                elif CommandName == "PBSetValue":  # Значение прогрессбара
                    self.PorgressLoadMess['value'] = CommandData
                elif CommandName == "LoadFromServerBtn":  # Кнопка загрузки файла с сервера
                    self.AttBtn['command'] = self.LoadFile
                    self.AttBtn['image'] = self.ImageList[3]
                    self.AttBtn['text'] = 'Скачать\nфайл'
                elif CommandName == "LoadFileToServerBtn":  # Кнопка загрузки файла
                    self.AttBtn['command'] = self.AttFile
                    self.AttBtn['image'] = self.ImageList[3]
                    self.AttBtn['text'] = 'Прикрепить\nфайл'
                    self.PorgressLoadMess['value'] = 0
                elif CommandName == "CanselLoadBtn":  # Кнопка отмена
                    self.AttBtn['command'] = self.StopSending
                    self.AttBtn['text'] = u'  Отмена'
                    self.AttBtn['image'] = self.ImageList[7]
                elif CommandName == "ShowFileState":  # Строка состояния загрузки файла
                    self.SpeedLabel.place(x=435, y=110)
                elif CommandName == "ForgetFileState":
                    self.SpeedLabel.place_forget()
                # ++ Форма сообщения

                elif CommandName == "ShowMessage":
                    showinfo("Информация", CommandData)


        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Авторизация на сервере
    #
    def LoginOnServer(self):
        stream = threading.Thread(target=self.Authorization)
        stream.start()  # Вешаем авторизацию в отдельный поток

    # Прикрепление файла
    #
    def AttFile(self):
        self.FilePath = askopenfilename(parent=self)
        FileName = self.FilePath
        FileName = FileName.split('/');
        if self.FilePath != '':
            FileSize = os.path.getsize(self.FilePath) / 1024 / 1024
            if FileSize > self.MAX_FILE_SIZE:
                showerror("Ошибка", "Размер файла не должен превышать " + str(self.MAX_FILE_SIZE) + "мб!")
                self.FilePath = ""
                return
            self.CatTextAndSetHint(self.FileLabel, FileName.pop(), 43)
        else:
            self.FileLabel['text'] = "No attached file"

    # Загрузка файла
    #
    def LoadFile(self):
        FilePath = asksaveasfilename(initialfile=self.FileLabel["text"])
        if not FilePath:
            return
        # self.LoadingFile(FilePath)
        threading._start_new_thread(self.LoadingFile, (FilePath,))  # Запуск отправления данных на сервер

    def LoadingFile(self, FilePath):
        try:
            self.CheckStop = True  # Остановка проверки соединения
            CountBlocks = SendQuestion("LoadFile?" + str(self.CurMesID))  # Получение количества блоков
            if CountBlocks == '0':
                self.CheckStop = False
                return

            self.SendingMessage = True
            # Передача файла

            self.CommandQueue.put(("StateSendBtn", "disabled"), True)  # Блокируем кнопку отправки и "назад"
            self.CommandQueue.put(("CanselLoadBtn", 0), True)  # Делаем кнопку отмена
            self.CommandQueue.put(("PBSetValue", 0), True)  # Установим значение статусбара в 0
            self.CommandQueue.put(("PBSetMax", CountBlocks), True)  # Настройка прогрессбара
            self.CommandQueue.put(("StateBackBtn", "disabled"), True)
            self.CommandQueue.put(("ShowFileState", 0), True)

            FileSize = CountBlocks
            StandartSize = (1024 * 1024)
            blocksize = StandartSize
            INF = 10 ** 20
            SpeedList = {
                StandartSize / 16: INF,
                StandartSize / 8: INF,
                StandartSize / 4: INF,
                StandartSize / 2: INF,
                StandartSize: INF,
                StandartSize * 2: INF,
                StandartSize * 3: INF,
                StandartSize * 4: INF
            }
            if FileSize / 1024 / 1024 < 20:
                SpeedList[StandartSize * 2] = 0
                SpeedList[StandartSize * 3] = 0
                SpeedList[StandartSize * 4] = 0
            CurSize = 0
            File = open(FilePath, "wb")
            OperationTime = 0
            _tmpTime = 0
            Speed = 0
            while FileSize > CurSize:
                File.write(ReciveData())
                # Увеличиваем прогрессбар
                CurSize += blocksize
                self.CommandQueue.put(("PBSetValue", CurSize), True)
                if not self.SendingMessage:
                    SendData("stop")  # остановим передачу данных на сервер
                    break;
                if _tmpTime != 0:
                    OperationTime = time.time() - _tmpTime
                    Speed = blocksize / OperationTime / 1024  # kb/s
                    m, s = divmod((FileSize - CurSize) / blocksize * OperationTime, 60)
                    h, m = divmod(m, 60)
                    self.SpeedLabel["text"] = "t=%d:%02d:%02d v=%dkb\s" % (h, m, s, Speed)
                    SpeedList[blocksize] = Speed
                    blocksize = max(SpeedList, key=SpeedList.get)
                SendData(blocksize)  # Подтверждение передачи файла
                _tmpTime = time.time()
            ##            for i in range(int(CountBlocks)):
            ##                File.write(ReciveData())
            ##                # Увеличиваем прогрессбар
            ##                self.CommandQueue.put(("PBSetValue", i), True)
            ##                if not self.SendingMessage:
            ##                    SendData("stop") # остановим передачу данных на сервер
            ##                    break;
            ##                SendData("")
            ##            ReciveData() # Подтверждение передачи файла
            File.close()
            self.CheckStop = False
            if not self.SendingMessage:
                os.remove(FilePath)
            self.CommandQueue.put(("StateBackBtn", "enabled"), True)
            self.CommandQueue.put(('PBSetValue', 0), True)
            self.CommandQueue.put(('LoadFromServerBtn', 0), True)
            self.CommandQueue.put(('StateSendBtn', 'enabled'), True)
            self.CommandQueue.put(("ForgetFileState", 0), True)
            if self.SendingMessage:
                self.CommandQueue.put(('ShowMessage', 'Файл успешно загружен!'), True)

        except Exception as e:
            showerror("Ошибка", e.args)
            self._disconnect_event()

    # Отмена загрузки с/на серверa
    #
    def StopSending(self):
        self.SendingMessage = False

    # Передача сообщения с файлом
    #
    def SendTextAndFile(self, FilePath):
        try:
            Text = self.editlist[2][3].get(1.0, END + '-1c')  # Загрузим сообщение в память

            self.CheckStop = True  # Остановка проверки соединения

            self.SendingMessage = True  # Разрешение на передачу сообщения
            self.CommandQueue.put(("StateBackBtn", "disabled"), True)
            self.CommandQueue.put(("StateSendBtn", "disabled"), True)  # Блокируем кнопку отправки
            self.CommandQueue.put(("PBSetValue", 0), True)  # Установим значение статусбара в 0

            # Передача файла, если он есть
            if FilePath:
                self.CommandQueue.put(("CanselLoadBtn", 0), True)  # Делаем кнопку отмена
                # self.SendingFile # Разрешение на передачу
                BLOCK_SIZE = 1024 * 512  # размер блока

                File = open(FilePath, "rb")
                buff = File.read()  # Считаем файл в оперативку
                size = len(buff)
                blocks = size / BLOCK_SIZE  # Колиечство блоков
                if size % BLOCK_SIZE:
                    blocks += 1

                self.CommandQueue.put(("PBSetMax", size), True)  # Настройка прогрессбара

                SendData(size)  # Передаем размер файла

                FileSize = size
                StandartSize = (1024 * 1024)
                blocksize = StandartSize
                INF = 10 ** 20
                SpeedList = {
                    StandartSize / 16: INF,
                    StandartSize / 8: INF,
                    StandartSize / 4: INF,
                    StandartSize / 2: INF,
                    StandartSize: INF,
                    StandartSize * 2: INF,
                    StandartSize * 3: INF,
                    StandartSize * 4: INF
                }
                if FileSize / 1024 / 1024 < 20:
                    SpeedList[StandartSize * 2] = 0
                    SpeedList[StandartSize * 3] = 0
                    SpeedList[StandartSize * 4] = 0
                CurSize = 0
                OperationTime = 0
                _tmpTime = 0
                Speed = 0
                self.CommandQueue.put(("ShowFileState", 0), True)
                while FileSize > CurSize:
                    SendData(buff[CurSize:CurSize + blocksize])
                    ReciveData()
                    # Увеличиваем прогрессбар
                    CurSize += blocksize
                    self.CommandQueue.put(("PBSetValue", CurSize), True)
                    if not self.SendingMessage:
                        SendData("stop")  # остановим передачу данных на сервер
                        break;
                    if _tmpTime != 0:
                        OperationTime = time.time() - _tmpTime
                        Speed = blocksize / OperationTime / 1024  # kb/s
                        m, s = divmod((FileSize - CurSize) / blocksize * OperationTime, 60)
                        h, m = divmod(m, 60)
                        self.SpeedLabel["text"] = "t=%d:%02d:%02d v=%dkb\s" % (h, m, s, Speed)
                        SpeedList[blocksize] = Speed
                        blocksize = max(SpeedList, key=SpeedList.get)
                    _tmpTime = time.time()
                ##                SendData(blocks) # Передаем количество блоков
                ##                for i in range(blocks):
                ##                    SendData(buff[i * BLOCK_SIZE:(i + 1) * BLOCK_SIZE])
                ##                    ReciveData()
                ##                    # Увеличиваем прогрессбар
                ##                    self.CommandQueue.put(("PBSetValue", i), True)
                ##                    if not self.SendingMessage:
                ##                        SendData("stop") # остановим передачу данных на сервер
                ##                        break;
                if self.SendingMessage:
                    SendData("stoploading")
                File.close()
            else:
                SendData(0)
            self.CommandQueue.put(("LoadFileToServerBtn", 0), True)  # Делаем кнопку загрузки файла

            if not self.SendingMessage:
                self.CommandQueue.put(("ForgetFileState", 0), True)
                self.CommandQueue.put(("StateBackBtn", "enabled"), True)
                self.CommandQueue.put(("PBSetValue", 0), True)  # Установим значение статусбара в 0
                self.CheckStop = False  # Возобновление проверки соединения
                self.CommandQueue.put(("StateSendBtn", "enabled"), True)  # Разблокируем кнопку отправки сообщения
                return

            ReciveData()  # Подтверждение получение файла

            # Передадим зашифрованное сообщение
            # и получим ответ о получении
            SendQuestion(CryptUnit._GenSessionKeyAndEncryptMsg(Text.encode("utf-16"), self.PUBLICKEY, self.KEYS[0]))
            self.CommandQueue.put(("OpenGT", 0), True)  # Откроем главное окно
            self.CommandQueue.put(("StateLoadBtn", "enabled"), True)
            self.CommandQueue.put(("ForgetFileState", 0), True)
            self.CommandQueue.put(("PBSetValue", 0), True)  # Установим значение статусбара в 0
            self.CommandQueue.put(("StateSendBtn", "enabled"), True)  # Разблокируем кнопку отправки сообщения
            self.CommandQueue.put(("StateBackBtn", "enabled"), True)
            self.CheckStop = False  # Возобновление проверки соединения
            return
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Получение логина из
    # форматированной строки
    #
    def GetLoginFromFormatStr(self, FormatStr):
        FormatStr.split()
        Start = FormatStr.find("<") + 1  # Индекс начала логина
        End = FormatStr.rfind(">")  # Индекс конца логина
        if Start == 0 or End == -1:
            if Start == 0 and End == -1:
                FormatStr = FormatStr.split()
                if len(FormatStr) == 1:
                    return FormatStr[0]
            return
        FormatStr = FormatStr[Start:End].split()
        FormatStr = "".join(FormatStr)
        return FormatStr

    # Отправление сообщения
    # Ответ на сообщение пользователя
    # Новое сообщения для пользователя
    # Отмена передачи файла
    #
    def SendMessage(self):
        try:
            if self.SendBtn['text'] == u'Отправить':  # Отправление сообщения

                quest = 'NewMessage'
                if self.editlist[2][1].get() == "":
                    showerror("Ошибка", "Заполните адресатов!")
                    return
                elif self.editlist[2][2].get() == "":
                    showerror("Ошибка", "Заполните тему сообщения!")
                    return
                UsersInfo = self.editlist[2][1].get()
                # Выделяем логины пользователей
                # На входе строка содержит любую последовательность,
                # id пользователя пишется в угловых скобках
                UsersInfo = UsersInfo.split(';')  # Разделим на строки каждого пользователя
                # Выделим логин
                Logins = []
                for UserInfo in UsersInfo:
                    Logins.append(self.GetLoginFromFormatStr(UserInfo))
                quest += '?%s?%s?%s' % (
                    self.GetLoginFromFormatStr(self.editlist[2][0].get()),
                    ";".join(Logins), self.editlist[2][2].get()
                )
                tmp = self.FilePath
                quest += '?' + tmp.split('/').pop()  # Название прикрепленного файла
                if 'NO' == SendQuestion(quest):  # Отправим на сервер запрос о новом сообщении
                    showerror("Ошибка", "Заявленные адресаты не зарегестрированы!" \
                                        "\nПроверьте корректность написания логинов получателей\nФормат логина получателя: [<]Login[>]")
                    return  # Такого адресата нет
                self.CommandQueue.put(("StateSendBtn", "disabled"), True)
                threading._start_new_thread(self.SendTextAndFile,
                                            (self.FilePath,))  # Запуск отправления данных на сервер
                return

            elif self.SendBtn['text'] == u'Ответить':  # Ответ на сообщение
                From = self.editlist[2][1].get()
                To = self.editlist[2][0].get()
                for i in range(2):  # Очистим поля ввода
                    self.editlist[2][i]['state'] = 'normal'
                    self.editlist[2][i].delete(0, END)
                self.editlist[2][2]['state'] = 'normal'
                FormatString = self.editlist[2][2].get().split(":")
                if FormatString[0][:2] == "RE":
                    if FormatString:
                        if FormatString[0] == "RE":
                            FormatString[0] = "RE[1]"
                        else:
                            REList = FormatString[0].split("[")
                            REList = REList[1].split("]")[0]
                            if REList.isdigit():
                                REList = str(int(REList) + 1)
                                REList = "RE[" + REList + "]"
                                FormatString[0] = REList
                    FormatString = ":".join(FormatString)
                    self.editlist[2][2].delete(0, END)
                    self.editlist[2][2].insert(0, FormatString)  # Тема
                else:
                    self.editlist[2][2].insert(0, "RE: ")

                self.editlist[2][0].insert(0, From)  # От
                self.editlist[2][1].insert(0, To)  # Кому
                self.editlist[2][0]['state'] = 'readonly'
                self.editlist[2][3]['state'] = 'normal'
                self.AttBtn['state'] = "enable"
                self.FileLabel['text'] = "No attached file"
                self.FilePath = ''

                i = 4
                DateStr = self.MessageDate.split()
                TitleStr = u"\n\n>> %s в %s, %s написал(а):\n" % (DateStr[0], DateStr[1], self.FIO)

                self.editlist[2][3].insert("1.0", TitleStr)
                while (self.editlist[2][3].get(str(i) + ".0", END + '-1c') != u""):
                    self.editlist[2][3].insert(str(i) + ".0", u'> ')
                    i += 1
                    # self.editlist[2][3].insert('0.0', (To + u': «'))
                    # self.editlist[2][3].insert(END, '»\n--------------------------------------\n\t')

            elif self.SendBtn['text'] == u'Новое\nписьмо':
                self.CommandQueue.put(('StateSendBtn', 'disabled'), True)
                self.AttBtn['state'] = "enable"
                self.FileLabel['text'] = "No attached file"
                self.FilePath = ''
                self.editlist[2][2]['state'] = 'normal'
                self.editlist[2][1]['state'] = 'normal'
                self.editlist[2][2].delete(0, END)  # Тема
                self.editlist[2][3]['state'] = 'normal'
                self.editlist[2][3].delete('0.0', END)

            self.SendBtn['text'] = 'Отправить'
            self.AttBtn['text'] = 'Прикрепить\nфайл'
            self.AttBtn['command'] = self.AttFile
            self.master.title("Новое письмо")
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Регистрация в базе
    #
    def RegisterForDataBase(self):
        # stream = threading.Thread(target = Registration)
        # stream.start() # Вешаем регистрацию в отдельный поток
        # Проверим корректность введенных данных
        NotCorrectData = False
        for edit in self.editlist[1]:
            for j in edit.get():
                if not j.isalpha() and not j == ' ' and not (j in "!@#$%^&*()-_+=:,./?\\|`~[]{}.") and j in range(10):
                    NotCorrectData = True
        if NotCorrectData:  # Данные содержат ошибки
            self.StatusLabel2['foreground'] = 'red'
            self.StatusLabel2['text'] = 'Допустимы только [Буквы] [0..9] !@#$%^&*()-_+=:,./?\\|`~[]{}.'
            return
        try:
            self.StatusLabel2['foreground'] = 'Dim Gray'
            InitSocket()  # Установим подключение к серверу
            self.StatusLabel2['text'] = 'Подключение к серверу..'
            if not ConnectToServer(5):
                self.StatusLabel2['foreground'] = 'red'
                self.StatusLabel2['text'] = 'Сервер недоступен'
                return
            hello = ReciveData()
            if hello == "NO":  # Получение приветствия от сервера
                self.StatusLabel2['foreground'] = 'red'  # Сервер перегружен
                self.StatusLabel2['text'] = 'Сервер перегружен'
                # разрываем соединение
                SendQuestion('Exit')
                CloseSocket()
                return
            elif hello != "Server v4.4":
                self.StatusLabel2['foreground'] = 'red'  # Сервер имеет неподходящую версию
                self.StatusLabel2['text'] = 'Сервер ранней версии'
                # разрываем соединение
                SendQuestion('Exit')
                CloseSocket()
                return

            # Защита от роботов
            SendQuestion('Reg')
            self.OpenCaptTab()

        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Выход
    def LogOut(self):
        try:
            self.StopCheckTimer = True  # Остоновим таймер проверки соединения
            # разрываем соединение
            SendQuestion('Exit')
            CloseSocket()
            self.StatusLabel1['foreground'] = 'red'
            self.PasswordEdit.delete(0, END)
            self._edit_change_1(None)
            self.StatusLabel1['text'] = ''
            self.SetSort0()
            self.CommandQueue.put(("OpenLT", 0), True)
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Изменение данных пользователя
    #
    def ChangeUserData(self):
        try:
            self.CheckStop = True  # Остановка проверки соединения

            quest = 'UpdateUserData'
            for i in range(6):
                quest += '?' + self.editlist[4][i].get()
            req = SendQuestion(quest)
            if 'OK' != req:
                if 'NO' == req:
                    showerror('Ошибка', 'Данные пользователя\nне были изменены!')
                else:
                    showwarning("Внимание", "Пользователь с таким логином\nуже зарегестрирован!")
            else:
                showinfo("Информация", "Данные пользователя\nуспешно изменены!")
                self.Refresh()
            self.editlist[4][4].delete(0, END)
            self.editlist[4][5].delete(0, END)
            self.Apply['state'] = 'disabled'
            self.CheckStop = False  # Возобновим проверку соединения
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Авторизация
    #
    def Authorization(self):
        try:
            self.Connected = False
            self.StatusLabel1['foreground'] = 'Dim Gray'
            InitSocket()  # Установим подключение к серверу
            self.StatusLabel1['text'] = 'Подключение к серверу..'
            if not ConnectToServer(5):
                self.StatusLabel1['foreground'] = 'red'
                self.StatusLabel1['text'] = 'Сервер недоступен'
                CloseSocket()
                return

            self.StatusLabel1['text'] = 'Ожидание ответа..'
            answ = ReciveData()
            if answ != "Server v4.4":
                self.StatusLabel1['foreground'] = 'red'
                self.StatusLabel1['text'] = 'Сервер ранней версии'
                # разрываем соединение
                SendQuestion('Exit')
                CloseSocket()
                return
            elif answ == "No":  # Получение приветствия от сервера
                self.StatusLabel1['foreground'] = 'red'  # Сервер перегружен
                self.StatusLabel1['text'] = 'Сервер перегружен'
                # разрываем соединение
                SendQuestion('Exit')
                CloseSocket()
                return
            print answ
            self.StatusLabel1['text'] = 'Авторизация..'

            # формируем запрос для идентификации пользователя
            req = SendQuestion('Login?' + self.LoginEdit.get() + '?' + self.PasswordEdit.get())
            # Возможны варианты
            # NO в случае неудачи
            # открытый ключ [<PUBLICKEY>] в случае удачной авторизации
            if req == 'NO':
                self.PasswordEdit.delete(0, END)
                self._edit_change_1(None)
                self.StatusLabel1['text'] = 'Неверное имя или пароль'
            else:
                if req == 'BANNED':
                    self.PasswordEdit.delete(0, END)
                    self._edit_change_1(None)
                    self.StatusLabel1['text'] = 'Вы заблокированы'
                else:  # Положительный ответ
                    self.PUBLICKEY = req  # Сохраним публичный ключ сервера

                    SendData(self.KEYS[0])  # Отправим публичный ключ клиента серверу

                    self.Connected = True
                    self.after(1000, self.CheckConnection)  # Вешаем проверку соединения в отдельный поток
                    self.CommandQueue.put(("OpenGT", 0), True)  # Откроем главное окно
                    self.StatusLabel1['text'] = ''
                    return
            # Не авторищирован - разрываем соединение
            SendQuestion('Exit')
            CloseSocket()
            self.StatusLabel1['foreground'] = 'red'
            return
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Регистрация
    #
    def Registration(self):
        # Проверим корректность введенных данных
        NotCorrectData = False
        for edit in self.editlist[1]:
            for j in edit.get():
                if not j.isalpha() and not j == ' ' and not (j in "!@#$%^&*()-_+=:,./?\\|`~[]{}.") and j in range(10):
                    NotCorrectData = True
        if NotCorrectData:  # Данные содержат ошибки
            self.StatusLabel2['foreground'] = 'red'
            self.StatusLabel2['text'] = 'Допустимы только [Буквы] [0..9] !@#$%^&*()-_+=:,./?\\|`~[]{}.'
            return
        try:
            self.StatusLabel2['foreground'] = 'Dim Gray'
            InitSocket()  # Установим подключение к серверу
            self.StatusLabel2['text'] = 'Подключение к серверу..'
            if not ConnectToServer(5):
                self.StatusLabel2['foreground'] = 'red'
                self.StatusLabel2['text'] = 'Сервер недоступен'
                return
            print ReciveData()  # Получение приветствия от сервера
            # Защита от роботов
            self.OpenCaptTab()

        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение

    # Действие при отключении от сервера
    #
    def _disconnect_event(self):
        self.Connected = False
        self.CommandQueue.put(("OpenLT", 0), True)

    # Проверка соединения
    #
    def CheckConnection(self):
        self.Connected = True
        if self.CheckStop:  # Приостановление проверки
            self.after(3000, self.CheckConnection)
            return

        if self.StopCheckTimer:  # Остановка проверки
            self.StopCheckTimer = False
            return

        try:
            answer = SendQuestion('Reply')
            if answer:
                if answer == 'Refresh':
                    if self.CountNewMessages == '':
                        self.NewMessCounter.place(x=426, y=129, height=19)
                    count = SendQuestion('HowManyNews')
                    self.CountNewMessages = str(count)
                    self.NewMessCounter['text'] = str(count)
                    self.SetHint(self.NewMessCounter, 'Количество новых\nсообщений')
                elif self.CountNewMessages != '':
                    self.NewMessCounter.place_forget()
                    self.CountNewMessages = ''
                self.after(3000, self.CheckConnection)
                return
        except Exception, e:
            pass
        self.StatusLabel1['foreground'] = 'red'
        self.StatusLabel1['text'] = 'Сервер недоступен'
        self._disconnect_event()

    # Генерация ключей
    #
    def GenKeys(self):
        print "Generate crypt keys..."
        self.KEYS = CryptUnit._GenerateKeys()
        self.CommandQueue.put(("OpenLT", 0), True)
        print "OK."

    # Событие закрытия программы
    #
    def CloseProgram(self, event):
        try:
            self.CommandQueue.put(("Close", 0), True)
            SendQuestion('Exit')
            CloseSocket()
            self.after_cancel(self.TimerID1)
        except Exception, e:
            showerror("Ошибка", e.args)
            self._disconnect_event()  # Разрываем соединение
