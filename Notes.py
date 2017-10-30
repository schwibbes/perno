import sublime
import sublime_plugin
import re
import sys
import hashlib

sys.path.append("/usr/local/lib/python2.7/site-packages")
from bson.objectid import ObjectId
from pymongo import MongoClient
 
REP_START = '[['
REP_END = ']]'

SCOPE_TAG = 'entity.name.tag.topic.notes'
SCOPE_ID = 'comment.id.notes'
SCOPE_QUERY = 'keyword.query'
SCOPE_FULL = 'source.block.note'
SCOPE_COMPACT = 'source.notes.compact'
SCOPE_REPORT = 'comment.block.report.notes'

SCOPES = [
	SCOPE_TAG,
	SCOPE_QUERY,
	SCOPE_COMPACT,
	SCOPE_FULL,
	SCOPE_REPORT]

settings = sublime.load_settings("Notes.sublime-settings")


class ClearReportCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		self.clear_views(edit)

	def clear_views(self, edit):
		regs = self.view.find_by_selector(SCOPE_REPORT)
		for reg in regs:
			self.view.erase(edit, reg)

class DeleteTicketCommand(sublime_plugin.TextCommand):
	client = MongoClient(settings.get("mongo_uri", "mongodb://192.168.99.100:27017"))
	db = client[settings.get("mongo_db", "mynotes")]

	def run(self,edit):
		self.delete(edit)

	def delete(self, edit):
		for s in self.view.sel():
			scope_and_score = [ (scope, self.view.score_selector(s.end(), scope)) for scope in SCOPES ]
			matched_scope = max(scope_and_score,key=lambda item:item[1])[0]
			text = self.view.substr(self.expand_to_scope(matched_scope, s))
			search_res = re.search('.*~([0-9a-f]{24})', text)
			if search_res:
				self.db.notes.delete_one({'_id': ObjectId(search_res.group(1)) })
				self.view.erase(edit, self.expand_to_scope(matched_scope, s))
				self.view.set_status("savestate", "deleted ticket: " + search_res.group(1))
				sublime.set_timeout(lambda: self.view.erase_status("savestate"), 2000)
				
	def expand_to_scope(self, scope, initial_selection):
		for reg_with_scope in self.view.find_by_selector(scope):
			if reg_with_scope.contains(initial_selection):
				return reg_with_scope



class SubmitCommand(sublime_plugin.TextCommand):

	client = MongoClient(settings.get("mongo_uri", "mongodb://192.168.99.100:27017"))
	db = client[settings.get("mongo_db", "mynotes")]


	def run(self, edit):
		for s in self.view.sel():
			scope_and_score = [ (scope, self.view.score_selector(s.end(), scope)) for scope in SCOPES ]
			matched_scope = max(scope_and_score,key=lambda item:item[1])
			if matched_scope[1] == 0:
				self.status_msg("nothing to do at point")
			else:
				self.run_action(edit, matched_scope[0], self.expand_to_scope(matched_scope[0], s))
			
	
	def expand_to_scope(self, scope, initial_selection):
		for reg_with_scope in self.view.find_by_selector(scope):
			if reg_with_scope.contains(initial_selection):
				return reg_with_scope

	def sub_scope(self, region, scope):
		return [reg for reg in self.view.find_by_selector(scope) if region.contains(reg)]
	
	def save(self, region):

		ticket = {
			"head": self.view.substr(region).splitlines()[0],
			"topics": [self.view.substr(x) for x in self.sub_scope(region, SCOPE_TAG)]
		}

		id_fields = self.sub_scope(region, SCOPE_ID)
		if len(id_fields) == 1:
			ticket['_id'] = ObjectId(self.id_from_region(id_fields[0]))
			self.db.notes.replace_one({'_id': ticket['_id']}, ticket)
			self.status_msg("ticket updated")
		else:
			self.db.notes.insert_one(ticket)
			self.status_msg("ticket created")

	def id_from_region(self, region):
		return self.view.substr(region).replace('~', '')

	def status_msg(self, msg):
		self.view.set_status("savestate", str(msg))
		sublime.set_timeout(lambda: self.view.erase_status("savestate"), 2000)
	
	def show_details(self,edit, region):
		id_fields = self.sub_scope(region, SCOPE_ID)
		if len(id_fields) == 1:
			ticket = self.db.notes.find_one({'_id': ObjectId(self.id_from_region(id_fields[0])) })
			self.print_ticket(edit,ticket)
			#self.view.add_phantom("test", self.view.sel()[0], "<a href='google.de'>bla</a>", sublime.LAYOUT_INLINE)

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
		as_text = (
			str(ticket['head']) + '\n'
			+ "  ~" + str(ticket['_id']) + '\n'
			+ '\n'.join(["  " + t for t in ticket['topics']])
		)

		print(ticket['topics'])
		as_text += ("\n  " 
			+ "sha1:" + hashlib.sha1(as_text.encode("utf-8")).hexdigest()
			+ '\n' + '-')
		
		current_line = self.view.line(self.view.sel()[0])
		self.view.replace(
			edit, 
			current_line,
			as_text)

	def run_action(self, edit, scope, region):
		if scope == SCOPE_QUERY:
			#TODO: parse query
			cursor = self.db.notes.find()
			self.print_headline(edit, cursor)
		elif scope == SCOPE_FULL:
			self.save(region)
		elif scope == SCOPE_COMPACT:
			self.show_details(edit, region)
		elif scope == SCOPE_TAG:
			cursor = self.db.notes.find({'topics': self.view.substr(region) })
			self.print_headline(edit,cursor)
		elif scope == SCOPE_REPORT:
			print("save all")

	def cleanup(self):
		self.client.close() 
