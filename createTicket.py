#!/bin/env python3
import sys, os, json
from modules.jira_api import JiraAPI
from process_input import get_arguments

def modify_json(ifile):
	f = open(ifile)
	d = json.load(f)
	f.close()
	url = d['emailBody']
	d.update({'emailBody': url%(sys.argv[3])})
	f = open(ifile, 'w')
	json.dump(d, f, indent=2)
	f.close()
	return d

ifile = 'envs.json'
if len(sys.argv)==4: modify_json(ifile)
f = open(ifile)
args = json.load(f)
api = JiraAPI(args, sys.argv[1], sys.argv[2])
ticket = api.check_duplicate()
if ticket: 
	print(">> Not creating duplicate ticket!")
else:
	api.create_issue()
	key = api.get_key()
	print(">> New ticket created with number ", key)