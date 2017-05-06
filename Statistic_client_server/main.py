# Низкоуровневое получение данных
#
import sqlite3
from time import sleep


def update_statistic(t):
    """
    Вывод статистики на графике
    :param t: 
    :return: 
    """
    # необходимо учитывать как тех, кто послал, так и тех, кто принял
    ids = set([x[3] for x in t]).union(set([x[4] for x in t]))
    # print(ids)
    for id in ids:
        user = UsersCur.execute("SELECT * FROM users WHERE id=?", str(id)).fetchone()
        # получить логин и id
        user_login = user[0]
        user_id = user[6]
        messages_from = len(UsersCur.execute("SELECT * from messages where __From = {}".format(user_id)).fetchall())
        messages_to = len(UsersCur.execute("SELECT * from messages where __To = {}".format(user_id)).fetchall())
        # пришлось поменять код сервера, чтобы не удалялось сообщение из базы
        messages_deleted = len(
            UsersCur.execute(
                "SELECT * from messages where (__FROM = {} and _FROM = 0) || (__TO = {} and _TO = 0)".format(user_id,
                                                                                                             user_id)).fetchall())
        print("{:10} {:<5d} {:<8d} {:<8d}".format(user_login, messages_from, messages_to, messages_deleted))


# версия 1. используем прямое подключение базе, игнорируя сервер
UsersDB = sqlite3.connect("..\Server\Bin\DB\\USERS.db")
UsersCur = UsersDB.cursor()
# для получения первоначальное статистики
prev_t = []
print("{:10} {:5} {:8} {:8}".format("USER", "SEND", "RECIEVED", "DELETED"))
while 1:
    UsersCur = UsersDB.cursor()
    t = UsersCur.execute("SELECT * FROM messages").fetchall()
    if prev_t != t:
        # самый простой способ получить разницу списков
        diff = list(set(t) - set(prev_t))
        prev_t = t
        update_statistic(diff)
        UsersCur.close()
    # print(t)
    sleep(5)
