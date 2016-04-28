#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import pymongo
import time
import urllib
import urllib2
import json
import random
from threading import Timer

define("port", default=8811, help="run on the given port", type=int)

global KB_ALL
global KB_CHAIN
global KB_SINGLE
KB_ALL = [
	"!CP is wrong",
	"There are too many repeat crimes after murderers are released",
	"the sentences are not siff enough",
	"!it against the law to kill a person",
	"It is against the law for a citizen to kill another citizen and it is legal for the state to kill a citizen after the due process of law",
	"CP would decrease violent crime",
	"CP would act as a deterrent to carrying weapons",
	"!the state just one person or body of people i.e. a judge",
	"the people are merely representatives of the state",
	"killing of human life is wrong",
	"CP kills people",
	"People can't decide who to kill",
	"The state decide who to kill",
	"CP is acceptable",
]
KB_CHAIN = [
	[
		"!CP is wrong",
		"There are too many repeat crimes after murderers are released",
		"the sentences are not siff enough"
	],
	[
		"!it against the law to kill a person",
		"It is against the law for a citizen to kill another citizen and it is legal for the state to kill a citizen after the due process of law"
	],
	[
		"CP would decrease violent crime",
		"CP would act as a deterrent to carrying weapons"
	],
	[
		"!the state just one person or body of people i.e. a judge",
		"the people are merely representatives of the state"
	]
]
KB_SINGLE = [
	[
		"killing of human life is wrong"
	],
	[
		"CP kills people"
	],
	[
		"People can't decide who to kill"
	],
	[
		"The state decide who to kill"
	],
	[
		"CP is acceptable"
	]
]
# KB_CHAIN_WITH_STATUS = [
# 	[
# 		[
# 			"!CP is wrong",
# 			"There are too many repeat crimes after murderers are released",
# 			"the sentences are not siff enough"
# 		],
# 		[
# 			0,
# 			0,
# 			0
# 		]
# 	],
# 	[
# 		[
# 			"!it against the law to kill a person",
# 			"It is against the law for a citizen to kill another citizen and it is legal for the state to kill a citizen after the due process of law"
# 		],
# 		[
# 			0,
# 			0
# 		]
# 	],
# 	[
# 		[
# 			"CP would decrease violent crime",
# 			"CP would act as a deterrent to carrying weapons"
# 		],
# 		[
# 			0,
# 			0
# 		]
# 	],
# 	[
# 		[
# 			"!the state just one person or body of people i.e. a judge",
# 			"the people are merely representatives of the state"
# 		],
# 		[
# 			0,
# 			0
# 		]
# 	]
# ]
# KB_SINGLE_WITH_STATUS = [
# 	[
# 		"killing of human life is wrong",
# 		0
# 	],
# 	[
# 		"CP kills people",
# 		0
# 	],
# 	[
# 		"People can't decide who to kill",
# 		0
# 	],
# 	[
# 		"The state decide who to kill",
# 		0
# 	],
# 	[
# 		"CP is acceptable",
# 		0
# 	]
# ]

# knowledgeBase = [
# 	{
# 		"CP is wrong",
# 		"CP kills people",
# 		"killing of human life is wrong"
# 	},
# 	{
# 		"There are too many repeat crimes after murderers are released",
# 		"the sentences are not stiff enough"
# 	},
# 	{
# 		"it against the law to kill a person"
# 	},
# 	{
# 		"the state just one person or a body of people"
# 	},
# 	{
# 		"People can't decide who to kill"
# 	},
# 	{
# 		"The state can't decide who to kill",
# 		"the state just one person or a body of prople i.e. a judge"
# 	}
# ]

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/Test", TestHandler),
			(r"/Resolve2", Resolution2Handler),
			(r"/Termination2", Termination2Handler),
			(r"/StartAgent", StartAgentHandler),
		]
		settings = dict(
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			debug=True,
			)
		# conn = pymongo.Connection("localhost", 27017)
		# self.db = conn["kebiao"]
		tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		pass

class StartAgentHandler(tornado.web.RequestHandler):
	def get(self):
		pass

	def post(self):
		dialogueID = self.get_argument("dialogueID", 0)

		if dialogueID :
			dialogueID = dialogueID
			print "DialogueID:"+dialogueID
			participantID = self.getParticipantID(dialogueID)

			Timer(0, self.newPerformMoveThread, [dialogueID, participantID]).start()

	def newPerformMoveThread(self, dialogueID, participantID):
		CHECKING_INTERVAL = 10
		print "\nNew PerformMove Thread Created."
		while self.getGameStatus(dialogueID) :
			print "\nGame status: game is on."
			if self.getMoves(dialogueID, participantID):
				print "\nLegal moves exist."
				self.performMove(dialogueID, participantID)
			print "\nSleep for 10s."
			time.sleep(CHECKING_INTERVAL)

	def getParticipantID(self, dialogueID):
		print "\nGet participantID from DGEP.\nThe result:\n"
		MOVES_URL = "http://www.arg.dundee.ac.uk:8080/dialogue/%s/join/%s/%s" % (dialogueID, "Resp", "ID")

		result = json.loads(urllib.urlopen(MOVES_URL).read())
		print result
		return str(result["participantID"])

	def performMove(self, dialogueID, participantID):
		# get knowledge base
		global KB_ALL
		global KB_CHAIN
		global KB_SINGLE
		# get available moves
		moves =  self.getMoves(dialogueID, participantID)
		# get last move type
		lastMoveType = self.getLastMoveType(dialogueID)

		print "Performing move."

		# get FS
		FS = self.getCSByKeyWord(dialogueID, "FS")
		# get CS Init
		CSInit = self.getCSByKeyWord(dialogueID, "Init")
		# get CS Resp
		CSResp = self.getCSByKeyWord(dialogueID, "Resp")

		# init move data variable
		data = {}
		data["speaker"] = participantID

		if lastMoveType == "Question":
			# fake data
			p = "CP is wrong"
			NOT_P = ""
			if p[0] == "!":
				NOT_P = p[1:-1]
			else:
				NOT_P = "!"+p

			if p in KB_ALL :
				data["reply"] = {
					"p": p
				}
				self.sendMove(dialogueID, data, "Statement")
			elif "!"+p in KB_ALL :
				data["reply"] = {
					"p": NOT_P
				}
				self.sendMove(dialogueID, data, "Statement")
			else:
				data["reply"] = {
					"p": p
				}
				self.sendMove(dialogueID, data, "Withdraw")

		if lastMoveType == "Challenge":
			# fake data
			p = "CP is wrong"
			NOT_P = ""
			if p[0] == "!":
				NOT_P = p[1:-1]
			else:
				NOT_P = "!"+p

			if p in CSResp or p in KB_ALL:
				supports = [i for i in KB_CHAIN if p in i]
				if not supports:
					data["reply"] = {
						"p": p
					}
					self.sendMove(dialogueID, data, "Withdraw")

				if len(supports) == 1:
					if supports[0].index(p) == len(supports[0]) - 1:
						data["reply"] = {
							"p": p
						}
						self.sendMove(dialogueID, data, "Withdraw")
					else:
						data["reply"] = {
							"p": p,
							"q": supports[0][supports[0].index(p)+1]
						}
						self.sendMove(dialogueID, data, "Defence")

				if len(supports) > 1:
					selectedSupport = []
					supportsForSelectedSupportCountMax = 0
					for support in supports:
						# ">=" to make sure at least one support is sellected
						if len(support) - 1 - support.index(p) >= supportsForSelectedSupportCountMax:
							selectedSupport = support
					if selectedSupport.index(p) == len(selectedSupport) - 1:
						data["reply"] = {
							"p": p
						}
						self.sendMove(dialogueID, data, "Withdraw")
					else:
						data["reply"] = {
							"p": p,
							"q": selectedSupport[selectedSupport.index(p)+1]
						}
						self.sendMove(dialogueID, data, "Defence")

			elif NOT_P in KB_ALL:
				data["reply"] = {
					"p": NOT_P
				}
				self.sendMove(dialogueID, data, "Statement")
			else:
				data["reply"] = {
					"p": p
				}
				self.sendMove(dialogueID, data, "Withdraw")

		if lastMoveType == "Resolve":
			# fake data
			p = "CP is wrong"
			NOT_P = ""
			if p[0] == "!":
				NOT_P = p[1:-1]
			else:
				NOT_P = "!"+p

			# the agent is set to be the Resp player
			if p in FS or NOT_P in FS:
				data["reply"] = {
					"p": FS[0]
				}
				self.sendMove(dialogueID, data, "Withdraw")
			elif p not in KB_ALL and NOT_P not in KB_ALL:
				if random.choice([True, False]):
					data["reply"] = {
						"p": p
					}
				else:
					data["reply"] = {
						"p": NOT_P
					}
				self.sendMove(dialogueID, data, "Withdraw")
			elif p in KB_ALL:
				data["reply"] = {
					"p": NOT_P
				}
				self.sendMove(dialogueID, data, "Withdraw")
			else:
				# NOT_P in KB_ALL
				data["reply"] = {
					"p": p
				}
				self.sendMove(dialogueID, data, "Withdraw")

		if lastMoveType == "StartOfGame":
			pass

		if lastMoveType == "Withdraw":
			# fake data
			p = "CP is wrong"
			q = "!CP is wrong"
			Resolution = [i for i in moves if i["MoveID"] == "Resolve"]
			if Resolution:
				data["reply"] = {
					"p": p,
					"q": q
				}
				self.sendMove(dialogueID, data, "Resolve")
			else:
				# select a random move
				randomMove = random.choice(moves)
				if randomMove["moveID"] == "Statement":
					data["reply"] = {
						"p": random.choice([i for i in KB_ALL if i not in CSResp])
					}
					self.sendMove(dialogueID, data, "Statement")
				elif randomMove["moveID"] == "Question":
					data["reply"] = {
						"p": random.choice([i for i in KB_ALL if i not in CSResp])
					}
					self.sendMove(dialogueID, data, "Question")
				else:
					data['reply'] = randomMove["reply"]
					self.sendMove(dialogueID, data, randomMove["moveID"])


		if lastMoveType == "Statement":
			# fake data
			p = "CP is wrong"
			NOT_P = ""
			if p[0] == "!":
				NOT_P = p[1:-1]
			else:
				NOT_P = "!"+p
			Resolution = [i for i in moves if i["MoveID"] == "Resolve"]
			if Resolution:
				data["reply"] = {
					"p": p,
					"q": q
				}
				self.sendMove(dialogueID, data, "Resolve")
			elif NOT_P in KB_ALL:
				data["reply"] = {
					"p": NOT_P
				}
				self.sendMove(dialogueID, data, "Statement")
			elif p not in KB_ALL:
				data["reply"] = {
					"p": p
				}
				self.sendMove(dialogueID, data, "Challenge")
			else:
				# select a random move
				randomMove = random.choice(moves)
				if randomMove["moveID"] == "Statement":
					data["reply"] = {
						"p": random.choice([i for i in KB_ALL if i not in CSResp])
					}
					self.sendMove(dialogueID, data, "Statement")
				elif randomMove["moveID"] == "Question":
					data["reply"] = {
						"p": random.choice([i for i in KB_ALL if i not in CSResp])
					}
					self.sendMove(dialogueID, data, "Question")
				else:
					data['reply'] = randomMove["reply"]
					self.sendMove(dialogueID, data, randomMove["moveID"])

	def sendMove(self, dialogueID, data, interactionID):
		print "\nMove Data:"
		print data
		print "\nInteractionID: "+interactionID
		# url = "http://arg.dundee.ac.uk:8080/dialogue/%s/interaction/%s" % (dialogueID, interactionID)
		# # url = "http://127.0.0.1:8811/StartAgent" for test
		# encodedData = urllib.urlencode(data)
		# req = urllib2.Request(url, encodedData)
		# response = urllib2.urlopen(req)
		# content = response.read()
		# print content
		pass

	def getLastMoveType(self, dialogueID):
		print "Get the type of the last move from DGEP."
		#get the type of last move from DGEP
		HISTORY_URL = "http://www.arg.dundee.ac.uk:8080/dialogue/%s/history" % (dialogueID)

		# result = json.loads(urllib.urlopen(HISTORY_URL).read())
		result = {
			"history": [
				{
					"player": 1378,
					"move": "Question",
					"reply": {
						"p": "Britain should disarm",
						"q": "foo"
					}
				}
			]
		}

		history = result["history"]

		if len(history) == 0:
			return "StartOfGame"
		else:
			print "\nThe move type is: "+history[-1]["move"]
			return history[-1]["move"]

	def getCSByKeyWord(self, dialogueID, which):
		#get commitment store content from DGEP
		STORE_URL = "http://www.arg.dundee.ac.uk:8080/dialogue/%s/stores" % (dialogueID)

		# result = json.loads(urllib.urlopen(STORE_URL).read())
		result = {
			"Stores": [
				{
					"Owner": "Init",
					"Name": "FS",
					"Contents": [
						"Britain should disarm"
					]
				},
				{
					"Owner": "Init",
					"Name": "CS",
					"Contents": [
						"Britain should disarm"
					]
				},
				{
					"Owner": "Resp",
					"Name": "CS",
					"Contents": [
						"Britain should disarm"
					]
				}
			]
		}

		# get the target CS
		store = {}
		if which == "FS":
			store = [i for i in result["Stores"] if i["Name"] == "FS"][0]
		elif which == "Init":
			store = [i for i in result["Stores"] if i["Name"] == "CS" and i["Owner"] == "Init"][0]
		elif which == "Resp":
			store = [i for i in result["Stores"] if i["Name"] == "CS" and i["Owner"] == "Resp"][0]

		return store["Contents"]

	def getMoves(self, dialogueID, participantID):
		print "\nGet legal moves."
		MOVES_URL = "http://www.arg.dundee.ac.uk:8080/dialogue/%s/moves" % (dialogueID)

		result = json.loads(urllib.urlopen(MOVES_URL).read())
		print "\nAvailable moves:\n"
		print result
		# print result[participantID]
		# test data
		return result["26"]

	def getGameStatus(self, dialogueID):
		print "\nCheck game status."
		return True

class TestHandler(tornado.web.RequestHandler):
	def get(self):
		# p = self.get_argument('p', None)
		#
		# if not p:
		# 	return "Parameter Missing: p"
		# coll = self.application.db.record
		#
		# if( not coll.find_one({"p": p}) ):
		# 	new_one = {"p": p, "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()) ), "result": None}
		# 	coll.insert(new_one)
		# record = coll.find_one({"p": p})
		# while( record.result == None ):
		# 	time.sleep(5)
		# 	record = coll.find_one({"p": p})
		# # would dgep wait for the return?
		#
		# return record.result
		pass

def post(self):
		# data for commitment store contents
		# p for the statement that the player withdraws or challenges
		data = self.get_argument("data", None)
		p = self.get_argument("p", None)

		if not data:
			return "Parameter Missing: data"

		# ss for simple_statements
		# tfs for truth-functional statements
		# IC for immediate consequences
		ss = []
		tfs = []
		IC = []
		for item in data:
			if type(item) == types.StringType:
				statements.append(item)
			else:
				logic_statements.append(item)

		for s in ss:
			l = len(s)
			for tf in tfs:
				if tf[2:2+l] == ss:
					IC.append(tf[2+l+3:-2])

		if p in IC:
			self.write('{"result":"True"}')
		else:
			self.write('{"result":"False"}')

class Resolution2Handler(tornado.web.RequestHandler):
	def get(self):
		pass

	def post(self):
		# data for commitment store contents
		# p for the statement that the player withdraws or challenges
		data = self.get_argument("data", None)
		p = self.get_argument("p", None)

		if not data:
			return "Parameter Missing: data"

		# ss for simple_statements
		# tfs for truth-functional statements
		# IC for immediate consequences
		ss = []
		tfs = []
		IC = []
		for item in data:
			if type(item) == types.StringType:
				statements.append(item)
			else:
				logic_statements.append(item)

		# >>> a = "aaa"
		# >>> b = "bbb"
		# >>> c = "{"aaa","bbb"}"
		# >>> c[2:2+len(a)]
		# 'aaa'
		# >>> c[2:2+len(a)] == a
		# True
		# >>> c[2+len(a)+3:-2]
		# 'bbb'
		for s in ss:
			l = len(s)
			for tf in tfs:
				if tf[2:2+l] == ss:
					IC.append(tf[2+l+3:-2])

		if p in IC:
			# return "resolve p and !p"
			# return True
			LENGTH_OF_P = len(p)
			relatedConditionals = [i for i in tfs if p == i[2+LENGTH_OF_P+3:-2]]
			antecedent = relatedConditionals[0][2:2+LENGTH_OF_P]
			consequent = relatedConditionals[0][2+LENGTH_OF_P+3:-2]
			self.write('{"result":["'+antecedent+'","'+consequent+'"]}')
		else:
			# return "none"
			# return False
			self.write('{"result":[]}')

class Termination2Handler(tornado.web.RequestHandler):
	def get(self):
		pass

	def post(self):
		CS = json.loads(self.get_argument("CS", ""))
		FS_CS = json.loads(self.get_argument("FS_CS", ""))

		if FS_CS["Contents"][0] in CS["Contents"]:
			self.write('{"result":"True"}')
		else:
			self.write('{"result":"False"}')


def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
