import sublime
import sublime_plugin
import re
import sys
import hashlib

sys.path.append("/usr/local/lib/python2.7/site-packages")
from bson.objectid import ObjectId
from pymongo import MongoClient
 
pattern = re.compile("^([A-Z][0-9]+)+$")
REP_START = '[['
REP_END = ']]'

SCOPE_TAG = 'entity.name.tag.topic.notes'
SCOPE_QUERY = 'keyword.query'
SCOPE_FULL = 'source.block.note'
SCOPE_COMPACT = 'source.notes.compact'
SCOPE_REPORT = 'comment.block.report.notes'

settings = sublime.load_settings("Notes.sublime-settings")


class ClearReportCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		self.clear_views(edit)

	def clear_views(self, edit):
		regs = self.view.find_by_selector(SCOPE_REPORT)
		for reg in regs:
			self.view.erase(edit, reg)


class SubmitCommand(sublime_plugin.TextCommand):

	client = MongoClient(settings.get("mongo_uri", "mongodb://192.168.99.100:27017"))
	db = client[settings.get("mongo_db", "mynotes")]

	scopes = [
		SCOPE_TAG,
		SCOPE_QUERY,
		SCOPE_COMPACT,
		SCOPE_FULL]

	
	def run(self, edit):
		for s in self.view.sel():
			res = [ (scope, self.view.score_selector(s.end(), scope)) for scope in self.scopes ]
			print(res)
			max(res,key=lambda item:item[1])[0]
		

	
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
			self.view.set_status("savestate", "updated existing note")
			self.db.notes.replace_one({'_id': ticket['_id']}, ticket)
		else:
			self.db.notes.insert_one(ticket)
			self.view.set_status("savestate", "saved new note")

		sublime.set_timeout(
			lambda: self.view.erase_status("savestate"), 2000)

	def save(self, text):
		ticket = self.text2ticket(text)
		

	def print_headline(self, edit, cursor):
		as_text = ""
		for doc in cursor:
			as_text += str(doc['head']) + " ~" + str(doc['_id']) + "\n"
		
		blob = self.view.expand_by_class(self.view.sel()[0], sublime.CLASS_EMPTY_LINE)
		self.view.insert(edit, 
			blob.end() , 
			REP_START + "\n" 
			+ as_text
			+ "sha1:" + hashlib.sha1(as_text.encode("utf-8")).hexdigest()
			+ "\n" + REP_END
			+ "\n")

	def print_ticket(self, edit, ticket):
		as_text = '\n'.join([
			str(ticket['head']),
			"  ~" + str(ticket['_id']),
			'  \n  '.join(ticket['topics']),
			'\n  '.join(ticket['ts']),
			'\n  '.join(ticket['body'])
		])
		
		as_text += "\n  " + "sha1:" + hashlib.sha1(as_text.encode("utf-8")).hexdigest()
		
		current_line = self.view.line(self.view.sel()[0])
		self.view.replace(
			edit, 
			current_line,
			as_text)

	def select(self, text, edit):
		text = text.strip()
		if text.startswith('NOTE:'):
			search_res = re.search('.*~([0-9a-f]{24})', text)
			if search_res:
				ticket = self.db.notes.find_one({'_id': ObjectId(search_res.group(1)) })
				self.print_ticket(edit,ticket)
			#self.view.add_phantom("test", self.view.sel()[0], "<a href='google.de'>bla</a>", sublime.LAYOUT_INLINE)
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
