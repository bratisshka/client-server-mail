import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import matplotlib.animation as animation
from matplotlib.ticker import FormatStrFormatter
from time import sleep


def update_statistic(t):
    ids = set([x[3] for x in t]).union(set([x[4] for x in t]))
    # print(ids)
    user_logins = []
    all_messages_from = []
    all_messages_to = []
    all_messages_delete = []
    for id in ids:
        user = UsersCur.execute("SELECT * FROM users WHERE id=?", str(id)).fetchone()
        user_login = user[0]
        user_logins.append(user_login)
        user_id = user[6]
        messages_from = len(UsersCur.execute("SELECT * from messages where __From = {}".format(user_id)).fetchall())
        messages_to = len(UsersCur.execute("SELECT * from messages where __To = {}".format(user_id)).fetchall())

        messages_deleted = len(
            UsersCur.execute(
                "SELECT * from messages where (__FROM = {} and _FROM = 0) || (__TO = {} and _TO = 0)".format(user_id,
                                                                                                             user_id)).fetchall())
        print("{:10} {:<5d} {:<8d} {:<8d}".format(user_login, messages_from, messages_to, messages_deleted))

        all_messages_from.append(messages_from)
        all_messages_to.append(messages_to)
        all_messages_delete.append(messages_deleted)
    return user_logins, all_messages_from, all_messages_to, all_messages_delete


UsersDB = sqlite3.connect("..\Server\Bin\DB\\USERS.db")
UsersCur = UsersDB.cursor()

prev_t = []
print("{:10} {:5} {:8} {:8}".format("USER", "SEND", "RECIEVED", "DELETED"))
# while 1:
#     UsersCur = UsersDB.cursor()
#     t = UsersCur.execute("SELECT * FROM messages").fetchall()
#     if prev_t != t:
#         diff = list(set(t) - set(prev_t))
#         prev_t = t
#         update_statistic(diff)
#         UsersCur.close()
#     # print(t)
#     sleep(5)

UsersCur = UsersDB.cursor()
t = UsersCur.execute("SELECT * FROM messages").fetchall()
diff = list(set(t) - set(prev_t))
prev_t = t
user_logins, all_messages_from, all_messages_to, all_messages_delete = update_statistic(diff)
UsersCur.close()

n_groups = len(user_logins)

#   plot
from pandas import DataFrame


change = all_messages_from
messages_to = all_messages_to
user = user_logins
change = [[a, b, c] for a, b, c in zip(all_messages_from, all_messages_to, all_messages_delete)]
grad = DataFrame(change, columns=['Send', 'Recieved', 'Deleted'])
pos = np.arange(len(change))

grad.plot( kind='barh', title='Scotres by users')

# add the numbers to the side of each bar
for p, c, ch in zip(pos, user, all_messages_from):
    plt.annotate(str(ch), xy=(ch + 0.05, p - 0.19), va='center')
for p, c, ch in zip(pos, user, all_messages_to):
    plt.annotate(str(ch), xy=(ch + 0.05, p - 0.01), va='center')
for p, c, ch in zip(pos, user, all_messages_delete):
    plt.annotate(str(ch), xy=(ch + 0.05, p + 0.165), va='center')

# cutomize ticks
ticks = plt.yticks(pos, user)
xt = plt.xticks()[0]
plt.xticks(xt, [' '] * len(xt))

def animate(i):


plt.show()
