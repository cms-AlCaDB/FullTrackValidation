#!/bin/env python3
import sys, os, json
from process_input import *

def modify_json(ifile, url):
	"""Modifying json for putting Jenkins build URL inside email text"""
	if os.path.exists(ifile):
		f = open(ifile)
	else:
		raise FileNotFoundError('Error: Please create a file %s first'% ifile)
	d = json.load(f)
	email = d['emailBody']
	if not '%s' in email: 
		print('**Warning: No place to put URL in email text. Skipping!!')
	else:
		d.update({'emailBody': email%(url)})
	f.close()
	return d

if __name__ == '__main__':
	from modules.jira_api import JiraAPI
	get_user()
	args = modify_json('envs.json', parsedArgs.url)
	api = JiraAPI(args, parsedArgs.user, parsedArgs.password)
	ticket = api.check_duplicate()
	if ticket: 
		print(">> Not creating duplicate ticket!")
	else:
		api.create_issue()
		key = api.get_key()
		print(">> New ticket created with number ", key)
