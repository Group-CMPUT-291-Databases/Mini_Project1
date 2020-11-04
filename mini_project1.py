import sqlite3, sys, getpass, time
from datetime import date

connection = None
cursor = None
currentPID = None

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
    cursor.execute("DROP TABLE IF EXISTS questions")
    cursor.execute("DROP TABLE IF EXISTS answers")
    cursor.execute("DROP TABLE IF EXISTS posts")
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
    insertPriviledged = "INSERT INTO privileged VALUES \
        ('u100');"
    insertBadges = "INSERT INTO badges VALUES ('testbadge','gold')"
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

    #Checks if user is new or returning
    print("Login System")
    print("Type returning for returning user or new to create a new account")
    loginType = input()
    while True:
        if loginType.lower() == 'returning' or loginType.lower() == 'new':
            break
        else:
            print("Type returning for returning user or new to create a new account")
            loginType = input()

    #Returning user login
    #Verifies inputted user id is already in system
    #Then verifies password matches that of password stored in the system
    #Password is hidden by built in python library getpass
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
    
    #New user login
    #Gets the users id, name, city, password and creates a new table entry with those values and the current date
    #Verifies the user id is proper len to be entered
    #Verifies the user id isnt already in use
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
    #Post Search Function
    #Given user input(s) returns a list of posts that include the searched keywords
    global connection, cursor

    #Gets the keyword(s) from user input, seperates them into a list so they can be check seperately
    print("Enter keyword(s) to search for.")
    print("Seperate different keywords with ', ' : ",end='')
    keywords = input()
    keywords = keywords.split(', ')

    #For each entered keyword obtains all posts that include that word in the title,body or tag
    #Also returns 1 to indicate the post includes a keyword
    #Adds found posts to a list
    #Repeats for all keywords
    posts = []
    for keyword in keywords:
        if ',' in keyword:
            continue
        else:
            keyword = keyword.lower()
            hold = "%"+keyword+"%"
            hold2 = "'"+keyword+"'"
            statement = "SELECT p.*,1 FROM posts p, tags t WHERE (p.pid = t.pid AND lower(t.tag) LIKE ?) OR (lower(p.title) LIKE ? OR lower(p.body) LIKE ?)"
            cursor.execute(statement,(hold,hold,hold,))
            kposts = cursor.fetchall()
            print(kposts)
            posts = posts + kposts
            print(posts)
    print(keywords)
    #Checks over all found posts
    #For each found post finds and adds that posts votes count and appends it to that posts returned list (adds 0 if no votes exist)
    #For each found question post checks and adds number of answers the post has and appends it to that posts returned list (0 if no answers, no appending if post is an answer)
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
    
    #Finds duplicate posts via pid from post list
    #Each time a duplicate is found increases the number of keyword occurance on first occurance of that post
    #Adds index of duplicate post to be removed later
    removed = []
    for i in range(0,len(posts)):
        for j in range(0,len(posts)):
            #print(posts[i][0]," ",posts[j][0])
            if i != j and i not in removed:
                if posts[i][0] == posts[j][0]:
                    posts[i][5] += posts[j][5]
                    removed.append(j)
    
    #Removes posts based off of indexs in removed list
    #To handle changing size of posts list removed is sorted and stored indexes are decreased by 1 everytime a post is removed
    modifier = 0
    removed.sort()
    for index in removed:
        posts.remove(posts[index-modifier])
        modifier += 1

    #Sorts posts based off of the number of matching keywords and returns the sorted list of posts
    posts.sort(reverse=True,key=sortFunc)
    return posts

def sortFunc(post):
    return post[5]

def add_tag(searched_pid):
    #Function to add a tag to posts
    #Passes the pid of the post returned from Search_Posts
    global connection, cursor
    tag_loop = True
    
    #Asks user to add a tag
    while tag_loop != False:
        print("Please enter the tag name")
        tag_name = input()
        cursor.execute("INSERT INTO tags VALUES (?,?)",(searched_pid,tag_name))
        print("Your tag was added!")
        print("Do you want to add another tag to this post? y/n")
        user_response = input()
        if user_response.lower() == 'y':
            continue
            
        elif user_response.lower() == 'n':
            tag_loop = False
    
    
    #Displays the added tag      
    cursor.execute("SELECT tag FROM tags WHERE pid = ?",(searched_pid,))
    tag_added = cursor.fetchall()
    print("Tags associated with the post:")
    print(tag_added)
    connection.commit()
    
    return tag_added   

def edit_post(edit_type, searched_pid):
    #Function to edit the post
    #Passes what action is need i.e edit the title or edit the body text.Also passes the pid of the post to edit which is returned from Search_Posts
    global connection, cursor
   
    #Checks what action is needed     
    print(type(searched_pid))
    if edit_type.lower() == 'edit title':
        cursor.execute("SELECT title FROM posts WHERE pid = ?",(searched_pid,))
        prev_title = cursor.fetchone()
        connection.commit()
        print("The previous title is :")
        print(prev_title)
        print("\n Enter the new title :")
        new_title = input()
        cursor.execute("UPDATE posts SET title = ? WHERE pid = ?",(new_title,searched_pid,))
        connection.commit()
        
        
    elif edit_type.lower() == 'edit body text':
        cursor.execute("SELECT body FROM posts WHERE pid = ?",(searched_pid,))
        prev_body = cursor.fetchone()
        connection.commit()
        print("The previous body text is :")
        print(prev_body)
        print("Enter the new body text :")
        new_body = input()
        cursor.execute("UPDATE posts SET body = ? WHERE pid =?",(new_body,searched_pid,))
        connection.commit()  
        
    #Displays the changes made to the post
    cursor.execute("SELECT * FROM posts WHERE pid = ?",(searched_pid,))
    edited_post = cursor.fetchall()
    print("Edited post is")
    print(edited_post)
    connection.commit()    
    
    return

def check_user_type(user_id):
    #Function checks whether the user is privileged. Returns a Boolean
    
    global connection, cursor
    is_priv_user = True
    cursor.execute("SELECT * FROM privileged ")
    priv_users = cursor.fetchall()
   
    for person in priv_users:
        for value in person:
            if user_id.lower() == value:
                is_priv_user = True
    
            else:
                is_priv_user = False
    connection.commit()
    return is_priv_user

def postQuestion(uid):
    global cursor, connection, currentPID

    print("Question Title: ",end='')
    title = input()
    print("Question Body: ",end='')
    body = input()

    #cursor.execute("INSERT INTO users VALUES (?,?,?,?,date('now'))",(uid,name,password,city))
    cursor.execute("INSERT INTO posts VALUES (?,date('now'),?,?,?)",(currentPID,title,body,uid))
    cursor.execute("INSERT INTO questions VALUES (?,NULL)",(currentPID,))
    nextInt = int(currentPID[1:]) + 1
    currentPID = 'p' + str(nextInt)

    connection.commit()

def post_action_answer(uid,pid):
    global connection, cursor, currentPID

    print("Answer Title: ",end='')
    title = input()
    print("Answer Body: ",end='')
    body = input()
    print(pid)
    check_ifquestion = '''
                        SELECT posts.pid, questions.pid
                        FROM posts, questions
                        WHERE posts.pid = questions.pid
                        AND posts.pid = ?
                    '''

    insert_answers = '''
                            INSERT INTO answers (pid, qid)
                                VALUES (?, ?);
                                    
                            '''
    insert_posts = '''
                            INSERT INTO posts (pid, pdate, title, body, poster) VALUES
                                    (?,?,?,?,? );
                                    
                            '''
    cursor.execute(check_ifquestion,(pid,))
    #if question pid and post pid are equal, questionbool is true
    questionbool = cursor.fetchone()
    print(questionbool)
    #if questionbool is not true, insert answers and posts.
    if questionbool:
        post_date = date.today()
        cursor.execute(insert_posts,(currentPID, post_date,title,body,uid))
        cursor.execute(insert_answers, (currentPID, pid))
        nextInt = int(currentPID[1:]) + 1
        currentPID = 'p' + str(nextInt)

    else:
        return None
   
    connection.commit()
    return True

def post_action_vote(uid,pid):
    global connection, cursor

    check_ifvote = '''
                        SELECT posts.pid, users.uid, votes.uid, votes.pid
                        FROM posts, users, votes, votes
                        WHERE posts.pid = votes.pid and users.uid = votes.uid
                    '''

    insert_votes = '''
                            INSERT INTO votes (pid, vno, vdate, uid) VALUES
                                    (?, ?, ?, ?);
                                    
                            '''
	
    select_vote_count = '''
                            SELECT MAX(votes.vno) 
                            FROM votes, posts
                            WHERE votes.pid = posts.pid and posts.pid = ?
                            GROUP BY posts.pid
                            '''

    cursor.execute(select_vote_count,(pid,))
    max_vote = cursor.fetchone()
    if not max_vote:
        max_vote = 1
        vote_date = date.today()
        cursor.execute(insert_votes,(pid,max_vote,vote_date,uid))
    else:
        max_vote = max_vote[0] + 1
        vote_date = date.today()
        cursor.execute(insert_votes,(pid,max_vote,vote_date,uid))

    return

def post_action_mark_as_the_accepted(answer_id,user_id):
    global connection, cursor, currentPID

    check_ifanswer = '''
                        SELECT answers.pid
                        FROM answers 
                        WHERE answers.pid = ?

                    '''


    check_ifquestion = '''
                        SELECT questions.pid, questions.theaid
                        FROM questions, answers
                        WHERE questions.pid = answers.qid and answers.pid = ?

                    '''


    insert_theacceptedanswer = '''
                                UPDATE questions SET theaid = ? WHERE pid = ?;  
                            '''
    update_theacceptedanswer = '''
                                UPDATE questions
                                SET theaid = ? WHERE pid = ?;
                            '''
    cursor.execute(check_ifanswer,(answer_id,))
    answerbool = cursor.fetchone()
    if not answerbool:
        print("\nNot an answer")
        return
    
    cursor.execute(check_ifquestion,(answer_id,))
    questionbool = cursor.fetchone()
    print(questionbool)

    #update questions set theaid = 'p019' where pid = 'p018';
    if questionbool[1] != None:
   		print("The answer is already accepted. Do you want to change it?[Y/N]")
   		input1 = input()
   		if input1 == 'Y':
   			cursor.execute(update_theacceptedanswer,(answer_id,questionbool[0]))
   		elif input1 == 'N':
   			return None
   		else:
   			print("Invalid input")
    else: 
        cursor.execute(insert_theacceptedanswer,(answer_id,questionbool[0]))
   
    connection.commit()
    return

def post_action_give_badge(user_id,post_id):
    global connection, cursor

    timegiven = date.today()

    check_ubadges = '''
                    SELECT u.uid, u.bdate
                    FROM ubadges u
                    WHERE u.uid = ? AND u.bdate = ?
                    '''
    check_badges = '''
                        SELECT badges.bname
                        FROM badges
                    '''

    give_badge = '''
                            INSERT INTO ubadges (uid,bdate, bname) VALUES
                                    (?, ?, ?);
                                    
                            '''
    cursor.execute(check_ubadges,(user_id,timegiven))
    ubadgesbool = cursor.fetchone()
    if ubadgesbool:
        print("Selected user has already received a badge today")
        return

    cursor.execute(check_badges)
    badges = cursor.fetchall()

    for i in range(0,len(badges)):
        print(i,'. ',badges[i][0])
    print("Type the number correspodning badge to select it")
    num = input()
    selectedBadge = None
    select = False
    while select != True:
        for i in range(0,len(badges)):
            if num == str(i):
                selectedBadge = badges[i][0]
                select = True
        if select != True:
            print("Not a valid selection")
            num = input()

    cursor.execute(give_badge,(user_id,timegiven,selectedBadge))
   
    connection.commit()
    return

def main(argv):
    global connection, cursor, currentPID

    #Database input
    #Takes a command line argument for a path to a database
    #If no database is provided creates or clears, and inserts test data into mini_project1.db
    #Taking a database as input is preferable as the foreign keys and drop tables in the pre-set one causes problems
    if len(argv) > 1:
        for i in range(1,len(argv)):
            if i == 1:
                databaseType = argv[i]
            if i == 2:
                filePath = argv[i]
    if databaseType == '-i':
        setConnection(filePath)
        createTables()
        insertData()
    elif databaseType == '-d':
        setConnection(filePath)

    #currentUser is user that logged in for all questions that need it
    #currentUser is a string
    currentUser = login()

    #Sets the next pid to be used for question and answer posts
    cursor.execute("SELECT p.pid FROM posts p")
    pids = cursor.fetchall()
    nextInt = int(pids[len(pids)-1][0][1:]) + 1
    currentPID = 'p' + str(nextInt)

    #Main loop for main menu
    #I assume questions are assignment questions are called from here
    mainLoop = True
    posts = []
    selectedPost = None
    user_type = False
    while mainLoop != False:
        print('\n')
        print("Type 'logout' to return to login menu")
        print("Type 'quit' to exit program")
        print("Type 'search' to search for keywords")
        print("Type 'question' to post a question")

        #Only displays these options once potential posts have been found
        if len(posts) != 0:
            user_type = check_user_type(currentUser)
            print("Type 'answer question' to post an answer to a search question")
            print("Type 'vote' to upvote a post")
            if user_type == True:
                print("Type 'add accepted' to select an answer as the accepted")
                print("Type 'give badge' to give a badge to the posts poster")
                print("Type 'add a tag' to add a tag to this post")
                print("Type 'edit title' to edit the post title")
                print("Type 'edit body text' to edit the post body ")

        print(currentPID)
        option = input()

        if option.lower() == "logout":
            print('\n')
            posts = None
            selectedPost = None
            currentUser = login()
        elif option.lower() == "question":
            print('\n')
            postQuestion(currentUser)
        elif option.lower() == 'add a tag' and user_type == True:
            searched_pid = selectedPost[0]
            add_tag(searched_pid) 
            
        elif option.lower() == 'edit title' and user_type == True: 
            searched_pid = selectedPost[0]            
            edit_post(option, searched_pid) 
            
        elif option.lower() == 'edit body text' and user_type == True: 
            searched_pid = selectedPost[0]            
            edit_post(option, searched_pid)

        elif option.lower() == 'answer question':
            searched_pid = selectedPost[0]
            post_action_answer(currentUser,searched_pid)

        elif option.lower() == 'vote':
            searched_pid = selectedPost[0]
            post_action_vote(currentUser,searched_pid)

        elif option.lower() == 'add accepted' and user_type == True:
            searched_pid = selectedPost[0]
            post_action_mark_as_the_accepted(searched_pid,currentUser)

        elif option.lower() == 'give badge' and user_type == True:
            searched_pid = selectedPost[0]
            selected_uid = selectedPost[4]
            post_action_give_badge(selected_uid,searched_pid)

        #Search fucntion, returns a list of posts and then gets user input for a post they want to perform actions on
        #All posts are stored in posts, the user selected post is stored in selectedPost
        elif option.lower() == "search":
            print('\n')
            posts = searchPosts()
            if len(posts) != 0:
                if len(posts) > 5:
                    for i in range (0,5):
                        print(i,'. ',posts[i])
                    print("Type the number of the correspoding post to select it for actions, or type more to see more selections")
                    num = input()
                    select = False
                    cap = len(posts)
                    bot = 0
                    top = 5

                    while select != True:
                        if num.lower() == "more" and bot+5<cap:
                            bot = bot + 5
                            if top + 5 >= cap:
                                top = cap
                            else:
                                top = top + 5
                            for i in range (bot,top):
                                print(i,'. ',posts[i])
                            print("Type the number of the correspoding post to select it for actions")
                            num = input()
                        for i in range(bot,top):
                            if num == str(i):
                                selectedPost = posts[i]
                                select = True
                        if select != True:
                            print("Not a valid selection")
                            num = input()
                else:
                    for i in range(0,len(posts)):
                        print(i,'. ',posts[i])
                    print("Type the number of the correspoding post to select it for actions")
                    num = input()
                    select = False
                    while select != True:
                        for i in range(0,len(posts)):
                            if num == str(i):
                                selectedPost = posts[i]
                                select = True
                        if select != True:
                            print("Not a valid selection")
                            num = input()

        #Example elif for post related actions, only display once posts have been found
        elif len(posts) != 0 and option.lower == "something":
            #Post related function calls here
            continue
        elif option.lower() == 'quit':
            connection.commit()
            mainLoop = False


if __name__ == "__main__":
    main(sys.argv)