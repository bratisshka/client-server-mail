# coding=utf-8

import sqlite3 as lite
import tkMessageBox
from Tkinter import *
from config import get_command, set_command  # а вот это вот дичайший костыль

BASE_NAME = "..\Server\Bin\DB\USERS.db"


class But_print:
    def __init__(self, root):
        scrollbar = Scrollbar(orient=VERTICAL)
        self.root = root
        self.lbox1 = Listbox(root, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lbox1.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.lbox1.config(height='25')
        self.lbox1.pack(side=TOP, fill=X)
        self.lbox1.pack()
        self.lbox1.delete(0, END)
        # кнопка выхода из формы
        self.butExit = Button(root, text="Выход",  # надпись на кнопке
                              bg="white", fg="black",
                              )
        self.butExit.place(x=570, y=405, width=100, height=40)
        self.butExit.bind("<Button-1>", self.ExitFun)
        # кнопка блокирования пользователя
        self.butLock = Button(root, text="Блокировать",  # надпись на кнопке
                              bg="white", fg="black",
                              )
        self.butLock.place(x=460, y=405, width=100, height=40)
        self.butLock.bind("<Button-1>", self.ClockFun)
        # кнопка разблокирования пользователя
        self.butUnLock = Button(root, text="Разблокировать",  # надпись на кнопке
                                bg="white", fg="black",
                                )
        self.butUnLock.place(x=350, y=405, width=100, height=40)
        self.butUnLock.bind("<Button-1>", self.UnClockFun)
        # self.butExit.place(x=460, y=405, width=100, height=40)
        # spisok = [1,2,3,4,5,6,7,8,9,10,11,21,87,6,7,4,7,3,3,2,4,5,3,2,4,2,4,2,4,24,2,4,4]
        # i=0
        # for i in spisok:
        #    self.lbox1.insert(END, "Users list:")
        #   i=i+1

        con = lite.connect(BASE_NAME)  # соединение с базой
        with con:
            cur = con.cursor()
            cur.execute("SELECT Login, Name, Surname,ConConection FROM Users")
            rows = cur.fetchall()
            #self.lbox1.insert(END, "Логин     Имя    Фамилия    Блокирован(0)\Разблокирован(1)")
            now_rows = [list(row) for row in rows]
            for row in now_rows:
                if row[3] == 1:
                    row[3] = u"UNBLOCKED"
                else:
                    row[3] = u"BLOCKED"
            rows = now_rows
            # print(rows)
            for row in rows:
                UpdateRow = str(row).replace("[u'", "")
                UpdateRow = UpdateRow.replace("',", "")
                UpdateRow = UpdateRow.replace("u'", "")
                UpdateRow = UpdateRow.replace("']", "")
                UpdateRow = UpdateRow.replace(" ", "    ")
                self.lbox1.insert(END, UpdateRow)

    def ClockFun(self, event):  # Кнопка блокировки
        try:
            selectIndex = self.lbox1.curselection()
            if len(selectIndex) == 0:
                tkMessageBox.showerror("Error!!!!", "Пользователь не выбран")
                return
            if selectIndex[0] != 0:
                value = self.lbox1.get(selectIndex[0], selectIndex[0])
                SplitString = str((value[0])).split(" ")
                manival = SplitString[0].replace("(u'", "")
                manival2 = manival.replace("',", "")
                con = lite.connect(BASE_NAME)
                cur = con.cursor()
                cur.execute("UPDATE  Users SET ConConection = '" + str(FALSE) + "'" + "WHERE Login ='" + manival2 + "'")
                # -----------------------------------------------------------------------------
                cur.execute("SELECT Login, Name, Surname,ConConection FROM Users")
                set_command(manival2, 1)
                rows = cur.fetchall()
                now_rows = [list(row) for row in rows]
                for row in now_rows:
                    if row[3] == 1:
                        row[3] = u"UNBLOCKED"
                    else:
                        row[3] = u"BLOCKED"
                rows = now_rows
                self.lbox1.delete(0, END)
                # self.lbox1.insert(END, "Логин     Имя    Фамилия    Блокирован(0)\Разблокирован(1)")

                for row in rows:
                    UpdateRow = str(row).replace("[u'", "")
                    UpdateRow = UpdateRow.replace("',", "")
                    UpdateRow = UpdateRow.replace("u'", "")
                    UpdateRow = UpdateRow.replace("']", "")
                    UpdateRow = UpdateRow.replace(" ", "    ")
                    self.lbox1.insert(END, UpdateRow)
                    # ----------------------------------------------------------------------
                con.commit()
                con.close()
        except Exception, e:
            tkMessageBox.showerror("Error!!!!", "Произошла ошибка при блокировании пользователя" + e.args)
            return

    def UnClockFun(self, event):  # Кнопка разблокировки
        try:
            selectIndex = self.lbox1.curselection()
            if len(selectIndex) == 0:
                tkMessageBox.showerror("Error!!!!", "Пользователь не выбран")
                return
            if selectIndex[0] != 0:
                value = self.lbox1.get(selectIndex[0], selectIndex[0])
                SplitString = str((value[0])).split(" ")
                manival = SplitString[0].replace("(u'", "")
                manival2 = manival.replace("',", "")
                con = lite.connect(BASE_NAME)
                cur = con.cursor()
                cur.execute("UPDATE  Users SET ConConection = '" + str(TRUE) + "'" + "WHERE Login ='" + manival2 + "'")

                # -----------------------------------------------------------------------------
                cur.execute("SELECT Login, Name, Surname,ConConection FROM Users")
                rows = cur.fetchall()
                now_rows = [list(row) for row in rows]
                for row in now_rows:
                    if row[3] == 1:
                        row[3] = u"UNBLOCKED"
                    else:
                        row[3] = u"BLOCKED"
                rows = now_rows
                self.lbox1.delete(0, END)
                # self.lbox1.insert(END, "Логин     Имя    Фамилия    Блокирован(0)\Разблокирован(1)")
                for row in rows:
                    UpdateRow = str(row).replace("[u'", "")
                    UpdateRow = UpdateRow.replace("',", "")
                    UpdateRow = UpdateRow.replace("u'", "")
                    UpdateRow = UpdateRow.replace("']", "")
                    UpdateRow = UpdateRow.replace(" ", "    ")
                    self.lbox1.insert(END, UpdateRow)
                    # ----------------------------------------------------------------------
                con.commit()
                con.close()
        except Exception, e:
            tkMessageBox.showerror("Error!!!!", "Произошла ошибка при разблокировании пользователя" + e.args)
            return

    def ExitFun(self, event):
        self.root.destroy()


if __name__ == "__main__":
    root = Tk()  # Окно
    root.geometry('700x450')  # Размер окнаа
    root.title('Списки пользователей')  # Заголовок окна
    root.resizable(width=False, height=False)  # Запрет на изменение размеров окна
    obj = But_print(root)
    root.mainloop()
