import sqlite3
UsersDB = sqlite3.connect("..\Server\Bin\DB\USERS.db")
UsersCur = UsersDB.cursor()
print( UsersCur.execute("SELECT * from messages").fetchall())