#!/usr/bin/env python

import argparse
import urllib.request
import request
import parse
import solver
from getpass import getpass

argp = argparse.ArgumentParser()
argp.add_argument('-u', '--user', type=str)
argp.add_argument('-p', '--password', type=str)
argp.add_argument('-n', '--runs', type=int)
args = argp.parse_args()

nruns = 1
user = None
password = None

if(args.runs):
    nruns = args.runs
user = args.user
password = args.password

if(not user):
    user = input('Username: ')
if(not password):
    password = getpass('Password: ')

hit_rate = 0

for i in range(nruns):
    if(not request.check_login()):
        print("Session invalid. Logging in")
        request.login(user, password)
    data = request.get_questions()
    parser = parse.QuestionPageParser()
    parser.feed(data);

    hit_rate_round = 0;

    for question in parser.questions:
        question.correct_answers = solver.find_answers(question)
        if(len(question.correct_answers) > 0):
            hit_rate_round += 1 / len(parser.questions)


    data = request.send_solution(parser.submit_url, parser.questions,
        parser.hidden_data)

    parser = parse.SolutionPageParser()
    parser.feed(data)

    for question in parser.questions:
        solver.add_question(question)
        for answer in question.correct_answers:
            solver.add_answer(question, answer)

    hit_rate += hit_rate_round / nruns

    print('Round {0} of {1}'.format(i + 1, nruns))
    print('Round hit rate: {0:.2f} %'.format(hit_rate_round * 100))

print('Overall hit rate: {0:.2f} %'.format(hit_rate * 100))
