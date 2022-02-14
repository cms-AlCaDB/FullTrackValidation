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
options.set_preference('security.sandbox.content.level', 3)

import config.environment
url = os.getenv('TWIKI')

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
		print(">> Copying page content ...")
		edit_key = '/html/body/div/div/div/div[1]/div/div[1]/div[1]/div[2]/div[1]/span[2]/span[1]/a'
		self.wait.until(presence_of_element_located((By.XPATH, edit_key)))
		self.browser.find_element(By.XPATH, edit_key).click()
		try:
			topic = self.browser.find_element(By.XPATH, '//*[@id="topic"]').get_attribute("value")
		except:
			self.browser.find_element(By.XPATH, '/html/body/div/div/div/div[1]/div[1]/div/div/div[2]/form[2]/input[4]').click()
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
	dmytro = 'https://dmytro.web.cern.ch/dmytro/cmsprodmon/requests.php?campaign='
	conddb = 'https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/'
	GTdiff = 'https://cms-conddb.cern.ch/cmsDbBrowser/diff/Prod/gts'
	reqmgr = 'https://cmsweb.cern.ch/reqmgr2/fetch?rid='
	daslink= 'https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod/global&input=summary+dataset='
	HLT = ('HLT', str(*campID['HLT']))
	PR = ('Prompt', str(*campID['PR']))
	EXPR = ('Express', str(*campID['EXPR']))

	section = '\n\n---++ Week %s' %envs['Week'].strip('Week').strip()
	section += '\n---+++ %s\n' %envs['Title']
	section += '\n*Description*: %s\n' %envs['emailSubject']
	section += '\n%StartTwisty%'

	section += '\n*Campaign IDs and JIRA link*: '
	for wf, campaign in (HLT, PR, EXPR): 
		if not wf in envs['WorkflowsToSubmit'].split('/'): continue
		section += '\n   * *{2} Campaign*: [[{0}{1}][{1}]]'.format(dmytro, campaign, wf)
	section += '\n   * *Jira*: [[https://its.cern.ch/jira/browse/CMSALCA-{jira}][CMSALCA-{jira}]]\n'.format(jira=envs['Jira'])

	section += '\n*Hypernews links*: '
	section += '\n   * *New tag validation request*: [[{0}][{0}]]'.format(envs['ValidationRequest'])
	section += '\n   * *Request email with full details about validation*: [[][]]'
	section += '\n   * *Email after the new tag is deployed*: [[][]]'

	section += '\n\n*Details for the workflows*:  \n   * *Dataset*: %s' % envs['Dataset']
	for run, LS in ast.literal_eval(envs['Run']).items():
		section += '\n   * *Run/s*: %s, LS: %s recorded on %s with B-field %sT' % (run, LS, envs['start_date'], envs['b_field'])
	section += '\n   * *HLT Key*: %s' % envs['hlt_key']
	section += '\n   * *CMSSW*: %s\n' % envs['HLT_release']

	# GT table
	section += '\n%TABLE{ caption="Conditions Table" valign="middle" headeralign="center"}%'
	c1 = '\n| *Conditions Type* |'; c2 = '\n| Target |'; c3 = '\n| Reference |'; c4 = '\n| Common |'; c5 = '\n| |'
	for wf, campID in (HLT, PR, EXPR):
		if not wf in envs['WorkflowsToSubmit']: continue
		c1 += ' *%s* |'% wf
		c2 += ' [[{0}{1}][{1}]] |'.format(conddb, envs['TargetGT_%s' % wf])
		c3 += ' [[{0}{1}][{1}]] |'.format(conddb, envs['ReferenceGT_%s' % wf])
		c4 += ' [[{0}{1}][{1}]] |'.format(conddb, envs['TargetGT_Prompt']) if wf=='HLT' else ' |'
		c5 += ' [[{0}][{1}]] |'.format('%s/%s/%s' %(GTdiff, envs['TargetGT_%s' % wf], envs['ReferenceGT_%s' % wf]), 'Target vs Reference')
	section += c1 + c2 + c3 + c4 + c5 if 'HLT' in envs['WorkflowsToSubmit'] else c1 + c2 + c3 + c5

	# Request Manager Workflow table
	section += '\n\n%TABLE{ caption="Workflows Table" valign="middle" headeralign="center" dataalign="center,left,left,left,center,center"}%'
	section += '\n| *Index* | *PD* | *Description* | *Workflow name* | *DQM Plots* | *Overlay* |'

	CondList = ['New Conditions', 'Reference Conditions'] if envs['NewOrReference']=='Both' else ['New Conditions'] if envs['NewOrReference']=='New' else ['Reference Conditions']
	count = 1; pd_sect = len(envs['WorkflowsToSubmit'].split('/'))*len(CondList)
	for dataset in envs['Dataset'].split(','):
		dname = dataset.split('/')[1].strip()
		for condition, ckey in [('HLT', 'HLT'), ('Express', 'EXPR'), ('Prompt', 'PR')]:
			if not condition in envs['WorkflowsToSubmit']: continue
			for Type in CondList:
				section += '\n|WF%s| %s | %s %s | %s | %s | %s |'%(
					count,
					'[[{0}{1}+run={2}][{1}]]'.format(daslink, dataset, envs['run_number']) if (count%pd_sect==1 or pd_sect==1) else '^',
					condition,
					Type,
					'[[{0}{1}][{1}]]'.format(reqmgr, wf_names[ckey+'_'+Type.replace(' ', '').lower()[:5]+'_'+dname]),
					'[[%s][%s]]' % (dqm[ckey+'_'+Type.replace(' ', '').lower()[:5]+'_'+dname], 'DQM'),
					'[[%s][%s]]' % (dqm[condition+'_'+dname], 'Overlay plots') if (count%len(CondList)==1 and len(CondList)==2) else '^' 
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
		sec = section.split('_')[:3]
		wtype = ('_').join([sec[0], sec[1][:5], sec[2]]).strip()
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

	if envs['NewOrReference']=='Both':
		for ds in envs['Dataset'].split(','):
			dname = ds.split('/')[1].strip()
			for key, wf in [('HLT', 'HLT'), ('EXPR', 'Express'), ('PR', 'Prompt')]:
				if not wf in envs['WorkflowsToSubmit']: continue
				s2 = 'dataset=%s;' % dataset[key+'_newco_'+dname]
				s5 = 'referenceobj1=other%3A%3A{}%3A%3A;'.format(dataset[key+'_refer_'+dname])
				links[wf+'_'+dname] = s1 + s2 + s4 + s5 + s3
	return links

#--------------------------------------------------------------------------

if __name__ == '__main__':
	try:
		instance = AccessFirefox()
		print("Trying to open TWiki.cern.ch")
		instance.login(url)
		OrignalTopic = instance.copy_page_content()

		config = get_config_for_twiki()
		links = get_DQM_links(**config)
		NewSection = compose_section(dqm=links, **config)
		instance.append_section(NewSection)
	except Exception as e:
		print(e)
	finally:
		instance.browser.quit()

	#------------------------------------------------------------------------