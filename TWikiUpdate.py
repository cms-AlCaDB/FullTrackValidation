#!/bin/env python3

## Script for updating TWiki documentation
## 
## Author: Pritam Kalbhor (physics.pritam@gmail.com)
##

import os, sys, glob, time, json, pdb, ast
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.firefox.options import Options

from argparse import ArgumentParser
parser = ArgumentParser(description="Options for batch run")
parser.add_argument('--headless', action="store_true", dest='headless', help='Do things without opening browser')
args = parser.parse_known_args()[0]

options = Options()
options.setAcceptInsecureCerts = True
options.setAcceptUntrustedCertificates = True
options.setAssumeUntrustedCertificateIssuer = False
options.headless = args.headless

# options.binary = os.path.join(os.environ['HOME'], ".local/firefox/firefox") 
# provide path of geckodriver for firefox
# sys.path.append(os.path.join(os.environ['HOME'], ".local/bin"))

url = "https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVTriggerConditionValidation2021"

class AccessFirefox:
	def __init__(self):
		self.profile_path = os.path.join(os.environ['HOME'],'.mozilla/firefox')
		self.profile_name = 'alcauser'
		self.profile_file = self.get_profile_file()
		options.profile = self.profile_file
		self.browser = webdriver.Firefox(options=options)
		self.wait = WebDriverWait(self.browser, 50)

	def get_profile_file(self):
		if not os.path.exists(self.profile_path):
			raise FileNotFoundError('Please create a firefox profile named %s'%self.profile_name)
		files = glob.glob(self.profile_path+'/*'+self.profile_name)
		pfile = str(*files)
		if os.path.exists(pfile): return pfile

	def login(self, url):
		"""Require SSL certificate for login"""
		self.browser.get(url)
		xpath = '//*[@id="ctl00_ctl00_NICEMasterPageBodyContent_SiteContentPlaceholder_hlCertificateAuth"]'
		text = '//*[ text() = "Sign in using your CERN Certificate" ]'
		self.wait.until(presence_of_element_located((By.XPATH, xpath)))
		self.browser.find_element(By.XPATH, xpath).click()
		print("Login done!")

	def copy_page_content(self):
		edit_key = '/html/body/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/span[2]/span[1]/a'
		self.wait.until(presence_of_element_located((By.XPATH, edit_key)))
		self.browser.find_element(By.XPATH, edit_key).click()
		topic = self.browser.find_element(By.XPATH, '//*[@id="topic"]').get_attribute("value")
		return topic

	def append_section(self, section):
		OriginalText = self.browser.find_element(By.XPATH, '//*[@id="topic"]').get_attribute("value")
		OriginalText = OriginalText.strip().strip("%MyButtons%")
		NewText = OriginalText + section
		topic = self.browser.find_element(By.XPATH, '//*[@id="topic"]')
		self.browser.execute_script("arguments[0].value=arguments[1];", topic, NewText)
		topic.submit()

def get_config_for_twiki():
	from modules.jira_api import get_workflow_id_names
	campID, wf_names = get_workflow_id_names()
	envs = json.load(open('envs.json'))
	return {'campID':campID, 'wf_names':wf_names, 'envs':envs}

def compose_section(campID, wf_names, envs, dqm={}, **kwargs):
	"""Compose twiki section"""
	section = '\n\n---++ %s' %envs['Week']
	section += '\n---+++ %s\n' %envs['Title']
	section += '\n*Description*: %s\n' %envs['emailSubject']
	section += '\n%StartTwisty%'

	dmytro = 'https://dmytro.web.cern.ch/dmytro/cmsprodmon/requests.php?campaign='
	section += '\n*Campaign IDs and JIRA link*: '
	section += '\n   * *HLT Campaign*: [[{0}{1}][{1}]]'.format(dmytro, str(*campID['HLT']))
	section += '\n   * *Express Campaign*: [[{0}{1}][{1}]]'.format(dmytro, str(*campID['EXPR']))
	section += '\n   * *Prompt Campaign*: [[{0}{1}][{1}]]'.format(dmytro, str(*campID['PR']))
	section += '\n   * *Jira*: [[https://its.cern.ch/jira/browse/CMSALCA-{jira}][CMSALCA-{jira}]]\n'.format(jira=envs['Jira'])

	section += '\n*Hypernews links*: '
	section += '\n   * *New tag validation request*: [[][]]'
	section += '\n   * *Request email with full details about validation*: [[][]]'
	section += '\n   * *Data-ops email after submission of relvals*: [[][]]'
	section += '\n   * *Email after the new tag is deployed*: [[][]]'

	# GT table
	conddb = 'https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/'
	GTdiff = 'https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts'
	HLTdiff  = '{0}/{1}/{2}'.format(GTdiff, envs['TargetGT_HLT'], envs['ReferenceGT_HLT'])
	PRdiff   = '{0}/{1}/{2}'.format(GTdiff, envs['TargetGT_PROMPT'], envs['ReferenceGT_PROMPT'])
	EXPRdiff = '{0}/{1}/{2}'.format(GTdiff, envs['TargetGT_EXPRESS'], envs['ReferenceGT_EXPRESS'])
	section += '\n*Details for the workflows*:  \n   * *Dataset*: %s' % envs['Dataset']
	
	for run, LS in ast.literal_eval(envs['Run']).items():
		section += '\n   * *Run/s*: %s, LS: %s recorded on %s with B-field %s' % (run, LS, envs['start_date'], envs['b_field'])
	section += '\n   * *HLT Key*: %s' % envs['hlt_key']
	section += '\n   * *CMSSW*: %s\n' % envs['HLT_release']
	section += '\n| *Conditions Type* | *HLT* | *Prompt* | *Express* |'
	section += '\n| Target | [[{0}{1}][{1}]] | [[{0}{2}][{2}]] | [[{0}{3}][{3}]] |'.format(
		conddb, envs['TargetGT_HLT'], envs['TargetGT_PROMPT'], envs['TargetGT_EXPRESS']
		)
	section += '\n| Reference | [[{0}{1}][{1}]] | [[{0}{2}][{2}]] | [[{0}{3}][{3}]] |'.format(
		conddb, envs['ReferenceGT_HLT'], envs['ReferenceGT_PROMPT'], envs['ReferenceGT_EXPRESS']
		)
	section += '\n| Common | [[{0}{1}][{1}]] | | |'.format(conddb, envs['TargetGT_PROMPT'])
	section += '\n| | [[{1}{0} | [[{2}{0}  | [[{3}{0} |'.format('][Target vs Reference]]', HLTdiff, PRdiff, EXPRdiff)

	# Request Manager Workflow table
	reqmgr = 'https://cmsweb.cern.ch/reqmgr2/fetch?rid='
	section += '\n\n| *Workflow* | *Description* | *PD* | *Workflow name* | *DQM Plots* | *Overlay* |'
	count = 1
	for dataset in envs['Dataset'].split(','):
		for condition, ckey in [('HLT', 'HLT'), ('Express', 'EXPR'), ('Prompt', 'PR')]:
			for Type in ('newconditions', 'reference'):
				section += '\n|WF%s| %s %s | %s | %s | %s | %s |'%(
					 count, 
					 condition, 
					 Type, 
					 dataset if count%6==1 else '^', 
					 '[[{0}{1}][{1}]]'.format(reqmgr, wf_names[ckey+'_'+Type[:5]]),
					 '[[%s][%s]]' % (dqm[ckey+'_'+Type[:5]], 'DQM'),
					 '[[%s][%s]]' % (dqm[ckey], 'Overlay plots') if count%2==1 else '^' 
					)
				count += 1
	section += '\n%ENDTWISTY%'
	section += '\n%MyButtons%'
	return section

def get_DQM_links(envs, **kwargs):
	"""Create DQM links. Inputs needed are
	1) workflow_config.json file which contains configuration of the submission
	2) envs dictionary containing input information of run_number"""
	ifile = 'workflow_config.json'	
	if os.path.exists(ifile):
		config = json.load(open(ifile))
	else:
		raise FileNotFoundError('Create %s by submitting relval for production' %ifile)

	dataset = dict()
	for section in config.keys():
		sec = section.split('_')[:2]
		wtype = ('_').join((sec[0], sec[1][:5])).strip()
		cmssw = config[section]['Config']['CMSSWVersion']
		pstring = config[section]['Config']['ProcessingString']
		dname = config[section]['Config']['Task1']['InputDataset'].split('/')[1].strip()
		dataset[wtype] = '/'+ dname +'/'+ cmssw +'-'+ pstring +'-v1/DQMIO'

	links = dict.fromkeys(dataset)
	s1 = 'https://cmsweb.cern.ch/dqm/relval/start?runnr=%s;' % envs['run_number']
	s3 = 'workspace=Everything'
	s4 = 'referencepos=ratiooverlay;referenceshow=all;referencenorm=True;'
	for key in links.keys():
		s2 = 'dataset=%s;' % dataset[key]
		links[key] = s1 + s2 + s3
	for key in ('HLT', 'EXPR', 'PR'):
		s2 = 'dataset=%s;' % dataset[key+'_newco']
		s5 = 'referenceobj1=other%3A%3A{}%3A%3A;'.format(dataset[key+'_refer'])
		links[key.split('_')[0].strip()] = s1 + s2 + s4 + s5 + s3 

	return links

#--------------------------------------------------------------------------

if __name__ == '__main__':
	instance = AccessFirefox()
	print("Trying to open TWiki.cern.ch")
	instance.login(url)
	OrignalTopic = instance.copy_page_content()

	config = get_config_for_twiki()
	links = get_DQM_links(**config)
	NewSection = compose_section(**config, dqm=links)
	instance.append_section(NewSection)
	instance.browser.quit()


	#------------------------------------------------------------------------

