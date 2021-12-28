from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

from flask import Flask, request, session, Response
from flask_restful import Api, Resource
from flask_session import Session
from flask_cors import CORS

import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1ku_JyM36zMu2IVxjfUtil9phubcyoQXUkc5VUue_Se8'
ALLQ_RANGE = 'All Questions!A:F'
TRANSACTION_RANGE = 'MCQTransactions!A:D'
YOUTUBE_M_RANGE = 'YouTube Links Math!A2:D'
YOUTUBE_S_RANGE = 'YouTube Links Science!A2:D'
DCQ_RANGE = "DailyChallenge!A2:E11"
DC_TRANSACTION_RANGE='DailyChallengeTransactions!A:D'
DC_PERF_RANGE='DailyChallengeRecentTransactions!A2:G'
MCQ_CHECK_RANGE='LastUserTransaction!A2:G'
DOUBTS_RANGE='All Transactions - Doubts!A:C'

# Question Dictionary

QDict = {}
YTMDict = {}
YTSDict = {}
DCDict = {}
curr_sheet = ""

# Helper Functions
def readSheet(sheet):
	result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=ALLQ_RANGE).execute()
	allRows = result.get('values', [])

	if not allRows:
		print('No Questions found.')
	else:
		for row in allRows:
				#print(row)
				QDict[row[0]] = []
				QDict[row[0]].append(row[1])
				QDict[row[0]].append(row[2])
				QDict[row[0]].append(row[3])
				QDict[row[0]].append(row[4])

	result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=YOUTUBE_M_RANGE).execute()
	allRows = result.get('values', [])

	if not allRows:
		print('No Links found.')
	else:
		for row in allRows:
				#print(row)
				YTMDict[row[0]] = []
				YTMDict[row[0]].append(row[1])
				YTMDict[row[0]].append(row[2])
				# YTMDict[row[0]].append(int(row[3]))
	

	result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=YOUTUBE_S_RANGE).execute()
	allRows = result.get('values', [])

	if not allRows:
		print('No Links found.')
	else:
		for row in allRows:
				#print(row)
				YTSDict[row[0]] = []
				YTSDict[row[0]].append(row[1])
				try:
					YTSDict[row[0]].append(row[2])
				except:
					YTSDict[row[0]].append("No Youtube video yet for this chapter")
				# YTSDict[row[0]].append(int(row[3]))


class BasicUser(Resource):
	def post(self):
		data= request.get_json()
		QNo = data.get("QNo")
		response = {"Question":QDict[QNo][0], "Answer":QDict[QNo][1], "Solution":QDict[QNo][2], "NextQuestion":QDict[QNo][3]}
		return response, 200

class QuestionCount(Resource):
	def post(self):
		data= request.get_json()
		CNo = data.get("ChapterNo")
		response = {"QCount":YTDict[CNo][2]}
		return response, 200


class Transaction(Resource):
	def post(self):
		global curr_sheet
		data= request.get_json()
		QNo = data.get("QNo")
		TS = str(datetime.datetime.now())
		Ans = data.get("Answer")
		Ph = data.get("Number")

		values = [[TS, Ph, QNo, Ans]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=TRANSACTION_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		print('{0} cells appended basic MCQs.'.format(result.get('updates').get('updatedCells')))
		return {"Updated Cells": result.get('updates').get('updatedCells')}, 200

class Queries(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		TS = str(datetime.datetime.now())
		Query = data.get("Query")
		Ph = data.get("Number")

		values = [[TS, Ph, Query]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=DOUBTS_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		print('{0} cells appended basic MCQs.'.format(result.get('updates').get('updatedCells')))
		return {"Updated Cells":result.get('updates').get('updatedCells')}, 200

class YouTubeLinks(Resource):
	def post(self):
		data= request.get_json()
		print("here")
		LinkIdx = data.get("LinkIdx")
		Subject = data.get("Subject")
		if "math" in Subject:
			response = {"ChapterName":YTMDict[LinkIdx][0], "Link":YTMDict[LinkIdx][1]}
		elif "science" in Subject:
			response = {"ChapterName":YTSDict[LinkIdx][0], "Link":YTSDict[LinkIdx][1]}
		return response, 200

'''
class DailyChallengeQuestion(Resource):
	def get(self):
		global curr_sheet
		result = curr_sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=DCQ_RANGE).execute()
		allRows = result.get('values', [])

		if not allRows:
			print('No Questions found.')
		else:
			for row in allRows:
				DCDict[row[1]] = [row[2], row[4]]

		return {"Daily Challenge Updated":str(datetime.datetime.now())}, 200

	def post(self):
		data= request.get_json()
		QNo = data.get("QNo")
		response = {"Question":DCDict[QNo][0], "NextQuestion":DCDict[QNo][1]}
		return response, 200

class DailyChallengeTransaction(Resource):
	def post(self):
		global curr_sheet
		data= request.get_json()
		QNo = data.get("QNo")
		TS = str(datetime.datetime.now())
		Ans = data.get("Answer")
		Ph = data.get("Number")

		values = [[TS, Ph, QNo, Ans]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=DC_TRANSACTION_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		print('{0} cells appended for Daily Challenge.'.format(result.get('updates').get('updatedCells')))
		return {"Updated Cells": result.get('updates').get('updatedCells')}, 200

class DailyChallengePerformance(Resource):
	def post(self):
		global curr_sheet
		result = curr_sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=DC_PERF_RANGE).execute()
		allRows = result.get('values', [])

		if not allRows:
			print('No Questions found.')
			return {"Error":"Performance Not Found"}, 500
		else:
			data= request.get_json()
			Ph = data.get("Number")
			for row in allRows:
				if(row[1] == Ph):
					return {"Performance":row[6]}, 200
'''
class MCQAnswer(Resource):
	def post(self):
		global curr_sheet
		result = curr_sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=MCQ_CHECK_RANGE).execute()
		allRows = result.get('values', [])

		if not allRows:
			print('No Questions found.')
			return {"Error":"Performance Not Found"}, 500
		else:
			data= request.get_json()
			Ph = data.get("Number")
			for row in allRows:
				if(row[1] == Ph):
					return {"Correct":row[5]}, 200


def main():
	app = Flask(__name__)
	api = Api(app)
	CORS(app)

	#Session Setup
	sess = Session()

	global curr_sheet
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.json'):
		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.json', 'w') as token:
			token.write(creds.to_json())

	service = build('sheets', 'v4', credentials=creds)

	# Call the Sheets API
	curr_sheet = service.spreadsheets()
	readSheet(curr_sheet)
	# API config
	api.add_resource(BasicUser, "/api/v1/basic_user", endpoint="BasicUser")
	api.add_resource(Transaction, "/api/v1/transaction", endpoint="Transaction")
	api.add_resource(YouTubeLinks, "/api/v1/yt_link", endpoint="YouTubeLinks")
	api.add_resource(MCQAnswer, "/api/v1/mcq_correction", endpoint="MCQAnswer")

	# api.add_resource(DailyChallengeQuestion, "/api/v1/update_challenge", endpoint="UpdateChallenge")
	# api.add_resource(DailyChallengeQuestion, "/api/v1/dc_question", endpoint="DailyChallenge")
	# api.add_resource(DailyChallengeTransaction, "/api/v1/dc_transaction", endpoint="DailyChallengeTransaction")
	# api.add_resource(DailyChallengePerformance, "/api/v1/dc_performance", endpoint="DailyChallengePerformance")

	api.add_resource(Queries, "/api/v1/query", endpoint="Queries")
	api.add_resource(QuestionCount, "/api/v1/qcount", endpoint="QuestionCount")

	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'sheets'

	sess.init_app(app)
	app.run(debug=False, host="0.0.0.0", port=7000)


if __name__ == '__main__':
	main()

