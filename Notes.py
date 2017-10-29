import sublime
import sublime_plugin
import re
import sys
import hashlib

sys.path.append("/usr/local/lib/python2.7/site-packages")
from bson.objectid import ObjectId
from pymongo import MongoClient
 
pattern = re.compile("^([A-Z][0-9]+)+$")

class SubmitCommand(sublime_plugin.TextCommand):

	client = MongoClient("mongodb://192.168.99.100:27017")
	db = client["test"]

	def run(self, edit):

		s = self.view.sel()
		for x in s:
			print("{:d}, {:d}".format(x.begin() , x.end()))

		strats = [
			lambda: self.view.substr(s[0]),
			lambda: self.view.substr(self.view.word(s[0])),
			lambda: self.view.substr(self.view.line(s[0])),
			lambda: self.view.substr(self.view.expand_by_class(s[0], sublime.CLASS_EMPTY_LINE)),
			]
		
		for strat in strats:
			if not self.select(strat(), edit):
				print("strat worked: " + str(strat().count('\n')))
				break
			else:
				print("retry after strat: " + strat())

	
	def text2ticket(self,text):
		lines = text.splitlines()
		_id = next(iter([x for x in lines if x.startswith("~")] or []), None)
		ticket = {
			"head": lines[0],
			"topics": [x for x in lines if x.startswith("#")],
			"ts": [x for x in lines if x.startswith("@")],
			"body": [x for x in lines[1:] if not x.startswith("@") and not x.startswith("#")]
		}
		if _id is not None:
			ticket['_id'] = ObjectId(_id[1:])
			print("replace")
			self.db.notes.replace_one({'_id': ticket['_id']}, ticket)
		else:
			self.db.notes.insert_one(ticket)
			print("insert")

	def clearDb():
		pass

	def save(self, text):
		ticket = self.text2ticket(text)
		

	def print_headline(self, edit, cursor):
		as_text = ""
		for doc in cursor:
			as_text += "*" + str(doc['head']) + " ~" + str(doc['_id']) + "\n"
		
		blob = self.view.expand_by_class(self.view.sel()[0], sublime.CLASS_EMPTY_LINE)
		self.view.insert(edit, 
			blob.end() , 
			"----------->\n" 
			+ as_text
			+ "<-----------"
			+ hashlib.sha1(as_text.encode("utf-8")).hexdigest()
			+ "\n")

	def print_ticket(self, edit, ticket):
		as_text = '\n'.join([
			"*" + str(ticket['head']),
			"~" + str(ticket['_id']),
			'\n'.join(ticket['topics']),
			'\n'.join(ticket['ts']),
			'\n'.join(ticket['body'])
		])
		
		as_text += "\n" + "sha1:" + hashlib.sha1(as_text.encode("utf-8")).hexdigest()
		
		current_line = self.view.line(self.view.sel()[0])
		self.view.replace(
			edit, 
			current_line,
			as_text)

	def select(self, text, edit):
		text = text.strip()
		if text.startswith('*NOTE:'):
			search_res = re.search('.*~([0-9a-f]{24})', text)
			if search_res:
				ticket = self.db.notes.find_one({'_id': ObjectId(search_res.group(1)) })
				self.print_ticket(edit,ticket)
		elif text.startswith('NOTE:'):
			self.save(text)
		elif text.startswith("?all"):
			cursor = self.db.notes.find()
			self.print_headline(edit, cursor)
		elif text.startswith("?today"):
			cursor = self.db.notes.find()
			self.print_headline(edit,cursor)
		elif text.startswith("#"):
			cursor = self.db.notes.find({'topics': text })
			self.print_headline(edit,cursor)
		else:
			return True

	def cleanup(self):
		self.client.close() 
