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
import json

define("port", default=8811, help="run on the given port", type=int)

global DIALOGUE_ID
global PARTICIPANT_ID
global KB_ALL
global KB_CHAIN
global KB_SINGLE
DIALOGUE_ID = 6
PARTICIPANT_ID = 26
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
	"killing of human life is wrong"",
	"CP kills people",
	"People can't decide who to kill",
	"The state decide who to kill",
	"CP is acceptable",
]
KB_CHAIN = [
	[
		[
			"!CP is wrong",
			"There are too many repeat crimes after murderers are released",
			"the sentences are not siff enough"
		],
		[
			0,
			0,
			0
		]
	],
	[
		[
			"!it against the law to kill a person",
			"It is against the law for a citizen to kill another citizen and it is legal for the state to kill a citizen after the due process of law"
		],
		[
			0,
			0
		]
	],
	[
		[
			"CP would decrease violent crime",
			"CP would act as a deterrent to carrying weapons"
		],
		[
			0,
			0
		]
	],
	[
		[
			"!the state just one person or body of people i.e. a judge",
			"the people are merely representatives of the state"
		],
		[
			0,
			0
		]
	]
]
KB_SINGLE = [
	[
		"killing of human life is wrong",
		0
	],
	[
		"CP kills people",
		0
	],
	[
		"People can't decide who to kill",
		0
	],
	[
		"The state decide who to kill",
		0
	],
	[
		"CP is acceptable",
		0
	]
]

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
			(r"/PerformMove", PerformMoveHandler),
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
			global DIALOGUE_ID
			global PARTICIPANT_ID
			DIALOGUE_ID = dialogueID
			PARTICIPANT_ID = self.getParticipantID(dialogueID)
			print DIALOGUE_ID
			print PARTICIPANT_ID

	def getParticipantID(self, dialogueID):
		MOVES_URL = "http://www.arg.dundee.ac.uk:8080/dialogue/%s/join/%s/%s" % (dialogueID, "Resp", "ID")

		result = json.loads(urllib.urlopen(MOVES_URL).read())
		print result
		return str(result["participantID"])

class PerformMoveHandler(tornado.web.RequestHandler):
	def get(self):
		global DIALOGUE_ID
		global PARTICIPANT_ID
		# get knowledge base
		global KB_ALL
		global KB_CHAIN
		global KB_SINGLE
		# get available moves
		moves =  self.getMoves()
		# get last move type
		lastMoveType = self.getLastMoveType()

		# init move data variable
		data = {}

		if lastMoveType == "question":
			# fake data
			p = "CP is wrong"

			if p in KB_ALL :
				data["reply"] = {
					"p": p
				}
			elif "!"+p in KB_ALL :
				data["reply"] = {
					"p": !p
				}
			data["speaker"] = PARTICIPANT_ID
			self.sendMove(data, "Statement")

		if lastMoveType == "challenge":
			pass

		if lastMoveType == "resolve":
			pass

		if lastMoveType == "start_of_game":
			pass

		if lastMoveType == "withdraw":
			pass

		if lastMoveType == "statement":
			pass

	def sendMove(self, data, interactionID):
        import urllib2
		url = "http://arg.dundee.ac.uk:8080/dialogue/%s/interaction/%s" % (%DIALOGUE_ID, interactionID)
		encodedData = urllib.urlencode(data)
		f = urllib2.urlopen(url, encodedData)
		content = f.read()
		print content

	def getLastMoveType(self):
		#get the type of last move from DGEP
		return "question"

	def getMoves(self):
		global DIALOGUE_ID
		global PARTICIPANT_ID
		MOVES_URL = "http://www.arg.dundee.ac.uk:8080/dialogue/%s/moves" % (DIALOGUE_ID)

		result = json.loads(urllib.urlopen(MOVES_URL).read())
		print PARTICIPANT_ID
		print type(PARTICIPANT_ID)
		# print result[PARTICIPANT_ID]
		return result["26"]



class TestHandler(tornado.web.RequestHandler):
	def get(self):
		p = self.get_argument('p', None)

		if not p:
			return "Parameter Missing: p"
		coll = self.application.db.record

		if( not coll.find_one({"p": p}) ):
			new_one = {"p": p, "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()) ), "result": None}
			coll.insert(new_one)
		record = coll.find_one({"p": p})
		while( record.result == None ):
			time.sleep(5)
			record = coll.find_one({"p": p})
		# would dgep wait for the return?

		return record.result

class JudgeHandler(tornado.web.RequestHandler):
	def get(self):
		msg = self.get_argument("msg", "")

		coll = self.application.db.record
		pending_records = coll.find({"result": None})

		self.render("judge.html",
			pending_records = pending_records,
			msg = msg,
			)

	def post(self):
		result = self.get_argument('result', None)
		p = self.get_argument('p', None)

		if not p or not result:
			return "Parameters Missing: p, result"

		coll = self.application.db.record
		record = coll.find_one({"p": p})
		if( not record ):
			return "Statement \""+p+"\" doesn't exist in the DB."
		record.result = result
		record.save()

		self.redirect("/judge?msg=success")

class PCSHandler(tornado.web.RequestHandler):
	def get(self):
		pass

	def post(self):
		data = self.get_argument("data", None)

		if not data:
			return "Parameter Missing: data"

		# ss for simple_statements
		# tfs for truth-functional statements
		# PCS for potential commitment store
		ss = []
		tfs = []
		PCS = []
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
					if tf[2+l+3:-2] not in ss:
						PCS.append(tf[2+l+3:-2])

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
			return True
		else:
			# return "none"
			return False

class InitKBHandler(tornado.web.RequestHandler):
	def get(self):
		import sae.const
		import MySQLdb
		import copy

		db=MySQLdb.connect(host=sae.const.MYSQL_HOST,port=int(sae.const.MYSQL_PORT ),user=sae.const.MYSQL_USER ,passwd=sae.const.MYSQL_PASS ,db=sae.const.MYSQL_DB)
		cursor = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
		sql = "SELECT * FROM knowledge_base WHERE premises != ''"
		cursor.execute(sql)

		result = cursor.fetchall()

		init_chains = []
		for row in result:
			premises = row['premises'].strip().split(',')
			for premise in premises:
				init_chains.append([int(premise),row['id']])

		statement_chains = []
		statement_chains = InitKBHandler.getCleanedList(self, InitKBHandler.solve(self, init_chains, init_chains))

		# now we've got statement_chains: [[7,6,1],[2,1], [2,5,4,3]]

		sql = "SELECT * FROM knowledge_base WHERE premises = '' "
		cursor.execute(sql)

		isolated_statements = []
		result = cursor.fetchall()

		for row in result:
			count = 0
			for init_chain in init_chains:
				if row['id'] in init_chain:
					count += 1
			if count is 0:
				isolated_statements.append(row['id'])

		# now we've got isolated_statements: [8,9]

		statement_chains_with_status = []
		isolated_statements_with_status = []

		for statement_chain in statement_chains:
			statement_chains_with_status.append([statement_chain, ([0])*len(statement_chain)])
		# now we've got statement_chains_with_status: [[[7,6,1],[0,0,0]],[[2,1],[0,0]], [[2,5,4,3],[0,0,0,0]]]


		isolated_statements_with_status = [isolated_statements, ([0])*len(isolated_statements)]

		#self.write("%s\n%s"%statement_chains_with_status,isolated_statements_with_status)
		for row in statement_chains_with_status:
			self.write("%s\n"%row)
		self.write("%s\n"%isolated_statements_with_status)
		#for row in isolated_statements:
		#   self.write("%s\n"%row)
		# now we've got isolated_statements_with_status: [[8,9],[0,0]]

	@staticmethod
	def getAllDistinctConsequence(self, List):
		result = []
		for item in List:
			if item[-1] not in result:
				result.append(item[-1])
		return result

	@staticmethod
	def getAllListEndWithThisConsequence(self, List, Consequence):
		result = []
		for item in List:
			if item[-1] is Consequence:
				result.append(item)
		return result

	@staticmethod
	def getCleanedList(self, List):
		import copy
		List_copy = copy.deepcopy(List)
		for one in List_copy:
			for two in List_copy:
				if one != two and one == two[len(two)-len(one):]:
					if one in List:
						List.remove(one)
		return List

	@staticmethod
	def solve(self, init_chains, chains_to_deal_with):
		print "to_deal:",init_chains
		import copy
		current_chains = []
		chains_to_remove = []

		no_more_new_chain = True
		distinct_consequences = InitKBHandler.getAllDistinctConsequence(self, chains_to_deal_with)
		for distinct_consequence in distinct_consequences:
			Lists = InitKBHandler.getAllListEndWithThisConsequence(self, chains_to_deal_with, distinct_consequence)
			for List in Lists:
				#prohibit cycle
				if List[0] == List[-1]:
					continue
				not_connected_with_others = True
				for init_chain in init_chains:
					if init_chain[0] == distinct_consequence:
						not_connected_with_others = False
						no_more_new_chain = False
						List_copy = copy.deepcopy(List)
						List_copy.extend(init_chain[1:])
						current_chains.append(List_copy)
						chains_to_remove.append(List)
						chains_to_remove.append(init_chain)
				if not_connected_with_others:
					current_chains.append(List)
		print "to_remove",chains_to_remove
		print "current",current_chains
		for chain in chains_to_remove:
			if chain in current_chains:
				current_chains.remove(chain)
		print "cleaned_current",current_chains
		if no_more_new_chain:
			return current_chains
		else:
			return InitKBHandler.solve(self, init_chains, current_chains)

def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
