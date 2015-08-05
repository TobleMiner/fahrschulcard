import sqlite3
from question import Question, Answer

conn = sqlite3.connect('license.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS "answers" (\
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,\
	`answer`	TEXT,\
	`question`	INTEGER)')

c.execute('CREATE TABLE IF NOT EXISTS "questions" (\
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,\
	`question`	TEXT,\
	`media`	TEXT)')
conn.commit()

def find_answers(question):
    if(question.media):
        t = (question.question, question.media)
        c.execute('SELECT answers.answer FROM questions, answers WHERE \
            questions.question = ? AND questions.id = answers.question AND \
            questions.media = ? ORDER BY answers.id ASC', t)
    else:
        t = (question.question, )
        c.execute('SELECT answers.answer FROM questions, answers WHERE \
            questions.question = ? AND questions.id = answers.question \
            ORDER BY answers.id ASC', t)
    answers = []
    row = c.fetchone()
    aid = 1
    while(row):
        if(question.type == Question.Type.multiple_choice):
            for answer in question.answers:
                if(answer.answer == row[0]):
                    answers.append(answer)
        elif(question.type == Question.Type.text):
            answer = Answer(aid)
            answer.answer = row[0]
            answers.append(answer)
            aid += 1
        row = c.fetchone()
    return answers

def add_question(question):
    if(question.media):
        t = (question.question, question.media)
        c.execute('SELECT * FROM questions WHERE question = ? AND media = ?', t)
    else:
        t = (question.question,)
        c.execute('SELECT * FROM questions WHERE question = ?', t)
    if(not c.fetchone()):
        t = (question.question, question.media)
        c.execute('INSERT INTO questions (question, media) VALUES (?, ?)', t)
        conn.commit();

def add_answer(question, answer):
    if(question.media):
        t = (question.question, question.media)
        c.execute('SELECT id FROM questions WHERE question = ? AND media = ?', t)
    else:
        t = (question.question,)
        c.execute('SELECT id FROM questions WHERE question = ?', t)
    qid = c.fetchone()[0]
    t = (answer.answer, qid)
    c.execute('SELECT * FROM answers WHERE answer = ? AND question = ?', t)
    if(not c.fetchone()):
        t = (answer.answer, qid)
        c.execute('INSERT INTO answers (answer, question) VALUES (?, ?)', t)
        conn.commit();
