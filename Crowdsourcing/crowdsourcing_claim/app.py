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
FILE_NAME = 'sentences.csv'
BUCKET_NAME = 'crowdsourcingclaim'

s3_client = boto3.client('s3', 
	aws_access_key_id=rootkey.AWS_SERVER_PUBLIC_KEY, 
	aws_secret_access_key=rootkey.AWS_SERVER_SECRET_KEY, 
	region_name=rootkey.REGION_NAME
)

s3_client.download_file(BUCKET_NAME, FILE_NAME, FILE_NAME)
df_sentences = pd.read_csv('sentences.csv')

def upload_file(exit=False):
	with open(FILE_NAME, "rb") as f:
		s3_client.upload_fileobj(f, BUCKET_NAME, FILE_NAME)
	print("uploaded file")
	if (exit == True):
		print("Uploaded on exit")
	sys.stdout.flush()

#########################################################

"""

FLASK

"""
app = Flask(__name__, static_url_path='/static')


@app.route("/")
def main():
	perc = str(int((df_sentences['answer_to_give'].sum())*10000 / (len(df_sentences)*3)))
	return render_template('index.html', perc_completion=perc)


def pick_new_sentence():
	perc = str(int((df_sentences['answer_to_give'].sum())*10000 / (len(df_sentences)*3)))
	if len(df_sentences[df_sentences['answer_to_give'] < 3]) == 0:
		return {'sentence_id': -1, 'sentence_text': 'Experiment is over! Thanks for participating!'}
	rand_id = random.randint(0, len(df_sentences)-1)
	while df_sentences.at[rand_id, 'answer_to_give'] >= 3:
		rand_id = random.randint(0, len(df_sentences)-1)
	return {'sentence_id': rand_id, 'sentence_text': df_sentences.at[rand_id, 'sentence'], 'perc_completion': perc}

"""

Receives: old_sentence_id, response
Updates results on df_sentences
Returns: sentence_text, sentence_id

"""
@app.route("/send_sentence")
def send_sentence():

	global df_sentences

	#Read values
	old_sentence_id = request.args.get('sentence_id', 0, type=int)
	response = request.args.get('response', 0, type=str)

	#User just entered
	if old_sentence_id != -1:
		answer_to_give = df_sentences.at[old_sentence_id, 'answer_to_give']
		df_sentences.at[old_sentence_id, 'answer_' + str(answer_to_give)] = response
		df_sentences.at[old_sentence_id, 'answer_to_give'] = answer_to_give + 1
		df_sentences.to_csv('sentences.csv', index=False)


	#Pick a sentence among the ones that have not been touched
	new_data = pick_new_sentence()
	return jsonify(new_data)

"""

Runs the application server side

"""
print("Starting crowdsourcing...")
sys.stdout.flush()
scheduler = BackgroundScheduler()
scheduler.add_job(func=upload_file, trigger="interval", seconds=600)
scheduler.start()
upload_file()
if __name__ == "__main__":
	app.run(debug=False, use_reloader=False)

	atexit.register(lambda: upload_file(exit=True))