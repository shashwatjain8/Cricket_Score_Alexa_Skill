#!/usr/bin/env python
from flask import Flask
from flask_ask import Ask, statement, question, session

import requests
from bs4 import BeautifulSoup

# This script relies on Cricinfo RSS Live Feed (http://static.cricinfo.com/rss/livescores.xml)


app = Flask(__name__)
ask = Ask(app, '/cricketscore')


def fetch_score_data():
	
	url = "http://static.cricinfo.com/rss/livescores.xml"

	score_data_raw = requests.get(url)
	score_data_soup = BeautifulSoup(score_data_raw.text, features = "html.parser")
	score_data = score_data_soup.find_all('description')

	return score_data	


def getscore(teamname):
	score_data = fetch_score_data()
	if len(score_data) < 2:
		return "Looks like no matches are live."
	
	flag = False

	for i, game in enumerate(score_data[1:], 1): 
		if teamname in game.text:
			flag = True
			team_score = game.text
			break

	if flag:
		return team_score
	else:
		return "Looks like no matches are live for team " + teamname

@app.route('/')
def homepage():
    return 'Welcome to Cricket Score Notifier'

@ask.launch
def start_skill():
    message = 'Hey.. Which team\'s score would you like to know?'
    return question(message)

@ask.intent("TeamIntent")
def team_intent():
	team = intent['slots']['teamname']['value']
	team_score =  getscore(team)
	team_score = team_score.replace('/'," for ")
	team_score = team_score.replace('*'," with innings in progess ")
	return statement(team_score)

@ask.intent("NoIntent")
def no_Intent():
    message = 'Well that is fine...Maybe next time'
    return statement(message)

@ask.intent("CancelIntent")
def cancel_Intent():
    message = 'See you again...bye'
    return statement(message)

@ask.intent("HelpIntent")
def help_Intent():
    message = 'Utter the team name for which you want to know the score..'
    return statement(message)

if __name__ == '__main__':
    app.run(debug = True)