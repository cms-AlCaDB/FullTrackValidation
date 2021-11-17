#!/bin/env python3
#
# Author : Pritam Kalbhor (physics.pritam@gmail.com)
#

import glob, os, sys, json, ast
import runregistry, subprocess
from datetime import datetime
from collections import namedtuple
from modules.jira_api import JiraAPI

from argparse import ArgumentParser
from getpass import getpass, getuser
parser = ArgumentParser(description="Options for batch run")
parser.add_argument('-u', '--user', type=str, dest='user', help='user name')
group = parser.add_mutually_exclusive_group()
group.add_argument('-p', '--pwstdin', type=str, dest='password')
group.add_argument('--pat', action="store_true", help='use PAT')
parser.add_argument('--url', type=str, help='Put url for Jenkins build')
parsedArgs = parser.parse_known_args()[0]

def get_input():
	"""Retrieve most recently edited input template. 
	   Commit time will be recorded.
	   Avoid commiting more than one templates"""
	files = glob.glob("Validations/*")
	dlist = list()
	for f in files: dlist.append(os.path.getmtime(f))
	if len(set(dlist)) > 2: 
		files.sort(key=os.path.getmtime)
		return files[-1]
	else:
		File = namedtuple("File", ["path", "time"])
		commit_dates = list()
		for f in files:
			raw_time = subprocess.getoutput("git log -n 1 --pretty=format:%cd {}".format(f))
			Time = datetime.strptime(raw_time, '%a %b %d %H:%M:%S %Y %z').strftime('%Y-%m-%d %H:%M:%S')
			pair = File(path=f, time=Time)
			commit_dates.append(pair)
		commit_dates.sort(key=lambda file: file.time)
		return commit_dates[-1].path

def get_run(run_number):
	"""Returns run configuration in json format. Input param: run number"""
	# import urllib3; urllib3.disable_warnings()
	run = runregistry.get_run(run_number=int(run_number))
	return run

def get_arguments():
	"""Returns input arguments after processing input template in dictionary format"""
	print(">> We will be processing lastly edited template: ", get_input())
	file="_NewValidation.txt"

	# Ignore lines starting with hash #. Delete empty lines
	os.system("""sed '/^#.*$/d' "%s" > %s""" %(get_input(), file))
	os.system("""sed -i '/^[[:space:]]*$/d' %s""" %(file))
	
	iFile = open(file, 'r')
	args = dict()
	for line in iFile:
		args[line.split(':')[0].strip()] = ":".join(line.split(':')[1:]).strip()
	args['Labels'] = [v.strip() for v in args['Labels'].split(',')]
	args['run_number'] = args['Run'].split(":")[0].strip("{").strip("'")
	week = [v for v in args['Labels'] if 'Week' in v]
	year = [v for v in args['Labels'] if '202' in v]
	args['Week']  = "{}".format(week[0])
	args['Year']  = "{}".format(year[0])
	args['Label'] = "{}".format("_".join(args['Labels']))
	iFile.close()
	return args

def get_mappings():
	mappings = dict()
	mappings['TargetGT_HLT'] 	 = 'newgt'
	mappings['TargetGT_EXPRESS'] = 'newgt'
	mappings['TargetGT_PROMPT']  = 'newgt'
	mappings['ReferenceGT_HLT']  	= 'gt'
	mappings['ReferenceGT_EXPRESS'] = 'gt'
	mappings['ReferenceGT_PROMPT']  = 'gt'
	mappings['Dataset']			= 'ds'

def build_HLT_workflow(args):
	hlt_dict = dict()
	hlt_dict['HLT_release'] = args['HLT_release']
	hlt_dict['PR_release'] = args['PR_release']
	options = hlt_dict['options'] = dict()
	if round(args['b_field'])==0: options['B0T'] = ""
	if "Cosmics" in args['class']: options['cosmics'] = ""
	if args['HLT_release'] != args['PR_release']: 
		options['recoCmsswDir'] = args['PR_release']
	options['HLTCustomMenu'] = None if args['HLT_Type'] == 'GRun' else "orcoff:"+args['hlt_key']
	options['HLT'] 			 = args['HLT_Type']
	options['Type'] 		 = "HLT+RECO"
	options['ds']			 = args['Dataset']
	options['basegt']		 = args['TargetGT_PROMPT']
	options['gt']			 = args['ReferenceGT_HLT']
	options['newgt']		 = args['TargetGT_HLT']
	options['runLs']		 = ast.literal_eval(args['Run'])
	options['jira']		 	 = args['Jira']
	return hlt_dict

def build_Express_workflow(args):
	express_dict = dict()
	express_dict['Expr_release'] = args['Expr_release']
	options = express_dict['options'] = dict()
	if round(args['b_field'])==0: options['B0T'] = ""
	if "Cosmics" in args['class']: options['cosmics'] = ""
	options['Type'] 		 = "EXPR"
	options['ds']			 = args['Dataset']
	options['gt']			 = args['ReferenceGT_EXPRESS']
	options['newgt']		 = args['TargetGT_EXPRESS']
	options['runLs']		 = ast.literal_eval(args['Run'])
	options['jira']		 	 = args['Jira']
	options['two_WFs']		 = ""
	return express_dict

def build_Prompt_workflow(args):
	prompt_dict = dict()
	prompt_dict['PR_release'] = args['PR_release']
	options = prompt_dict['options'] = dict()
	if round(args['b_field'])==0: options['B0T'] = ""
	if "Cosmics" in args['class']: options['cosmics'] = ""
	options['Type'] 		 = "PR"
	options['ds']			 = args['Dataset']
	options['gt']			 = args['ReferenceGT_PROMPT']
	options['newgt']		 = args['TargetGT_PROMPT']
	options['runLs']		 = ast.literal_eval(args['Run'])
	options['jira']		 	 = str(args['Jira'])
	options['two_WFs']		 = ""
	return prompt_dict

def compose_email(args):
	title_text = "{Title} ({Week}, {Year})".format(Title = args['Title'], Week = args['Week'], Year = args['Year'])
	emailSubject = "[HLT/Express/Prompt] Full track validation of {}".format(title_text)
	emailBody = """Dear colleagues,
We are going to perform full track validation of {title_text}
Details of the workflow:
- Target HLT GT: {TargetGT_HLT}
- Reference HLT GT: {ReferenceGT_HLT}

- Target Express GT: {TargetGT_EXPRESS}
- Reference Express GT: {ReferenceGT_EXPRESS}

- Target Prompt GT: {TargetGT_PROMPT}
- Reference Prompt GT: {ReferenceGT_PROMPT}

- Run: {run_number} recorded on {start_date} with magnetic field {b_field}T
- HLT Menu: {hlt_key}
- CMSSW version: {HLT_release} for HLT/Express/Prompt
- Dataset: {Dataset}

The cmsDriver configuration for the submission is accessible here [2].
Validation details will be documented at [3].
Once the workflows are ready, we will ask the {Subsystem} validators to report the outcome of the checks at JIRA [4].

Best regards,
Pritam, Amandeep, Tamas, Francesco, Helena (for AlCa/DB)

[1] https://cmsoms.cern.ch/cms/runs/report?cms_run={run_number}&cms_run_sequence=GLOBAL-RUN
[2] %s
[3] https://twiki.cern.ch/twiki/bin/view/CMS/PdmVTriggerConditionValidation2021
[4] https://its.cern.ch/jira/browse/CMSALCA-{Jira}
""".format(title_text=title_text, **args)
	args['emailSubject'] = emailSubject
	args['emailBody'] = emailBody
	return args

def create_emailConfig(args):
	configfile = open("email.txt", "w")
	configfile.write("Subject: %s"%args['emailSubject'])
	configfile.write("\nFrom: AlCaDB Team <alcadb.user@cern.ch>\n")
	configfile.write(args['emailBody'])
	configfile.close()

def check_requirements():
	import pkg_resources
	required = list()
	with open('requirements.txt', 'r') as f:
		for line in f:
			required.append(line.strip())

	installed_packages = pkg_resources.working_set
	packages = [i.key for i in installed_packages]
	print(packages, required)
	for pkg in required:
		if not pkg in packages:
			os.system("pip3 install {} --user".format(pkg))

def extract_keys(args):
	"""Extract keys from run-registry"""
	def get_date(raw_time):
		return datetime.strptime(raw_time, '%Y-%m-%dT%H:%M:%SZ').strftime('%b-%d %Y')
	run = get_run(args['run_number'])
	oms = run['oms_attributes']
	args['cmssw_version'] = oms['cmssw_version']
	args['b_field']     = float(oms['b_field'])
	args['start_time']  = oms['start_time']
	args['start_date']  = get_date(oms['start_time'])
	args['class']		= run['class']
	if not 'CMSSW' in args['HLT_release'] : args['HLT_release'] = oms['cmssw_version']
	if not 'CMSSW' in args['PR_release']  : args['PR_release']  = oms['cmssw_version']
	if not 'CMSSW' in args['Expr_release']: args['Expr_release']  = oms['cmssw_version']
	if args['HLT_release'] != oms['cmssw_version']: 
		args['HLT_Type'] = "GRun"
		args['hlt_key']  = "the GRun menu for %s" %args['HLT_release']
	else:
		args['HLT_Type'] = "Custom"
		args['hlt_key']  = oms['hlt_key']
	return args

def get_user():
	"""Set username and password for """
	if not parsedArgs.user: 
		parsedArgs.user = getuser()
	if not (parsedArgs.password or parsedArgs.pat):
		parsedArgs.password = getpass(prompt="Password of user '%s' for Jira: "% parsedArgs.user)

if __name__ == '__main__':
	get_user()					# set user and password for Jira
	args = get_arguments()
	args = extract_keys(args)
	try:
		api = JiraAPI(args, parsedArgs.user, parsedArgs.password)
		ticket = api.check_duplicate()
		if not ticket:
			args["Jira"]= int(api.get_key().split('-')[1].strip())+1
			print(">> Labels not matching with any older ticket. CMSALCA-{} will be created at later stage.".format(args["Jira"]))
		else:
			args["Jira"] = int(ticket.split('-')[1].strip())
	except:
		if args["Jira"] == 'None':
			raise ValueError("Check Error message. Provide ticket number in input template if you are facing error accessing Jira site")
		print(">> Jira site is not accessible. Ticket number is taken from input template. CMSALCA-%s" %args["Jira"])

	hlt_dict 	 = build_HLT_workflow(args)
	express_dict = build_Express_workflow(args)
	prompt_dict  = build_Prompt_workflow(args)

	for data, wid in zip([hlt_dict, express_dict, prompt_dict], ['HLT', 'Express', 'Prompt']):
		rfile = open("metadata_{}.json".format(wid), 'w')
		json.dump(data, rfile, indent=2)
		rfile.close()

	args = compose_email(args)
	jsonfile = open('envs.json', 'w')
	json.dump(args, jsonfile, indent=2)
	jsonfile.close()
