import urllib.request
import urllib.parse
from question import Question

base_url = 'https://fahrschulcard.de/'
useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'

class Response():
    def __init__(self, data, headers):
        self.data = data
        self.headers = headers
        self.cookies = {}
        cookies = headers['Set-Cookie'];
        if(cookies):
            for pair in cookies.split(';'):
                pair = pair.split('=')
                self.cookies[pair[0]] = pair[1]

def post(url, form_data, headers={}):
    data = urllib.parse.urlencode(form_data).encode('utf-8')
    request = urllib.request.Request(url)
    request.add_header("Content-Type",
        "application/x-www-form-urlencoded;charset=utf-8")
    request.add_header("User-Agent", useragent)
    for key, value in headers.items():
        request.add_header(key, value)
    with urllib.request.urlopen(request, data) as f:
        return Response(f.read().decode('utf-8'), f.info())

def login(user, password):
    url = urllib.parse.urljoin(base_url, '/de/fsc.html')
    formdata = {'logintype' : 'login', 'version' : 'fsc',
        'redirect_url' : 'fsc', 'user' : user, 'pass' : password}
    print(post(url, formdata).data)
    #return post(url, formdata).cookies['PHPSESSID'];

def get(url, headers={}):
    request = urllib.request.Request(url)
    request.add_header("Content-Type",
        "application/x-www-form-urlencoded;charset=utf-8")
    request.add_header("User-Agent", useragent)
    for key, value in headers.items():
        request.add_header(key, value)
    with urllib.request.urlopen(request) as f:
        return Response(f.read().decode('utf-8'), f.info())

def get_questions(session):
    url = urllib.parse.urljoin(base_url, '/de/fsc.html?id=fsc&view=view_bogen')
    headers = { 'Cookie' : "PHPSESSID=" + session}
    return get(url, headers).data

def get_session():
    url = base_url
    return get(url).cookies['PHPSESSID'];

def send_solution(url, session, questions, xtra):
    url = urllib.parse.urljoin(base_url, url)
    headers = { 'Cookie' : "PHPSESSID=" + session}
    data = xtra.copy()
    for question in questions:
        for answer in question.correct_answers:
            if(question.type == Question.Type.multiple_choice):
                data[str(question.id) + '_answer_' + str(answer.id)] = 'x'
            elif(question.type == Question.Type.text):
                data[str(question.id) + '_answer_' + str(answer.id)] = answer.answer
    return post(url, data, headers).data
