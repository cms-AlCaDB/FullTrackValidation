#!/bin/env python3
import sys, os, json
from modules.jira_api import JiraAPI
from process_input import get_arguments


ifile = open('envs.json')
args = json.load(ifile)
sysArgs = sys.argv
api = JiraAPI(args, sysArgs[1], sysArgs[2])
ticket = api.check_duplicate()
if ticket: 
	print(">> Not creating duplicate ticket!")
else:
	api.create_issue()
	key = api.get_key()
	print(">> New ticket created with number ", key)