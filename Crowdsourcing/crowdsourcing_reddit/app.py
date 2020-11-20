from flask import Flask, render_template, request, json, jsonify
import pandas as pd
import random
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import boto3
import rootkey
import time
import atexit
import sys
MAX_ANSWER_PER_SENTENCE = 3

"""

ACCESS AWS

"""
FILE_NAME = 'articles.csv'
BUCKET_NAME = 'crowdsourcingreddit'

s3_client = boto3.client('s3', 
	aws_access_key_id=rootkey.AWS_SERVER_PUBLIC_KEY, 
	aws_secret_access_key=rootkey.AWS_SERVER_SECRET_KEY, 
	region_name=rootkey.REGION_NAME
)

s3_client.download_file(BUCKET_NAME, FILE_NAME, FILE_NAME)
df_articles = pd.read_csv(FILE_NAME)

def upload_file():
	with open(FILE_NAME, "rb") as f:
		s3_client.upload_fileobj(f, BUCKET_NAME, FILE_NAME)
	print("uploaded file")
	sys.stdout.flush()

#########################################################

"""

FLASK

"""
app = Flask(__name__, static_url_path='/static')


@app.route("/")
def main():
	perc = "{:.2f}".format(((df_articles['answer_to_give'].sum())*100 / (len(df_articles)*3)))
	return render_template('index.html', perc_completion=perc)


def pick_new_article():
	perc = "{:.2f}".format(((df_articles['answer_to_give'].sum())*100 / (len(df_articles)*3)))
	if len(df_articles[df_articles['answer_to_give'] < 3]) == 0:
		return {'article_id': -1, 'text': 'Experiment is over! Thanks for participating!'}
	rand_id = random.randint(0, len(df_articles)-1)
	while df_articles.at[rand_id, 'answer_to_give'] >= 3:
		rand_id = random.randint(0, len(df_articles)-1)
	return {'article_id': rand_id, 'text': df_articles.at[rand_id, 'text'], 'title': df_articles.at[rand_id, 'title'], 'summary': df_articles.at[rand_id, 'summary'],'perc_completion': perc, 'url': df_articles.at[rand_id, 'url']}

"""

Receives: old_sentence_id, response
Updates results on df_articles
Returns: sentence_text, sentence_id

"""
@app.route("/send_article")
def send_sentence():

	global df_articles

	#Read values
	old_article_id = request.args.get('article_id', 0, type=int)
	response = request.args.get('response', 0, type=str)
	df_articles = pd.read_csv('articles.csv')

	#User just entered
	if old_article_id != -1:
		answer_to_give = df_articles.at[old_article_id, 'answer_to_give']
		df_articles.at[old_article_id, 'answer_' + str(answer_to_give)] = response
		df_articles.at[old_article_id, 'answer_to_give'] = answer_to_give + 1
		df_articles.to_csv('articles.csv', index=False)


	#Pick a new article
	new_data = pick_new_article()
	return jsonify(new_data)

"""

Runs the application server side

"""
print("Starting crowdsourcing...")
sys.stdout.flush()
scheduler = BackgroundScheduler()
scheduler.add_job(func=upload_file, trigger="interval", seconds=600)
scheduler.start()
if __name__ == "__main__":
	app.run(debug=False, use_reloader=False)
