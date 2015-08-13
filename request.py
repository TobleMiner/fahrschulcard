import urllib.request
import urllib.parse
import http.cookiejar
from question import Question
from parse import LoginPageParser

cj = http.cookiejar.CookieJar()

base_url = 'https://fahrschulcard.de/'
useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'

def cj_to_dict(jar):
    cookies = {}
    for cookie in jar:
        cookies[cookie.name] = cookie.value
    return cookies

def post(url, form_data, headers={}):
    data = urllib.parse.urlencode(form_data).encode('utf-8')
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    headers["User-Agent"] = useragent;
    for key, value in headers.items():
        opener.addheaders.append((key, value))
    with opener.open(url, data) as f:
        return f.read().decode('utf-8')

def login(user, password):
    url = urllib.parse.urljoin(base_url, '/de/fsc.html')
    formdata = {'logintype' : 'login', 'version' : 'fsc',
        'redirect_url' : 'fsc', 'user' : user, 'pass' : password}
    post(url, formdata)
    return cj_to_dict(cj)['PHPSESSID']

def get(url, headers={}):
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    headers["User-Agent"] = useragent;
    for key, value in headers.items():
        opener.addheaders.append((key, value))
    with opener.open(url) as f:
        return f.read().decode('utf-8')

def check_login():
    url = urllib.parse.urljoin(base_url, '/de/fsc.html?id=fsc&view=view_bogen')
    parser = LoginPageParser()
    parser.feed(get(url))
    return parser.login

def get_questions():
    url = urllib.parse.urljoin(base_url, '/de/fsc.html?id=fsc&view=view_bogen')
    return get(url)

def send_solution(url, questions, xtra):
    url = urllib.parse.urljoin(base_url, url)
    data = xtra.copy()
    for question in questions:
        for answer in question.correct_answers:
            if(question.type == Question.Type.multiple_choice):
                data[str(question.id) + '_answer_' + str(answer.id)] = 'x'
            elif(question.type == Question.Type.text):
                data[str(question.id) + '_answer_' + str(answer.id)] = answer.answer
    return post(url, data)
