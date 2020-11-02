import sqlite3, sys, getpass

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
    cursor.execute("CREATE TABLE posts ( pid char(4), pdate date, title text, body text, poster char(4), primary key (pid), foreign key (poster) references users);")
    cursor.execute("CREATE TABLE tags ( pid char(4), tag text, primary key (pid,tag), foreign key (pid) references posts);")
    cursor.execute("CREATE TABLE votes ( pid char(4), vno int, vdate text, uid char(4), primary key (pid,vno), foreign key (pid) references posts, foreign key (uid) references users);")
    cursor.execute("CREATE TABLE questions (pid char(4), theaid char(4), primary key (pid), foreign key (theaid) references answers);")
    cursor.execute("CREATE TABLE answers (pid char(4), qid char(4), primary key (pid), foreign key (qid) references questions);")

    connection.commit()
    return

def insertData():
    #Function to insert data
    global connection, cursor

    #Insert user data into below insert statement in the form            ('uid','name','password','City',date), \
    insertUsers = "INSERT INTO users VALUES \
         ('u100', 'Mark Smith', 'password', 'Calgary', '2020-10-27');"
    insertPriviledged = ""
    insertBadges = ""
    insertUBadges = ""
    insertPosts = ""
    insertTags = ""
    insertVotes = ""
    insertQuestions = ""
    insertAnswers = ""

    cursor.execute(insertUsers)
    cursor.execute(insertPriviledged)
    cursor.execute(insertBadges)
    cursor.execute(insertUBadges)
    cursor.execute(insertPosts)
    cursor.execute(insertTags)
    cursor.execute(insertVotes)
    cursor.execute(insertQuestions)
    cursor.execute(insertAnswers)
    connection.commit()

    return

def login():
    #Login in function
    #Verifies if a user is an existing user
    #or adds data to users table if user is a new user
    #Returns the uid of the logged in user
    global connection, cursor

    print("Login System")
    print("Type returning for returning user or new to create a new account")
    loginType = input()
    while True:
        if loginType.lower() == 'returning' or loginType.lower() == 'new':
            break
        else:
            print("Type returning for returning user or new to create a new account")
            loginType = input()

    if loginType.lower() == 'returning':
        found = False
        uid = None
        password = None
        while found != True:
            print("Enter user id: ",end='')
            uid = input()
            cursor.execute("SELECT uid FROM users")
            userIds = cursor.fetchall()
            for tup in userIds:
                for u in tup:
                    if uid.lower() == u:
                        found = True
            if found != True:
                print("ID not found")
        
        found = False
        while found != True:
            password = getpass.getpass("Enter password: ")
            cursor.execute("SELECT pwd FROM users WHERE uid = ?",(uid,))
            userPwd = cursor.fetchall()
            if password == userPwd[0][0]:
                found = True
            else:
                print("Incorrect Password.")
    
    if loginType.lower() == 'new':
        found = True
        uid = None
        name = None
        city = None
        password = None
        while found != False:
            exist = 0
            print("Enter new user id: ",end='')
            uid = input()
            if len(uid) != 4:
                print("Invalid user id",'\n')
            else:
                cursor.execute("SELECT uid FROM users")
                userIds = cursor.fetchall()
                for tup in userIds:
                    if uid.lower() == tup[0].lower():
                        exist += 1
                if exist > 0:
                    print("ID already in use",'\n')
                else:
                    found = False

        print("Enter name associated with the account: ",end='')
        name = input()
        print("Enter city of residence: ",end='')
        city = input()

        found = True
        while found != False:
            #Maybe use getpass here as well?
            print("Enter password for account: ")
            password = input()
            if password != None:
                found = False
    
        cursor.execute("INSERT INTO users VALUES (?,?,?,?,date('now'))",(uid,name,password,city))
    return uid

def main(argv):
    global connection, cursor

    #Database input
    #Takes a command line argument for a path to a database
    #If no database is provided creates or clears, and inserts test data into mini_project.db
    filePath = ''
    if len(argv) > 1:
        for i in range(1,len(argv)):
            if i == 1:
                filePath = argv[i]
        setConnection(filePath)
    else:
        filePath = "./mini_project1.db"
        setConnection(filePath)
        createTables()
        insertData()

    #currentUser is user that logged in for all questions that need it
    #currentUser is a string
    currentUser = login()

    #Main loop for main menu
    #I assume questions are assignment questions are called from here
    mainLoop = True
    while mainLoop != False:
        print('\n')
        print("MENU OPTIONS SHOULD GO HERE")
        print("Type 'logout' to return to login menu")
        print("Type 'quit' to exit program")
        option = input()
        if option.lower() == "logout":
            print('\n')
            currentUser = login()
        elif option.lower() == 'quit':
            mainLoop = False


if __name__ == "__main__":
    main(sys.argv)