from __future__ import print_function
import os.path
from sqlite3 import Time
from tokenize import Name
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
DEBUG = 0
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1eRER4f4vc9yFjISIXXhUZ9JBrkBp6GRoCPMKaFkB8Q8'
NEW_USER = "NewUser!A:C"
ALLQ_RANGE = 'AllQuestions!A:F'
TRANSACTION_RANGE = 'All Transactions - V2!A:D'
YOUTUBE_M_RANGE = 'YTLinksMath!A2:D'
YOUTUBE_S_RANGE = 'YTLinksSci!A2:D'
NOTES_M_E_RANGE = 'NotesMathEnglish!A2:D'
NOTES_M_K_RANGE = 'NotesMathKannada!A2:D'
NOTES_S_E_RANGE = 'NotesSci!A2:D'
NOTES_S_K_RANGE = 'NotesSci!A2:D'
# DCQ_RANGE = "DailyChallenge!A2:E11"
# DC_TRANSACTION_RANGE='DailyChallengeTransactions!A:D'
# DC_PERF_RANGE='DailyChallengeRecentTransactions!A2:G'
MCQ_CHECK_RANGE='Recent Actitvity Per User - V2!A2:G'
DOUBTS_RANGE='Doubts!A:C'
TRACK_DOUBTS_RANGE='Doubts!A:D'
FEEDBACK_RANGE='FeedBack/Suggestions!A:C'
UFEEDBACK_RANGE='UFeedBack!A:C'
QUIZ = 0
NOTES = 1
YTLINKS = 1
# Question Dictionary

UsersDict = {}
QDict = {}
YTDict = {"1" : {}, "2" : {}}
NotesDict = {"1" : {"E" : {}, "K" : {}}, "2" : {"E" : {}, "K" : {}}}
DCDict = {}
curr_sheet = ""

# Helper Functions
def readSheet(sheet):

	# Get all Questions
	if QUIZ:
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

	# Get Math Youtube Links
	if YTLINKS:
		result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=YOUTUBE_M_RANGE).execute()
		allRows = result.get('values', [])

		if not allRows:
			print('No Links found.')
		else:
			for row in allRows:
					#print(row)
					YTDict["1"][row[0]] = []
					YTDict["1"][row[0]].append(row[1])
					try:
						YTDict["1"][row[0]].append(row[2])
					except:
						YTDict["1"][row[0]].append("No Youtube video yet for this chapter")
					# YTDict["1"][row[0]].append(int(row[3]))


	# Get Science Youtube Links
		result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=YOUTUBE_S_RANGE).execute()
		allRows = result.get('values', [])

		if not allRows:
			print('No Links found.')
		else:
			for row in allRows:
					#print(row)
					YTDict["2"][row[0]] = []
					YTDict["2"][row[0]].append(row[1])
					try:
						YTDict["2"][row[0]].append(row[2])
					except:
						YTDict["2"][row[0]].append("No Youtube video yet for this chapter")
					# YTDict["2"][row[0]].append(int(row[3]))

	
	# Get Math Notes
	if NOTES:
		result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=NOTES_M_E_RANGE).execute()
		allRows = result.get('values', [])

		if not allRows:
			print('No Links found.')
		else:
			for row in allRows:
					#print(row)
					NotesDict["1"]["E"][row[0]] = []
					NotesDict["1"]["E"][row[0]].append(row[1])
					try:
						NotesDict["1"]["E"][row[0]].append(row[2])
					except:
						NotesDict["1"]["E"][row[0]].append("No notes yet for this chapter")
					# NotesDict["1"]["E"][row[0]].append(int(row[3]))

		result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=NOTES_M_K_RANGE).execute()
		allRows = result.get('values', [])

		if not allRows:
			print('No Links found.')
		else:
			for row in allRows:
					#print(row)
					NotesDict["1"]["K"][row[0]] = []
					NotesDict["1"]["K"][row[0]].append(row[1])
					try:
						NotesDict["1"]["K"][row[0]].append(row[2])
					except:
						NotesDict["1"]["K"][row[0]].append("No notes yet for this chapter")
					# NotesDict["1"]["K"][row[0]].append(int(row[3]))

	# Get Science Notes
		result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=NOTES_S_E_RANGE).execute()
		allRows = result.get('values', [])

		if not allRows:
			print('No Links found.')
		else:
			for row in allRows:
					#print(row)
					NotesDict["2"]["E"][row[0]] = []
					NotesDict["2"]["E"][row[0]].append(row[1])
					try:
						NotesDict["2"]["E"][row[0]].append(row[2])
					except:
						NotesDict["2"]["E"][row[0]].append("No notes yet for this chapter")
					# NotesDict["2"]["E"][row[0]].append(int(row[3]))

		result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=NOTES_S_K_RANGE).execute()
		allRows = result.get('values', [])

		if not allRows:
			print('No Links found.')
		else:
			for row in allRows:
					#print(row)
					NotesDict["2"]["K"][row[0]] = []
					NotesDict["2"]["K"][row[0]].append(row[1])
					try:
						NotesDict["2"]["K"][row[0]].append(row[2])
					except:
						NotesDict["2"]["K"][row[0]].append("No notes yet for this chapter")
					# NotesDict["2"]["K"][row[0]].append(int(row[3]))
		#get users data



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
		TimeStamp = str(datetime.datetime.now())
		Ans = data.get("Answer")
		Ph = data.get("Number")

		values = [[TimeStamp, Ph, QNo, Ans]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=TRANSACTION_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		print('{0} cells appended basic MCQs.'.format(result.get('updates').get('updatedCells')))
		return {"Updated Cells": result.get('updates').get('updatedCells')}, 200

class Queries(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		TimeStamp = str(datetime.datetime.now())
		Query = data.get("Query")
		Ph = data.get("Number")

		values = [[TimeStamp, Ph, Query]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=DOUBTS_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		print('{0} cells appended basic MCQs.'.format(result.get('updates').get('updatedCells')))
		return {"Updated Cells":result.get('updates').get('updatedCells')}, 200

class TrackQuery(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		Number = data.get("number")
		
		CurrentTimeStamp = datetime.datetime.now()
		formatter = "%Y-%m-%d %H:%M:%S"
		# DoubtsTimeStamp = str(datetime.datetime.now())

		result = curr_sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=TRACK_DOUBTS_RANGE).execute()
		allRows = result.get('values', [])
		doubts_list = []
		timestamp_list = []
		pending_doubts = 0
		if not allRows:
			print("Cool cool cool cool cool No Doubt No Doubt")
			return {"pending":str(0), "doubts":"Do ask Akka your doubts"}, 200
		else:
			for row in allRows:
				# print(row)
				if(row[1] == Number and row[3] == "Pending"):
					pending_doubts+=1
					DoubtsTimeStamp = datetime.datetime.strptime(row[0], formatter)
					# print(CurrentTimeStamp, DoubtsTimeStamp)
					TimeLeft = 6 - (CurrentTimeStamp - DoubtsTimeStamp).total_seconds()//3600
					Hours = " Hours"
					if TimeLeft <= 1:
						TimeLeft = 1
						Hours = " Hour"
					doubts_list.append(row[2] + " - Akka will resolve it in the next " + str(TimeLeft) + Hours)
					# timestamp_list.append((CurrentTimeStamp - DoubtsTimeStamp).total_seconds()//3600)

		if pending_doubts:
			return {"pending":str(pending_doubts), "doubts":"\n".join(doubts_list)}, 200
		else:
			return {"pending":str(0), "doubts":"Do ask Akka your doubts"}, 200

class YouTubeLinks(Resource):
	def post(self):
		data= request.get_json()
		# print("here")
		LinkIdx = data.get("LinkIdx")
		Subject = data.get("Subject")
		response = {"ChapterName":YTDict[Subject][LinkIdx][0], "Link":YTDict[Subject][LinkIdx][1]}
		return response, 200

class NotesLinks(Resource):
	def post(self):
		data= request.get_json()
		# print("here")
		Chapter = data.get("Chapter")
		Subject = data.get("Subject")
		response = {"ChapterName":NotesDict[Subject]["E"][Chapter][0], "LinkE":NotesDict[Subject]["E"][Chapter][1], "LinkK":NotesDict[Subject]["K"][Chapter][1]}
		return response, 200
class Feedback(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		Number = data.get("number")
		Name = data.get("name")
		Feedback = data.get("feedback")
		TimeStamp = str(datetime.datetime.now())
		values = [[TimeStamp, Number, Name, Feedback]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=FEEDBACK_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		return {"Updated Cells":result.get('updates').get('updatedCells')}, 200
class UserFeedback(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		Number = data.get("number")
		Name = data.get("name")
		Feedback = data.get("feedback")
		TimeStamp = str(datetime.datetime.now())
		values = [[TimeStamp, Number, Name, Feedback]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=UFEEDBACK_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		return {"Updated Cells":result.get('updates').get('updatedCells')}, 200

class NewUser1(Resource):
	def post(self):
		global curr_sheet
		result = curr_sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=NEW_USER).execute()
		allRows = result.get('values', [])

		data = request.get_json()
		Number = data.get("number")
		if not allRows:
			print("No Users Found")
		else:
			for row in allRows:
				if row[1] == Number:
					return {}, 200
		return {}, 500


class NewUser2(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		Number = data.get("number")
		Location = data.get("location")
		TimeStamp = str(datetime.datetime.now())

		values = [[TimeStamp, Number, Location]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=NEW_USER, valueInputOption='USER_ENTERED', body=body).execute()
		return {"Updated Cells":result.get('updates').get('updatedCells')}, 200

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
		TimeStamp = str(datetime.datetime.now())
		Ans = data.get("Answer")
		Ph = data.get("Number")

		values = [[TimeStamp, Ph, QNo, Ans]]
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
	api.add_resource(NewUser1, "/api/v1/newuser1", endpoint="NewUser1")
	api.add_resource(NewUser2, "/api/v1/newuser2", endpoint="NewUser2")
	api.add_resource(BasicUser, "/api/v1/basic_user", endpoint="BasicUser")
	api.add_resource(Transaction, "/api/v1/transaction", endpoint="Transaction")
	api.add_resource(YouTubeLinks, "/api/v1/yt_link", endpoint="YouTubeLinks")
	api.add_resource(NotesLinks, "/api/v1/notes_link", endpoint="NotesLinks")
	api.add_resource(MCQAnswer, "/api/v1/mcq_correction", endpoint="MCQAnswer")

	# api.add_resource(DailyChallengeQuestion, "/api/v1/update_challenge", endpoint="UpdateChallenge")
	# api.add_resource(DailyChallengeQuestion, "/api/v1/dc_question", endpoint="DailyChallenge")
	# api.add_resource(DailyChallengeTransaction, "/api/v1/dc_transaction", endpoint="DailyChallengeTransaction")
	# api.add_resource(DailyChallengePerformance, "/api/v1/dc_performance", endpoint="DailyChallengePerformance")

	api.add_resource(Queries, "/api/v1/query", endpoint="Queries")
	api.add_resource(TrackQuery, "/api/v1/tquery", endpoint="TrackQuery")
	api.add_resource(Feedback, "/api/v1/feedback", endpoint="Feedback")
	api.add_resource(UserFeedback, "/api/v1/ufeedback", endpoint="UserFeedback")
	api.add_resource(QuestionCount, "/api/v1/qcount", endpoint="QuestionCount")

	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'sheets'

	sess.init_app(app)
	if DEBUG:
		app.run(debug=False, host="0.0.0.0", port=7000)
	else:
		app.run(debug=False, host="0.0.0.0", port=80)


if __name__ == '__main__':
	main()

