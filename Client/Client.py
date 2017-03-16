#! /usr/bin/env Python
import os
import ClientGUI
from tkMessageBox import *

def main():
    try:
        # Графический интерфейс
        Form = ClientGUI.GUI()
        Form.master.title("")
        CenterX = Form.master.winfo_screenwidth() / 2
        CenterY = Form.master.winfo_screenheight() / 2
        Form.master.wm_geometry("+%d+%d" % (CenterX - 100, CenterY - 110)) # Установим окно по центру
        Form.master.resizable(width=False, height=False) # Запрет на изменение размеров окна
        Form.master.iconbitmap(default=os.path.join(os.path.abspath(os.curdir), 'bin\img\\') + 'logo.ico')
        Form.mainloop()
    except Exception, e:
        showerror("Ошибка", e.args)

main()
