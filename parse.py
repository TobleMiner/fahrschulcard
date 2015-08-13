from html.parser import HTMLParser
import question
import re

class QuestionPageParser(HTMLParser):
    def __init__(self):
        super(QuestionPageParser, self).__init__()
        self.current_question = None
        self.current_answer = None
        self.re_question_id = re.compile('\A[0-9]+')
        self.re_answer_id = re.compile('[0-9]+\Z')
        self.re_submit_url = re.compile('.*fsc\.html\?')
        self.re_media_pic_url = re.compile('/fileadmin/fahrschulboegen/online/pics/q_pic/.+\.jpg')
        self.capture_answer_data = False
        self.capture_question_data = False
        self.questions = []
        self.hidden_data = {}
        self.capture_hidden = False
        self.submit_url = None
    def handle_starttag(self, tag, attrs):
        dict = {}
        for value in attrs:
            dict[value[0]] = value[1]
        attrs = dict
        if(tag == 'form' and not self.submit_url):
            url = attrs['action']
            if(self.re_submit_url.search(url)):
                self.submit_url = url
                print(self.submit_url)
                self.capture_hidden = True
        elif(tag == 'div'):
            if('id' in attrs and 'class' in attrs and
                attrs['class'] == 'fb_frage'):
                print("Found question: " + attrs['id'])
                id = int(self.re_question_id.search(attrs['id']).group(0))
                self.current_question = question.Question(id)
                self.questions.append(self.current_question)
                self.capture_question_data = True
        elif(tag == 'input'):
            if(attrs['type'] == 'checkbox' and self.current_question):
                print("Found answer: " + attrs['id'])
                self.current_question.type = question.Question.Type.multiple_choice
                id = int(self.re_answer_id.search(attrs['id']).group(0))
                self.current_answer = question.Answer(id)
                self.current_question.answers.append(self.current_answer)
            elif(attrs['type'] == 'text' and self.current_question and
                'id' in attrs):
                print("Found input field for answer")
                id = int(self.re_answer_id.search(attrs['id']).group(0))
                self.current_answer = question.Answer(id)
                self.current_question.type = question.Question.Type.text
                self.current_question.answers.append(self.current_answer)
            elif(attrs['type'] == 'hidden' and self.capture_hidden):
                self.hidden_data[attrs['name']] = attrs['value']
        elif(tag == 'label'):
            if('id' in attrs and 'style' in attrs and 'for' in attrs):
                self.capture_answer_data = True
        elif(tag == 'video'):
            if(self.current_question and 'poster' in attrs and
                self.re_media_pic_url.search(attrs['poster'])):
                self.current_question.media = attrs['poster'];
        elif(tag == 'img'):
            if(self.current_question and 'src' in attrs and
                self.re_media_pic_url.search(attrs['src'])):
                self.current_question.media = attrs['src'];


    def handle_endtag(self, tag):
        if(tag == 'form'):
            self.capture_hidden = False

    def handle_data(self, data):
        if(self.capture_question_data):
            self.current_question.question = data.strip()
            self.capture_question_data = False
            print(data)
        if(self.capture_answer_data):
            print(data)
            self.current_answer.answer = data.strip()
            self.capture_answer_data = False

class SolutionPageParser(HTMLParser):
    def __init__(self):
        super(SolutionPageParser, self).__init__()
        self.current_question = None
        self.current_answer = None
        self.re_question_id = re.compile('\A[0-9]+')
        self.re_answer_id = re.compile('[0-9]+')
        self.re_answer_number = re.compile('[0-9,]+')
        self.re_answer_text = re.compile('Antwort:.+')
        self.re_media_pic_url = re.compile('/fileadmin/fahrschulboegen/online/pics/q_pic/.+\.jpg')
        self.capture_answer_data = False
        self.capture_question_data = False
        self.questions = []
    def handle_starttag(self, tag, attrs):
        dict = {}
        for value in attrs:
            dict[value[0]] = value[1]
        attrs = dict
        if(tag == 'div'):
            if('id' in attrs and 'class' in attrs and
                attrs['class'] == 'fb_frage'):
                print("Found question: " + attrs['id'])
                id = int(self.re_question_id.search(attrs['id']).group(0))
                self.current_question = question.Question(id)
                self.questions.append(self.current_question)
                self.capture_question_data = True
            elif('class' in attrs and attrs['class'] == 'fb_frage_antwort'):
                print("Found answer: " + attrs['id'])
                id = int(self.re_answer_id.search(attrs['id'],
                    self.re_answer_id.search(attrs['id']).end()).group(0))
                self.current_answer = question.Answer(id)
                self.current_question.answers.append(self.current_answer)
            elif((not ('class' in attrs or 'id' in attrs)) and
                self.current_answer and not self.current_answer.answer and
                self.current_question.type == question.Question.Type.multiple_choice):
                self.capture_answer_data = True
        elif(tag == 'img'):
            if('src' in attrs and attrs['src'] ==
                '/fileadmin/fahrschulboegen/online/pics/checked_soll.gif' and
                self.current_question):
                self.current_question.type = question.Question.Type.multiple_choice
                print("Correct answer is " + str(self.current_answer.id))
                self.current_question.correct_answers.append(self.current_answer)
            elif(self.current_question and 'src' in attrs and
                self.re_media_pic_url.search(attrs['src'])):
                self.current_question.media = attrs['src'];
        elif(tag == 'b'):
            if(self.current_question and self.current_answer and
                not self.current_question.type):
                self.current_question.type = question.Question.Type.text
                self.capture_answer_data = True
        elif(tag == 'label'):
            if('id' in attrs and 'style' in attrs and 'for' in attrs):
                self.capture_answer_data = True
        elif(tag == 'video'):
            if(self.current_question and 'poster' in attrs and
                self.re_media_pic_url.search(attrs['poster'])):
                self.current_question.media = attrs['poster'];

    def handle_data(self, data):
        data = data.strip()
        if(self.capture_question_data):
            print(data)
            self.current_question.question = data
            self.capture_question_data = False
        if(self.capture_answer_data):
            print(data)
            if(self.current_question.type == question.Question.Type.text):
                if(not self.re_answer_text.search(data)):
                    return
                data = self.re_answer_number.search(data)
                while(data):
                    self.current_answer.answer = data.group()
                    self.current_question.correct_answers.append(self.current_answer)
                    data = self.re_answer_number.search(data.group(), data.end())
                    if(data):
                        self.current_answer = question.Answer(self.current_answer.id + 1)
                self.capture_answer_data = False
                return
            self.current_answer.answer = data
            self.capture_answer_data = False

class LoginPageParser(HTMLParser):
    def __init__(self):
        super(LoginPageParser, self).__init__()
        self.login = True
    def handle_starttag(self, tag, attrs):
        dict = {}
        for value in attrs:
            dict[value[0]] = value[1]
        attrs = dict
        if(tag == 'div' and 'id' in attrs and attrs['id'] == 'failures'):
            self.login = False
