#!/bin/env python3
import sys, os
from modules.jira_api import JiraAPI
from process_input import get_arguments

args  = get_arguments()
sysArgs = sys.argv
api = JiraAPI(args, sysArgs[1], sysArgs[2])
ticket = api.check_duplicate()
if ticket: 
	print(">> Not creating duplicate ticket!")
else:
	api.create_issue()