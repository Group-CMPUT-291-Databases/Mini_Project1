import sqlite3

connection = None
cursor = None

def setConnection(path):
    #Sets up  db connection and creates cursor
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')
    connection.commit()
    return

def createTables():
    global connection, cursor

    #Clears tables so that for each program run no multiple table errors occur
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS privileged")
    cursor.execute("DROP TABLE IF EXISTS badges")
    cursor.execute("DROP TABLE IF EXISTS ubadges")
    cursor.execute("DROP TABLE IF EXISTS posts")
    cursor.execute("DROP TABLE IF EXISTS tags")
    cursor.execute("DROP TABLE IF EXISTS votes")
    cursor.execute("DROP TABLE IF EXISTS questions")
    cursor.execute("DROP TABLE IF EXISTS answers")

    cursor.execute("CREATE TABLE users (uid char(4), name text, pwd text, city text, crdate date, primary key (uid));")
    cursor.execute("CREATE TABLE privileged (uid char(4), primary key (uid), foreign key (uid) references users);")
    cursor.execute("CREATE TABLE badges (bname text, type text, primary key (bname));")
    cursor.execute("CREATE TABLE ubadges (uid char(4), bdate date, bname text, primary key (uid,bdate), foreign key (uid) references users, foreign key (bname) references badges);")
    cursor.execute("create table posts ( pid char(4), pdate date, title text, body text, poster char(4), primary key (pid), foreign key (poster) references users);")
    cursor.execute("create table tags ( pid char(4), tag text, primary key (pid,tag), foreign key (pid) references posts);")
    cursor.execute("create table votes ( pid char(4), vno int, vdate text, uid char(4), primary key (pid,vno), foreign key (pid) references posts, foreign key (uid) references users);")
    cursor.execute("create table questions (pid char(4), theaid char(4), primary key (pid), foreign key (theaid) references answers);")
    cursor.execute("create table answers (pid char(4), qid char(4), primary key (pid), foreign key (qid) references questions);")

    connection.commit()
    return

def insertData():
    #Function to insert data
    global connection, cursor
    return

def login():
    #Login in function
    #Verifies if a user is an existing user
    #or adds data to users table if user is a new user
    #Returns the uid of the logged in user
    return

def main():
    global connection, cursor

    filePath = "./mini_project1.db"
    setConnection(filePath)
    createTables()
    insertData()
    login()
    #Placeholder user, once login function is created uid of logged in user will be stored here
    currentUser = None


if __name__ == "__main__":
    main()