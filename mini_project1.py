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
    cursor.execute("DROP TABLE IF EXISTS votes")
    cursor.execute("DROP TABLE IF EXISTS tags")
    cursor.execute("DROP TABLE IF EXISTS privileged")
    cursor.execute("DROP TABLE IF EXISTS ubadges")
    cursor.execute("DROP TABLE IF EXISTS posts")
    cursor.execute("DROP TABLE IF EXISTS questions")
    cursor.execute("DROP TABLE IF EXISTS answers")
    cursor.execute("DROP TABLE IF EXISTS badges")
    cursor.execute("DROP TABLE IF EXISTS users")

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
         ('u100', 'Mark Smith', 'password', 'Calgary', '2020-10-27'), \
         ('u200', 'John Jones', 'abcde', 'Calgary', '2020-10-31');"
    insertPriviledged = ""
    insertBadges = ""
    insertUBadges = ""
    insertPosts = "INSERT INTO posts VALUES \
        ('p300','2020-11-01','This is a question','This will be for testing tags of a post','u200'), \
        ('p200','2020-11-01','Relational Database question 2','This is a test for posts involving searching, so heres a house as a test','u200'), \
        ('p100','2020-10-31','Relational Database question','This is a test for posts involving searching, so heres a house as a test','u100');"
    insertTags = "INSERT INTO tags VALUES \
        ('p300','database');"
    insertVotes = "INSERT INTO votes VALUES \
        ('p100',1,date('now'),'u200');"
    insertQuestions = "INSERT INTO questions VALUES \
        ('p200',NULL), \
        ('p100',NULL);"
    insertAnswers = "INSERT INTO answers VALUES \
        ('p300','p100');"

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
            cursor.execute("SELECT pwd FROM users WHERE uid = ?;",(uid,))
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
                cursor.execute("SELECT uid FROM users;")
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
def postQuestion():
    global connection, cursor
    return
def searchPosts():
    global connection, cursor

    print("Enter keyword(s) to search for.")
    print("Seperate different keywords with ', ' : ",end='')
    keywords = input()
    keywords = keywords.split(', ')

    posts = []
    for keyword in keywords:
        if ',' in keyword:
            continue
        else:
            keyword = keyword.lower()
            hold = "%"+keyword+"%"
            hold2 = "'"+keyword+"'"
            statement = "((LENGTH(p.title)+LENGTH(p.body)-LENGTH(REPLACE(lower(p.title),'" + keyword + "',''))-LENGTH(REPLACE(lower(p.body),'" + keyword + "','')))/LENGTH('"+keyword+"'))"
            statement = "SELECT p.*," + statement + " FROM posts p, tags t WHERE (p.pid = t.pid AND lower(t.tag) LIKE ?) OR (lower(p.title) LIKE ? OR lower(p.body) LIKE ?)"
            cursor.execute(statement,(hold,hold,hold,))
            kposts = cursor.fetchall()
            posts = posts + kposts

    for i in range(0,len(posts)):
        cursor.execute("SELECT p.pid, COUNT(v.vno) FROM posts p, votes v WHERE v.pid = ? AND p.pid = ? GROUP BY p.pid",(posts[i][0],posts[i][0],))
        vposts = cursor.fetchall()
        if len(vposts) == 0:
            posts[i] = list(posts[i])
            posts[i].append(0)
        else:
            posts[i] = list(posts[i])
            posts[i].append(vposts[0][1])

        cursor.execute("SELECT q.pid FROM questions q WHERE q.pid = ?",(posts[i][0],))
        if len(cursor.fetchall()) != 0:
            cursor.execute("SELECT COUNT(a.pid) FROM answers a, questions q WHERE q.pid = ? AND a.qid = q.pid GROUP BY q.pid",(posts[i][0],))
            acount = cursor.fetchall()
            if len(acount) == 0:
                posts[i].append(0)
            else:
                posts[i].append(acount[0][0])

    return posts
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
        print("Type 'search' to search for keywords")
        option = input()
        if option.lower() == "logout":
            print('\n')
            currentUser = login()
        elif option.lower() == "search":
            print('\n')
            posts = searchPosts()
            print(posts)
        elif option.lower() == 'quit':
            mainLoop = False


if __name__ == "__main__":
    main(sys.argv)