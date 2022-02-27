from __future__ import print_function
import imp
import os.path
import re
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
SPREADSHEET_ID = '1_cI2G8TvBrYxiEEixKnayq7bLubDb0yQS8oNO4twWoM'
PAID_USER = "PaidUserData!A:A"
YOUTUBE_LINKS_RANGE = 'YTLinks!A2:C'
FEEDBACK_RANGE = 'FeedBack!A:D'
SCREENSHOT_RANGE = 'ScreenShots!A2:D'
NEW_USER = 'UserData!A2:C'

curr_sheet = ""

# Helper Functions
# def readSheet(sheet):

# 	# Get all Questions
# 	if QUIZ:
# 		result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=ALLQ_RANGE).execute()
# 		allRows = result.get('values', [])

# 		if not allRows:
# 			print('No Questions found.')
# 		else:
# 			for row in allRows:
# 					#print(row)
# 					QDict[row[0]] = []
# 					QDict[row[0]].append(row[1])
# 					QDict[row[0]].append(row[2])
# 					QDict[row[0]].append(row[3])
# 					QDict[row[0]].append(row[4])

# 	# Get Youtube Links
# 	if YTLINKS:
# 		result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=YOUTUBE_LINKS_RANGE).execute()
# 		allRows = result.get('values', [])

# 		if not allRows:
# 			print('No Links found.')
# 		else:
# 			for row in allRows:
# 					#print(row)
# 					YTDict[row[0]] = []
# 					YTDict[row[0]].append(row[1])
# 					try:
# 						YTDict[row[0]].append(row[2])
# 					except:
# 						YTDict[row[0]].append("No Youtube video yet")

class CheckPaidUser(Resource):
	def post(self):
		global curr_sheet
		result = curr_sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=PAID_USER).execute()
		allRows = result.get('values', [])

		data = request.get_json()
		Number = data.get("number")
		if not allRows:
			print("No Users Found")
		else:
			for row in allRows:
				if row[0] == Number:
					return {}, 200
		return {}, 500

import pytz
class GetCurrenTime(Resource):
	def post(self):
		global curr_sheet
		IST = pytz.timezone('Asia/Kolkata')
		curr_time = datetime.datetime.now(IST)
		curr_hour = curr_time.time().hour
		begin_working_hour = 17
		end_working_hour = 22
		if curr_hour >= begin_working_hour and curr_hour < end_working_hour:
			return {}, 200
		return {}, 500


# class YouTubeLinks(Resource):
# 	def post(self):
# 		data= request.get_json()
# 		# print("here")
# 		LinkIdx = data.get("LinkId")
# 		response = {"Mode":YTDict[LinkIdx][0], "Link":YTDict[LinkIdx][1]}
# 		return response, 200


class Feedback(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		Number = data.get("number")
		Name = data.get("name")
		Feedback = data.get("feedback")
		IST = pytz.timezone('Asia/Kolkata')
		TimeStamp = str(datetime.datetime.now(IST))
		values = [[TimeStamp, Number, Name, Feedback]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=FEEDBACK_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		return {"Updated Cells":result.get('updates').get('updatedCells')}, 200

class StoreScreenShot(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		Number = data.get("number")
		Name = data.get("name")
		ScreenShot = data.get("screenshot")
		IST = pytz.timezone('Asia/Kolkata')
		TimeStamp = str(datetime.datetime.now(IST))
		values = [[TimeStamp, Number, Name, ScreenShot]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=SCREENSHOT_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		return {"Updated Cells":result.get('updates').get('updatedCells')}, 200

class UserFeedback(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		Number = data.get("number")
		Name = data.get("name")
		Feedback = data.get("feedback")
		IST = pytz.timezone('Asia/Kolkata')
		TimeStamp = str(datetime.datetime.now(IST))
		values = [[TimeStamp, Number, Name, Feedback]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=UFEEDBACK_RANGE, valueInputOption='USER_ENTERED', body=body).execute()
		return {"Updated Cells":result.get('updates').get('updatedCells')}, 200


class NewUser2(Resource):
	def post(self):
		global curr_sheet
		data = request.get_json()
		Number = data.get("number")
		Name = data.get("name")
		IST = pytz.timezone('Asia/Kolkata')
		TimeStamp = str(datetime.datetime.now(IST))

		values = [[TimeStamp, Number, Name]]
		body = {'values': values}
		result = curr_sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=NEW_USER, valueInputOption='USER_ENTERED', body=body).execute()
		return {"Updated Cells":result.get('updates').get('updatedCells')}, 200

# class NewUser1(Resource):
# 	def post(self):
# 		global curr_sheet
# 		result = curr_sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=NEW_USER).execute()
# 		allRows = result.get('values', [])

# 		data = request.get_json()
# 		Number = data.get("number")
# 		if not allRows:
# 			print("No Users Found")
# 		else:
# 			for row in allRows:
# 				if row[1] == Number:
# 					return {}, 200
# 		return {}, 500

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
	# readSheet(curr_sheet)
	# API config
	api.add_resource(CheckPaidUser, "/api/v1/paiduser", endpoint="CheckPaidUser")
	api.add_resource(NewUser2, "/api/v1/newuser2", endpoint="NewUser2")
	api.add_resource(StoreScreenShot, "/api/v1/ss", endpoint="StoreScreenShot")
	api.add_resource(Feedback, "/api/v1/feedback", endpoint="Feedback")
	api.add_resource(GetCurrenTime, "/api/v1/getcurrenttime", endpoint="GetCurrenTime")

	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'sheets'

	sess.init_app(app)
	if DEBUG:
		app.run(debug=False, host="0.0.0.0", port=7000)
	else:
		app.run(debug=False, host="0.0.0.0", port=80)


if __name__ == '__main__':
	main()

