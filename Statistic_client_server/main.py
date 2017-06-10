import numpy as np
import matplotlib.pyplot as plt
import sqlite3
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
# means_men = all_messages_from
# means_women = all_messages_to
# means_deleted = all_messages_delete
# fig, ax = plt.subplots()
#
# index = np.arange(n_groups)
# bar_width = 0.2
#
# opacity = 0.4
# eror_config = {'ecolor': '0.3'}
#
# rects1 = plt.bar(index, means_men, bar_width, alpha=opacity, color='b',  error_kw=eror_config, label='From')
# rects2 = plt.bar(index + bar_width, means_women, bar_width, alpha=opacity, color='r', error_kw=eror_config, label='To')
# rects3 = plt.bar(index + bar_width*2, means_deleted, bar_width, alpha=opacity, color='g', error_kw=eror_config, label='Deleted')
#
# plt.xlabel('Users')
# plt.ylabel('Count')
# plt.title('Scotres by group and gender')
# plt.xticks(index + bar_width / 2, user_logins)
#
# ax.yaxis.set_major_formatter(FormatStrFormatter('%d'))
#
# def autolabel(rects):
#     for rect in rects:
#         height = rect.get_height()
#         ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
#                 '%d' % int(height),
#                 ha='center', va='bottom')
#
# autolabel(rects1)
# autolabel(rects2)
# autolabel(rects3)
#
# plt.legend()
#
# plt.tight_layout()
# plt.show()


#   plot_2
from pandas import DataFrame

change = all_messages_from
user = user_logins

grad = DataFrame({'change' : change, 'user': user})

change = grad.change[grad.change > 0]
user = grad.user[grad.change > 0]
pos = np.arange(len(change))

plt.title('Scotres by group and gender')
plt.barh(pos, change)
plt.xlabel('Count')

#add the numbers to the side of each bar
for p, c, ch in zip(pos, user, change):
    plt.annotate(str(ch), xy=(ch + 1, p + .15), va='center')

#cutomize ticks
ticks = plt.yticks(pos + .5, user)
xt = plt.xticks()[0]
plt.xticks(xt, [' '] * len(xt))

#minimize chartjunk
def remove_border(axes=None, top=False, right=False, left=True, bottom=True):
    ax = axes or plt.gca()
    ax.spines['top'].set_visible(top)
    ax.spines['right'].set_visible(right)
    ax.spines['left'].set_visible(left)
    ax.spines['bottom'].set_visible(bottom)

    # turn off all ticks
    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('none')

    # now re-enable visibles
    if top:
        ax.xaxis.tick_top()
    if bottom:
        ax.xaxis.tick_bottom()
    if left:
        ax.yaxis.tick_left()
    if right:
        ax.yaxis.tick_right()

#minimize chartjunk
remove_border(left=False, bottom=False)
plt.grid(axis = 'x', color ='white', linestyle='-')

plt.show()