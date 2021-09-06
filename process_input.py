#!/bin/env python3
import glob, os, sys, json, ast
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import runregistry
from modules.jira_api import JiraAPI

def get_input():
	files = glob.glob("Validations/*.txt")
	files.sort(key=os.path.getmtime)
	return files[0] 

def get_run(run_number):
	run = runregistry.get_run(run_number=int(run_number))
	# print(run['oms_attributes'].keys())
	return run

def get_arguments():
	file="_NewValidation.txt"
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
	Label = "_".join(args['Labels'])
	args['Week']  = "{}".format(week[0])
	args['Year']  = "{}".format(year[0])
	args['Label'] = "{}".format(Label)
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

def build_HLT_workflow(args, run):
	hlt_dict = dict()
	oms = run['oms_attributes']

	if args['HLT_release'] == 'None':
		hlt_dict['HLT_release'] = oms['cmssw_version']
		hlt_dict['PR_release'] = oms['cmssw_version']
	else:
		hlt_dict['HLT_release'] = args['HLT_release']
		hlt_dict['PR_release'] = args['PR_release']
	options = hlt_dict['options'] = dict()
	if round(oms['b_field'])==0:
		options['B0T'] = ""
	if run['class']=="Cosmics21CRUZET":
		options['cosmics'] = ""
	options['HLT'] 			 = "Custom"
	options['Type'] 		 = "HLT+RECO"
	options['HLTCustomMenu'] = "orcoff:"+oms['hlt_key']
	options['ds']			 = args['Dataset']
	options['basegt']		 = args['ReferenceGT_PROMPT']
	options['gt']			 = args['ReferenceGT_HLT']
	options['newgt']		 = args['TargetGT_HLT']
	options['runLs']		 = ast.literal_eval(args['Run'])
	options['jira']		 	 = args['Jira']
	return hlt_dict

def build_Express_workflow(args, run):
	express_dict = dict()
	oms = run['oms_attributes']

	if args['HLT_release'] == 'None':
		express_dict['HLT_release'] = oms['cmssw_version']
		express_dict['PR_release'] = oms['cmssw_version']
	else:
		express_dict['HLT_release'] = args['HLT_release']
		express_dict['PR_release'] = args['PR_release']
	options = express_dict['options'] = dict()
	if round(oms['b_field'])==0:
		options['B0T'] = ""
	if run['class']=="Cosmics21CRUZET":
		options['cosmics'] = ""
	options['HLT'] 			 = "Custom"
	options['Type'] 		 = "EXPR+RECO"
	options['HLTCustomMenu'] = "orcoff:"+oms['hlt_key']
	options['ds']			 = args['Dataset']
	options['basegt']		 = args['ReferenceGT_PROMPT']
	options['gt']			 = args['ReferenceGT_EXPRESS']
	options['newgt']		 = args['TargetGT_EXPRESS']
	options['runLs']		 = ast.literal_eval(args['Run'])
	options['jira']		 	 = args['Jira']
	return express_dict

def build_Prompt_workflow(args, run):
	prompt_dict = dict()
	oms = run['oms_attributes']

	if args['PR_release'] == 'None':
		prompt_dict['PR_release'] = oms['cmssw_version']
	else:
		prompt_dict['PR_release'] = args['PR_release']
	options = prompt_dict['options'] = dict()
	if round(oms['b_field'])==0:
		options['B0T'] = ""
	if run['class']=="Cosmics21CRUZET":
		options['cosmics'] = ""
	options['Type'] 		 = "PR"
	options['ds']			 = args['Dataset']
	options['gt']			 = args['ReferenceGT_PROMPT']
	options['newgt']		 = args['TargetGT_PROMPT']
	options['runLs']		 = ast.literal_eval(args['Run'])
	options['jira']		 	 = str(args['Jira'])
	options['two_WFs']		 = ""
	return prompt_dict

def compose_email(args):
	emailSubject = "[HLT/EXPRESS/PROMPT] Full track validation of {Title} ({Week}, {Year})".format(Title = args['Title'], Week = args['Week'], Year = args['Year'])
	emailBody = """Dear colleaques,
We are going to perform {emailSubject}
Details of the workflow:
- Target HLT GT: {TargetGT_HLT}
- Reference HLT GT: {ReferenceGT_HLT}

- Target EXPRESS GT: {TargetGT_EXPRESS}
- Reference EXPRESS GT: {ReferenceGT_EXPRESS}

- Target PROMPT GT: {TargetGT_PROMPT}
- Reference PROMPT GT: {ReferenceGT_PROMPT}

- The data chosen for validation is from {class}, run {run_number}
- HLT Menu: {hlt_key}
- CMSSW version to be used: {HLT_release} for HLT/EXPRESS/PROMPT
- The chosen datasets are: {Dataset}

{Subsystem} experts are invited to scrutinize the results as well at [2].
Once the workflows are ready, we will ask the {Subsystem} validators to report the outcome of the checks at JIRA [3]

Best regards,
Pritam, Amandeep, Francesco, Tamas, Helena (for AlCa/DB)

[1] https://cmsoms.cern.ch/cms/runs/report?cms_run={run_number}&cms_run_sequence=GLOBAL-RUN
[2] https://twiki.cern.ch/twiki/bin/view/CMS/PdmVTriggerConditionValidation2021
[3] https://its.cern.ch/jira/browse/CMSALCA-{Jira}
""".format(emailSubject=emailSubject, **args)
	args['emailSubject'] = emailSubject
	args['emailBody'] = emailBody
	return args

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

if __name__ == '__main__':
	args  = get_arguments()

	sysArgs = sys.argv
	api = JiraAPI(args, sysArgs[1], sysArgs[2])
	ticket = api.check_duplicate()
	if not ticket: 
		args["Jira"]= int(api.get_key().split('-')[1].strip())+1
		print(">> Labels not matching with any older ticket. CMSALCA-{} will be created at later stage.".format(args["Jira"]))
	else:
		args["Jira"] = int(ticket.split('-')[1].strip())

	try:
		run = get_run(args['run_number'])
	except:
		run = {'class': args['class']}
		run['oms_attributes'] = {'cmssw_version': args['HLT_release'],
								 'b_field': int(args['b_field']),
								 'hlt_key': args['hlt_key']
								}

	hlt_dict 	 = build_HLT_workflow(args, run)
	express_dict = build_Express_workflow(args, run)
	prompt_dict  = build_Prompt_workflow(args, run)

	for data, wid in zip([hlt_dict, express_dict, prompt_dict], ['HLT', 'Express', 'Prompt']):
		rfile = open("metadata_{}.json".format(wid), 'w')
		json.dump(data, rfile, indent=2)
		rfile.close()

	args = compose_email(args)

	jsonfile = open('envs.json', 'w')
	json.dump(args, jsonfile, indent=2)