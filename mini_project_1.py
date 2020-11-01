import sqlite3
import time
from datetime import date

connection = None
cursor = None
answer_id = 1001
vote_number = 1001



def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return


def drop_tables():
    global connection, cursor

    drop_user = "DROP TABLE IF EXISTS user; "
    drop_privileged = "DROP TABLE IF EXISTS privileged; "
    drop_badges = "DROP TABLE IF EXISTS badges; "
    drop_ubadges = "DROP TABLE IF EXISTS ubadges;"
    drop_posts = "DROP TABLE IF EXISTS posts;"
    drop_tags = "DROP TABLE IF EXISTS tags;"
    drop_votes = "DROP TABLE IF EXISTS votes;"
    drop_questions = "DROP TABLE IF EXISTS questions;"
    drop_answers = "DROP TABLE IF EXISTS answers;"





    cursor.execute(drop_user)
    cursor.execute(drop_privileged)
    cursor.execute(drop_badges)
    cursor.execute(drop_ubadges)
    cursor.execute(drop_posts)
    cursor.execute(drop_tags)
    cursor.execute(drop_votes)
    cursor.execute(drop_questions)
    cursor.execute(drop_answers)


def define_tables():
    global connection, cursor

    users_query = '''
                        CREATE TABLE users (
								  uid		char(4),
								  name		text,
								  pwd		text,
								  city		text,
								  crdate	date,
								  primary key (uid)
);
                    '''

    privileged_query = '''
                        CREATE TABLE privileged (
								  uid		char(4),
								  primary key (uid),
								  foreign key (uid) references users
);
                    '''

    badges_query = '''
                   CREATE TABLE badges (
							  bname		text,
							  type		text,
							  primary key (bname)
);
                '''
    ubadges_query = '''
                   CREATE TABLE ubadges (
							  uid		char(4),
							  bdate		date,
							  bname		text,
							  primary key (uid,bdate),
							  foreign key (uid) references users,
							  foreign key (bname) references badges
);
                '''
    posts_query = '''
                   CREATE TABLE posts (
							  pid		char(4),
							  pdate		date,
							  title		text,
							  body		text,
							  poster	char(4),
							  primary key (pid),
							  foreign key (poster) references users
);
                '''
    tags_query = '''
                   CREATE TABLE tags (
							  pid		char(4),
							  tag		text,
							  primary key (pid,tag),
							  foreign key (pid) references posts
);
                '''
    votes_query = '''
                  CREATE TABLE votes (
							  pid		char(4),
							  vno		int,
							  vdate		text,
							  uid		char(4),
							  primary key (pid,vno),
							  foreign key (pid) references posts,
							  foreign key (uid) references users
);
                '''
    questions_query = '''
                   CREATE TABLE questions (
							  pid		char(4),
							  theaid	char(4),
							  primary key (pid),
							  foreign key (theaid) references answers
);
                '''
    answers_query = '''
                   CREATE TABLE answers (
							  pid		char(4),
							  qid		char(4),
							  primary key (pid),
							  foreign key (qid) references questions
);
                '''

    cursor.execute(users_query)
    cursor.execute(privileged_query)
    cursor.execute(badges_query)
    cursor.execute(ubadges_query)
    cursor.execute(posts_query)
    cursor.execute(tags_query)
    cursor.execute(votes_query)
    cursor.execute(questions_query)
    cursor.execute(answers_query)
    connection.commit()

    return


def post_action_answer(uid,pid,title,body):
    global connection, cursor, answer_id

   check_ifquestion = '''
                        SELECT posts.pid, questions.pid
                        FROM posts, questions
                        WHERE posts.pid = questions.pid
                    '''

   insert_answers = '''
                            INSERT INTO answers (pid, qid) VALUES
                                    (answer_id, questions.pid);
                                    
                            '''
	insert_posts = '''
                            INSERT INTO posts (pid, qdate, title, body, poster) VALUES
                                    (answer_id, post_date, title, body, uid );
                                    
                            '''
    cursor.execute(check_ifquestion)
    questionbool = cursor.fetchone()

   if not questionbool:
   		cursor.execute(insert_answers)
		post_date = date.today()
		cursor.execute(insert_posts)
		answer_id= answer_id + 1

	else:
		return None
   
    connection.commit()
    return True

def post_action_vote(uid,pid):
    global connection, cursor, answer_id, vote_number

   check_ifvote = '''
                        SELECT posts.pid, users.uid, votes.uid, votes.pid
                        FROM posts, users, votes, votes
                        WHERE posts.pid = votes.pid and users.uid = votes.uid
                    '''

   insert_votes = '''
                            INSERT INTO votes (pid, vno, vdate, uid) VALUES
                                    (posts.pid, vote_number, vote_date, users.uid);
                                    
                            '''
	
    cursor.execute(check_ifvote)
    votebool = cursor.fetchone()


   if not votebool:
   		
		vote_date = date.today()
		cursor.execute(insert_votes)
		vote_number = vote_number + 1

	else:
		return None

def post_action_mark_as_the_accepted(answer_id,question_id,user_id):
    global connection, cursor, answer_id

   check_ifanswer = '''
                        SELECT answers.pid
                        FROM answers 
                        WHERE answers.pid = answer_id

                    '''


   check_ifquestion = '''
                        SELECT questions.pid
                        FROM questions 
                        WHERE questions.pid = answer_id

                    '''

    check_privilege = '''
                        SELECT privilege.uid
                        FROM privilege
                        WHERE answers.pid = user_id

                    '''

    check_ifaccceptedanswer = '''
                        SELECT questions.theaid
                        FROM questions 
                        WHERE questions.theaid = answer_id

                    '''


   insert_theacceptedanswer = '''
                            INSERT INTO questions (pid, theaid) VALUES
                                    (question_id, answer_id);
                                    
                            '''
	delete_theacceptedanswer = '''
                            DELETE FROM questions
                            WHERE questions.theaid = answer_id);
                                    
                            '''
    cursor.execute(check_ifanswer)
    answerbool = cursor.fetchone()

    cursor.execute(check_ifquestion)
    questionbool = cursor.fetchone()

    cursor.execute(check_privilege)
    privilegebool = cursor.fetchone()

    cursor.execute(check_ifaccceptedanswer)
    acceptedanswerbool = cursor.fetchone()

   if answerbool and not questionbool and privilegebool:
   		if acceptedanswerbool:
   			print("The answer is already accepted. Do you want to change it?[Y/N]")
   			input1 = input()
   			if input1 == 'Y':
   				cursor.execute(delete_theacceptedanswer)
   			else if input1 == 'N':
   				return None
   			else:
   				print("Invalid input")
   		else: cursor.execute(insert_theacceptedanswer)
		

	else:
		return None
   
    connection.commit()
    return
    
def post_action_give_badge(user_id,post_id,bodge_name):
    global connection, cursor

    timegiven = date.today()

   check_privilege = '''
                        SELECT privilege.uid
                        FROM privilege
                        WHERE answers.pid = user_id

                    '''

   give_badge = '''
                            INSERT INTO ubadges (uid,bdate, bname) VALUES
                                    (answer_id, timegiven, badge_name);
                                    
                            '''
	cursor.execute(check_privilege)
	privilegebool = cursor.fetchone()



   if privilegebool:
   		cursor.execute(give_badge)
		

	else:
		return None
   
    connection.commit()
    return




def main():
    global connection, cursor

    path = "./mini_project1.db"
    connect(path)
    drop_tables()
    define_tables()
    post_action_answer()
    post_action_vote()
    post_action_mark_as_the_accepted()
    post_action_give_badge()

    

    connection.commit()
    connection.close()
    return


if __name__ == "__main__":
    main()